"""Tests for templates module public API."""

from pathlib import Path

import pytest

from color_scheme_templates import (
    configure,
    get_template,
    list_templates,
    reload_templates,
    reset,
)
from color_scheme_templates.errors import TemplateNotFoundError


class TestConfigureAndLoad:
    """Tests for configure and load_templates public API."""

    def test_configure_sets_project_root(self, tmp_path: Path) -> None:
        """Test that configure sets the project root."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        templates_dir = project_root / "templates"
        templates_dir.mkdir()
        (templates_dir / "test.j2").write_text("test")

        configure(project_root=project_root)
        resolver = reload_templates()
        templates = resolver.list_all()
        assert "test.j2" in templates

    def test_configure_sets_user_templates_path(self, tmp_path: Path) -> None:
        """Test that configure sets user templates path."""
        user_path = tmp_path / "user_templates"
        user_path.mkdir()
        (user_path / "custom.j2").write_text("custom")

        configure(user_templates_path=user_path)
        resolver = reload_templates()
        templates = resolver.list_all()
        assert "custom.j2" in templates

    def test_get_template_retrieves_template(self, sample_templates_dir: Path) -> None:
        """Test getting a template by name."""
        configure(project_root=sample_templates_dir.parent)
        template_path = get_template("colors.css.j2")
        assert template_path.exists()
        assert template_path.name == "colors.css.j2"

    def test_get_template_not_found(self, sample_templates_dir: Path) -> None:
        """Test that getting non-existent template raises error."""
        configure(project_root=sample_templates_dir.parent)
        with pytest.raises(TemplateNotFoundError):
            get_template("nonexistent.j2")

    def test_list_templates_returns_all(self, sample_templates_dir: Path) -> None:
        """Test listing all available templates."""
        configure(project_root=sample_templates_dir.parent)
        templates = list_templates()
        assert "colors.css.j2" in templates
        assert "colors.json.j2" in templates
        assert len(templates) >= 2

    def test_reload_templates_clears_cache(self, sample_templates_dir: Path) -> None:
        """Test that reload_templates clears the cached resolver."""
        configure(project_root=sample_templates_dir.parent)
        templates1 = list_templates()
        assert len(templates1) > 0

        # Reload and verify we get a fresh instance
        reloaded = reload_templates()
        templates2 = reloaded.list_all()
        assert templates1 == templates2

    def test_reset_clears_state(self, sample_templates_dir: Path) -> None:
        """Test that reset clears all state."""
        configure(project_root=sample_templates_dir.parent)
        templates_before = list_templates()
        assert len(templates_before) > 0

        reset()

        # After reset, without reconfiguring, should get empty templates
        templates_after = list_templates()
        assert len(templates_after) == 0


class TestGlobalState:
    """Tests for global state management."""

    def test_load_templates_caches_resolver(self, sample_templates_dir: Path) -> None:
        """Test that load_templates caches the resolver."""
        from color_scheme_templates import load_templates

        configure(project_root=sample_templates_dir.parent)
        resolver1 = load_templates()
        resolver2 = load_templates()
        assert resolver1 is resolver2

    def test_configure_resets_cache(self, sample_templates_dir: Path) -> None:
        """Test that calling configure resets the cached resolver."""
        from color_scheme_templates import load_templates

        configure(project_root=sample_templates_dir.parent)
        resolver1 = load_templates()

        # Reconfigure
        other_path = sample_templates_dir.parent / "other"
        other_path.mkdir(exist_ok=True)
        configure(project_root=other_path)
        resolver2 = load_templates()

        # Should be different resolver instances
        assert resolver1 is not resolver2

    def test_multiple_configure_calls(self, tmp_path: Path) -> None:
        """Test that multiple configure calls work correctly."""
        path1 = tmp_path / "path1"
        path2 = tmp_path / "path2"
        path1.mkdir()
        path2.mkdir()

        (path1 / "templates").mkdir()
        (path1 / "templates" / "t1.j2").write_text("t1")
        (path2 / "templates").mkdir()
        (path2 / "templates" / "t2.j2").write_text("t2")

        # First configuration
        configure(project_root=path1)
        templates1 = list_templates()
        assert "t1.j2" in templates1

        # Second configuration
        configure(project_root=path2)
        templates2 = list_templates()
        assert "t2.j2" in templates2
        assert "t1.j2" not in templates2
