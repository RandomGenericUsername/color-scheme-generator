"""Validation utilities for paths and configurations."""

from pathlib import Path


def validate_file(path: str | Path) -> Path:
    """Validate that a path points to an existing file.

    Args:
        path: File path to validate

    Returns:
        Path object if file exists

    Raises:
        FileNotFoundError: If file doesn't exist
        IsADirectoryError: If path is a directory
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")
    return file_path


def validate_directory(path: str | Path, create: bool = False) -> Path:
    """Validate that a path points to a directory.

    Args:
        path: Directory path to validate
        create: Create directory if it doesn't exist (default: False)

    Returns:
        Path object to directory

    Raises:
        NotADirectoryError: If path exists but is not a directory
    """
    dir_path = Path(path)
    if dir_path.exists() and not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path}")
    if create and not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
