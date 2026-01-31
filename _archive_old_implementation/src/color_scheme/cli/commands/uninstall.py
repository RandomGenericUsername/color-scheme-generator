from color_scheme.cli.utils.reusable_cli_options import (
    ConfigOption,
    VerboseOption,
    LogDirOption
)
from color_scheme.shared.config.logging import create_logger
from rich_logging import LogLevels
import typer
from pathlib import Path


def uninstall() -> None:
    print("uninstall")