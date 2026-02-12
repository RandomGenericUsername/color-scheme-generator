"""Tests for the template loader."""

from pathlib import Path

from color_scheme_templates.loader import TemplateLoader, discover_templates_in_dir
from color_scheme_templates.registry import TemplateRegistry


class TestDiscoverTemplatesInDir:
    """Tests for discover_templates_in_dir function."""

    def test_finds_j2_files(self, sample_templates_dir: Path) -> None:
        templates = discover_templates_in_dir(sample_templates_dir)
        assert "colors.css.j2" in templates
        assert "colors.json.j2" in templates

    def test_ignores_non_j2(self, tmp_path: Path) -> None:
        (tmp_path / "readme.md").write_text("# Readme")
        (tmp_path / "template.j2").write_text("")
        templates = discover_templates_in_dir(tmp_path)
        assert templates == ["template.j2"]

    def test_returns_empty_for_missing(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing"
        assert discover_templates_in_dir(missing) == []


class TestTemplateLoader:
    """Tests for TemplateLoader class."""

    def test_discovers_package_templates(self, sample_templates_dir: Path) -> None:
        TemplateRegistry.register(namespace="core", templates_dir=sample_templates_dir)
        loader = TemplateLoader()
        layers = loader.discover_layers()
        assert len(layers) == 1
        assert layers[0].layer == "package"
        assert "colors.css.j2" in layers[0].templates

    def test_discovers_project_templates(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        templates = project / "templates"
        templates.mkdir()
        (templates / "custom.j2").write_text("")

        loader = TemplateLoader(project_root=project)
        layers = loader.discover_layers()
        project_layers = [layer for layer in layers if layer.layer == "project"]
        assert len(project_layers) == 1
        assert "custom.j2" in project_layers[0].templates

    def test_layer_priority_order(
        self, sample_templates_dir: Path, tmp_path: Path
    ) -> None:
        TemplateRegistry.register(namespace="core", templates_dir=sample_templates_dir)

        project = tmp_path / "project"
        project.mkdir()
        (project / "templates").mkdir()
        (project / "templates" / "proj.j2").write_text("")

        user = tmp_path / "user"
        user.mkdir()
        (user / "user.j2").write_text("")

        loader = TemplateLoader(project_root=project, user_templates_path=user)
        layers = loader.discover_layers()
        layer_names = [layer.layer for layer in layers]
        assert layer_names == ["package", "project", "user"]
