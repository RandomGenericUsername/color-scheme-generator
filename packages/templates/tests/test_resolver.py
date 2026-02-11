"""Tests for the template resolver."""

from pathlib import Path

import pytest

from color_scheme_templates.errors import TemplateNotFoundError
from color_scheme_templates.loader import TemplateLayer
from color_scheme_templates.resolver import TemplateResolver


@pytest.fixture
def multi_layer(tmp_path: Path) -> tuple[list[TemplateLayer], Path, Path]:
    """Create multi-layer setup."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "colors.css.j2").write_text("/* pkg */")
    (pkg / "pkg_only.j2").write_text("")

    user = tmp_path / "user"
    user.mkdir()
    (user / "colors.css.j2").write_text("/* user */")
    (user / "user_only.j2").write_text("")

    layers = [
        TemplateLayer(
            layer="package",
            namespace="core",
            templates_dir=pkg,
            templates=["colors.css.j2", "pkg_only.j2"],
        ),
        TemplateLayer(
            layer="user",
            namespace="user",
            templates_dir=user,
            templates=["colors.css.j2", "user_only.j2"],
        ),
    ]
    return layers, pkg, user


class TestTemplateResolver:
    """Tests for TemplateResolver class."""

    def test_resolve_returns_highest_priority(
        self, multi_layer: tuple[list[TemplateLayer], Path, Path]
    ) -> None:
        layers, pkg, user = multi_layer
        resolver = TemplateResolver(layers)
        result = resolver.resolve("colors.css.j2")
        assert result == user / "colors.css.j2"

    def test_resolve_falls_back(
        self, multi_layer: tuple[list[TemplateLayer], Path, Path]
    ) -> None:
        layers, pkg, user = multi_layer
        resolver = TemplateResolver(layers)
        result = resolver.resolve("pkg_only.j2")
        assert result == pkg / "pkg_only.j2"

    def test_resolve_raises_not_found(
        self, multi_layer: tuple[list[TemplateLayer], Path, Path]
    ) -> None:
        layers, _, _ = multi_layer
        resolver = TemplateResolver(layers)
        with pytest.raises(TemplateNotFoundError, match="nonexistent.j2"):
            resolver.resolve("nonexistent.j2")

    def test_list_all(
        self, multi_layer: tuple[list[TemplateLayer], Path, Path]
    ) -> None:
        layers, pkg, user = multi_layer
        resolver = TemplateResolver(layers)
        all_templates = resolver.list_all()
        assert "colors.css.j2" in all_templates
        assert "pkg_only.j2" in all_templates
        assert "user_only.j2" in all_templates
        # colors.css.j2 should resolve to user (higher priority)
        assert all_templates["colors.css.j2"] == user / "colors.css.j2"
