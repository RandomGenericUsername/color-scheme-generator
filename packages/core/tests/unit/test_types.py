"""Tests for core type definitions."""

from pathlib import Path

import pytest

from color_scheme.config.enums import Backend
from color_scheme.core.types import Color, ColorScheme, GeneratorConfig


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

    def test_rgb_validation_negative(self):
        """Test RGB validation rejects negative values."""
        with pytest.raises(ValueError, match="RGB values must be in range 0-255"):
            Color(hex="#000000", rgb=(-1, 0, 0))

        with pytest.raises(ValueError, match="RGB values must be in range 0-255"):
            Color(hex="#000000", rgb=(0, -10, 0))

        with pytest.raises(ValueError, match="RGB values must be in range 0-255"):
            Color(hex="#000000", rgb=(0, 0, -255))

    def test_rgb_validation_too_large(self):
        """Test RGB validation rejects values > 255."""
        with pytest.raises(ValueError, match="RGB values must be in range 0-255"):
            Color(hex="#FFFFFF", rgb=(256, 255, 255))

        with pytest.raises(ValueError, match="RGB values must be in range 0-255"):
            Color(hex="#FFFFFF", rgb=(255, 300, 255))

        with pytest.raises(ValueError, match="RGB values must be in range 0-255"):
            Color(hex="#FFFFFF", rgb=(255, 255, 1000))

    def test_rgb_validation_boundary_values(self):
        """Test RGB validation accepts boundary values 0 and 255."""
        # Test 0
        color_black = Color(hex="#000000", rgb=(0, 0, 0))
        assert color_black.rgb == (0, 0, 0)

        # Test 255
        color_white = Color(hex="#FFFFFF", rgb=(255, 255, 255))
        assert color_white.rgb == (255, 255, 255)

        # Test mixed boundaries
        color_mixed = Color(hex="#FF0000", rgb=(255, 0, 0))
        assert color_mixed.rgb == (255, 0, 0)

    def test_hex_rgb_mismatch(self):
        """Test validation rejects mismatched hex and RGB values."""
        with pytest.raises(ValueError, match="RGB .* does not match hex"):
            Color(hex="#FF5733", rgb=(255, 255, 255))

        with pytest.raises(ValueError, match="RGB .* does not match hex"):
            Color(hex="#000000", rgb=(255, 255, 255))

        with pytest.raises(ValueError, match="RGB .* does not match hex"):
            Color(hex="#FFFFFF", rgb=(0, 0, 0))

    def test_hex_rgb_consistency_valid(self):
        """Test validation accepts matching hex and RGB values."""
        # Test various valid combinations
        valid_colors = [
            ("#FF5733", (255, 87, 51)),
            ("#000000", (0, 0, 0)),
            ("#FFFFFF", (255, 255, 255)),
            ("#1a1a1a", (26, 26, 26)),
            ("#ABCDEF", (171, 205, 239)),
            ("#123456", (18, 52, 86)),
        ]

        for hex_val, rgb_val in valid_colors:
            color = Color(hex=hex_val, rgb=rgb_val)
            assert color.hex == hex_val
            assert color.rgb == rgb_val

    def test_validation_order(self):
        """Test that RGB range validation happens before consistency check."""
        # RGB out of range should be caught first
        with pytest.raises(ValueError, match="RGB values must be in range 0-255"):
            Color(hex="#FF5733", rgb=(256, 87, 51))

    def test_combined_invalid_values(self):
        """Test multiple invalid conditions together."""
        # Both RGB out of range and mismatched
        with pytest.raises(ValueError, match="RGB values must be in range 0-255"):
            Color(hex="#FF5733", rgb=(300, -1, 400))


class TestColorScheme:
    """Tests for ColorScheme type."""

    def test_colorscheme_creation(self):
        """Test creating a ColorScheme."""
        colors = [
            Color(hex=f"#{i:02x}{i:02x}{i:02x}", rgb=(i, i, i)) for i in range(16)
        ]

        scheme = ColorScheme(
            background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
            foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
            cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
            colors=colors,
            source_image=Path("/tmp/test.png"),
            backend="custom",
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
                backend="custom",
            )


class TestGeneratorConfig:
    """Tests for GeneratorConfig type."""

    def test_from_settings(self, app_config):
        """Test creating config from settings."""
        config = GeneratorConfig.from_settings(app_config)

        assert config.backend is not None
        assert config.color_count == 16
        assert config.output_dir is not None
        assert config.formats is not None
        assert isinstance(config.backend_options, dict)

    def test_from_settings_with_overrides(self, app_config):
        """Test creating config with overrides."""
        config = GeneratorConfig.from_settings(
            app_config,
            backend=Backend.WALLUST,
            saturation_adjustment=0.8,
            backend_options={"test": "value"},
        )

        assert config.backend == Backend.WALLUST
        assert config.saturation_adjustment == 0.8
        assert config.backend_options == {"test": "value"}

    def test_get_backend_settings(self, app_config):
        """Test getting backend-specific settings."""
        # Test for each backend
        for backend in [Backend.PYWAL, Backend.WALLUST, Backend.CUSTOM]:
            config = GeneratorConfig(backend=backend)
            backend_settings = config.get_backend_settings(app_config)
            assert isinstance(backend_settings, dict)
