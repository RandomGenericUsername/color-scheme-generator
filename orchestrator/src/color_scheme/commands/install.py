"""Install command for color-scheme orchestrator."""

import logging
import sys
from typing import Optional

from color_scheme.config.config import OrchestratorConfig
from color_scheme.services import ContainerRunner, ImageBuilder
from color_scheme.utils.runtime import get_runtime_engine

logger = logging.getLogger(__name__)


def install_command(
    backends: Optional[list[str]] = None,
    config: Optional[OrchestratorConfig] = None,
    force_rebuild: bool = False,
) -> int:
    """
    Install and initialize backends.

    Builds container images and runs initialization for specified backends.

    Args:
        backends: Backends to install. If None, uses config defaults.
        config: Orchestrator configuration
        force_rebuild: Force rebuild images

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if config is None:
        config = OrchestratorConfig.default()

    if backends is None:
        backends = config.backends

    logger.info(f"Installing backends: {', '.join(backends)}")

    try:
        # Get container engine
        engine = get_runtime_engine(config.runtime)

        # Build images
        image_builder = ImageBuilder(engine)
        logger.info("Building container images...")

        built_images = {}
        for backend in backends:
            try:
                image_id = image_builder.build_backend_image(
                    backend,
                    force_rebuild=force_rebuild,
                )
                built_images[backend] = image_id
                logger.info(f"Built image for {backend}: {image_id}")
            except Exception as e:
                logger.error(f"Failed to build image for {backend}: {e}")
                return 1

        # Run container installations
        runner = ContainerRunner(engine, config)
        logger.info("Installing backends in containers...")

        install_results = runner.install_backends(
            backends=backends,
            force_rebuild=force_rebuild,
        )

        # Report results
        logger.info("\nInstallation results:")
        all_success = True
        for backend, status in install_results.items():
            if status == "success":
                logger.info(f"✓ {backend}: {status}")
            else:
                logger.error(f"✗ {backend}: {status}")
                all_success = False

        if all_success:
            logger.info("\nAll backends installed successfully!")
            return 0
        else:
            logger.error("\nSome backends failed to install")
            return 1

    except Exception as e:
        logger.error(f"Installation failed: {e}")
        if config.debug:
            import traceback
            traceback.print_exc()
        return 1
