"""Core type definitions for colorscheme generator."""

import colorsys
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend, ColorFormat


class Color(BaseModel):
    """Single color in multiple formats.

    Attributes:
        hex: Hex color code (e.g., "#FF5733")
        rgb: RGB tuple (0-255 for each channel)
        hsl: Optional HSL tuple (hue: 0-360, saturation: 0-1, lightness: 0-1)
    """

    hex: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    rgb: tuple[int, int, int]
    hsl: tuple[float, float, float] | None = None

    @field_validator("rgb")
    @classmethod
    def validate_rgb(cls, v: tuple[int, int, int]) -> tuple[int, int, int]:
        """Validate RGB values are in range 0-255."""
        if not all(0 <= val <= 255 for val in v):
            raise ValueError(f"RGB values must be in range 0-255, got {v}")
        return v

    @model_validator(mode="after")
    def validate_hex_rgb_match(self) -> "Color":
        """Validate that hex and RGB values are consistent."""
        hex_clean = self.hex.lstrip("#")
        expected_rgb = tuple(int(hex_clean[i : i + 2], 16) for i in (0, 2, 4))
        if self.rgb != expected_rgb:
            raise ValueError(f"RGB {self.rgb} does not match hex {self.hex}")
        return self

    def adjust_saturation(self, factor: float) -> "Color":
        """Adjust color saturation by a multiplier.

        Args:
            factor: Saturation multiplier (0.0-2.0)

        Returns:
            New Color with adjusted saturation
        """
        # Convert RGB (0-255) to RGB (0-1)
        r, g, b = self.rgb[0] / 255.0, self.rgb[1] / 255.0, self.rgb[2] / 255.0

        # Convert to HLS (Hue, Lightness, Saturation)
        hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)

        # Adjust saturation
        saturation = max(0.0, min(1.0, saturation * factor))  # Clamp to [0, 1]

        # Convert back to RGB
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

        # Convert to 0-255 range
        new_rgb = (
            int(round(r * 255)),
            int(round(g * 255)),
            int(round(b * 255)),
        )

        # Convert to hex
        new_hex = f"#{new_rgb[0]:02X}{new_rgb[1]:02X}{new_rgb[2]:02X}"

        # Create new Color with adjusted values
        return Color(
            hex=new_hex,
            rgb=new_rgb,
            hsl=(hue * 360, saturation, lightness) if self.hsl else None,
        )


class ColorScheme(BaseModel):
    """Complete color scheme from image.

    Attributes:
        background: Background color
        foreground: Foreground/text color
        cursor: Cursor color
        colors: List of 16 terminal colors (ANSI colors 0-15)
        source_image: Path to source image
        backend: Backend used for generation
        generated_at: Timestamp of generation
        output_files: Dict of format -> path (populated by OutputManager)
    """

    background: Color
    foreground: Color
    cursor: Color
    colors: list[Color] = Field(..., min_length=16, max_length=16)

    # Metadata
    source_image: Path
    backend: str
    generated_at: datetime = Field(default_factory=datetime.now)

    # Output files (populated by OutputManager after writing)
    output_files: dict[str, Path] = Field(default_factory=dict)


class GeneratorConfig(BaseModel):
    """Runtime configuration for color scheme generation.

    Attributes:
        backend: Backend to use
        color_count: Number of colors (fixed at 16)
        saturation_adjustment: Saturation adjustment factor
        output_dir: Output directory
        formats: Output formats
        backend_options: Backend-specific options
    """

    # Color extraction settings (for backends)
    backend: Backend | None = None
    color_count: int = 16  # Hardcoded, not configurable

    saturation_adjustment: float | None = None

    # File output settings (for OutputManager)
    output_dir: Path | None = None
    formats: list[ColorFormat] | None = None

    # Backend-specific options (merged with settings)
    backend_options: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_settings(cls, settings: AppConfig, **overrides: Any) -> "GeneratorConfig":
        """Create config from settings with optional overrides."""
        return cls(
            backend=overrides.get("backend")
            or Backend(settings.generation.default_backend),
            color_count=16,
            saturation_adjustment=overrides.get("saturation_adjustment")
            or settings.generation.saturation_adjustment,
            output_dir=overrides.get("output_dir") or settings.output.directory,
            formats=overrides.get("formats")
            or [ColorFormat(f) for f in settings.output.formats],
            backend_options=overrides.get("backend_options", {}),
        )

    def get_backend_settings(self, settings: AppConfig) -> dict[str, Any]:
        """Get backend-specific settings merged with runtime options."""
        backend = self.backend or Backend(settings.generation.default_backend)

        if backend == Backend.PYWAL:
            base_settings = settings.backends.pywal.model_dump()
        elif backend == Backend.WALLUST:
            base_settings = settings.backends.wallust.model_dump()
        elif backend == Backend.CUSTOM:
            base_settings = settings.backends.custom.model_dump()
        else:
            base_settings = {}

        return {**base_settings, **self.backend_options}
