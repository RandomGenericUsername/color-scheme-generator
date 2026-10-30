from __future__ import annotations

import json
import logging
import os
import tempfile
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from oci_runtime import engine_qualified_image

from color_scheme_generator.adapters.template_dir_resolver import (
    missing_template_names,
)
from color_scheme_generator.domain.enums import Backend, ColorFormat
from color_scheme_generator.domain.exceptions import (
    ConfigResolutionError,
    ContainerImageNotFoundError,
    ContainerTimeoutError,
    InvalidImageError,
)
from color_scheme_generator.domain.models import (
    Color,
    ColorScheme,
    ContainerMount,
    GenerationResult,
    ManagedContainer,
)

logger = logging.getLogger(__name__)

_CONTAINER_ENV = {
    "HOME": "/tmp",
    "XDG_CONFIG_HOME": "/tmp/.config",
    "XDG_CACHE_HOME": "/tmp/.cache",
    "COLORSCHEME_CONFIG_FILE_PATH": "/csg-config/settings.toml",
    "COLORSCHEME_TEMPLATES_TEMPLATES_DIR": "/templates",
    "COLORSCHEME__RUNTIME__MODE": "local",
}

_BOOT_ID_PATH = Path("/proc/sys/kernel/random/boot_id")
_MANAGED_LABEL = "csg.managed"
_SWEEP_GRACE_SECONDS = 60


def _read_boot_id() -> str:
    """Return the host boot id, or "" when the host does not expose it."""
    try:
        with _BOOT_ID_PATH.open("r", encoding="utf-8") as handle:
            return handle.readline().strip()
    except OSError:
        return ""


def _parse_container_timestamp(raw: str | None) -> datetime | None:
    """Parse an engine or label timestamp, returning an aware UTC datetime."""
    if not raw:
        return None
    value = raw.strip()
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


if TYPE_CHECKING:
    from color_scheme_generator.adapters.template_dir_resolver import TemplateDirResolver
    from color_scheme_generator.domain.models import (
        AppSettings,
        GenerationRequest,
    )
    from color_scheme_generator.ports.container_runtime import ContainerRuntimePort


class ContainerProcessor:
    def __init__(
        self,
        container_runtime: ContainerRuntimePort,
        template_dir_resolver: TemplateDirResolver | None = None,
        default_settings_path: Path | None = None,
        engine_value: str | None = None,
        templates_dir: Path | str | None = None,
    ) -> None:
        self._container_runtime = container_runtime
        self._template_dir_resolver = template_dir_resolver
        self._default_settings_path = default_settings_path
        self._engine_value = engine_value
        # Explicit CLI --templates-dir (main.py): wins over every resolver
        # chain branch below, so the container bind-mounts the SAME dir the
        # local processor would render from. Without it, container mode
        # silently ignored the flag and mounted resolver defaults instead.
        self._templates_dir = Path(templates_dir) if templates_dir is not None else None

    def _select_image(self, settings: AppSettings, backend_value: str) -> str:
        prefix = settings.container.image_prefix
        tag = settings.container.image_tag
        engine = self._engine_value or settings.container.engine
        base = f"{prefix}-{backend_value}"
        return engine_qualified_image(base, engine, tag)

    def _serialize_settings(self, settings: AppSettings) -> str:
        lines: list[str] = []
        def kv(key: str, value: object) -> None:
            if value is None:
                lines.append(f"# {key} = null")
            elif isinstance(value, bool):
                lines.append(f"{key} = {'true' if value else 'false'}")
            elif isinstance(value, (int, float)):
                lines.append(f"{key} = {value}")
            else:
                escaped = str(value).replace("\\", "\\\\").replace("\"", "\\\"")
                lines.append(f"{key} = \"{escaped}\"")

        lines.append("[output]")
        kv("directory", str(settings.output.directory))
        fmt_list = ", ".join(
            f'"{f.value}"' if isinstance(f, ColorFormat) else f'"{f}"'
            for f in settings.output.default_formats
        )
        lines.append(f"default_formats = [{fmt_list}]")
        kv("overwrite", settings.output.overwrite)
        kv("apply_to_terminal", settings.output.apply_to_terminal)
        lines.append("")
        lines.append("[generation]")
        kv("backend", settings.generation.backend.value)
        if settings.generation.default_params:
            lines.append("default_params = {")
            for k, v in settings.generation.default_params.items():
                ev = str(v).replace("\\", "\\\\").replace("\"", "\\\"")
                lines.append(f"  \"{k}\" = \"{ev}\",")
            lines.append("}")
        lines.append("")
        lines.append("[runtime]")
        # The inner `csg generate` always runs locally inside the container,
        # regardless of the outer settings' runtime mode. Force it explicitly
        # rather than relying on _CONTAINER_ENV to correct it.
        kv("mode", "local")
        lines.append("")
        lines.append("[container]")
        kv("engine", settings.container.engine)
        kv("image_prefix", settings.container.image_prefix)
        kv("image_tag", settings.container.image_tag)
        kv("timeout_seconds", settings.container.timeout_seconds)
        kv("memory_limit", settings.container.memory_limit)
        return "\n".join(lines) + "\n"

    def _parse_color_scheme_from_json(self, raw: str) -> ColorScheme | None:
        if not raw.strip():
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        try:
            return ColorScheme(
                background=Color(data["background"]["hex"], tuple(data["background"]["rgb"])),
                foreground=Color(data["foreground"]["hex"], tuple(data["foreground"]["rgb"])),
                cursor=Color(data["cursor"]["hex"], tuple(data["cursor"]["rgb"])),
                colors=tuple(
                    Color(c["hex"], tuple(c["rgb"])) for c in data["colors"]
                ),
                source_image=Path(data["source_image"]),
                backend=Backend(data["backend"]),
                generated_at=datetime.fromisoformat(data["generated_at"]),
            )
        except (KeyError, TypeError, ValueError):
            return None

    def _resolve_templates_dir(
        self, formats: tuple[ColorFormat, ...] = ()
    ) -> Path:
        """Templates dir for the /templates bind-mount, validated before use.

        Precedence: explicit CLI ``--templates-dir`` > resolver chain >
        settings-adjacent defaults > system path. The explicit branch is
        what makes ``csg generate --templates-dir <dir> --runtime
        container`` mount the requested dir instead of silently mounting
        resolver defaults (the container previously ignored the flag).

        BUG-002: every requested ``colors.<fmt>.j2`` template must exist
        before the directory is mounted. Mounting a decoy ``templates/``
        produced an inner empty success and an outer exit 0.
        """
        if self._templates_dir is not None:
            templates_dir = self._templates_dir
        elif self._template_dir_resolver:
            templates_dir = self._template_dir_resolver.resolve()
        elif self._default_settings_path:
            templates_dir = (
                self._default_settings_path.parent / "defaults" / "templates"
            )
        else:
            templates_dir = Path(
                "/usr/share/color-scheme-generator/templates"
            )
        if not templates_dir.is_dir():
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
        missing = missing_template_names(templates_dir, formats)
        if missing:
            raise ConfigResolutionError(
                "templates_dir",
                f"Templates directory {templates_dir} is missing requested "
                f"template(s): {', '.join(missing)}",
            )
        return templates_dir

    @staticmethod
    def _build_wrapper_labels(settings: AppSettings, session_id: str) -> dict[str, str]:
        labels = {
            "csg.managed": "true",
            "csg.session": session_id,
            "csg.created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "csg.timeout_seconds": str(settings.container.timeout_seconds),
        }
        boot_id = _read_boot_id()
        if boot_id:
            labels["csg.boot_id"] = boot_id
        return labels

    @staticmethod
    def _container_created_at(container: ManagedContainer) -> datetime | None:
        created = _parse_container_timestamp(container.created)
        if created is not None:
            return created
        return _parse_container_timestamp(container.labels.get("csg.created_at"))

    def _sweep_stale_containers(self, settings: AppSettings, session_id: str) -> None:
        """Best-effort removal of csg-owned wrappers left by a crashed run."""
        try:
            candidates = self._container_runtime.list_containers(
                filters={"label": "csg.managed=true"},
                show_all=True,
            )
        except Exception as exc:
            logger.warning("Skipping stale csg container sweep; inventory failed: %s", exc)
            return

        current_boot_id = _read_boot_id()
        now = datetime.now(UTC)

        for candidate in candidates:
            try:
                container = self._container_runtime.inspect_container(candidate.name)
            except Exception as exc:
                logger.warning(
                    "Skipping csg container %s; inspect failed: %s",
                    candidate.name,
                    exc,
                )
                continue

            labels = container.labels
            if labels.get(_MANAGED_LABEL) != "true":
                continue
            if labels.get("csg.session") == session_id:
                continue

            previous_boot = (
                current_boot_id
                and labels.get("csg.boot_id")
                and labels["csg.boot_id"] != current_boot_id
            )
            if previous_boot:
                reason = "previous boot"
            else:
                created = self._container_created_at(container)
                if created is None:
                    logger.debug("Skipping csg container %s; age is unknown", container.name)
                    continue

                timeout_seconds = settings.container.timeout_seconds
                raw_timeout = labels.get("csg.timeout_seconds")
                if raw_timeout:
                    try:
                        timeout_seconds = int(raw_timeout)
                    except ValueError:
                        logger.debug(
                            "Invalid csg.timeout_seconds on %s; using settings timeout",
                            container.name,
                        )

                age = now - created
                if age <= timedelta(seconds=timeout_seconds + _SWEEP_GRACE_SECONDS):
                    continue
                reason = (
                    f"age {age.total_seconds():.0f}s exceeds "
                    f"{timeout_seconds + _SWEEP_GRACE_SECONDS}s"
                )

            try:
                self._container_runtime.remove_container(container.name, force=True)
                logger.info("Removed stale csg container %s (%s)", container.name, reason)
            except Exception as exc:
                logger.warning(
                    "Failed to remove stale csg container %s: %s",
                    container.name,
                    exc,
                )

    def process_generate(
        self, request: GenerationRequest, settings: AppSettings
    ) -> GenerationResult:
        start = time.monotonic()
        temp_toml_path: Path | None = None
        session_id = str(uuid.uuid4())
        labels = self._build_wrapper_labels(settings, session_id)

        try:
            image = self._select_image(settings, request.config.backend.value)

            self._sweep_stale_containers(settings, session_id)

            if not self._container_runtime.image_exists(image):
                raise ContainerImageNotFoundError(image, request.config.backend)

            input_parent = request.image_path.resolve().parent
            if input_parent == Path("/"):
                raise InvalidImageError(
                    request.image_path,
                    "Cannot mount filesystem root as input directory",
                )

            if not request.image_path.is_file():
                raise FileNotFoundError(f"Input image not found: {request.image_path}")

            output_dir = request.config.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            templates_dir = self._resolve_templates_dir(request.config.formats)

            toml_content = self._serialize_settings(settings)
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".toml", mode="w"
            ) as f:
                f.write(toml_content)
                temp_toml_path = Path(f.name)

            try:
                os.chmod(temp_toml_path, 0o644)
            except OSError:
                logger.warning("Failed to chmod temp config file: %s", temp_toml_path)

            mounts = [
                ContainerMount(
                    source=input_parent,
                    target=PurePosixPath("/input"),
                    read_only=True,
                ),
                ContainerMount(
                    source=output_dir,
                    target=PurePosixPath("/output"),
                    read_only=False,
                ),
                ContainerMount(
                    source=temp_toml_path,
                    target=PurePosixPath("/csg-config/settings.toml"),
                    read_only=True,
                ),
                ContainerMount(
                    source=templates_dir,
                    target=PurePosixPath("/templates"),
                    read_only=True,
                ),
            ]

            inner_command = [
                "csg",
                "generate",
                f"/input/{request.image_path.name}",
                "--backend",
                request.config.backend.value,
            ]
            for key, value in request.config.params.items():
                inner_command.extend(["--param", f"{key}={value}"])
            for fmt in request.config.formats:
                inner_command.extend(["--format", fmt.value])
            inner_command.extend(["-o", "/output"])
            command_str = " ".join(inner_command)

            try:
                container_result = self._container_runtime.run(
                    image=image,
                    command=inner_command,
                    mounts=mounts,
                    timeout=settings.container.timeout_seconds,
                    environment=_CONTAINER_ENV,
                    memory_limit=settings.container.memory_limit,
                    labels=labels,
                )
            except ContainerTimeoutError:
                raise
            except Exception as exc:
                from color_scheme_generator.adapters.error_mapping import map_oci_error

                raise map_oci_error(exc, backend=request.config.backend) from exc

            duration = time.monotonic() - start

            inner: dict[str, object] = {}
            inner_parse_error = ""
            if container_result.stdout.strip():
                try:
                    parsed = json.loads(container_result.stdout)
                except json.JSONDecodeError as exc:
                    inner_parse_error = f"inner csg returned invalid JSON: {exc}"
                else:
                    if isinstance(parsed, dict):
                        inner = parsed
                    else:
                        inner_parse_error = "inner csg JSON output is not an object"
            else:
                inner_parse_error = "inner csg produced no JSON output"

            cs_data = inner.get("color_scheme")
            if cs_data and isinstance(cs_data, dict):
                from color_scheme_generator.domain.models import Color as _Color
                color_scheme = ColorScheme(
                    background=_Color(
                        cs_data["background"]["hex"], tuple(cs_data["background"]["rgb"])
                    ),
                    foreground=_Color(
                        cs_data["foreground"]["hex"], tuple(cs_data["foreground"]["rgb"])
                    ),
                    cursor=_Color(cs_data["cursor"]["hex"], tuple(cs_data["cursor"]["rgb"])),
                    colors=tuple(_Color(c["hex"], tuple(c["rgb"])) for c in cs_data["colors"]),
                    source_image=request.image_path.resolve(),
                    backend=Backend(cs_data["backend"]),
                    generated_at=datetime.fromisoformat(cs_data["generated_at"]),
                )
            else:
                color_scheme = None

            # BUG-002: success is the conjunction of the container exit code,
            # the inner csg result, and every requested artifact landing on
            # the host. A decoy templates mount used to yield rc 0, an empty
            # `output_files`, and a false success.
            host_output = request.config.output_dir
            expected_names = [
                f"colors.{fmt.value}" for fmt in request.config.formats
            ]
            missing_names = [
                name for name in expected_names
                if not (host_output / name).is_file()
            ]
            output_files = tuple(
                host_output / name for name in expected_names
                if (host_output / name).is_file()
            )

            errors: list[str] = []
            if container_result.return_code != 0:
                errors.append(
                    f"container exited with code {container_result.return_code}"
                )
            if inner_parse_error:
                errors.append(inner_parse_error)
            elif inner.get("success") is not True:
                detail_parts: list[str] = []
                inner_stderr = str(inner.get("stderr") or "").strip()
                if inner_stderr:
                    detail_parts.append(inner_stderr)
                inner_errors = inner.get("errors")
                if isinstance(inner_errors, list):
                    detail_parts.extend(str(item) for item in inner_errors)
                detail = f": {'; '.join(detail_parts)}" if detail_parts else ""
                errors.append(f"inner csg reported success=false{detail}")
            if missing_names:
                errors.append(
                    "missing requested artifact(s) in "
                    f"{host_output}: {', '.join(missing_names)}"
                )

            stderr_parts: list[str] = []
            if container_result.stderr.strip():
                stderr_parts.append(container_result.stderr.strip())
            inner_stderr_raw = inner.get("stderr")
            if inner_stderr_raw:
                stderr_parts.append(str(inner_stderr_raw).strip())
            stderr_parts.extend(errors)

            success = not errors
            return GenerationResult(
                success=success,
                color_scheme=color_scheme,
                output_files=output_files,
                backend=request.config.backend,
                stderr="\n".join(part for part in stderr_parts if part),
                return_code=(
                    container_result.return_code
                    if container_result.return_code != 0
                    else (0 if success else 1)
                ),
                duration=duration,
                command=command_str,
                stdout=container_result.stdout,
                errors=tuple(errors),
            )

        except ContainerTimeoutError:
            return GenerationResult(
                success=False,
                color_scheme=None,
                output_files=(),
                backend=request.config.backend,
                stderr="Container execution timed out",
                return_code=-1,
                duration=time.monotonic() - start,
                errors=("Container execution timed out",),
            )
        finally:
            if temp_toml_path is not None and temp_toml_path.exists():
                temp_toml_path.unlink()

    def process_show(
        self, request: GenerationRequest, settings: AppSettings
    ) -> GenerationResult:
        start = time.monotonic()
        temp_toml_path: Path | None = None
        session_id = str(uuid.uuid4())
        labels = self._build_wrapper_labels(settings, session_id)

        try:
            image = self._select_image(settings, request.config.backend.value)

            self._sweep_stale_containers(settings, session_id)

            if not self._container_runtime.image_exists(image):
                raise ContainerImageNotFoundError(image, request.config.backend)

            input_parent = request.image_path.resolve().parent
            if input_parent == Path("/"):
                raise InvalidImageError(
                    request.image_path,
                    "Cannot mount filesystem root as input directory",
                )

            if not request.image_path.is_file():
                raise FileNotFoundError(f"Input image not found: {request.image_path}")

            templates_dir = self._resolve_templates_dir()

            toml_content = self._serialize_settings(settings)
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".toml", mode="w"
            ) as f:
                f.write(toml_content)
                temp_toml_path = Path(f.name)

            try:
                os.chmod(temp_toml_path, 0o644)
            except OSError:
                logger.warning("Failed to chmod temp config file: %s", temp_toml_path)

            mounts = [
                ContainerMount(
                    source=input_parent,
                    target=PurePosixPath("/input"),
                    read_only=True,
                ),
                ContainerMount(
                    source=temp_toml_path,
                    target=PurePosixPath("/csg-config/settings.toml"),
                    read_only=True,
                ),
                ContainerMount(
                    source=templates_dir,
                    target=PurePosixPath("/templates"),
                    read_only=True,
                ),
            ]

            inner_command = [
                "csg",
                "show",
                f"/input/{request.image_path.name}",
                "--backend",
                request.config.backend.value,
            ]
            for key, value in request.config.params.items():
                inner_command.extend(["--param", f"{key}={value}"])
            command_str = " ".join(inner_command)

            try:
                container_result = self._container_runtime.run(
                    image=image,
                    command=inner_command,
                    mounts=mounts,
                    timeout=settings.container.timeout_seconds,
                    environment=_CONTAINER_ENV,
                    memory_limit=settings.container.memory_limit,
                    labels=labels,
                )
            except ContainerTimeoutError:
                raise
            except Exception as exc:
                from color_scheme_generator.adapters.error_mapping import map_oci_error

                raise map_oci_error(exc, backend=request.config.backend) from exc

            duration = time.monotonic() - start

            color_scheme = self._parse_color_scheme_from_json(container_result.stdout)
            if color_scheme is not None:
                from dataclasses import replace
                color_scheme = replace(color_scheme, source_image=request.image_path.resolve())

            return GenerationResult(
                success=container_result.return_code == 0,
                color_scheme=color_scheme,
                output_files=(),
                backend=request.config.backend,
                stderr=container_result.stderr,
                return_code=container_result.return_code,
                duration=duration,
                command=command_str,
                stdout=container_result.stdout,
            )

        except ContainerTimeoutError:
            return GenerationResult(
                success=False,
                color_scheme=None,
                output_files=(),
                backend=request.config.backend,
                stderr="Container execution timed out",
                return_code=-1,
                duration=time.monotonic() - start,
            )
        finally:
            if temp_toml_path is not None and temp_toml_path.exists():
                temp_toml_path.unlink()
