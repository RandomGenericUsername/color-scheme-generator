"""Tests for pywal backend."""

from pathlib import Path
from unittest.mock import patch

import pytest

from color_scheme.backends.pywal import PywalGenerator
from color_scheme.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
)
from color_scheme.core.types import GeneratorConfig


class TestPywalGenerator:
    """Tests for PywalGenerator."""

    @pytest.fixture
    def generator(self, app_config):
        """Create PywalGenerator."""
        return PywalGenerator(app_config)

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
        assert generator.backend_name == "pywal"

    @patch("shutil.which")
    def test_is_available_true(self, mock_which, generator):
        """Test is_available when pywal is installed."""
        mock_which.return_value = "/usr/bin/wal"
        assert generator.is_available() is True

    @patch("shutil.which")
    def test_is_available_false(self, mock_which, generator):
        """Test is_available when pywal is not installed."""
        mock_which.return_value = None
        assert generator.is_available() is False

    @patch("shutil.which")
    def test_ensure_available_raises(self, mock_which, generator):
        """Test ensure_available raises when not available."""
        mock_which.return_value = None

        with pytest.raises(BackendNotAvailableError) as exc_info:
            generator.ensure_available()

        assert "pywal" in str(exc_info.value).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_success(
        self, mock_which, mock_run, generator, test_image, config, tmp_path
    ):
        """Test successful color generation."""
        mock_which.return_value = "/usr/bin/wal"

        # Mock subprocess.run to return success
        from unittest.mock import MagicMock

        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        mock_run.return_value = result

        # Mock pywal cache file
        cache_file = tmp_path / "colors.json"
        cache_file.write_text(
            """{
            "special": {
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "cursor": "#ff0000"
            },
            "colors": {
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
            }
        }"""
        )

        with patch.object(generator, "_get_cache_file", return_value=cache_file):
            scheme = generator.generate(test_image, config)

        assert scheme.backend == "pywal"
        assert len(scheme.colors) == 16
        assert scheme.background.hex == "#1A1A1A"
        assert scheme.foreground.hex == "#FFFFFF"

    @patch("shutil.which")
    def test_generate_invalid_image(self, mock_which, generator, config):
        """Test generation with invalid image."""
        mock_which.return_value = "/usr/bin/wal"
        invalid_path = Path("/nonexistent/image.png")

        with pytest.raises(InvalidImageError):
            generator.generate(invalid_path, config)

    @patch("shutil.which")
    def test_generate_directory_path(self, mock_which, generator, config, tmp_path):
        """Test generation with directory instead of file."""
        mock_which.return_value = "/usr/bin/wal"

        with pytest.raises(InvalidImageError) as exc_info:
            generator.generate(tmp_path, config)

        assert "Not a file" in str(exc_info.value)

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_subprocess_error(
        self, mock_which, mock_run, generator, test_image, config
    ):
        """Test generation with subprocess error."""
        mock_which.return_value = "/usr/bin/wal"
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "wal", stderr="pywal error"
        )

        with pytest.raises(ColorExtractionError) as exc_info:
            generator.generate(test_image, config)

        assert "Pywal failed" in str(exc_info.value)

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_timeout(
        self, mock_which, mock_run, generator, test_image, config
    ):
        """Test generation with timeout."""
        mock_which.return_value = "/usr/bin/wal"
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("wal", 30)

        with pytest.raises(ColorExtractionError) as exc_info:
            generator.generate(test_image, config)

        assert "timed out" in str(exc_info.value).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_cache_file_not_found(
        self, mock_which, mock_run, generator, test_image, config, tmp_path
    ):
        """Test generation when cache file doesn't exist."""
        from unittest.mock import MagicMock

        mock_which.return_value = "/usr/bin/wal"

        # Mock subprocess.run to return success (so the code tries to read cache)
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        mock_run.return_value = result

        # Mock cache file that doesn't exist
        cache_file = tmp_path / "nonexistent.json"

        with patch.object(generator, "_get_cache_file", return_value=cache_file):
            with pytest.raises(ColorExtractionError) as exc_info:
                generator.generate(test_image, config)

            assert "Cache file not found" in str(exc_info.value)

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_invalid_json(
        self, mock_which, mock_run, generator, test_image, config, tmp_path
    ):
        """Test generation with invalid JSON in cache."""
        from unittest.mock import MagicMock

        mock_which.return_value = "/usr/bin/wal"

        # Mock subprocess.run to return success (so the code tries to read cache)
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        mock_run.return_value = result

        # Mock cache file with invalid JSON
        cache_file = tmp_path / "invalid.json"
        cache_file.write_text("not valid json{")

        with patch.object(generator, "_get_cache_file", return_value=cache_file):
            with pytest.raises(ColorExtractionError) as exc_info:
                generator.generate(test_image, config)

            assert "Invalid JSON" in str(exc_info.value)

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_with_saturation(
        self, mock_which, mock_run, generator, test_image, tmp_path
    ):
        """Test generation with saturation adjustment."""
        from unittest.mock import MagicMock

        mock_which.return_value = "/usr/bin/wal"

        # Mock subprocess.run to return success
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        mock_run.return_value = result

        # Mock pywal cache file
        cache_file = tmp_path / "colors.json"
        cache_file.write_text(
            """{
            "special": {
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "cursor": "#ff0000"
            },
            "colors": {
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
            }
        }"""
        )

        config = GeneratorConfig(saturation_adjustment=1.5)

        with patch.object(generator, "_get_cache_file", return_value=cache_file):
            scheme = generator.generate(test_image, config)

        assert scheme.backend == "pywal"
        assert len(scheme.colors) == 16
