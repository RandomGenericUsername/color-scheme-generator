"""Unit tests for CLI main module."""

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image
from typer.testing import CliRunner

from color_scheme.cli.main import app
from color_scheme.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    ColorSchemeError,
    InvalidImageError,
    OutputWriteError,
    TemplateRenderError,
)


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def test_image(tmp_path):
    """Create a valid test image."""
    img_path = tmp_path / "test_image.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return img_path


def _mock_color():
    """Create mock Color."""
    c = MagicMock()
    c.adjust_saturation = MagicMock(return_value=c)
    c.hex = "#FF0000"
    c.rgb = (255, 0, 0)
    return c


def _mock_scheme():
    """Create mock ColorScheme."""
    s = MagicMock()
    s.background = _mock_color()
    s.foreground = _mock_color()
    s.cursor = _mock_color()
    s.colors = [_mock_color() for _ in range(16)]
    return s


class TestVersionCommand:
    """Tests for version command."""

    def test_version_outputs_version(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "color-scheme-core version" in result.stdout

    def test_version_has_semver(self, runner):
        """Test version contains semver pattern."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert re.search(r"\d+\.\d+\.\d+", result.stdout)


class TestGenerateErrors:
    """Tests for generate command error handling."""

    def test_image_not_found(self, runner, tmp_path):
        """Test error when image doesn't exist."""
        result = runner.invoke(
            app, ["generate", str(tmp_path / "nope.png"), "-o", str(tmp_path)]
        )
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_path_is_directory(self, runner, tmp_path):
        """Test error when path is directory."""
        result = runner.invoke(
            app, ["generate", str(tmp_path), "-o", str(tmp_path)]
        )
        assert result.exit_code == 1
        assert "not a file" in result.stdout.lower()

    def test_invalid_image_error(self, runner, test_image, tmp_path):
        """Test InvalidImageError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = InvalidImageError(str(test_image), "corrupt")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "invalid image" in result.stdout.lower()

    def test_backend_not_available_error(self, runner, test_image, tmp_path):
        """Test BackendNotAvailableError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            mock.return_value.auto_detect.side_effect = BackendNotAvailableError(
                "pywal", "not installed"
            )

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "not available" in result.stdout.lower()

    def test_color_extraction_error(self, runner, test_image, tmp_path):
        """Test ColorExtractionError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = ColorExtractionError("pywal", "failed")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "extraction failed" in result.stdout.lower()

    def test_template_render_error(self, runner, test_image, tmp_path):
        """Test TemplateRenderError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock_factory:
            with patch("color_scheme.cli.main.OutputManager") as mock_output:
                gen = MagicMock()
                gen.generate.return_value = _mock_scheme()
                mock_factory.return_value.auto_detect.return_value = MagicMock(value="custom")
                mock_factory.return_value.create.return_value = gen
                mock_output.return_value.write_outputs.side_effect = TemplateRenderError(
                    "colors.css.j2", "syntax error"
                )

                result = runner.invoke(
                    app, ["generate", str(test_image), "-o", str(tmp_path)]
                )
                assert result.exit_code == 1
                assert "template" in result.stdout.lower()

    def test_output_write_error(self, runner, test_image, tmp_path):
        """Test OutputWriteError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock_factory:
            with patch("color_scheme.cli.main.OutputManager") as mock_output:
                gen = MagicMock()
                gen.generate.return_value = _mock_scheme()
                mock_factory.return_value.auto_detect.return_value = MagicMock(value="custom")
                mock_factory.return_value.create.return_value = gen
                mock_output.return_value.write_outputs.side_effect = OutputWriteError(
                    Path("/readonly"), "permission denied"
                )

                result = runner.invoke(
                    app, ["generate", str(test_image), "-o", str(tmp_path)]
                )
                assert result.exit_code == 1
                assert "error" in result.stdout.lower()

    def test_colorscheme_error(self, runner, test_image, tmp_path):
        """Test ColorSchemeError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = ColorSchemeError("something broke")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "error" in result.stdout.lower()

    def test_unexpected_exception(self, runner, test_image, tmp_path):
        """Test unexpected Exception handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = RuntimeError("crash")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "unexpected error" in result.stdout.lower()


class TestGenerateSaturation:
    """Tests for saturation in generate command."""

    def test_saturation_adjustment(self, runner, test_image, tmp_path):
        """Test saturation option."""
        result = runner.invoke(
            app,
            ["generate", str(test_image), "-o", str(tmp_path), "-b", "custom", "-s", "1.5"],
        )
        assert result.exit_code == 0
        assert "saturation" in result.stdout.lower() or "1.5" in result.stdout


class TestShowErrors:
    """Tests for show command error handling."""

    def test_image_not_found(self, runner, tmp_path):
        """Test error when image doesn't exist."""
        result = runner.invoke(app, ["show", str(tmp_path / "nope.png")])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_path_is_directory(self, runner, tmp_path):
        """Test error when path is directory."""
        result = runner.invoke(app, ["show", str(tmp_path)])
        assert result.exit_code == 1
        assert "not a file" in result.stdout.lower()

    def test_invalid_image_error(self, runner, test_image):
        """Test InvalidImageError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = InvalidImageError(str(test_image), "corrupt")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "invalid image" in result.stdout.lower()

    def test_backend_not_available_error(self, runner, test_image):
        """Test BackendNotAvailableError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            mock.return_value.auto_detect.side_effect = BackendNotAvailableError(
                "pywal", "not installed"
            )

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "not available" in result.stdout.lower()

    def test_color_extraction_error(self, runner, test_image):
        """Test ColorExtractionError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = ColorExtractionError("pywal", "failed")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "extraction failed" in result.stdout.lower()

    def test_colorscheme_error(self, runner, test_image):
        """Test ColorSchemeError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = ColorSchemeError("broke")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "error" in result.stdout.lower()

    def test_unexpected_exception(self, runner, test_image):
        """Test unexpected Exception handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = RuntimeError("crash")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "unexpected error" in result.stdout.lower()


class TestShowSaturation:
    """Tests for saturation in show command."""

    def test_saturation_display(self, runner, test_image):
        """Test saturation option displays info."""
        result = runner.invoke(
            app, ["show", str(test_image), "-b", "custom", "-s", "1.5"]
        )
        assert result.exit_code == 0
        assert "saturation" in result.stdout.lower() or "1.5" in result.stdout


class TestMainEntryPoint:
    """Tests for main() entry point."""

    def test_main_callable(self):
        """Test main is callable."""
        from color_scheme.cli.main import main
        assert callable(main)

    def test_app_has_commands(self):
        """Test app has command decorator."""
        from color_scheme.cli.main import app
        assert hasattr(app, "command")
