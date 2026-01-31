"""Tests for core types."""

from datetime import datetime
from pathlib import Path

import pytest

from colorscheme_generator.config.enums import Backend, ColorFormat
from colorscheme_generator.core.types import (
    Color,
    ColorScheme,
    GeneratorConfig,
)


class TestColor:
    """Test Color type."""

    def test_create_color_basic(self):
        """Test creating a basic color."""
        color = Color(hex="#FF5733", rgb=(255, 87, 51))
        assert color.hex == "#FF5733"
        assert color.rgb == (255, 87, 51)
        assert color.hsl is None

    def test_create_color_with_hsl(self):
        """Test creating a color with HSL."""
        color = Color(hex="#FF5733", rgb=(255, 87, 51), hsl=(11.0, 1.0, 0.6))
        assert color.hsl == (11.0, 1.0, 0.6)

    def test_color_hex_validation(self):
        """Test hex color validation."""
        # Valid hex colors
        Color(hex="#FF5733", rgb=(255, 87, 51))
        Color(hex="#000000", rgb=(0, 0, 0))
        Color(hex="#FFFFFF", rgb=(255, 255, 255))

        # Invalid hex colors should raise validation error
        with pytest.raises(ValueError):
            Color(hex="FF5733", rgb=(255, 87, 51))  # Missing #

        with pytest.raises(ValueError):
            Color(hex="#FF57", rgb=(255, 87, 51))  # Too short

        with pytest.raises(ValueError):
            Color(hex="#FF5733AA", rgb=(255, 87, 51))  # Too long

    def test_color_rgb_tuple(self):
        """Test RGB tuple validation."""
        color = Color(hex="#FF5733", rgb=(255, 87, 51))
        assert isinstance(color.rgb, tuple)
        assert len(color.rgb) == 3
        assert all(isinstance(v, int) for v in color.rgb)

    def test_color_equality(self):
        """Test color equality."""
        color1 = Color(hex="#FF5733", rgb=(255, 87, 51))
        color2 = Color(hex="#FF5733", rgb=(255, 87, 51))
        assert color1 == color2

    def test_color_serialization(self):
        """Test color serialization."""
        color = Color(hex="#FF5733", rgb=(255, 87, 51))
        data = color.model_dump()
        assert data["hex"] == "#FF5733"
        assert data["rgb"] == (255, 87, 51)


class TestColorScheme:
    """Test ColorScheme type."""

    def test_create_color_scheme(self, sample_colors, sample_image):
        """Test creating a color scheme."""
        scheme = ColorScheme(
            background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
            foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
            cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
            colors=sample_colors,
            source_image=sample_image,
            backend="pywal",
        )

        assert scheme.background.hex == "#1a1a1a"
        assert scheme.foreground.hex == "#ffffff"
        assert scheme.cursor.hex == "#ff0000"
        assert len(scheme.colors) == 16
        assert scheme.backend == "pywal"
        assert scheme.source_image == sample_image

    def test_color_scheme_requires_16_colors(self, sample_image):
        """Test that color scheme requires exactly 16 colors."""
        # Too few colors
        with pytest.raises(ValueError):
            ColorScheme(
                background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
                foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
                cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
                colors=[Color(hex="#000000", rgb=(0, 0, 0))],  # Only 1
                source_image=sample_image,
                backend="pywal",
            )

        # Too many colors
        with pytest.raises(ValueError):
            colors = [
                Color(hex=f"#{i:02x}0000", rgb=(i, 0, 0)) for i in range(20)
            ]
            ColorScheme(
                background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
                foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
                cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
                colors=colors,
                source_image=sample_image,
                backend="pywal",
            )

    def test_color_scheme_generated_at(self, sample_color_scheme):
        """Test that generated_at is set automatically."""
        assert isinstance(sample_color_scheme.generated_at, datetime)

    def test_color_scheme_output_files_default(self, sample_color_scheme):
        """Test that output_files defaults to empty dict."""
        assert sample_color_scheme.output_files == {}

    def test_color_scheme_output_files_can_be_set(
        self, sample_color_scheme, tmp_path
    ):
        """Test that output_files can be set."""
        output_file = tmp_path / "colors.json"
        sample_color_scheme.output_files["json"] = output_file
        assert sample_color_scheme.output_files["json"] == output_file

    def test_color_scheme_serialization(self, sample_color_scheme):
        """Test color scheme serialization."""
        data = sample_color_scheme.model_dump()
        assert "background" in data
        assert "foreground" in data
        assert "cursor" in data
        assert "colors" in data
        assert len(data["colors"]) == 16
        assert "backend" in data
        assert "source_image" in data


class TestGeneratorConfig:
    """Test GeneratorConfig type."""

    def test_create_generator_config(self, tmp_path):
        """Test creating a generator config."""
        config = GeneratorConfig(
            backend=Backend.PYWAL,
            output_dir=tmp_path / "output",
            formats=[ColorFormat.JSON, ColorFormat.CSS],

            backend_options={},
        )

        assert config.backend == Backend.PYWAL
        assert config.output_dir == tmp_path / "output"
        assert config.formats == [ColorFormat.JSON, ColorFormat.CSS]

        assert config.backend_options == {}

    def test_generator_config_defaults(self):
        """Test generator config defaults."""
        config = GeneratorConfig(
            backend=Backend.PYWAL,
            output_dir=Path("/tmp/output"),
            formats=[ColorFormat.JSON],
        )

        # Fields are optional (None by default)

        assert config.saturation_adjustment is None
        assert config.backend_options == {}  # Default

    def test_generator_config_with_backend_options(self, tmp_path):
        """Test generator config with backend options."""
        config = GeneratorConfig(
            backend=Backend.CUSTOM,
            output_dir=tmp_path / "output",
            formats=[ColorFormat.JSON],
            backend_options={"algorithm": "median_cut", "n_clusters": 24},
        )

        assert config.backend_options["algorithm"] == "median_cut"
        assert config.backend_options["n_clusters"] == 24

    def test_generator_config_from_settings(self, mock_app_config, tmp_path):
        """Test creating config from settings."""
        config = GeneratorConfig.from_settings(
            mock_app_config,
            backend=Backend.PYWAL,
            output_dir=tmp_path / "output",
        )

        assert config.backend == Backend.PYWAL
        assert config.output_dir == tmp_path / "output"

    def test_generator_config_serialization(self, sample_generator_config):
        """Test generator config serialization."""
        data = sample_generator_config.model_dump()
        assert "backend" in data
        assert "output_dir" in data
        assert "formats" in data

        assert "backend_options" in data

    def test_generator_config_get_backend_settings_pywal(
        self, mock_app_config
    ):
        """Test getting backend settings for pywal."""
        config = GeneratorConfig(backend=Backend.PYWAL)
        settings = config.get_backend_settings(mock_app_config)



    def test_generator_config_get_backend_settings_wallust(
        self, mock_app_config
    ):
        """Test getting backend settings for wallust."""
        config = GeneratorConfig(backend=Backend.WALLUST)
        settings = config.get_backend_settings(mock_app_config)


        assert "backend_type" in settings

    def test_generator_config_get_backend_settings_custom(
        self, mock_app_config
    ):
        """Test getting backend settings for custom."""
        config = GeneratorConfig(backend=Backend.CUSTOM)
        settings = config.get_backend_settings(mock_app_config)

        assert "algorithm" in settings
        assert "n_clusters" in settings

    def test_generator_config_get_backend_settings_with_options(
        self, mock_app_config
    ):
        """Test getting backend settings with runtime options."""
        config = GeneratorConfig(
            backend=Backend.PYWAL, backend_options={"custom_option": "value"}
        )
        settings = config.get_backend_settings(mock_app_config)

        assert "custom_option" in settings
        assert settings["custom_option"] == "value"

    def test_generator_config_get_backend_settings_default_backend(
        self, mock_app_config
    ):
        """Test getting backend settings when no backend is specified."""
        config = GeneratorConfig()  # No backend specified
        settings = config.get_backend_settings(mock_app_config)

        # Should use default backend from settings (PYWAL)

