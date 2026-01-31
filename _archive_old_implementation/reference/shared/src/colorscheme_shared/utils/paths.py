"""Path manipulation utilities."""

from pathlib import Path


def expand_path(path: str | Path) -> Path:
    """Expand a path with user and environment variables.

    Args:
        path: Path string or Path object

    Returns:
        Expanded Path object
    """
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().expandvars()
