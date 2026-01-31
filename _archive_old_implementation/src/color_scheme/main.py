from color_scheme.shared.config.logging import create_logger
from color_scheme.cli.main import app as cli
from color_scheme.cli.utils.utils import get_project_path
from rich_logging import (
    RichLogger,
    LogLevels,
)
from pathlib import Path


project_root_dir: Path = get_project_path(levels_up=2)
logger: RichLogger = create_logger(
    name="color_scheme",
    log_level=LogLevels.DEBUG,
    output_to_file=False,
)

def main() -> None:
    cli()
