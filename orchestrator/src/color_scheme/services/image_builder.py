"""Image building service for backend containers."""

import logging
from pathlib import Path
from typing import Optional

from container_manager import (
    BuildContext,
    ContainerEngine,
)

from color_scheme.utils.passthrough import get_backend_dockerfile

logger = logging.getLogger(__name__)


class ImageBuilder:
    """Build container images for color-scheme backends."""

    def __init__(self, engine: ContainerEngine):
        """
        Initialize the image builder.

        Args:
            engine: Container engine to use for building
        """
        self.engine = engine

    def build_backend_image(
        self,
        backend: str,
        force_rebuild: bool = False,
    ) -> str:
        """
        Build a backend container image.

        Args:
            backend: Backend name (pywal, wallust, custom)
            force_rebuild: Force rebuild even if image exists

        Returns:
            Image ID or name

        Raises:
            ValueError: If backend is not recognized
            FileNotFoundError: If Dockerfile is not found
        """
        image_name = f"color-scheme-{backend}:latest"

        # Check if image already exists
        if not force_rebuild:
            try:
                info = self.engine.images.inspect(image_name)
                logger.info(f"Image {image_name} already exists: {info}")
                return image_name
            except Exception:
                # Image doesn't exist, will build it
                pass

        logger.info(f"Building image for backend: {backend}")

        # Get dockerfile path
        dockerfile_path = get_backend_dockerfile(backend)
        logger.debug(f"Using Dockerfile: {dockerfile_path}")

        # Read dockerfile content
        with open(dockerfile_path, "r") as f:
            dockerfile_content = f.read()

        # Create build context
        context = BuildContext(
            dockerfile=dockerfile_content,
            files={},  # No additional files for standard backends
        )

        # Build image
        try:
            image_id = self.engine.images.build(context, image_name)
            logger.info(f"Successfully built image: {image_id}")
            return image_id
        except Exception as e:
            logger.error(f"Failed to build image {image_name}: {e}")
            raise

    def build_custom_backend_image(
        self,
        backend_script: str,
        backend_name: str = "custom",
        force_rebuild: bool = False,
    ) -> str:
        """
        Build a custom backend container image.

        Args:
            backend_script: Python script content for the backend
            backend_name: Name for the image
            force_rebuild: Force rebuild even if image exists

        Returns:
            Image ID or name

        Raises:
            FileNotFoundError: If Dockerfile is not found
        """
        image_name = f"color-scheme-{backend_name}:latest"

        # Check if image already exists
        if not force_rebuild:
            try:
                info = self.engine.images.inspect(image_name)
                logger.info(f"Image {image_name} already exists: {info}")
                return image_name
            except Exception:
                # Image doesn't exist, will build it
                pass

        logger.info(f"Building custom backend image: {backend_name}")

        # Get dockerfile path
        dockerfile_path = get_backend_dockerfile("custom")

        # Read dockerfile content
        with open(dockerfile_path, "r") as f:
            dockerfile_content = f.read()

        # Create build context with backend script
        context = BuildContext(
            dockerfile=dockerfile_content,
            files={
                "backend.py": backend_script.encode("utf-8"),
            },
        )

        # Build image
        try:
            image_id = self.engine.images.build(context, image_name)
            logger.info(f"Successfully built custom image: {image_id}")
            return image_id
        except Exception as e:
            logger.error(f"Failed to build custom image {image_name}: {e}")
            raise

    def remove_image(self, image_name: str) -> None:
        """
        Remove a built image.

        Args:
            image_name: Image name to remove
        """
        try:
            self.engine.images.remove(image_name)
            logger.info(f"Removed image: {image_name}")
        except Exception as e:
            logger.warning(f"Failed to remove image {image_name}: {e}")

    def list_built_images(self) -> list[str]:
        """
        List all color-scheme backend images.

        Returns:
            List of image names/IDs
        """
        try:
            all_images = self.engine.images.list()
            # Filter for color-scheme images
            color_scheme_images = []
            for img in all_images:
                # Check if any tag contains "color-scheme"
                for tag in img.tags:
                    if "color-scheme" in tag:
                        color_scheme_images.append(tag)
                        break
            return color_scheme_images
        except Exception as e:
            logger.error(f"Failed to list images: {e}")
            return []
