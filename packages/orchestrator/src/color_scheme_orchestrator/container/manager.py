"""Container manager for orchestrating color extraction in containers."""

import os
import subprocess
from pathlib import Path

from color_scheme.config.enums import Backend

from color_scheme_orchestrator.config.unified import UnifiedConfig


class ContainerManager:
    """Manages container lifecycle for color scheme generation.

    Handles:
    - Container engine detection (Docker/Podman)
    - Image management (pull, list, remove)
    - Container execution
    - Volume mount configuration
    """

    def __init__(self, config: UnifiedConfig):
        """Initialize container manager.

        Args:
            config: Unified application configuration
        """
        self.config: UnifiedConfig = config
        self.engine: str = config.orchestrator.engine

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
        if self.config.orchestrator.image_registry:
            image_name = f"{self.config.orchestrator.image_registry}/{image_name}"

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
        template_dir = self.config.core.templates.directory
        if not template_dir.is_absolute():
            # Relative to current working directory
            template_dir = Path.cwd() / template_dir
        mounts.append(f"{template_dir.as_posix()}:/templates:ro")

        return mounts

    def run_generate(
        self,
        backend: Backend,
        image_path: Path,
        output_dir: Path,
        cli_args: list[str] | None = None,
    ) -> None:
        """Execute generate command in container.

        Args:
            backend: Backend to use
            image_path: Path to source image
            output_dir: Directory for output files
            cli_args: Additional CLI arguments to pass

        Raises:
            RuntimeError: If container execution fails
        """
        if cli_args is None:
            cli_args = []

        # Get image name
        image = self.get_image_name(backend)

        # Build volume mounts
        mounts = self.build_volume_mounts(image_path, output_dir)

        # Construct docker/podman command
        cmd = [self.engine, "run", "--rm"]

        # Run as current user to avoid permission issues with volume mounts
        user_id = os.getuid()
        group_id = os.getgid()
        cmd.extend(["--user", f"{user_id}:{group_id}"])

        # Add volume mounts
        for mount in mounts:
            cmd.extend(["-v", mount])

        # Add image
        cmd.append(image)

        # Add container command: generate /input/image.png [args]
        # (ENTRYPOINT already has "color-scheme")
        cmd.extend(["generate", "/input/image.png"])

        # Add CLI arguments
        cmd.extend(cli_args)

        # Execute container
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Container execution failed with exit code {result.returncode}: "
                f"{result.stderr}"
            )
