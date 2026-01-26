"""Tests for core type definitions."""

from pathlib import Path

import pytest

from color_scheme.config.settings import Settings
from color_scheme.core.types import Color, ColorScheme, GeneratorConfig
from color_scheme.config.enums import Backend


class TestColor:
    """Tests for Color type."""

    def test_color_creation(self):
        """Test creating a Color."""
        color = Color(hex="#FF5733", rgb=(255, 87, 51))
        assert color.hex == "#FF5733"
        assert color.rgb == (255, 87, 51)

    def test_color_validation(self):
        """Test Color validation."""
        with pytest.raises(ValueError):
            Color(hex="invalid", rgb=(255, 87, 51))

    def test_adjust_saturation(self):
        """Test saturation adjustment."""
        color = Color(hex="#FF5733", rgb=(255, 87, 51))

        # Test desaturation
        desaturated = color.adjust_saturation(0.5)
        assert desaturated.hex != color.hex

        # Test no change
        unchanged = color.adjust_saturation(1.0)
        assert unchanged.hex == color.hex


class TestColorScheme:
    """Tests for ColorScheme type."""

    def test_colorscheme_creation(self):
        """Test creating a ColorScheme."""
        colors = [
            Color(hex=f"#{i:02x}{i:02x}{i:02x}", rgb=(i, i, i))
            for i in range(16)
        ]

        scheme = ColorScheme(
            background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
            foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
            cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
            colors=colors,
            source_image=Path("/tmp/test.png"),
            backend="custom"
        )

        assert len(scheme.colors) == 16
        assert scheme.backend == "custom"

    def test_colorscheme_validation(self):
        """Test ColorScheme validation."""
        colors = [Color(hex="#000000", rgb=(0, 0, 0)) for _ in range(15)]

        with pytest.raises(ValueError):
            ColorScheme(
                background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
                foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
                cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
                colors=colors,  # Only 15 colors, needs 16
                source_image=Path("/tmp/test.png"),
                backend="custom"
            )


class TestGeneratorConfig:
    """Tests for GeneratorConfig type."""

    def test_from_settings(self):
        """Test creating config from settings."""
        settings = Settings.get()
        config = GeneratorConfig.from_settings(settings)

        assert config.backend is not None
        assert config.color_count == 16
        assert config.output_dir is not None
        assert config.formats is not None
        assert isinstance(config.backend_options, dict)

    def test_from_settings_with_overrides(self):
        """Test creating config with overrides."""
        settings = Settings.get()
        config = GeneratorConfig.from_settings(
            settings,
            backend=Backend.WALLUST,
            saturation_adjustment=0.8,
            backend_options={"test": "value"}
        )

        assert config.backend == Backend.WALLUST
        assert config.saturation_adjustment == 0.8
        assert config.backend_options == {"test": "value"}

    def test_get_backend_settings(self):
        """Test getting backend-specific settings."""
        settings = Settings.get()

        # Test for each backend
        for backend in [Backend.PYWAL, Backend.WALLUST, Backend.CUSTOM]:
            config = GeneratorConfig(backend=backend)
            backend_settings = config.get_backend_settings(settings)
            assert isinstance(backend_settings, dict)
