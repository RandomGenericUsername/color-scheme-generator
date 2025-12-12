"""Commands for the color-scheme orchestrator."""

from color_scheme.commands.generate import generate_command
from color_scheme.commands.install import install_command
from color_scheme.commands.show import show_command
from color_scheme.commands.status import status_command

__all__ = [
    "generate_command",
    "install_command",
    "show_command",
    "status_command",
]
