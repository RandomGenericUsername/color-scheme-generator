"""Core types and base classes for color scheme generation."""

from color_scheme.core.base import ColorSchemeGenerator
from color_scheme.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    ColorSchemeError,
    InvalidImageError,
    OutputWriteError,
    TemplateRenderError,
)
from color_scheme.core.types import Color, ColorScheme, GeneratorConfig

__all__ = [
    "Color",
    "ColorScheme",
    "GeneratorConfig",
    "ColorSchemeGenerator",
    "ColorSchemeError",
    "InvalidImageError",
    "ColorExtractionError",
    "BackendNotAvailableError",
    "OutputWriteError",
    "TemplateRenderError",
]
