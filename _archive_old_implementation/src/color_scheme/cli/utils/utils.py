
import inspect
from pathlib import Path
from rich_logging import LogLevels
from color_scheme.cli.config.settings import (
    VERBOSE_TO_LOG_LEVEL,
    DEFAULT_LOG_LEVEL
)


def get_project_path(levels_up: int = 0) -> Path:
    """
    Get ancestor directory from the calling file.
    levels_up: 0 = caller's directory, 1 = parent, 2 = grandparent, etc.
    """
    caller_frame = inspect.currentframe().f_back
    caller_file = caller_frame.f_globals['__file__']
    return Path(caller_file).resolve().parents[levels_up]


def resolve_log_level(
    verbose: int | None,
    log_level: LogLevels | None,
    default_log_level: LogLevels = DEFAULT_LOG_LEVEL
) -> LogLevels:
    """
    Resolve the log level based on verbosity and explicit log level.
    """
    if log_level is not None:
        return log_level

    if verbose is not None:
        resolved_log_level: LogLevels = VERBOSE_TO_LOG_LEVEL.get(verbose, None)
        if resolved_log_level is None:
            print(f"Warning: Verbosity level {verbose} is out of range. Using default log level {default_log_level}.")
        return resolved_log_level or default_log_level
    
    return default_log_level 