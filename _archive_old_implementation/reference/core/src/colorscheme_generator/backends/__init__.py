"""Backend implementations for color extraction.

This module contains concrete implementations of ColorSchemeGenerator
for different backends (pywal, wallust, custom).
"""

from colorscheme_generator.backends.custom import CustomGenerator
from colorscheme_generator.backends.pywal import PywalGenerator
from colorscheme_generator.backends.wallust import WallustGenerator

__all__ = [
    "PywalGenerator",
    "WallustGenerator",
    "CustomGenerator",
]
