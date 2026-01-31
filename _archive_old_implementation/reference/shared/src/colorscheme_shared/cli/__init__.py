"""Shared CLI utilities for color-scheme projects.

Provides common utilities for both Typer and argparse-based CLIs.
"""

from colorscheme_shared.cli.backends import BackendValidator

__all__ = [
    "BackendValidator",
]
