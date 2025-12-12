"""Colorscheme Generator - Generate color schemes from images.

This module provides a flexible system for extracting color schemes from images
using multiple backends (pywal, wallust, custom) and writing them to various
output formats.

Architecture:
    - Backends: Extract colors from images → ColorScheme object
    - OutputManager: Write ColorScheme to files using templates

Example:
    >>> from colorscheme_generator import ColorSchemeGeneratorFactory
    >>> from colorscheme_generator.config.settings import Settings
    >>> from colorscheme_generator.core.types import GeneratorConfig
    >>> from colorscheme_generator.config.enums import Backend
    >>>
    >>> settings = Settings.get()
    >>> config = GeneratorConfig.from_settings(settings)
    >>>
    >>> # Extract colors
    >>> generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
    >>> scheme = generator.generate(Path("~/wallpapers/mountain.png"), config)
    >>>
    >>> # Write files
    >>> from colorscheme_generator.core.managers import OutputManager
    >>> manager = OutputManager(settings)
    >>> output_files = manager.write_outputs(
    ...     scheme, config.output_dir, config.formats
    ... )
"""

__version__ = "0.1.0"

# Core exports
# Configuration exports
# Backends
from colorscheme_generator.backends.wallust import WallustGenerator
from colorscheme_generator.config import (
    AppConfig,
    Backend,
    ColorFormat,
    Settings,
)
from colorscheme_generator.core import (
    Color,
    ColorScheme,
    ColorSchemeGenerator,
    GeneratorConfig,
)
from colorscheme_generator.core.managers import OutputManager

# Factory
from colorscheme_generator.factory import ColorSchemeGeneratorFactory

__all__ = [
    # Version
    "__version__",
    # Core
    "ColorSchemeGenerator",
    "Color",
    "ColorScheme",
    "GeneratorConfig",
    "OutputManager",
    # Config
    "AppConfig",
    "Backend",
    "ColorFormat",
    "Settings",
    # Backends
    "WallustGenerator",
    # Factory
    "ColorSchemeGeneratorFactory",
]
