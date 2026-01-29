"""Container manager for orchestrating color extraction in containers."""

from color_scheme.config.config import AppConfig  # type: ignore[import-untyped]


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
