"""Status command for color-scheme orchestrator."""

import logging
from typing import Optional

from color_scheme.config.config import OrchestratorConfig
from color_scheme.services import ImageBuilder
from color_scheme.utils.runtime import (
    detect_container_runtime,
    verify_runtime_availability,
)

logger = logging.getLogger(__name__)


def status_command(
    config: Optional[OrchestratorConfig] = None,
) -> int:
    """
    Show orchestrator status.

    Displays information about:
    - Container runtime availability
    - Built images
    - Configuration

    Args:
        config: Orchestrator configuration

    Returns:
        Exit code (0 if healthy, 1 if issues found)
    """
    if config is None:
        config = OrchestratorConfig.default()

    print("\n=== Color Scheme Orchestrator Status ===\n")

    # Check runtime availability
    runtime_status = check_runtime_status(config.runtime)

    # Try to get image information
    images_status = check_images_status(config)

    # Show configuration paths
    show_path_status(config)

    # Determine exit code
    if not runtime_status:
        return 1

    print()
    return 0


def check_runtime_status(preferred_runtime: Optional[str]) -> bool:
    """
    Check container runtime availability.

    Args:
        preferred_runtime: Preferred runtime name

    Returns:
        True if runtime is available
    """
    print("Container Runtime:")

    try:
        runtime = detect_container_runtime(preferred_runtime)
        print(f"  ✓ {runtime.value.upper()}")

        # Try to get version
        try:
            from color_scheme.utils.runtime import get_runtime_engine
            engine = get_runtime_engine(preferred_runtime)
            version = engine.version()
            print(f"    Version: {version}")
            print(f"    Available: Yes")
        except Exception as e:
            print(f"    Available: No ({e})")
            return False

        return True

    except Exception as e:
        print(f"  ✗ No runtime available")
        print(f"    Error: {e}")
        print(f"\n  Install Docker or Podman to use color-scheme orchestrator")
        return False


def check_images_status(config: OrchestratorConfig) -> None:
    """
    Check built container images.

    Args:
        config: Orchestrator configuration
    """
    print("\nBuilt Images:")

    if not verify_runtime_availability(config.runtime):
        print("  (Runtime not available)")
        return

    try:
        from color_scheme.utils.runtime import get_runtime_engine
        engine = get_runtime_engine(config.runtime)

        builder = ImageBuilder(engine)
        images = builder.list_built_images()

        if images:
            for image in images:
                print(f"  ✓ {image}")
        else:
            print("  (No images built)")
            print(f"\n  Run 'color-scheme install' to build default backends")

    except Exception as e:
        logger.debug(f"Failed to list images: {e}")
        print("  (Unable to query images)")


def show_path_status(config: OrchestratorConfig) -> None:
    """
    Show configuration paths and their status.

    Args:
        config: Orchestrator configuration
    """
    print("\nConfiguration Paths:")

    paths = {
        "Output":  config.output_dir,
        "Config":  config.config_dir,
        "Cache":   config.cache_dir,
    }

    for name, path in paths.items():
        exists = "✓" if path.exists() else "✗"
        print(f"  {exists} {name:8} {path}")
