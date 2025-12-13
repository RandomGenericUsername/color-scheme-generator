"""Logging infrastructure for the color-scheme orchestrator.

This module provides Rich-based logging with configurable verbosity levels.
"""

from color_scheme.logging.config import (
    LoggingConfig,
    get_logger,
    setup_logging,
)

__all__ = [
    "LoggingConfig",
    "get_logger",
    "setup_logging",
]

