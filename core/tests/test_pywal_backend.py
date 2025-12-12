"""Tests for PywalGenerator backend."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from colorscheme_generator.backends.pywal import PywalGenerator
from colorscheme_generator.config.enums import Backend, ColorFormat
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
)
from colorscheme_generator.core.types import (
    ColorScheme,
    GeneratorConfig,
)


class TestPywalGeneratorInit:
    """Test PywalGenerator initialization."""

    def test_init_with_config(self, mock_app_config):
        """Test initialization with config."""
        generator = PywalGenerator(mock_app_config)

        assert generator.settings == mock_app_config
        assert generator.backend_name == "pywal"





class TestPywalGeneratorAvailability:
    """Test PywalGenerator availability checks."""

    def test_is_available_cli_mode_found(self, mock_app_config):
        """Test availability check in CLI mode when wal is found."""
        with patch("shutil.which", return_value="/usr/bin/wal"):
            generator = PywalGenerator(mock_app_config)
            assert generator.is_available() is True

    def test_is_available_cli_mode_not_found(self, mock_app_config):
        """Test availability check in CLI mode when wal is not found."""
        with patch("shutil.which", return_value=None):
            generator = PywalGenerator(mock_app_config)
            assert generator.is_available() is False




class TestPywalGeneratorGenerate:
    """Test PywalGenerator generate method."""

    def test_generate_success(self, mock_app_config, sample_image, tmp_path):
        """Test successful color generation."""
        # Setup
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()


        # Create mock colors.json
        colors_data = {
            "special": {
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "cursor": "#ff0000",
            },
            "colors": {
                f"color{i}": f"#{i:02x}{i:02x}{i:02x}" for i in range(16)
            },
        }
        colors_file = cache_dir / "colors.json"
        colors_file.write_text(json.dumps(colors_data))

        generator = PywalGenerator(mock_app_config)
        generator.cache_dir = cache_dir

        config = GeneratorConfig(
            backend=Backend.PYWAL,
            output_dir=tmp_path / "output",
            formats=[ColorFormat.JSON],
        )

        with patch("shutil.which", return_value="/usr/bin/wal"):
            with patch.object(generator, "_run_pywal_cli"):
                scheme = generator.generate(sample_image, config)

        assert isinstance(scheme, ColorScheme)
        assert scheme.backend == "pywal"
        assert scheme.background.hex == "#1a1a1a"
        assert scheme.foreground.hex == "#ffffff"
        assert len(scheme.colors) == 16

    def test_generate_image_not_found(self, mock_app_config, tmp_path):
        """Test generation with non-existent image."""
        generator = PywalGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.PYWAL)

        non_existent = tmp_path / "nonexistent.png"

        with patch("shutil.which", return_value="/usr/bin/wal"):
            with pytest.raises(InvalidImageError) as exc_info:
                generator.generate(non_existent, config)

        assert "does not exist" in str(exc_info.value)

    def test_generate_image_not_file(self, mock_app_config, tmp_path):
        """Test generation with directory instead of file."""
        generator = PywalGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.PYWAL)

        directory = tmp_path / "dir"
        directory.mkdir()

        with patch("shutil.which", return_value="/usr/bin/wal"):
            with pytest.raises(InvalidImageError) as exc_info:
                generator.generate(directory, config)

        assert "Not a file" in str(exc_info.value)

    def test_generate_pywal_fails(self, mock_app_config, sample_image):
        """Test generation when pywal command fails."""
        generator = PywalGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.PYWAL)

        with patch("shutil.which", return_value="/usr/bin/wal"):
            with patch.object(
                generator, "_run_pywal_cli", side_effect=Exception("Pywal error")
            ):
                with pytest.raises(ColorExtractionError) as exc_info:
                    generator.generate(sample_image, config)

            assert "Failed to run pywal" in str(exc_info.value)

    def test_generate_colors_file_missing(
        self, mock_app_config, sample_image, tmp_path
    ):
        """Test generation when colors.json is missing."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()


        generator = PywalGenerator(mock_app_config)
        generator.cache_dir = cache_dir
        config = GeneratorConfig(backend=Backend.PYWAL)

        with patch("shutil.which", return_value="/usr/bin/wal"):
            with patch.object(generator, "_run_pywal_cli"):
                with pytest.raises(ColorExtractionError) as exc_info:
                    generator.generate(sample_image, config)

            assert "output file not found" in str(exc_info.value)

    def test_generate_colors_file_invalid_json(
        self, mock_app_config, sample_image, tmp_path
    ):
        """Test generation when colors.json has invalid JSON."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()


        # Create invalid JSON file
        colors_file = cache_dir / "colors.json"
        colors_file.write_text("invalid json{")

        generator = PywalGenerator(mock_app_config)
        generator.cache_dir = cache_dir
        config = GeneratorConfig(backend=Backend.PYWAL)

        with patch("shutil.which", return_value="/usr/bin/wal"):
            with patch.object(generator, "_run_pywal_cli"):
                with pytest.raises(ColorExtractionError) as exc_info:
                    generator.generate(sample_image, config)

            assert "Failed to read pywal output" in str(exc_info.value)


class TestPywalGeneratorCLI:
    """Test PywalGenerator CLI execution."""

    def test_run_pywal_cli_success(self, mock_app_config, sample_image):
        """Test successful CLI execution."""
        generator = PywalGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.PYWAL)

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            generator._run_pywal_cli(sample_image, config)

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args[0] == "wal"
            assert "-i" in args
            assert str(sample_image) in args

    def test_run_pywal_cli_command_fails(self, mock_app_config, sample_image):
        """Test CLI execution when command fails."""
        generator = PywalGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.PYWAL)

        with patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(
                1, "wal", stderr="Error message"
            ),
        ):
            with pytest.raises(ColorExtractionError) as exc_info:
                generator._run_pywal_cli(sample_image, config)

            assert "Pywal command failed" in str(exc_info.value)

    def test_run_pywal_cli_not_found(self, mock_app_config, sample_image):
        """Test CLI execution when wal command not found."""
        generator = PywalGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.PYWAL)

        with patch("subprocess.run", side_effect=FileNotFoundError()):
            with pytest.raises(BackendNotAvailableError) as exc_info:
                generator._run_pywal_cli(sample_image, config)

            assert "wal command not found" in str(exc_info.value)


class TestPywalGeneratorParsing:
    """Test PywalGenerator parsing methods."""

    def test_parse_pywal_output_complete(self, mock_app_config, sample_image):
        """Test parsing complete pywal output."""
        generator = PywalGenerator(mock_app_config)

        pywal_data = {
            "special": {
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "cursor": "#ff0000",
            },
            "colors": {
                f"color{i}": f"#{i:02x}{i:02x}{i:02x}" for i in range(16)
            },
        }

        scheme = generator._parse_pywal_output(pywal_data, sample_image)

        assert isinstance(scheme, ColorScheme)
        assert scheme.background.hex == "#1a1a1a"
        assert scheme.foreground.hex == "#ffffff"
        assert scheme.cursor.hex == "#ff0000"
        assert len(scheme.colors) == 16
        assert scheme.backend == "pywal"
        # source_image is stored as Path object
        assert str(scheme.source_image) == str(sample_image)

    def test_parse_pywal_output_missing_special(
        self, mock_app_config, sample_image
    ):
        """Test parsing when special colors are missing."""
        generator = PywalGenerator(mock_app_config)

        pywal_data = {
            "colors": {
                f"color{i}": f"#{i:02x}{i:02x}{i:02x}" for i in range(16)
            }
        }

        scheme = generator._parse_pywal_output(pywal_data, sample_image)

        # Should use defaults
        assert scheme.background.hex == "#000000"
        assert scheme.foreground.hex == "#ffffff"

    def test_parse_pywal_output_missing_colors(
        self, mock_app_config, sample_image
    ):
        """Test parsing when some colors are missing."""
        generator = PywalGenerator(mock_app_config)

        pywal_data = {
            "special": {
                "background": "#1a1a1a",
                "foreground": "#ffffff",
            },
            "colors": {
                "color0": "#000000",
                "color1": "#111111",
                # Missing color2-15
            },
        }

        scheme = generator._parse_pywal_output(pywal_data, sample_image)

        assert len(scheme.colors) == 16
        # First two should be from data
        assert scheme.colors[0].hex == "#000000"
        assert scheme.colors[1].hex == "#111111"
        # Rest should be fallback
        assert scheme.colors[2].hex == "#000000"

    def test_parse_color_with_hash(self, mock_app_config):
        """Test parsing color with hash prefix."""
        generator = PywalGenerator(mock_app_config)

        color = generator._parse_color("#1a2b3c")

        assert color.hex == "#1a2b3c"
        assert color.rgb == (26, 43, 60)

    def test_parse_color_without_hash(self, mock_app_config):
        """Test parsing color without hash prefix."""
        generator = PywalGenerator(mock_app_config)

        color = generator._parse_color("1a2b3c")

        assert color.hex == "#1a2b3c"
        assert color.rgb == (26, 43, 60)


class TestPywalGeneratorIntegration:
    """Test PywalGenerator integration scenarios."""

    def test_full_workflow_cli_mode(
        self, mock_app_config, sample_image, tmp_path
    ):
        """Test full workflow in CLI mode."""
        # Setup cache directory
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()


        # Create mock colors.json
        colors_data = {
            "special": {
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "cursor": "#ff0000",
            },
            "colors": {
                f"color{i}": f"#{i:02x}{i:02x}{i:02x}" for i in range(16)
            },
        }
        colors_file = cache_dir / "colors.json"
        colors_file.write_text(json.dumps(colors_data))

        # Create generator and config
        generator = PywalGenerator(mock_app_config)
        generator.cache_dir = cache_dir

        config = GeneratorConfig(
            backend=Backend.PYWAL,
            output_dir=tmp_path / "output",
            formats=[ColorFormat.JSON],
        )

        # Mock CLI execution
        with (
            patch("shutil.which", return_value="/usr/bin/wal"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            # Check availability
            assert generator.is_available() is True

            # Generate colors
            scheme = generator.generate(sample_image, config)

            assert isinstance(scheme, ColorScheme)
            assert scheme.backend == "pywal"
            assert len(scheme.colors) == 16
