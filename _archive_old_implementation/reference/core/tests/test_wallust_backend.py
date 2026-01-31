"""Tests for WallustGenerator backend."""

import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from colorscheme_generator.backends.wallust import WallustGenerator
from colorscheme_generator.config.enums import Backend
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
)
from colorscheme_generator.core.types import ColorScheme, GeneratorConfig


class TestWallustGeneratorInit:
    """Test WallustGenerator initialization."""

    def test_init_with_config(self, mock_app_config):
        """Test initialization with config."""
        generator = WallustGenerator(mock_app_config)

        assert generator.settings == mock_app_config
        assert generator.backend_name == "wallust"

        assert generator.backend_type == "resized"
        assert generator.cache_dir == Path.home() / ".cache" / "wallust"


class TestWallustGeneratorAvailability:
    """Test WallustGenerator availability checks."""

    def test_is_available_found(self, mock_app_config, mock_shutil_which):
        """Test availability when wallust is found."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)

        assert generator.is_available() is True
        mock_shutil_which.assert_called_once_with("wallust")

    def test_is_available_not_found(self, mock_app_config, mock_shutil_which):
        """Test availability when wallust is not found."""
        mock_shutil_which.return_value = None
        generator = WallustGenerator(mock_app_config)

        assert generator.is_available() is False


class TestWallustGeneratorGenerate:
    """Test WallustGenerator generate method."""

    def test_generate_backend_not_available(
        self, mock_app_config, sample_image, mock_shutil_which
    ):
        """Test generation when wallust is not available."""
        mock_shutil_which.return_value = None
        generator = WallustGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.WALLUST)

        with pytest.raises(BackendNotAvailableError) as exc_info:
            generator.generate(sample_image, config)

        assert "wallust" in str(exc_info.value).lower()

    def test_generate_image_not_found(
        self, mock_app_config, tmp_path, mock_shutil_which
    ):
        """Test generation with non-existent image."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.WALLUST)

        non_existent = tmp_path / "nonexistent.png"

        with pytest.raises(InvalidImageError) as exc_info:
            generator.generate(non_existent, config)

        assert "does not exist" in str(exc_info.value)

    def test_generate_image_not_file(
        self, mock_app_config, tmp_path, mock_shutil_which
    ):
        """Test generation with directory instead of file."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.WALLUST)

        directory = tmp_path / "dir"
        directory.mkdir()

        with pytest.raises(InvalidImageError) as exc_info:
            generator.generate(directory, config)

        assert "Not a file" in str(exc_info.value)

    def test_generate_success(
        self, mock_app_config, sample_image, mock_shutil_which, tmp_path
    ):
        """Test successful generation."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)
        generator.cache_dir = tmp_path / "wallust"

        # Create cache directory structure (wallust creates hash-based subdirs)
        cache_subdir = generator.cache_dir / "abc123"
        cache_subdir.mkdir(parents=True)

        # Create mock wallust output (flat structure, not nested)
        colors_file = cache_subdir / "Resized_Lch_auto_Dark"
        wallust_data = {
            "background": "#1a1a1a",
            "foreground": "#ffffff",
            "cursor": "#ff0000",
            **{f"color{i}": f"#{i:02x}{i:02x}{i:02x}" for i in range(16)},
        }
        colors_file.write_text(json.dumps(wallust_data))

        config = GeneratorConfig(backend=Backend.WALLUST)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")
            scheme = generator.generate(sample_image, config)

        assert isinstance(scheme, ColorScheme)
        assert scheme.backend == "wallust"
        assert len(scheme.colors) == 16
        assert str(scheme.source_image) == str(sample_image)

    def test_generate_wallust_command_fails(
        self, mock_app_config, sample_image, mock_shutil_which
    ):
        """Test generation when wallust command fails."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.WALLUST)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "wallust", stderr="Error"
            )

            with pytest.raises(ColorExtractionError) as exc_info:
                generator.generate(sample_image, config)

            assert "wallust command failed" in str(exc_info.value).lower()

    def test_generate_colors_file_missing(
        self, mock_app_config, sample_image, mock_shutil_which, tmp_path
    ):
        """Test generation when colors file is missing."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)
        generator.cache_dir = tmp_path / "wallust"
        generator.cache_dir.mkdir()

        config = GeneratorConfig(backend=Backend.WALLUST)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")

            with pytest.raises(ColorExtractionError) as exc_info:
                generator.generate(sample_image, config)

            # Error message is about finding cache file, not reading
            assert "cache" in str(exc_info.value).lower()

    def test_generate_invalid_json(
        self, mock_app_config, sample_image, mock_shutil_which, tmp_path
    ):
        """Test generation when colors file has invalid JSON."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)
        generator.cache_dir = tmp_path / "wallust"

        # Create cache directory structure
        cache_subdir = generator.cache_dir / "abc123"
        cache_subdir.mkdir(parents=True)

        # Create invalid JSON file
        colors_file = cache_subdir / "Resized_Lch_auto_Dark"
        colors_file.write_text("invalid json{")

        config = GeneratorConfig(backend=Backend.WALLUST)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")

            with pytest.raises(ColorExtractionError) as exc_info:
                generator.generate(sample_image, config)

            assert "failed to read" in str(exc_info.value).lower()


class TestWallustGeneratorCLI:
    """Test WallustGenerator CLI execution."""

    def test_run_wallust_success(
        self, mock_app_config, sample_image, mock_shutil_which
    ):
        """Test successful CLI execution."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)
        config = GeneratorConfig(backend=Backend.WALLUST)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")
            generator._run_wallust(sample_image, config)

        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "wallust" in call_args[0][0]
        assert str(sample_image) in call_args[0][0]

    def test_run_wallust_with_backend_type(
        self, mock_app_config, sample_image, mock_shutil_which
    ):
        """Test CLI execution with backend type."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)
        generator.backend_type = "full"
        config = GeneratorConfig(backend=Backend.WALLUST)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")
            generator._run_wallust(sample_image, config)

        call_args = mock_run.call_args[0][0]
        assert "--backend" in call_args
        assert "full" in call_args


class TestWallustGeneratorParsing:
    """Test WallustGenerator parsing methods."""

    def test_parse_wallust_output_complete(
        self, mock_app_config, sample_image
    ):
        """Test parsing complete wallust output."""
        generator = WallustGenerator(mock_app_config)

        # Wallust uses flat structure, not nested under "colors"
        wallust_data = {
            "background": "#1a1a1a",
            "foreground": "#ffffff",
            "cursor": "#ff0000",
            **{f"color{i}": f"#{i:02x}{i:02x}{i:02x}" for i in range(16)},
        }

        scheme = generator._parse_wallust_output(wallust_data, sample_image)

        assert scheme.background.hex == "#1a1a1a"
        assert scheme.foreground.hex == "#ffffff"
        assert scheme.cursor.hex == "#ff0000"
        assert len(scheme.colors) == 16
        assert scheme.backend == "wallust"
        assert str(scheme.source_image) == str(sample_image)

    def test_parse_wallust_output_missing_special(
        self, mock_app_config, sample_image
    ):
        """Test parsing when special colors are missing."""
        generator = WallustGenerator(mock_app_config)

        wallust_data = {
            f"color{i}": f"#{i:02x}{i:02x}{i:02x}" for i in range(16)
        }

        scheme = generator._parse_wallust_output(wallust_data, sample_image)

        # Should use defaults
        assert scheme.background.hex == "#000000"
        assert scheme.foreground.hex == "#ffffff"

    def test_parse_color_with_hash(self, mock_app_config):
        """Test parsing color with hash prefix."""
        generator = WallustGenerator(mock_app_config)

        color = generator._parse_color("#1a2b3c")

        assert color.hex == "#1a2b3c"
        assert color.rgb == (26, 43, 60)

    def test_parse_color_without_hash(self, mock_app_config):
        """Test parsing color without hash prefix."""
        generator = WallustGenerator(mock_app_config)

        color = generator._parse_color("1a2b3c")

        assert color.hex == "#1a2b3c"
        assert color.rgb == (26, 43, 60)


class TestWallustGeneratorIntegration:
    """Test WallustGenerator integration scenarios."""

    def test_full_workflow(
        self, mock_app_config, sample_image, mock_shutil_which, tmp_path
    ):
        """Test full workflow from image to ColorScheme."""
        mock_shutil_which.return_value = "/usr/bin/wallust"
        generator = WallustGenerator(mock_app_config)
        generator.cache_dir = tmp_path / "wallust"

        # Create cache directory structure
        cache_subdir = generator.cache_dir / "abc123"
        cache_subdir.mkdir(parents=True)

        # Create mock wallust output (flat structure)
        colors_file = cache_subdir / "Resized_Lch_auto_Dark"
        wallust_data = {
            "background": "#1a1a1a",
            "foreground": "#ffffff",
            "cursor": "#ff0000",
            **{f"color{i}": f"#{i:02x}{i:02x}{i:02x}" for i in range(16)},
        }
        colors_file.write_text(json.dumps(wallust_data))

        config = GeneratorConfig(backend=Backend.WALLUST)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")
            scheme = generator.generate(sample_image, config)

        assert isinstance(scheme, ColorScheme)
        assert len(scheme.colors) == 16
        assert scheme.backend == "wallust"
        assert scheme.background.hex == "#1a1a1a"
