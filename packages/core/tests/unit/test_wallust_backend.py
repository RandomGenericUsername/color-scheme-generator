"""Tests for wallust backend."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from color_scheme.backends.wallust import WallustGenerator
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
)
from color_scheme.core.types import GeneratorConfig


class TestWallustGenerator:
    """Tests for WallustGenerator."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def generator(self, settings):
        """Create WallustGenerator."""
        return WallustGenerator(settings)

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    @pytest.fixture
    def config(self):
        """Create GeneratorConfig."""
        return GeneratorConfig()

    def test_backend_name(self, generator):
        """Test backend name."""
        assert generator.backend_name == "wallust"

    @patch("shutil.which")
    def test_is_available_true(self, mock_which, generator):
        """Test is_available when wallust is installed."""
        mock_which.return_value = "/usr/bin/wallust"
        assert generator.is_available() is True

    @patch("shutil.which")
    def test_is_available_false(self, mock_which, generator):
        """Test is_available when wallust is not installed."""
        mock_which.return_value = None
        assert generator.is_available() is False

    @patch("shutil.which")
    def test_ensure_available_raises(self, mock_which, generator):
        """Test ensure_available raises when not available."""
        mock_which.return_value = None

        with pytest.raises(BackendNotAvailableError) as exc_info:
            generator.ensure_available()

        assert "wallust" in str(exc_info.value).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_success(self, mock_which, mock_run, generator, test_image, config):
        """Test successful color generation."""
        mock_which.return_value = "/usr/bin/wallust"

        # Mock wallust JSON output
        mock_run.return_value = MagicMock()
        mock_run.return_value.stdout = '''{
            "background": "#1a1a1a",
            "foreground": "#ffffff",
            "cursor": "#ff0000",
            "color0": "#000000",
            "color1": "#111111",
            "color2": "#222222",
            "color3": "#333333",
            "color4": "#444444",
            "color5": "#555555",
            "color6": "#666666",
            "color7": "#777777",
            "color8": "#888888",
            "color9": "#999999",
            "color10": "#aaaaaa",
            "color11": "#bbbbbb",
            "color12": "#cccccc",
            "color13": "#dddddd",
            "color14": "#eeeeee",
            "color15": "#ffffff"
        }'''

        scheme = generator.generate(test_image, config)

        assert scheme.backend == "wallust"
        assert len(scheme.colors) == 16
        assert scheme.background.hex == "#1A1A1A"
        assert scheme.foreground.hex == "#FFFFFF"

    @patch("shutil.which")
    def test_generate_invalid_image(self, mock_which, generator, config):
        """Test generation with invalid image."""
        mock_which.return_value = "/usr/bin/wallust"
        invalid_path = Path("/nonexistent/image.png")

        with pytest.raises(InvalidImageError):
            generator.generate(invalid_path, config)

    @patch("shutil.which")
    def test_generate_directory_path(self, mock_which, generator, config, tmp_path):
        """Test generation with directory instead of file."""
        mock_which.return_value = "/usr/bin/wallust"

        with pytest.raises(InvalidImageError) as exc_info:
            generator.generate(tmp_path, config)

        assert "Not a file" in str(exc_info.value)

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_subprocess_error(self, mock_which, mock_run, generator, test_image, config):
        """Test generation with subprocess error."""
        mock_which.return_value = "/usr/bin/wallust"
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "wallust", stderr="wallust error"
        )

        with pytest.raises(ColorExtractionError) as exc_info:
            generator.generate(test_image, config)

        assert "Wallust failed" in str(exc_info.value)

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_timeout(self, mock_which, mock_run, generator, test_image, config):
        """Test generation with timeout."""
        mock_which.return_value = "/usr/bin/wallust"
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("wallust", 30)

        with pytest.raises(ColorExtractionError) as exc_info:
            generator.generate(test_image, config)

        assert "timed out" in str(exc_info.value).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_invalid_json(self, mock_which, mock_run, generator, test_image, config):
        """Test generation with invalid JSON output."""
        mock_which.return_value = "/usr/bin/wallust"

        # Mock wallust output with invalid JSON
        mock_run.return_value = MagicMock()
        mock_run.return_value.stdout = "not valid json{"

        with pytest.raises(ColorExtractionError) as exc_info:
            generator.generate(test_image, config)

        assert "Invalid JSON" in str(exc_info.value)

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_with_saturation(self, mock_which, mock_run, generator, test_image):
        """Test generation with saturation adjustment."""
        mock_which.return_value = "/usr/bin/wallust"

        # Mock wallust JSON output
        mock_run.return_value = MagicMock()
        mock_run.return_value.stdout = '''{
            "background": "#1a1a1a",
            "foreground": "#ffffff",
            "cursor": "#ff0000",
            "color0": "#000000",
            "color1": "#111111",
            "color2": "#222222",
            "color3": "#333333",
            "color4": "#444444",
            "color5": "#555555",
            "color6": "#666666",
            "color7": "#777777",
            "color8": "#888888",
            "color9": "#999999",
            "color10": "#aaaaaa",
            "color11": "#bbbbbb",
            "color12": "#cccccc",
            "color13": "#dddddd",
            "color14": "#eeeeee",
            "color15": "#ffffff"
        }'''

        config = GeneratorConfig(saturation_adjustment=1.5)
        scheme = generator.generate(test_image, config)

        assert scheme.backend == "wallust"
        assert len(scheme.colors) == 16
