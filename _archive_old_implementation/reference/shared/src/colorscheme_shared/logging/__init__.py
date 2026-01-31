"""Shared logging infrastructure for color-scheme projects.

This module provides Rich-based logging with configurable levels
for use across multiple color-scheme applications.
"""

from colorscheme_shared.logging.config import (
    LoggingConfig,
    get_console,
    get_logger,
    setup_logging,
)

__all__ = [
    "LoggingConfig",
    "get_logger",
    "setup_logging",
    "get_console",
]
