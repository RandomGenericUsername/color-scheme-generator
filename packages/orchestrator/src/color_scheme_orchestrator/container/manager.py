"""Container manager for orchestrating color extraction in containers."""

from pathlib import Path

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

    def build_volume_mounts(
        self,
        image_path: Path,
        output_dir: Path,
    ) -> list[str]:
        """Build volume mount specifications for container.

        Args:
            image_path: Path to source image on host
            output_dir: Path to output directory on host

        Returns:
            List of volume mount strings in Docker -v format
        """
        mounts = []

        # Image file (read-only)
        mounts.append(f"{image_path.as_posix()}:/input/image.png:ro")

        # Output directory (read-write)
        mounts.append(f"{output_dir.as_posix()}:/output:rw")

        # Templates directory (read-only)
        # Resolve template directory to absolute path
        template_dir = self.settings.templates.directory
        if not template_dir.is_absolute():
            # Relative to current working directory
            template_dir = Path.cwd() / template_dir
        mounts.append(f"{template_dir.as_posix()}:/templates:ro")

        return mounts
