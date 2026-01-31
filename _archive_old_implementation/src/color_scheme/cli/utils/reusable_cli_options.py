from typing import Annotated, TypeAlias
from pathlib import Path
import typer
from rich_logging import LogLevels


LogLevelOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--log-level",
        "-l",
        help="Set the log level",
    ),
]


ConfigOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--config",
        "-c",
        help="Path or URL to config repository",
    ),
]

VerboseOption: TypeAlias = Annotated[
    int | None,
    typer.Option(
        "--verbose",
        "-v",
        count=True,
        min=0, 
        max=3,
        help="Increase verbosity (-v, -vv, -vvv)",
    ),
]

LogDirOption: TypeAlias = Annotated[
    Path | None,
    typer.Option(
        "--log-directory",
        "-L",
        help="Directory for log files",
    ),
]
