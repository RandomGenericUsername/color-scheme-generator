"""Generate command for color-scheme orchestrator."""

import logging
from typing import Optional

from color_scheme.config.config import OrchestratorConfig
from color_scheme.services import ContainerRunner, ImageBuilder
from color_scheme.utils.passthrough import (
    extract_backend_from_args,
    should_use_default_backends,
)
from color_scheme.utils.runtime import get_runtime_engine

logger = logging.getLogger(__name__)


def generate_command(
    args: list[str],
    config: Optional[OrchestratorConfig] = None,
) -> int:
    """
    Generate a color scheme.

    Parses arguments to determine backend and delegates to appropriate
    backend container. Falls back to default backends if none specified.

    Args:
        args: Command line arguments (without command name)
        config: Orchestrator configuration

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if config is None:
        config = OrchestratorConfig.default()

    # Determine which backend to use
    if should_use_default_backends(args):
        backends = config.backends
        logger.info(f"Using default backends: {', '.join(backends)}")
    else:
        backend = extract_backend_from_args(args)
        if backend:
            backends = [backend]
            logger.info(f"Using specified backend: {backend}")
        else:
            backends = config.backends
            logger.info(f"Using default backends: {', '.join(backends)}")

    logger.info(f"Generating color scheme with {', '.join(backends)}")

    try:
        # Get container engine
        engine = get_runtime_engine(config.runtime)

        # Build images for backends
        image_builder = ImageBuilder(engine)
        logger.info("Ensuring container images are built...")

        for backend in backends:
            try:
                image_id = image_builder.build_backend_image(
                    backend,
                    force_rebuild=False,
                )
                logger.debug(f"Using image for {backend}: {image_id}")
            except Exception as e:
                logger.error(f"Failed to prepare image for {backend}: {e}")
                return 1

        # Run generate command in container
        runner = ContainerRunner(engine, config)
        logger.info("Generating color scheme in container...")

        try:
            output = runner.generate_scheme(
                backend=backends[0],  # Use first backend
                args=args,
            )
            logger.info("Color scheme generated successfully!")
            print(output)
            return 0
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            if config.debug:
                import traceback
                traceback.print_exc()
            return 1

    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        if config.debug:
            import traceback
            traceback.print_exc()
        return 1
