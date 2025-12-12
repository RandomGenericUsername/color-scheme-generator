"""Show command for color-scheme orchestrator."""

import logging
from typing import Optional

from color_scheme.config.config import OrchestratorConfig

logger = logging.getLogger(__name__)


def show_command(
    resource: Optional[str] = None,
    config: Optional[OrchestratorConfig] = None,
) -> int:
    """
    Show information about color-scheme orchestrator.

    Args:
        resource: What to show (backends, config, help)
        config: Orchestrator configuration

    Returns:
        Exit code (always 0)
    """
    if config is None:
        config = OrchestratorConfig.default()

    if resource is None or resource == "backends":
        show_backends(config)
    elif resource == "config":
        show_config(config)
    elif resource == "help":
        show_help()
    else:
        logger.warning(f"Unknown resource: {resource}")
        show_help()

    return 0


def show_backends(config: OrchestratorConfig) -> None:
    """Show available backends."""
    print("\n=== Available Backends ===\n")

    print("Default backends (used when no --backend specified):")
    for backend in config.backends:
        print(f"  • {backend}")

    print("\nSupported backends:")
    backends_info = {
        "pywal": "Fast color extraction from images using haishoku",
        "wallust": "Color palette extraction optimized for wallpapers",
        "custom": "User-provided custom Python backend",
    }

    for backend, description in backends_info.items():
        marker = "●" if backend in config.backends else "○"
        print(f"  {marker} {backend}: {description}")

    print()


def show_config(config: OrchestratorConfig) -> None:
    """Show current configuration."""
    print("\n=== Current Configuration ===\n")

    print("Directories:")
    print(f"  Output:    {config.output_dir}")
    print(f"  Config:    {config.config_dir}")
    print(f"  Cache:     {config.cache_dir}")

    print("\nBackends:")
    for backend in config.backends:
        print(f"  • {backend}")

    print("\nContainer Settings:")
    print(f"  Timeout:       {config.container_timeout}s")
    print(f"  Memory limit:  {config.container_memory_limit}")
    if config.container_cpuset_cpus:
        print(f"  CPUs:          {config.container_cpuset_cpus}")

    print("\nRuntime:")
    print(f"  Preferred: {config.runtime or 'auto-detect'}")
    if config.runtime_path:
        print(f"  Path:      {config.runtime_path}")

    print("\nLogging:")
    print(f"  Verbose: {config.verbose}")
    print(f"  Debug:   {config.debug}")

    print()


def show_help() -> None:
    """Show help information."""
    print("""
=== Color Scheme Orchestrator ===

Container-based backend orchestration for the colorscheme-generator tool.

USAGE:
    color-scheme COMMAND [OPTIONS] [ARGS]

COMMANDS:
    install          Install and initialize backends
    generate         Generate a color scheme
    show             Show information
    status           Show system status

EXAMPLES:
    # Install default backends
    color-scheme install

    # Generate using default backends
    color-scheme generate -i image.jpg

    # Generate using specific backend
    color-scheme generate --backend pywal -i image.jpg

    # Show available backends
    color-scheme show backends

    # Show current configuration
    color-scheme show config

OPTIONS (all commands):
    --runtime RUNTIME      Use specific runtime (docker/podman)
    --output-dir DIR       Output directory
    --config-dir DIR       Config directory
    --verbose, -v          Verbose output
    --debug, -d            Debug output

ENVIRONMENT VARIABLES:
    COLOR_SCHEME_RUNTIME          Container runtime to use
    COLOR_SCHEME_OUTPUT_DIR       Output directory
    COLOR_SCHEME_CONFIG_DIR       Config directory
    COLOR_SCHEME_CONTAINER_TIMEOUT    Timeout in seconds
    COLOR_SCHEME_VERBOSE          Enable verbose mode
    COLOR_SCHEME_DEBUG            Enable debug mode

For more information, visit: https://github.com/RandomGenericUsername/color-scheme-generator
    """)
