"""Tests for OutputManager."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from color_scheme.config.enums import Backend, ColorFormat
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import (
    OutputWriteError,
    TemplateRenderError,
)
from color_scheme.core.types import Color, ColorScheme
from color_scheme.output.manager import OutputManager


class TestOutputManagerInit:
    """Test OutputManager initialization."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    def test_init_with_settings(self, settings):
        """Test initialization with settings."""
        manager = OutputManager(settings)

        assert manager.settings == settings
        assert manager.template_env is not None
        assert manager.template_env.loader is not None

    def test_init_with_absolute_template_path(self, tmp_path):
        """Test initialization with absolute template path."""
        from color_scheme.config.config import AppConfig, TemplateSettings

        # Create a temporary template directory
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        # Create a minimal template
        (template_dir / "colors.json.j2").write_text('{"test": "{{ backend }}"}')

        # Create settings with absolute path
        settings = AppConfig(
            templates=TemplateSettings(directory=template_dir)
        )

        manager = OutputManager(settings)

        assert manager.settings == settings
        assert manager.template_env is not None
        assert manager.template_env.loader is not None


class TestWriteOutputs:
    """Test OutputManager.write_outputs method."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def manager(self, settings):
        """Create OutputManager instance."""
        return OutputManager(settings)

    @pytest.fixture
    def color_scheme(self, tmp_path):
        """Create test color scheme."""
        return ColorScheme(
            source_image=tmp_path / "test.png",
            backend=Backend.CUSTOM,
            generated_at=datetime(2024, 1, 1, 12, 0, 0),
            background=Color(hex="#000000", rgb=(0, 0, 0)),
            foreground=Color(hex="#FFFFFF", rgb=(255, 255, 255)),
            cursor=Color(hex="#FF0000", rgb=(255, 0, 0)),
            colors=[
                Color(hex="#000000", rgb=(0, 0, 0)),
                Color(hex="#FF0000", rgb=(255, 0, 0)),
                Color(hex="#00FF00", rgb=(0, 255, 0)),
                Color(hex="#0000FF", rgb=(0, 0, 255)),
                Color(hex="#FFFF00", rgb=(255, 255, 0)),
                Color(hex="#FF00FF", rgb=(255, 0, 255)),
                Color(hex="#00FFFF", rgb=(0, 255, 255)),
                Color(hex="#FFFFFF", rgb=(255, 255, 255)),
                Color(hex="#808080", rgb=(128, 128, 128)),
                Color(hex="#800000", rgb=(128, 0, 0)),
                Color(hex="#008000", rgb=(0, 128, 0)),
                Color(hex="#000080", rgb=(0, 0, 128)),
                Color(hex="#808000", rgb=(128, 128, 0)),
                Color(hex="#800080", rgb=(128, 0, 128)),
                Color(hex="#008080", rgb=(0, 128, 128)),
                Color(hex="#C0C0C0", rgb=(192, 192, 192)),
            ],
        )

    def test_write_single_format(self, manager, color_scheme, tmp_path):
        """Test writing a single output format."""
        output_dir = tmp_path / "output"
        formats = [ColorFormat.JSON]

        manager.write_outputs(color_scheme, output_dir, formats)

        # Check JSON file was created
        json_file = output_dir / "colors.json"
        assert json_file.exists()
        assert json_file.is_file()

        # Verify content contains expected data
        content = json_file.read_text()
        assert '"source_image"' in content
        assert '"backend": "custom"' in content
        assert '"#000000"' in content

    def test_write_multiple_formats(self, manager, color_scheme, tmp_path):
        """Test writing multiple output formats."""
        output_dir = tmp_path / "output"
        formats = [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.YAML]

        manager.write_outputs(color_scheme, output_dir, formats)

        # Check all files were created
        assert (output_dir / "colors.json").exists()
        assert (output_dir / "colors.css").exists()
        assert (output_dir / "colors.yaml").exists()

    def test_creates_output_directory(self, manager, color_scheme, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "nested" / "output" / "dir"
        formats = [ColorFormat.JSON]

        manager.write_outputs(color_scheme, output_dir, formats)

        assert output_dir.exists()
        assert output_dir.is_dir()
        assert (output_dir / "colors.json").exists()

    def test_write_sequences_format(self, manager, color_scheme, tmp_path):
        """Test writing SEQUENCES format (binary with escape sequences)."""
        output_dir = tmp_path / "output"
        formats = [ColorFormat.SEQUENCES]

        manager.write_outputs(color_scheme, output_dir, formats)

        # Check file was created
        seq_file = output_dir / "colors.sequences"
        assert seq_file.exists()

        # Read binary content
        content = seq_file.read_bytes()

        # Verify it contains escape sequences (ESC = 0x1b)
        assert b"\x1b" in content
        # Verify it contains color codes
        assert b"4;0" in content  # First color code


class TestErrorHandling:
    """Test error handling in OutputManager."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def manager(self, settings):
        """Create OutputManager instance."""
        return OutputManager(settings)

    @pytest.fixture
    def color_scheme(self, tmp_path):
        """Create test color scheme."""
        return ColorScheme(
            source_image=tmp_path / "test.png",
            backend=Backend.CUSTOM,
            generated_at=datetime(2024, 1, 1, 12, 0, 0),
            background=Color(hex="#000000", rgb=(0, 0, 0)),
            foreground=Color(hex="#FFFFFF", rgb=(255, 255, 255)),
            cursor=Color(hex="#FF0000", rgb=(255, 0, 0)),
            colors=[
                Color(hex="#000000", rgb=(0, 0, 0)),
                Color(hex="#FF0000", rgb=(255, 0, 0)),
                Color(hex="#00FF00", rgb=(0, 255, 0)),
                Color(hex="#0000FF", rgb=(0, 0, 255)),
                Color(hex="#FFFF00", rgb=(255, 255, 0)),
                Color(hex="#FF00FF", rgb=(255, 0, 255)),
                Color(hex="#00FFFF", rgb=(0, 255, 255)),
                Color(hex="#FFFFFF", rgb=(255, 255, 255)),
                Color(hex="#808080", rgb=(128, 128, 128)),
                Color(hex="#800000", rgb=(128, 0, 0)),
                Color(hex="#008000", rgb=(0, 128, 0)),
                Color(hex="#000080", rgb=(0, 0, 128)),
                Color(hex="#808000", rgb=(128, 128, 0)),
                Color(hex="#800080", rgb=(128, 0, 128)),
                Color(hex="#008080", rgb=(0, 128, 128)),
                Color(hex="#C0C0C0", rgb=(192, 192, 192)),
            ],
        )

    def test_template_not_found(self, manager, color_scheme, tmp_path):
        """Test error when template is not found."""
        output_dir = tmp_path / "output"

        # Create a fake format enum value
        # We'll patch the ColorFormat to include a non-existent format
        from unittest.mock import Mock

        fake_format = Mock()
        fake_format.value = "nonexistent"

        with pytest.raises(TemplateRenderError) as exc_info:
            manager._render_template(color_scheme, fake_format)

        assert "nonexistent" in exc_info.value.template_name

    def test_permission_denied_write(self, manager, color_scheme, tmp_path):
        """Test error when permission denied during write."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create a read-only file
        output_file = output_dir / "colors.json"
        output_file.touch()
        output_file.chmod(0o444)

        formats = [ColorFormat.JSON]

        try:
            with pytest.raises(OutputWriteError) as exc_info:
                manager.write_outputs(color_scheme, output_dir, formats)

            assert "colors.json" in exc_info.value.file_path
            assert "Permission denied" in exc_info.value.reason
        finally:
            # Cleanup - restore write permission
            output_file.chmod(0o644)

    def test_permission_denied_binary_write(self, manager, color_scheme, tmp_path):
        """Test error when permission denied during binary write."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create a read-only file
        output_file = output_dir / "colors.sequences"
        output_file.touch()
        output_file.chmod(0o444)

        formats = [ColorFormat.SEQUENCES]

        try:
            with pytest.raises(OutputWriteError) as exc_info:
                manager.write_outputs(color_scheme, output_dir, formats)

            assert "colors.sequences" in exc_info.value.file_path
            assert "Permission denied" in exc_info.value.reason
        finally:
            # Cleanup - restore write permission
            output_file.chmod(0o644)

    def test_oserror_write_file(self, manager, color_scheme, tmp_path):
        """Test OSError handling in _write_file."""
        from unittest.mock import Mock, PropertyMock

        # Mock file path that raises OSError
        mock_path = Mock(spec=Path)
        mock_path.write_text.side_effect = OSError("Disk full")
        # Configure the return value for __str__
        type(mock_path).__str__ = Mock(return_value="/fake/path/colors.json")

        with pytest.raises(OutputWriteError) as exc_info:
            manager._write_file(mock_path, "test content")

        assert "/fake/path/colors.json" in exc_info.value.file_path
        assert "Disk full" in exc_info.value.reason

    def test_oserror_write_binary_file(self, manager, color_scheme, tmp_path):
        """Test OSError handling in _write_binary_file."""
        from unittest.mock import Mock, PropertyMock

        # Mock file path that raises OSError
        mock_path = Mock(spec=Path)
        mock_path.write_bytes.side_effect = OSError("Disk full")
        # Configure the return value for __str__
        type(mock_path).__str__ = Mock(return_value="/fake/path/colors.sequences")

        with pytest.raises(OutputWriteError) as exc_info:
            manager._write_binary_file(mock_path, b"test content")

        assert "/fake/path/colors.sequences" in exc_info.value.file_path
        assert "Disk full" in exc_info.value.reason

    def test_template_render_general_error(self, manager, color_scheme):
        """Test general exception handling in _render_template."""
        from unittest.mock import Mock

        # Mock format with value that exists, but make render fail
        fake_format = Mock()
        fake_format.value = "json"

        # Mock the template to raise an exception during rendering
        original_get_template = manager.template_env.get_template

        def mock_get_template(name):
            template = original_get_template(name)
            original_render = template.render
            template.render = Mock(side_effect=RuntimeError("Template error"))
            return template

        manager.template_env.get_template = mock_get_template

        with pytest.raises(TemplateRenderError) as exc_info:
            manager._render_template(color_scheme, fake_format)

        assert "colors.json.j2" in exc_info.value.template_name
        assert "Template error" in exc_info.value.reason
