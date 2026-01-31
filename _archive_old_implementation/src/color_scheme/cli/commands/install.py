from color_scheme.cli.utils.reusable_cli_options import (
    ConfigOption,
    VerboseOption,
    LogDirOption
)
from color_scheme.shared.config.logging import create_logger
import typer
from rich_logging import LogLevels
from pathlib import Path
from color_scheme.cli.utils.reusable_cli_options import (
    ConfigOption, 
    VerboseOption, 
    LogDirOption,
    LogLevelOption
)
from color_scheme.cli.utils.utils import resolve_log_level

def install(
    config: ConfigOption = None,
    verbose: VerboseOption = None,
    log_dir: LogDirOption = None,
    log_level: LogLevelOption = None,
) -> None:
    resolved_log_level: LogLevels = resolve_log_level(verbose, log_level)
    print(f"Resolved log level: {resolved_log_level}")
    pass