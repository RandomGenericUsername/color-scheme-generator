"""Container runtime detection and management."""

import logging
from typing import Optional

from container_manager import (
    ContainerEngine,
    ContainerEngineFactory,
    ContainerRuntime,
    RuntimeNotAvailableError,
)

from color_scheme.config.constants import RUNTIME_DETECTION_ORDER

logger = logging.getLogger(__name__)


def detect_container_runtime(
    preferred_runtime: Optional[str] = None,
) -> ContainerRuntime:
    """
    Detect available container runtime.

    Args:
        preferred_runtime: Preferred runtime ("docker" or "podman").
                          If specified and available, will be used.
                          Otherwise, fallback to detection order.

    Returns:
        Detected ContainerRuntime

    Raises:
        RuntimeNotAvailableError: If no runtime is available
    """
    runtimes_to_try: list[str] = []

    # Add preferred runtime first if specified
    if preferred_runtime:
        if preferred_runtime.lower() in ("docker", "podman"):
            runtimes_to_try.append(preferred_runtime.lower())
        else:
            logger.warning(
                f"Unknown runtime preference: {preferred_runtime}. "
                f"Falling back to auto-detection."
            )

    # Add detection order
    runtimes_to_try.extend(RUNTIME_DETECTION_ORDER)

    # Try each runtime
    for runtime_name in runtimes_to_try:
        try:
            if runtime_name.lower() == "docker":
                runtime = ContainerRuntime.DOCKER
            elif runtime_name.lower() == "podman":
                runtime = ContainerRuntime.PODMAN
            else:
                continue

            # Try to create engine - this will fail if not available
            engine = ContainerEngineFactory.create(runtime)
            logger.info(f"Using container runtime: {runtime_name}")
            logger.debug(f"Runtime version: {engine.version()}")
            return runtime

        except RuntimeNotAvailableError:
            logger.debug(f"Runtime {runtime_name} not available")
            continue

    # No runtime found
    raise RuntimeNotAvailableError(
        "No container runtime found. "
        "Please install Docker or Podman."
    )


def get_runtime_engine(
    preferred_runtime: Optional[str] = None,
) -> ContainerEngine:
    """
    Get a container engine instance for the detected runtime.

    Args:
        preferred_runtime: Preferred runtime name (optional)

    Returns:
        Configured ContainerEngine instance

    Raises:
        RuntimeNotAvailableError: If no runtime is available
    """
    runtime = detect_container_runtime(preferred_runtime)
    return ContainerEngineFactory.create(runtime)


def verify_runtime_availability(
    runtime_name: Optional[str] = None,
) -> bool:
    """
    Verify that a container runtime is available.

    Args:
        runtime_name: Specific runtime to check ("docker", "podman")
                     If None, checks if any runtime is available.

    Returns:
        True if runtime is available, False otherwise
    """
    try:
        detect_container_runtime(runtime_name)
        return True
    except RuntimeNotAvailableError:
        return False
