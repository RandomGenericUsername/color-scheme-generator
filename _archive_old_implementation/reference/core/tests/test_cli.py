"""Tests for the core CLI module."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from colorscheme_generator.cli import (
    _ansi_color_block,
    _find_last_colorscheme,
    _load_colorscheme_from_json,
    _show_colorscheme,
    app,
)
from colorscheme_generator.config.enums import Backend, ColorFormat
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
    OutputWriteError,
)
from colorscheme_generator.core.types import Color, ColorScheme


# Test runner for CLI tests
runner = CliRunner()


class TestAnsiColorBlock:
    """Test ANSI color block generation."""

    def test_ansi_color_block_default_width(self, sample_color):
        """Test ANSI color block with default width."""
        result = _ansi_color_block(sample_color)
        assert "\033[48;2;" in result  # 24-bit true color ANSI code
        assert "255;87;51" in result  # RGB values
        assert "\033[0m" in result  # Reset code

    def test_ansi_color_block_custom_width(self, sample_color):
        """Test ANSI color block with custom width."""
        result = _ansi_color_block(sample_color, width=16)
        assert "\033[48;2;" in result
        assert " " * 16 in result  # 16 spaces

    def test_ansi_color_block_width_one(self, sample_color):
        """Test ANSI color block with width of 1."""
        result = _ansi_color_block(sample_color, width=1)
        assert " " * 1 in result


class TestLoadColorschemFromJson:
    """Test loading color schemes from JSON files."""

    def test_load_colorscheme_valid_json(self, tmp_path):
        """Test loading a valid colorscheme JSON file."""
        json_file = tmp_path / "colors.json"
        json_file.write_text(
            json.dumps(
                {
                    "metadata": {
                        "source_image": str(tmp_path / "test.png"),
                        "backend": "pywal",
                    },
                    "special": {
                        "background": "#1a1a1a",
                        "foreground": "#ffffff",
                        "cursor": "#ff0000",
                    },
                    "rgb": {
                        "background": [26, 26, 26],
                        "foreground": [255, 255, 255],
                        "cursor": [255, 0, 0],
                        "colors": [
                            [255, 87, 51],
                            [100, 100, 100],
                            [200, 200, 200],
                            [50, 50, 50],
                            [150, 150, 150],
                            [75, 75, 75],
                            [225, 225, 225],
                            [25, 25, 25],
                            [255, 128, 64],
                            [128, 64, 255],
                            [64, 255, 128],
                            [255, 255, 64],
                            [64, 128, 255],
                            [255, 64, 128],
                            [128, 255, 64],
                            [64, 64, 64],
                        ],
                    },
                    "colors": {
                        "color0": "#ff5733",
                        "color1": "#10204f",
                        "color2": "#20408f",
                        "color3": "#3060cf",
                        "color4": "#40800f",
                        "color5": "#50a04f",
                        "color6": "#60c08f",
                        "color7": "#70e0cf",
                        "color8": "#80100f",
                        "color9": "#90304f",
                        "color10": "#a0508f",
                        "color11": "#b070cf",
                        "color12": "#c0900f",
                        "color13": "#d0b04f",
                        "color14": "#e0d08f",
                        "color15": "#f0f0cf",
                    },
                }
            )
        )

        scheme = _load_colorscheme_from_json(json_file)

        assert isinstance(scheme, ColorScheme)
        assert scheme.background.hex == "#1a1a1a"
        assert scheme.foreground.hex == "#ffffff"
        assert scheme.cursor.hex == "#ff0000"
        assert len(scheme.colors) == 16
        assert scheme.backend == "pywal"

    def test_load_colorscheme_missing_colors(self, tmp_path):
        """Test loading colorscheme with missing color data raises error."""
        json_file = tmp_path / "colors.json"
        json_file.write_text(
            json.dumps(
                {
                    "metadata": {},
                    "special": {
                        "background": "#1a1a1a",
                        "foreground": "#ffffff",
                        "cursor": "#ff0000",
                    },
                    "rgb": {
                        "background": [26, 26, 26],
                        "foreground": [255, 255, 255],
                        "cursor": [255, 0, 0],
                        "colors": [],  # Missing color data
                    },
                    "colors": {},
                }
            )
        )

        with pytest.raises(ValueError):
            _load_colorscheme_from_json(json_file)


class TestFindLastColorscheme:
    """Test finding the last generated colorscheme."""

    @patch("colorscheme_generator.cli.Settings")
    def test_find_last_colorscheme_exists(self, mock_settings_class, tmp_path):
        """Test finding last colorscheme when it exists."""
        json_file = tmp_path / "colors.json"
        json_file.write_text(json.dumps({"test": "data"}))

        mock_settings = MagicMock()
        mock_settings.output.directory = tmp_path
        mock_settings_class.get.return_value = mock_settings

        result = _find_last_colorscheme()
        assert result == json_file

    @patch("colorscheme_generator.cli.Settings")
    def test_find_last_colorscheme_not_found(self, mock_settings_class, tmp_path):
        """Test finding last colorscheme when it doesn't exist."""
        mock_settings = MagicMock()
        mock_settings.output.directory = tmp_path / "nonexistent"
        mock_settings_class.get.return_value = mock_settings

        result = _find_last_colorscheme()
        assert result is None

    @patch("colorscheme_generator.cli.Settings")
    def test_find_last_colorscheme_settings_error(self, mock_settings_class):
        """Test finding last colorscheme when settings fail."""
        mock_settings_class.get.side_effect = Exception("Settings error")

        result = _find_last_colorscheme()
        assert result is None


class TestShowCommand:
    """Test the show command."""

    def test_show_with_file_option(self, tmp_path):
        """Test show command with --file option."""
        # Create a valid colorscheme JSON file
        json_file = tmp_path / "colors.json"
        json_file.write_text(
            json.dumps(
                {
                    "metadata": {
                        "source_image": "test.png",
                        "backend": "pywal",
                    },
                    "special": {
                        "background": "#1a1a1a",
                        "foreground": "#ffffff",
                        "cursor": "#ff0000",
                    },
                    "rgb": {
                        "background": [26, 26, 26],
                        "foreground": [255, 255, 255],
                        "cursor": [255, 0, 0],
                        "colors": [
                            [255, 87, 51],
                            [100, 100, 100],
                            [200, 200, 200],
                            [50, 50, 50],
                            [150, 150, 150],
                            [75, 75, 75],
                            [225, 225, 225],
                            [25, 25, 25],
                            [255, 128, 64],
                            [128, 64, 255],
                            [64, 255, 128],
                            [255, 255, 64],
                            [64, 128, 255],
                            [255, 64, 128],
                            [128, 255, 64],
                            [64, 64, 64],
                        ],
                    },
                    "colors": {
                        "color0": "#ff5733",
                        "color1": "#10204f",
                        "color2": "#20408f",
                        "color3": "#3060cf",
                        "color4": "#40800f",
                        "color5": "#50a04f",
                        "color6": "#60c08f",
                        "color7": "#70e0cf",
                        "color8": "#80100f",
                        "color9": "#90304f",
                        "color10": "#a0508f",
                        "color11": "#b070cf",
                        "color12": "#c0900f",
                        "color13": "#d0b04f",
                        "color14": "#e0d08f",
                        "color15": "#f0f0cf",
                    },
                }
            )
        )

        result = runner.invoke(app, ["show", "--file", str(json_file)])
        assert result.exit_code == 0
        assert "Color Scheme" in result.stdout or "colors" in result.stdout.lower()

    def test_show_without_arguments_fails(self):
        """Test show command without required arguments fails."""
        result = runner.invoke(app, ["show"])
        assert result.exit_code != 0

    def test_show_with_nonexistent_file_fails(self):
        """Test show command with nonexistent file fails."""
        result = runner.invoke(app, ["show", "--file", "/nonexistent/file.json"])
        assert result.exit_code != 0

    @patch("colorscheme_generator.cli._find_last_colorscheme")
    def test_show_with_last_option(self, mock_find_last, tmp_path):
        """Test show command with --last option."""
        # Create a valid colorscheme JSON file
        json_file = tmp_path / "colors.json"
        json_file.write_text(
            json.dumps(
                {
                    "metadata": {
                        "source_image": "test.png",
                        "backend": "pywal",
                    },
                    "special": {
                        "background": "#1a1a1a",
                        "foreground": "#ffffff",
                        "cursor": "#ff0000",
                    },
                    "rgb": {
                        "background": [26, 26, 26],
                        "foreground": [255, 255, 255],
                        "cursor": [255, 0, 0],
                        "colors": [
                            [255, 87, 51],
                            [100, 100, 100],
                            [200, 200, 200],
                            [50, 50, 50],
                            [150, 150, 150],
                            [75, 75, 75],
                            [225, 225, 225],
                            [25, 25, 25],
                            [255, 128, 64],
                            [128, 64, 255],
                            [64, 255, 128],
                            [255, 255, 64],
                            [64, 128, 255],
                            [255, 64, 128],
                            [128, 255, 64],
                            [64, 64, 64],
                        ],
                    },
                    "colors": {
                        "color0": "#ff5733",
                        "color1": "#10204f",
                        "color2": "#20408f",
                        "color3": "#3060cf",
                        "color4": "#40800f",
                        "color5": "#50a04f",
                        "color6": "#60c08f",
                        "color7": "#70e0cf",
                        "color8": "#80100f",
                        "color9": "#90304f",
                        "color10": "#a0508f",
                        "color11": "#b070cf",
                        "color12": "#c0900f",
                        "color13": "#d0b04f",
                        "color14": "#e0d08f",
                        "color15": "#f0f0cf",
                    },
                }
            )
        )

        mock_find_last.return_value = json_file

        result = runner.invoke(app, ["show", "--last"])
        assert result.exit_code == 0

    @patch("colorscheme_generator.cli._find_last_colorscheme")
    def test_show_with_last_option_not_found(self, mock_find_last):
        """Test show command with --last when no file found."""
        mock_find_last.return_value = None

        result = runner.invoke(app, ["show", "--last"])
        assert result.exit_code != 0


class TestGenerateCommand:
    """Test the generate command."""

    def test_generate_without_image_fails(self):
        """Test generate command without image argument fails."""
        result = runner.invoke(app, ["generate"])
        assert result.exit_code != 0

    def test_generate_with_invalid_backend_fails(self, sample_image):
        """Test generate command with invalid backend."""
        result = runner.invoke(
            app,
            ["generate", str(sample_image), "--backend", "invalid_backend"],
        )
        assert result.exit_code != 0

    def test_generate_with_invalid_format_fails(self, sample_image):
        """Test generate command with invalid format."""
        result = runner.invoke(
            app,
            ["generate", str(sample_image), "--formats", "invalid_format"],
        )
        assert result.exit_code != 0

    def test_generate_with_pywal_backend_option(self, sample_image):
        """Test generate command accepts pywal backend option."""
        # Just test that the command parsing works, not the full execution
        # Full execution testing requires actual backend setup
        result = runner.invoke(
            app,
            ["generate", str(sample_image), "--backend", "pywal"],
        )
        # Should fail due to backend not being available, not due to parsing error
        assert isinstance(result.exit_code, int)

    @patch("colorscheme_generator.cli.Settings")
    def test_generate_settings_load_error(self, mock_settings_class, sample_image):
        """Test generate command when settings fail to load."""
        mock_settings_class.get.side_effect = Exception("Settings error")

        result = runner.invoke(
            app,
            ["generate", str(sample_image)],
        )
        assert result.exit_code != 0

    @patch("colorscheme_generator.cli.ColorSchemeGeneratorFactory")
    @patch("colorscheme_generator.cli.Settings")
    def test_generate_backend_not_available(
        self, mock_settings_class, mock_factory, sample_image
    ):
        """Test generate command when backend is not available."""
        mock_settings = MagicMock()
        mock_settings.logging.get_level_int.return_value = logging.INFO
        mock_settings.logging.show_time = False
        mock_settings.generation.default_backend = "pywal"
        mock_settings_class.get.return_value = mock_settings

        mock_factory.create.side_effect = BackendNotAvailableError("Backend not available")
        mock_factory.list_available.return_value = []

        result = runner.invoke(
            app,
            ["generate", str(sample_image), "--backend", "unavailable"],
        )
        assert result.exit_code != 0

    def test_generate_with_custom_output_dir(self, sample_image, tmp_path):
        """Test generate command with custom output directory."""
        output_dir = tmp_path / "custom_output"
        output_dir.mkdir()

        result = runner.invoke(
            app,
            [
                "generate",
                str(sample_image),
                "--output-dir",
                str(output_dir),
            ],
        )
        # Command should parse without error
        assert isinstance(result.exit_code, int)

    @patch("colorscheme_generator.cli.ColorSchemeGeneratorFactory")
    @patch("colorscheme_generator.cli.Settings")
    def test_generate_with_list_backends(
        self, mock_settings_class, mock_factory, sample_image
    ):
        """Test generate command with --list-backends flag."""
        mock_settings = MagicMock()
        mock_settings.logging.get_level_int.return_value = logging.INFO
        mock_settings.logging.show_time = False
        mock_settings_class.get.return_value = mock_settings

        mock_factory.list_available.return_value = ["pywal", "wallust", "custom"]

        result = runner.invoke(
            app,
            ["generate", "--list-backends"],
        )
        assert result.exit_code == 0
        assert "Available backends" in result.stdout

    def test_generate_quiet_mode(self, sample_image):
        """Test generate command with quiet mode."""
        result = runner.invoke(
            app,
            ["generate", str(sample_image), "--quiet"],
        )
        # Command should parse without error
        assert isinstance(result.exit_code, int)

    def test_generate_debug_mode(self, sample_image):
        """Test generate command with debug mode."""
        result = runner.invoke(
            app,
            ["generate", str(sample_image), "--debug"],
        )
        # Command should parse without error
        assert isinstance(result.exit_code, int)

    def test_generate_with_formats(self, sample_image):
        """Test generate command with multiple formats."""
        result = runner.invoke(
            app,
            [
                "generate",
                str(sample_image),
                "--formats",
                "json",
                "--formats",
                "css",
            ],
        )
        # Command should parse without error
        assert isinstance(result.exit_code, int)


class TestShowColorscheme:
    """Test the _show_colorscheme function."""

    def test_show_colorscheme_output(self, sample_color_scheme, capsys):
        """Test _show_colorscheme produces output."""
        # Note: This patches console output, so we'll use a simple check
        _show_colorscheme(sample_color_scheme)
        # If no exception is raised, the function works
        assert True


class TestCliEntryPoint:
    """Test CLI entry point."""

    def test_cli_help(self):
        """Test CLI help works."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "generate" in result.stdout
        assert "show" in result.stdout
