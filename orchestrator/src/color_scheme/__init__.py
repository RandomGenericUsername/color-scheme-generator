"""Color Scheme Orchestrator - Container-based backend orchestration."""

__version__ = "0.1.0"
__author__ = "color-scheme contributors"
__license__ = "MIT"

from color_scheme.cli import main
from color_scheme.commands import (
    generate_command,
    install_command,
    show_command,
    status_command,
)
from color_scheme.config.config import OrchestratorConfig
from color_scheme.services import ContainerRunner, ImageBuilder
from color_scheme.utils.runtime import (
    detect_container_runtime,
    get_runtime_engine,
    verify_runtime_availability,
)

__all__ = [
    "ContainerRunner",
    "ImageBuilder",
    "OrchestratorConfig",
    "detect_container_runtime",
    "generate_command",
    "get_runtime_engine",
    "install_command",
    "main",
    "show_command",
    "status_command",
    "verify_runtime_availability",
]
