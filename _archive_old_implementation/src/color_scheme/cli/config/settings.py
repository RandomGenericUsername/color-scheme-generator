from rich_logging import LogLevels

DEFAULT_LOG_LEVEL = LogLevels.WARNING
VERBOSE_TO_LOG_LEVEL = {
    1: LogLevels.ERROR,
    2: LogLevels.INFO,
    3: LogLevels.DEBUG,
}