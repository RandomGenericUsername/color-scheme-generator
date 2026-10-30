from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath

import pytest

from color_scheme_generator.adapters import container_processor as container_processor_module
from color_scheme_generator.adapters.container_processor import ContainerProcessor
from color_scheme_generator.domain.enums import Backend, ColorFormat, RuntimeMode
from color_scheme_generator.domain.exceptions import ContainerImageNotFoundError
from color_scheme_generator.domain.models import (
    AppSettings,
    ContainerMount,
    ContainerSettings,
    GenerationRequest,
    GenerationSettings,
    GeneratorConfig,
    ManagedContainer,
    OutputSettings,
    RuntimeSettings,
)


@dataclass
class _FakeRunResult:
    return_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.1


class _SweepRuntime:
    def __init__(
        self,
        containers: list[ManagedContainer] | None = None,
        *,
        image_exists: bool = True,
        list_error: Exception | None = None,
        inspect_errors: dict[str, Exception] | None = None,
        remove_errors: dict[str, Exception] | None = None,
    ) -> None:
        self.containers = {container.name: container for container in containers or []}
        self._image_exists = image_exists
        self._list_error = list_error
        self._inspect_errors = inspect_errors or {}
        self._remove_errors = remove_errors or {}
        self.calls: list[tuple[str, object]] = []
        self.run_calls: list[dict[str, object]] = []
        self.run_labels: dict[str, str] | None = None

    def list_containers(
        self,
        filters: dict[str, str] | None = None,
        show_all: bool = True,
    ) -> list[ManagedContainer]:
        self.calls.append(("list", {"filters": filters, "show_all": show_all}))
        if self._list_error is not None:
            raise self._list_error
        return list(self.containers.values())

    def inspect_container(self, name: str) -> ManagedContainer:
        self.calls.append(("inspect", name))
        error = self._inspect_errors.get(name)
        if error is not None:
            raise error
        return self.containers[name]

    def remove_container(self, name: str, force: bool = True) -> None:
        self.calls.append(("remove", {"name": name, "force": force}))
        error = self._remove_errors.get(name)
        if error is not None:
            raise error
        self.containers.pop(name, None)

    def image_exists(self, image: str) -> bool:
        self.calls.append(("image_exists", image))
        return self._image_exists

    def run(
        self,
        image: str,
        command: list[str],
        mounts: list[ContainerMount],
        timeout: int,
        environment: dict[str, str] | None = None,
        memory_limit: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> _FakeRunResult:
        self.calls.append(("run", image))
        self.run_labels = labels
        self.run_calls.append(
            {
                "image": image,
                "command": command,
                "mounts": mounts,
                "timeout": timeout,
                "environment": environment,
                "memory_limit": memory_limit,
                "labels": labels,
            }
        )
        for mount in mounts:
            if not mount.read_only and mount.target == PurePosixPath("/output"):
                source = Path(mount.source)
                source.mkdir(parents=True, exist_ok=True)
                (source / "colors.json").write_text("dummy")
        return _FakeRunResult(
            stdout=json.dumps(
                {"success": True, "output_files": ["/output/colors.json"]}
            )
        )

    def call_names(self) -> list[str]:
        return [name for name, _ in self.calls]


@pytest.fixture(autouse=True)
def _stub_boot_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(container_processor_module, "_read_boot_id", lambda: "boot-current")


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.isoformat().replace("+00:00", "Z")


def _managed_container(
    name: str,
    *,
    age_seconds: float = 0,
    boot_id: str | None = "boot-current",
    timeout_seconds: int = 60,
    engine_created: str | None = "auto",
    label_overrides: dict[str, str] | None = None,
) -> ManagedContainer:
    created_at = _rfc3339(_utc_now() - timedelta(seconds=age_seconds))
    labels = {
        "csg.managed": "true",
        "csg.session": "stale-session",
        "csg.created_at": created_at,
        "csg.timeout_seconds": str(timeout_seconds),
    }
    if boot_id is not None:
        labels["csg.boot_id"] = boot_id
    if label_overrides is not None:
        labels.update(label_overrides)
    created = created_at if engine_created == "auto" else engine_created
    return ManagedContainer(name=name, state="exited", labels=labels, created=created)


def _settings(timeout_seconds: int = 60) -> AppSettings:
    return AppSettings(
        output=OutputSettings(
            directory=Path("/tmp/out"),
            default_formats=(),
            overwrite=True,
        ),
        generation=GenerationSettings(backend=Backend.CUSTOM, default_params={}),
        runtime=RuntimeSettings(mode=RuntimeMode.CONTAINER),
        container=ContainerSettings(
            engine="podman",
            image_prefix="csg",
            image_tag="v0.2.0",
            timeout_seconds=timeout_seconds,
            memory_limit="512m",
        ),
    )


def _make_processor(
    tmp_path: Path,
    runtime: _SweepRuntime,
    *,
    timeout_seconds: int = 60,
) -> tuple[ContainerProcessor, AppSettings, GenerationRequest, Path]:
    image = tmp_path / "wallpaper.png"
    image.write_text("dummy")
    templates = tmp_path / "templates"
    templates.mkdir()
    (templates / "colors.json.j2").write_text(
        "{{ background.hex }}\n", encoding="utf-8"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    processor = ContainerProcessor(runtime, templates_dir=templates)
    request = GenerationRequest(
        image_path=image,
        config=GeneratorConfig(
            backend=Backend.CUSTOM,
            params={},
            formats=(ColorFormat.JSON,),
            output_dir=output_dir,
        ),
    )
    return processor, _settings(timeout_seconds), request, output_dir


def _assert_wrapper_labels(labels: dict[str, str] | None, timeout_seconds: int) -> None:
    assert labels is not None
    assert labels["csg.managed"] == "true"
    assert uuid.UUID(labels["csg.session"])
    assert labels["csg.timeout_seconds"] == str(timeout_seconds)
    parsed = datetime.fromisoformat(labels["csg.created_at"].replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    assert labels["csg.boot_id"] == "boot-current"


class TestWrapperLabels:
    def test_generate_labels_the_wrapper_and_sweeps_first(self, tmp_path: Path) -> None:
        runtime = _SweepRuntime()
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_generate(request, settings)

        assert result.success is True
        _assert_wrapper_labels(runtime.run_labels, 60)
        assert runtime.call_names()[0] == "list"
        assert runtime.call_names()[1] == "image_exists"
        assert "run" in runtime.call_names()

    def test_show_labels_the_wrapper(self, tmp_path: Path) -> None:
        runtime = _SweepRuntime()
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_show(request, settings)

        assert result.success is True
        _assert_wrapper_labels(runtime.run_labels, 60)
        assert runtime.run_calls[0]["command"][1] == "show"  # type: ignore[index]

    def test_boot_id_label_omitted_when_not_readable(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(container_processor_module, "_read_boot_id", lambda: "")
        runtime = _SweepRuntime()
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        processor.process_generate(request, settings)

        assert runtime.run_labels is not None
        assert "csg.boot_id" not in runtime.run_labels


class TestStaleSweep:
    def test_normal_run_leaves_no_wrapper(self, tmp_path: Path) -> None:
        runtime = _SweepRuntime()
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_generate(request, settings)

        assert result.success is True
        assert runtime.containers == {}
        assert "remove" not in runtime.call_names()

    def test_stale_same_boot_wrapper_removed_and_run_succeeds(self, tmp_path: Path) -> None:
        stale = _managed_container("csg-stale", age_seconds=125)
        runtime = _SweepRuntime([stale])
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_generate(request, settings)

        assert result.success is True
        assert "csg-stale" not in runtime.containers
        assert ("remove", {"name": "csg-stale", "force": True}) in runtime.calls
        assert runtime.run_calls

    def test_previous_boot_wrapper_removed_immediately(self, tmp_path: Path) -> None:
        previous_boot = _managed_container(
            "csg-previous-boot", age_seconds=5, boot_id="boot-previous"
        )
        runtime = _SweepRuntime([previous_boot])
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_generate(request, settings)

        assert result.success is True
        assert "csg-previous-boot" not in runtime.containers
        assert ("remove", {"name": "csg-previous-boot", "force": True}) in runtime.calls

    def test_young_same_boot_wrapper_kept(self, tmp_path: Path) -> None:
        young = _managed_container("csg-young", age_seconds=30)
        runtime = _SweepRuntime([young])
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_generate(request, settings)

        assert result.success is True
        assert "csg-young" in runtime.containers
        assert "remove" not in runtime.call_names()

    def test_unparseable_age_is_skipped(self, tmp_path: Path) -> None:
        unknown = ManagedContainer(
            name="csg-unknown-age",
            state="exited",
            labels={
                "csg.managed": "true",
                "csg.session": "stale-session",
                "csg.created_at": "not-a-timestamp",
                "csg.timeout_seconds": "60",
                "csg.boot_id": "boot-current",
            },
            created="also-not-a-timestamp",
        )
        runtime = _SweepRuntime([unknown])
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_generate(request, settings)

        assert result.success is True
        assert "csg-unknown-age" in runtime.containers
        assert "remove" not in runtime.call_names()

    def test_created_at_label_is_the_fallback_age_source(self, tmp_path: Path) -> None:
        stale = _managed_container("csg-label-age", age_seconds=125, engine_created=None)
        runtime = _SweepRuntime([stale])
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_generate(request, settings)

        assert result.success is True
        assert "csg-label-age" not in runtime.containers

    def test_invalid_timeout_label_falls_back_to_settings_timeout(self, tmp_path: Path) -> None:
        borderline = _managed_container(
            "csg-borderline",
            age_seconds=100,
            timeout_seconds=60,
            label_overrides={"csg.timeout_seconds": "not-an-int"},
        )
        runtime = _SweepRuntime([borderline])
        processor, settings, request, _ = _make_processor(tmp_path, runtime, timeout_seconds=60)

        result = processor.process_generate(request, settings)

        assert result.success is True
        # 60 s settings timeout + 60 s grace keeps a 100 s old container.
        assert "csg-borderline" in runtime.containers

    def test_unlabelled_and_foreign_containers_untouched(self, tmp_path: Path) -> None:
        now = _rfc3339(_utc_now() - timedelta(hours=1))
        unlabelled = ManagedContainer(
            name="manual-csg-image",
            state="running",
            labels={},
            created=now,
        )
        foreign = ManagedContainer(
            name="foreign-labelled",
            state="running",
            labels={"other.tool": "true"},
            created=now,
        )
        managed_without_flag = ManagedContainer(
            name="managed-false",
            state="exited",
            labels={"csg.managed": "false", "csg.session": "other"},
            created=now,
        )
        runtime = _SweepRuntime([unlabelled, foreign, managed_without_flag])
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_generate(request, settings)

        assert result.success is True
        assert set(runtime.containers) == {
            "manual-csg-image",
            "foreign-labelled",
            "managed-false",
        }
        assert "remove" not in runtime.call_names()

    def test_show_also_sweeps_stale_wrappers(self, tmp_path: Path) -> None:
        stale = _managed_container("csg-show-stale", age_seconds=125)
        runtime = _SweepRuntime([stale])
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        result = processor.process_show(request, settings)

        assert result.success is True
        assert "csg-show-stale" not in runtime.containers
        assert ("remove", {"name": "csg-show-stale", "force": True}) in runtime.calls


class TestBestEffort:
    def test_inventory_failure_does_not_block_generation(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        runtime = _SweepRuntime(list_error=RuntimeError("engine unavailable"))
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        caplog.set_level("WARNING")
        result = processor.process_generate(request, settings)

        assert result.success is True
        assert runtime.run_calls
        assert "inventory failed" in caplog.text

    def test_inspect_failure_does_not_block_generation(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        stale = _managed_container("csg-vanished", age_seconds=125)
        runtime = _SweepRuntime([stale], inspect_errors={"csg-vanished": RuntimeError("not found")})
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        caplog.set_level("WARNING")
        result = processor.process_generate(request, settings)

        assert result.success is True
        assert "csg-vanished" in runtime.containers
        assert runtime.run_calls
        assert "inspect failed" in caplog.text

    def test_remove_failure_does_not_block_generation(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        stale = _managed_container("csg-stuck", age_seconds=125)
        runtime = _SweepRuntime([stale], remove_errors={"csg-stuck": RuntimeError("in use")})
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        caplog.set_level("WARNING")
        result = processor.process_generate(request, settings)

        assert result.success is True
        assert "csg-stuck" in runtime.containers
        assert runtime.run_calls
        assert "Failed to remove stale csg container" in caplog.text

    def test_sweep_runs_before_image_preflight(self, tmp_path: Path) -> None:
        stale = _managed_container("csg-preflight-stale", age_seconds=125)
        runtime = _SweepRuntime([stale], image_exists=False)
        processor, settings, request, _ = _make_processor(tmp_path, runtime)

        with pytest.raises(ContainerImageNotFoundError):
            processor.process_generate(request, settings)

        assert "csg-preflight-stale" not in runtime.containers
        names = runtime.call_names()
        assert names.index("list") < names.index("inspect") < names.index("remove")
        assert names.index("remove") < names.index("image_exists")
        assert "run" not in names
