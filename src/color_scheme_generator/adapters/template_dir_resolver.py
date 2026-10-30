from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

from color_scheme_generator.domain.enums import ColorFormat
from color_scheme_generator.domain.exceptions import ConfigResolutionError

_PACKAGE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_TEMPLATES_DIR = _PACKAGE_DIR / "defaults" / "templates"
_ENV_VAR = "COLORSCHEME_TEMPLATES_TEMPLATES_DIR"
_XDG_SUBDIR = "color-scheme-generator"
_TEMPLATE_PREFIX = "colors."
_TEMPLATE_SUFFIX = ".j2"


def template_name_for(fmt: ColorFormat) -> str:
    """Return the catalog template filename for *fmt* (``colors.<fmt>.j2``)."""
    return f"{_TEMPLATE_PREFIX}{fmt.value}{_TEMPLATE_SUFFIX}"


def has_csg_templates(dir_path: Path) -> bool:
    """True when *dir_path* holds at least one csg ``colors.*.j2`` template.

    BUG-002: a ``templates/`` directory discovered in the CWD is not
    necessarily a csg catalog. The AGS selector app ships
    ``templates/ags-app/``; accepting that directory made ``csg generate``
    render nothing and exit 0.
    """
    if not dir_path.is_dir():
        return False
    try:
        entries = dir_path.iterdir()
    except OSError:
        return False
    return any(
        entry.is_file()
        and entry.name.startswith(_TEMPLATE_PREFIX)
        and entry.suffix == _TEMPLATE_SUFFIX
        for entry in entries
    )


def missing_template_names(
    dir_path: Path, formats: Iterable[ColorFormat]
) -> tuple[str, ...]:
    """Return the requested ``colors.<fmt>.j2`` templates absent from *dir_path*."""
    return tuple(
        name
        for name in (template_name_for(fmt) for fmt in formats)
        if not (dir_path / name).is_file()
    )


def _require_catalog(path: Path, source: str) -> Path:
    """Validate an explicitly requested templates directory, or fail loudly."""
    if not path.is_dir():
        raise ConfigResolutionError(
            "templates_dir",
            f"{source} is not a directory: {path}",
        )
    if not has_csg_templates(path):
        raise ConfigResolutionError(
            "templates_dir",
            f"{source} is not a csg template catalog "
            f"(no colors.*.j2 templates found): {path}",
        )
    return path


class TemplateDirResolver:
    """Resolve a templates directory that is guaranteed to hold a csg catalog.

    Discovery order stays ``--templates-dir`` > env > CWD ``templates/`` (up
    to three parents) > XDG > packaged defaults. Unlike the old resolver, a
    discovered candidate is only accepted when it contains at least one
    ``colors.*.j2`` template; a decoy directory falls through to the next
    source. Explicit CLI/env paths fail with :class:`ConfigResolutionError`
    instead of silently falling back.
    """

    def resolve(self, settings_dir: Path | None = None) -> Path:
        if settings_dir is not None:
            return _require_catalog(
                Path(settings_dir).expanduser().resolve(), "--templates-dir"
            )

        env_value = os.environ.get(_ENV_VAR)
        if env_value:
            return _require_catalog(Path(env_value).expanduser().resolve(), _ENV_VAR)

        for candidate in self._cwd_candidates():
            if has_csg_templates(candidate):
                return candidate.resolve()

        xdg_home = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
        candidate = xdg_home / _XDG_SUBDIR / "templates"
        if has_csg_templates(candidate):
            return candidate.resolve()

        if not has_csg_templates(_DEFAULT_TEMPLATES_DIR):
            raise ConfigResolutionError(
                "templates_dir",
                "Packaged template catalog is missing or has no colors.*.j2 "
                f"templates: {_DEFAULT_TEMPLATES_DIR}",
            )
        return _DEFAULT_TEMPLATES_DIR.resolve()

    @staticmethod
    def _cwd_candidates() -> Iterable[Path]:
        cwd = Path.cwd()
        yield cwd / "templates"
        for parent in tuple(cwd.parents)[:3]:
            yield parent / "templates"
