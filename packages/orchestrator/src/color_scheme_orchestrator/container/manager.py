"""Container manager for orchestrating color extraction in containers."""

from color_scheme.config.config import AppConfig  # type: ignore[import-untyped]
from color_scheme.config.enums import Backend


class ContainerManager:
    """Manages container lifecycle for color scheme generation.

    Handles:
    - Container engine detection (Docker/Podman)
    - Image management (pull, list, remove)
    - Container execution
    - Volume mount configuration
    """

    def __init__(self, settings: AppConfig):
        """Initialize container manager.

        Args:
            settings: Application configuration
        """
        self.settings: AppConfig = settings
        self.engine: str = settings.container.engine

    def get_image_name(self, backend: Backend) -> str:
        """Get full image name for a backend.

        Args:
            backend: Backend to get image for

        Returns:
            Full image name (with registry if configured)
        """
        # Base image name
        image_name = f"color-scheme-{backend.value}:latest"

        # Add registry prefix if configured
        if self.settings.container.image_registry:
            image_name = f"{self.settings.container.image_registry}/{image_name}"

        return image_name
