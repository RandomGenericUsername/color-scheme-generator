"""Core module for colorscheme generator.

This module contains the core abstractions and types used throughout
the colorscheme generator.
"""

from colorscheme_generator.core.base import ColorSchemeGenerator
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    ColorSchemeGeneratorError,
    InvalidImageError,
    OutputWriteError,
    TemplateRenderError,
)
from colorscheme_generator.core.types import (
    Color,
    ColorScheme,
    GeneratorConfig,
)

__all__ = [
    # Base classes
    "ColorSchemeGenerator",
    # Types
    "Color",
    "ColorScheme",
    "GeneratorConfig",
    # Exceptions
    "ColorSchemeGeneratorError",
    "BackendNotAvailableError",
    "ColorExtractionError",
    "TemplateRenderError",
    "OutputWriteError",
    "InvalidImageError",
]
