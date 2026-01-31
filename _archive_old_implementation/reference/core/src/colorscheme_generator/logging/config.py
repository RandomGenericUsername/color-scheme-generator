"""Logging configuration for colorscheme generator.

Uses Python standard logging levels with Rich formatting.
"""

import logging
import sys
from dataclasses import dataclass, field
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


# Module-level logger cache
_loggers: dict[str, logging.Logger] = {}

# Default console for logging
_console: Optional[Console] = None


@dataclass
class LoggingConfig:
    """Configuration for logging behavior.

    Attributes:
        level: Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        show_time: Whether to show timestamps in log messages
        show_path: Whether to show file path in log messages
        rich_tracebacks: Whether to use rich tracebacks for exceptions
    """

    level: int = logging.INFO
    show_time: bool = True
    show_path: bool = False
    rich_tracebacks: bool = True

    # Internal state
    _initialized: bool = field(default=False, repr=False)

    @classmethod
    def from_string(cls, level_str: str) -> "LoggingConfig":
        """Create config from level string.

        Args:
            level_str: Level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            LoggingConfig with appropriate level
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        level = level_map.get(level_str.upper(), logging.INFO)
        return cls(level=level)


def setup_logging(
    config: Optional[LoggingConfig] = None,
    console: Optional[Console] = None,
) -> None:
    """Initialize logging with Rich handler.

    Args:
        config: Logging configuration (defaults to INFO level)
        console: Rich console to use (creates new if not provided)
    """
    global _console

    if config is None:
        config = LoggingConfig()

    if console is None:
        console = Console(stderr=True)

    _console = console

    # Create Rich handler
    handler = RichHandler(
        console=console,
        show_time=config.show_time,
        show_path=config.show_path,
        rich_tracebacks=config.rich_tracebacks,
        tracebacks_show_locals=config.level == logging.DEBUG,
        markup=True,
    )

    # Set format - Rich handles most formatting
    handler.setFormatter(logging.Formatter("%(message)s"))

    # Configure root logger for our package
    root_logger = logging.getLogger("colorscheme_generator")
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(config.level)

    # Don't propagate to root logger
    root_logger.propagate = False

    config._initialized = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]

    # Create logger under our package namespace
    if not name.startswith("colorscheme_generator"):
        full_name = f"colorscheme_generator.{name}"
    else:
        full_name = name

    logger = logging.getLogger(full_name)
    _loggers[name] = logger

    return logger


def get_console() -> Console:
    """Get the logging console.

    Returns:
        Rich console used for logging
    """
    global _console
    if _console is None:
        _console = Console(stderr=True)
    return _console

