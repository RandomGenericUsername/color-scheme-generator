from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from color_scheme_generator.adapters.template_dir_resolver import TemplateDirResolver
from color_scheme_generator.domain.exceptions import ConfigResolutionError
from color_scheme_generator.ports.template_dir_resolver import TemplateDirResolverPort


def _write_catalog(templates_dir: Path, *names: str) -> Path:
    templates_dir.mkdir(parents=True, exist_ok=True)
    for name in names or ("colors.json.j2",):
        (templates_dir / name).write_text("{{ background.hex }}\n", encoding="utf-8")
    return templates_dir


def _packaged_catalog() -> Path:
    return (
        Path(__file__).resolve().parent.parent.parent.parent
        / "src"
        / "color_scheme_generator"
        / "defaults"
        / "templates"
    ).resolve()


class TestTemplateDirResolver:
    def test_resolve_uses_env_var_first(self, tmp_path: Path) -> None:
        templates_dir = _write_catalog(tmp_path / "custom-templates")

        with patch.dict(os.environ, {"COLORSCHEME_TEMPLATES_TEMPLATES_DIR": str(templates_dir)}):
            resolver = TemplateDirResolver()
            result = resolver.resolve()

        assert result == templates_dir.resolve()

    def test_resolve_falls_back_to_xdg(self, tmp_path: Path) -> None:
        xdg_config = tmp_path / "xdg-config"
        templates_dir = _write_catalog(
            xdg_config / "color-scheme-generator" / "templates"
        )

        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg_config)}):
            resolver = TemplateDirResolver()
            result = resolver.resolve()

        assert result == templates_dir.resolve()

    def test_resolve_falls_back_to_package_defaults(self) -> None:
        resolver = TemplateDirResolver()
        result = resolver.resolve()

        assert result == _packaged_catalog()

    def test_decoy_cwd_templates_is_not_selected(self, tmp_path: Path) -> None:
        """BUG-002: ``templates/`` from the AGS selector is not a csg catalog."""
        app_dir = tmp_path / "wallpaper-selector"
        (app_dir / "templates" / "ags-app").mkdir(parents=True)

        with patch("pathlib.Path.cwd", return_value=app_dir):
            resolver = TemplateDirResolver()
            result = resolver.resolve()

        assert result == _packaged_catalog()
        assert list(result.glob("colors.*.j2"))

    def test_decoy_cwd_templates_falls_through_to_parent_catalog(
        self, tmp_path: Path
    ) -> None:
        parent_catalog = _write_catalog(tmp_path / "templates")
        app_dir = tmp_path / "app"
        (app_dir / "templates" / "ags-app").mkdir(parents=True)

        with patch("pathlib.Path.cwd", return_value=app_dir):
            resolver = TemplateDirResolver()
            result = resolver.resolve()

        assert result == parent_catalog.resolve()

    def test_explicit_templates_dir_without_catalog_raises(self, tmp_path: Path) -> None:
        decoy = tmp_path / "templates"
        (decoy / "ags-app").mkdir(parents=True)

        with pytest.raises(ConfigResolutionError) as exc_info:
            TemplateDirResolver().resolve(settings_dir=decoy)

        assert exc_info.value.key == "templates_dir"
        assert "not a csg template catalog" in exc_info.value.reason
        assert str(decoy) in exc_info.value.reason

    def test_env_templates_dir_without_catalog_raises(self, tmp_path: Path) -> None:
        decoy = tmp_path / "templates"
        (decoy / "ags-app").mkdir(parents=True)

        with patch.dict(os.environ, {"COLORSCHEME_TEMPLATES_TEMPLATES_DIR": str(decoy)}):
            with pytest.raises(ConfigResolutionError) as exc_info:
                TemplateDirResolver().resolve()

        assert exc_info.value.key == "templates_dir"
        assert "COLORSCHEME_TEMPLATES_TEMPLATES_DIR" in exc_info.value.reason

    def test_explicit_missing_templates_dir_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ConfigResolutionError) as exc_info:
            TemplateDirResolver().resolve(settings_dir=tmp_path / "missing")

        assert "is not a directory" in exc_info.value.reason

    def test_structural_subtyping(self) -> None:
        resolver = TemplateDirResolver()
        assert isinstance(resolver, TemplateDirResolverPort)
