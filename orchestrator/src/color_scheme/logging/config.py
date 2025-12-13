"""Logging configuration for the color-scheme orchestrator.

This module provides logging setup using Rich for beautiful terminal output.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


@dataclass
class LoggingConfig:
    """Configuration for logging behavior.

    Attributes:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        show_time: Whether to show timestamps in log output
        show_path: Whether to show file paths in log output
        rich_tracebacks: Whether to use Rich for traceback formatting
    """

    level: int = logging.INFO
    show_time: bool = True
    show_path: bool = False
    rich_tracebacks: bool = True


# Module-level console for logging
_console: Optional[Console] = None


def get_console() -> Console:
    """Get the logging console instance.

    Returns:
        The Rich Console used for logging output.
    """
    global _console
    if _console is None:
        _console = Console(stderr=True)
    return _console


def setup_logging(
    config: Optional[LoggingConfig] = None,
    console: Optional[Console] = None,
) -> None:
    """Set up logging with Rich handler.

    Args:
        config: Logging configuration. Uses defaults if not provided.
        console: Rich Console to use. Creates new one if not provided.
    """
    global _console

    if config is None:
        config = LoggingConfig()

    if console is not None:
        _console = console
    else:
        _console = Console(stderr=True)

    # Create Rich handler
    handler = RichHandler(
        console=_console,
        show_time=config.show_time,
        show_path=config.show_path,
        rich_tracebacks=config.rich_tracebacks,
        tracebacks_show_locals=config.level == logging.DEBUG,
    )

    # Configure the color_scheme logger
    logger = logging.getLogger("color_scheme")
    logger.setLevel(config.level)

    # Remove existing handlers
    logger.handlers.clear()

    # Add Rich handler
    logger.addHandler(handler)

    # Don't propagate to root logger
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance configured for the color_scheme package.
    """
    return logging.getLogger(name)

