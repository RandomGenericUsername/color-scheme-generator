"""Logging infrastructure for colorscheme generator.

This module provides Rich-based logging with configurable levels.
"""

from colorscheme_generator.logging.config import (
    LoggingConfig,
    get_logger,
    setup_logging,
)
from colorscheme_generator.logging.display import ColorSchemeDisplay

__all__ = [
    "ColorSchemeDisplay",
    "LoggingConfig",
    "get_logger",
    "setup_logging",
]

