"""Tests for OutputManager."""

from pathlib import Path
from unittest.mock import patch

import pytest

from colorscheme_generator.config.enums import ColorFormat
from colorscheme_generator.core.exceptions import (
    OutputWriteError,
    TemplateRenderError,
)
from colorscheme_generator.core.managers.output_manager import OutputManager


class TestOutputManagerInit:
    """Test OutputManager initialization."""

    def test_init_with_config(self, mock_app_config):
        """Test initialization with config."""
        manager = OutputManager(mock_app_config)

        assert manager.settings == mock_app_config
        assert manager.template_env is not None
        assert manager.template_env.loader is not None



    def test_init_with_relative_template_dir(self, mock_app_config):
        """Test initialization with relative template directory."""
        # Set a relative path
        mock_app_config.templates.directory = Path("templates")
        manager = OutputManager(mock_app_config)

        # Should resolve to absolute path relative to package root
        assert manager.template_env.loader is not None


class TestOutputManagerWriteOutputs:
    """Test OutputManager write_outputs method."""

    def test_write_outputs_single_format(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test writing outputs in a single format."""
        manager = OutputManager(mock_app_config)
        output_dir = tmp_path / "output"

        # Mock template rendering
        with patch.object(manager, "_render_template") as mock_render:
            mock_render.return_value = '{"test": "content"}'

            output_files = manager.write_outputs(
                sample_color_scheme, output_dir, [ColorFormat.JSON]
            )

        assert len(output_files) == 1
        assert "json" in output_files
        assert output_files["json"].exists()
        assert output_files["json"].read_text() == '{"test": "content"}'

    def test_write_outputs_multiple_formats(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test writing outputs in multiple formats."""
        manager = OutputManager(mock_app_config)
        output_dir = tmp_path / "output"

        # Mock template rendering
        with patch.object(manager, "_render_template") as mock_render:
            mock_render.side_effect = [
                '{"test": "json"}',
                ".test { color: #000; }",
                "test: yaml",
            ]

            output_files = manager.write_outputs(
                sample_color_scheme,
                output_dir,
                [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.YAML],
            )

        assert len(output_files) == 3
        assert "json" in output_files
        assert "css" in output_files
        assert "yaml" in output_files
        assert output_files["json"].read_text() == '{"test": "json"}'
        assert output_files["css"].read_text() == ".test { color: #000; }"
        assert output_files["yaml"].read_text() == "test: yaml"

    def test_write_outputs_creates_directory(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test that output directory is created if it doesn't exist."""
        manager = OutputManager(mock_app_config)
        output_dir = tmp_path / "nested" / "output" / "dir"

        assert not output_dir.exists()

        with patch.object(manager, "_render_template") as mock_render:
            mock_render.return_value = "test"
            manager.write_outputs(
                sample_color_scheme, output_dir, [ColorFormat.JSON]
            )

        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_write_outputs_template_error(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test handling of template rendering errors."""
        manager = OutputManager(mock_app_config)
        output_dir = tmp_path / "output"

        with patch.object(manager, "_render_template") as mock_render:
            mock_render.side_effect = TemplateRenderError(
                "test.j2", "Template error"
            )

            with pytest.raises(TemplateRenderError) as exc_info:
                manager.write_outputs(
                    sample_color_scheme, output_dir, [ColorFormat.JSON]
                )

            assert "test.j2" in str(exc_info.value)

    def test_write_outputs_write_error(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test handling of file write errors."""
        manager = OutputManager(mock_app_config)
        output_dir = tmp_path / "output"

        with patch.object(manager, "_render_template") as mock_render:
            mock_render.return_value = "test"

            with patch.object(manager, "_write_file") as mock_write:
                mock_write.side_effect = OutputWriteError(
                    "test.json", "Write error"
                )

                with pytest.raises(OutputWriteError) as exc_info:
                    manager.write_outputs(
                        sample_color_scheme, output_dir, [ColorFormat.JSON]
                    )

                assert "test.json" in str(exc_info.value)

    def test_write_outputs_unexpected_error(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test handling of unexpected errors."""
        manager = OutputManager(mock_app_config)
        output_dir = tmp_path / "output"

        with patch.object(manager, "_render_template") as mock_render:
            mock_render.side_effect = RuntimeError("Unexpected error")

            with pytest.raises(OutputWriteError) as exc_info:
                manager.write_outputs(
                    sample_color_scheme, output_dir, [ColorFormat.JSON]
                )

            assert "unexpected error" in str(exc_info.value).lower()


class TestOutputManagerRenderTemplate:
    """Test OutputManager _render_template method."""

    def test_render_template_json(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test rendering JSON template."""
        # Create a simple JSON template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "colors.json.j2"
        template_file.write_text('{"background": "{{ background.hex }}"}')

        mock_app_config.templates.directory = template_dir
        manager = OutputManager(mock_app_config)

        content = manager._render_template(
            sample_color_scheme, ColorFormat.JSON
        )

        assert '"background"' in content
        assert sample_color_scheme.background.hex in content

    def test_render_template_css(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test rendering CSS template."""
        # Create a simple CSS template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "colors.css.j2"
        template_file.write_text(":root { --bg: {{ background.hex }}; }")

        mock_app_config.templates.directory = template_dir
        manager = OutputManager(mock_app_config)

        content = manager._render_template(
            sample_color_scheme, ColorFormat.CSS
        )

        assert ":root" in content
        assert sample_color_scheme.background.hex in content

    def test_render_template_not_found(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test rendering with missing template."""
        # Create empty template directory
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        mock_app_config.templates.directory = template_dir
        manager = OutputManager(mock_app_config)

        with pytest.raises(TemplateRenderError) as exc_info:
            manager._render_template(sample_color_scheme, ColorFormat.JSON)

        assert "not found" in str(exc_info.value).lower()

    def test_render_template_undefined_variable(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test rendering with undefined variable in strict mode."""
        # Create template with undefined variable
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "colors.json.j2"
        template_file.write_text('{"test": "{{ undefined_var }}"}')

        mock_app_config.templates.directory = template_dir
        mock_app_config.templates.directory = template_dir

        manager = OutputManager(mock_app_config)

        with pytest.raises(TemplateRenderError) as exc_info:
            manager._render_template(sample_color_scheme, ColorFormat.JSON)

        assert "undefined" in str(exc_info.value).lower()

    def test_render_template_with_generic_error(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test rendering with generic exception (non-UndefinedError)."""
        # Create a valid template
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "colors.json.j2"
        template_file.write_text('{"test": "{{ background.hex }}"}')

        mock_app_config.templates.directory = template_dir
        manager = OutputManager(mock_app_config)

        # Mock the template.render to raise a generic exception
        with patch.object(
            manager.template_env.get_template("colors.json.j2"),
            "render",
            side_effect=RuntimeError("Generic error"),
        ):
            with pytest.raises(TemplateRenderError) as exc_info:
                manager._render_template(sample_color_scheme, ColorFormat.JSON)

            assert "Generic error" in str(exc_info.value)

    def test_render_template_context(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test that template context includes all required variables."""
        # Create template that uses all context variables
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "colors.json.j2"
        template_content = """{
  "background": "{{ background.hex }}",
  "foreground": "{{ foreground.hex }}",
  "cursor": "{{ cursor.hex }}",
  "colors": [
    {%- for color in colors -%}
    "{{ color.hex }}"{% if not loop.last %}, {% endif %}
    {%- endfor -%}
  ],
  "source_image": "{{ source_image }}",
  "backend": "{{ backend }}",
  "generated_at": "{{ generated_at }}"
}
"""
        template_file.write_text(template_content)

        mock_app_config.templates.directory = template_dir
        manager = OutputManager(mock_app_config)

        content = manager._render_template(
            sample_color_scheme, ColorFormat.JSON
        )

        # Verify all context variables are present
        assert sample_color_scheme.background.hex in content
        assert sample_color_scheme.foreground.hex in content
        assert sample_color_scheme.cursor.hex in content
        assert sample_color_scheme.backend in content
        assert str(sample_color_scheme.source_image) in content


class TestOutputManagerWriteFile:
    """Test OutputManager _write_file method."""

    def test_write_file_success(self, mock_app_config, tmp_path):
        """Test successful file writing."""
        manager = OutputManager(mock_app_config)
        file_path = tmp_path / "test.txt"
        content = "test content"

        manager._write_file(file_path, content)

        assert file_path.exists()
        assert file_path.read_text() == content

    def test_write_file_permission_error(self, mock_app_config, tmp_path):
        """Test handling of permission errors."""
        manager = OutputManager(mock_app_config)
        file_path = tmp_path / "test.txt"

        with patch.object(Path, "write_text") as mock_write:
            mock_write.side_effect = PermissionError("Permission denied")

            with pytest.raises(OutputWriteError) as exc_info:
                manager._write_file(file_path, "test")

            assert "permission denied" in str(exc_info.value).lower()

    def test_write_file_os_error(self, mock_app_config, tmp_path):
        """Test handling of OS errors."""
        manager = OutputManager(mock_app_config)
        file_path = tmp_path / "test.txt"

        with patch.object(Path, "write_text") as mock_write:
            mock_write.side_effect = OSError("Disk full")

            with pytest.raises(OutputWriteError) as exc_info:
                manager._write_file(file_path, "test")

            assert "disk full" in str(exc_info.value).lower()


class TestOutputManagerIntegration:
    """Test OutputManager integration scenarios."""

    def test_full_workflow(
        self, mock_app_config, sample_color_scheme, tmp_path
    ):
        """Test full workflow from ColorScheme to files."""
        # Create templates
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        json_template = template_dir / "colors.json.j2"
        json_template.write_text('{"background": "{{ background.hex }}"}')

        css_template = template_dir / "colors.css.j2"
        css_template.write_text(":root { --bg: {{ background.hex }}; }")

        mock_app_config.templates.directory = template_dir
        manager = OutputManager(mock_app_config)

        output_dir = tmp_path / "output"
        output_files = manager.write_outputs(
            sample_color_scheme,
            output_dir,
            [ColorFormat.JSON, ColorFormat.CSS],
        )

        # Verify files were created
        assert len(output_files) == 2
        assert output_files["json"].exists()
        assert output_files["css"].exists()

        # Verify content
        json_content = output_files["json"].read_text()
        assert sample_color_scheme.background.hex in json_content

        css_content = output_files["css"].read_text()
        assert sample_color_scheme.background.hex in css_content
