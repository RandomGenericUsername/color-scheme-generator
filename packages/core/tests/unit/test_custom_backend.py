"""Tests for custom backend."""

from pathlib import Path
from unittest.mock import patch

import pytest

from color_scheme.backends.custom import CustomGenerator
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import ColorExtractionError, InvalidImageError
from color_scheme.core.types import GeneratorConfig


class TestCustomGenerator:
    """Tests for CustomGenerator."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def generator(self, settings):
        """Create CustomGenerator."""
        return CustomGenerator(settings)

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
        assert generator.backend_name == "custom"

    def test_is_available(self, generator):
        """Test is_available."""
        assert generator.is_available() is True

    def test_generate_success(self, generator, test_image, config):
        """Test successful color generation."""
        scheme = generator.generate(test_image, config)

        assert scheme.backend == "custom"
        assert len(scheme.colors) == 16
        assert scheme.source_image == test_image.resolve()

        # Check color format
        assert scheme.background.hex.startswith("#")
        assert len(scheme.background.hex) == 7

    def test_generate_invalid_image(self, generator, config):
        """Test generation with invalid image."""
        invalid_path = Path("/nonexistent/image.png")

        with pytest.raises(InvalidImageError) as exc_info:
            generator.generate(invalid_path, config)

        assert "does not exist" in str(exc_info.value).lower()

    def test_generate_not_a_file(self, generator, config, tmp_path):
        """Test generation with directory instead of file."""
        with pytest.raises(InvalidImageError) as exc_info:
            generator.generate(tmp_path, config)

        assert "not a file" in str(exc_info.value).lower()

    def test_generate_with_saturation_adjustment(self, generator, test_image):
        """Test generation with saturation adjustment."""
        config = GeneratorConfig(saturation_adjustment=1.5)
        scheme = generator.generate(test_image, config)

        assert scheme.backend == "custom"
        assert len(scheme.colors) == 16

    def test_generate_with_few_clusters(self, test_image):
        """Test generation when extracting fewer than 16 colors."""
        # Create generator with only 8 clusters to trigger duplication logic
        from color_scheme.config.config import (
            AppConfig,
            BackendSettings,
            CustomBackendSettings,
        )

        settings = AppConfig(
            backends=BackendSettings(
                custom=CustomBackendSettings(algorithm="kmeans", n_clusters=8)
            )
        )
        generator = CustomGenerator(settings)
        config = GeneratorConfig()

        scheme = generator.generate(test_image, config)

        # Should still have exactly 16 colors (duplicated)
        assert len(scheme.colors) == 16

    def test_generate_with_many_clusters(self, test_image):
        """Test generation when extracting more than 16 colors."""
        # Create generator with 20 clusters to trigger truncation logic
        from color_scheme.config.config import (
            AppConfig,
            BackendSettings,
            CustomBackendSettings,
        )

        settings = AppConfig(
            backends=BackendSettings(
                custom=CustomBackendSettings(algorithm="kmeans", n_clusters=20)
            )
        )
        generator = CustomGenerator(settings)
        config = GeneratorConfig()

        scheme = generator.generate(test_image, config)

        # Should be truncated to exactly 16 colors
        assert len(scheme.colors) == 16

    def test_generate_with_corrupt_image(self, generator, config, tmp_path):
        """Test generation with corrupt image file."""
        # Create a file that looks like an image but isn't
        corrupt_image = tmp_path / "corrupt.png"
        corrupt_image.write_text("not an image")

        with pytest.raises(InvalidImageError) as exc_info:
            generator.generate(corrupt_image, config)

        assert "corrupt.png" in str(exc_info.value).lower()

    def test_generate_color_extraction_error(self, generator, test_image, config):
        """Test color extraction error handling."""
        # Mock _extract_colors_kmeans to raise an exception
        with patch.object(
            generator, "_extract_colors_kmeans", side_effect=RuntimeError("Test error")
        ):
            with pytest.raises(ColorExtractionError) as exc_info:
                generator.generate(test_image, config)

            assert "custom" in str(exc_info.value).lower()
            assert "test error" in str(exc_info.value).lower()
