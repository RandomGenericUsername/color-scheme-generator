"""Container execution service for running color-scheme commands."""

import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from container_manager import (
    ContainerEngine,
    RunConfig,
    VolumeMount,
)

from color_scheme.config.config import OrchestratorConfig
from color_scheme.utils.passthrough import build_passthrough_command

logger = logging.getLogger(__name__)


class ContainerRunner:
    """Execute color-scheme commands inside containers."""

    def __init__(
        self,
        engine: ContainerEngine,
        config: OrchestratorConfig,
    ):
        """
        Initialize the container runner.

        Args:
            engine: Container engine to use
            config: Orchestrator configuration
        """
        self.engine = engine
        self.config = config

    def run_backend(
        self,
        backend: str,
        command: str,
        args: list[str],
        image_name: Optional[str] = None,
    ) -> str:
        """
        Run a backend command in a container.

        Args:
            backend: Backend name (pywal, wallust, custom)
            command: Command to run (install, generate, etc.)
            args: Arguments to pass to the command
            image_name: Override default image name

        Returns:
            Container output/logs

        Raises:
            RuntimeError: If container execution fails
        """
        if image_name is None:
            image_name = f"color-scheme-{backend}:latest"

        container_name = f"color-scheme-{backend}-{uuid.uuid4().hex[:8]}"

        # Extract and mount image path if present in args
        translated_args, image_mount = self._extract_and_mount_image(args)

        # Build volume mounts
        volumes = self._prepare_volume_mounts()
        if image_mount:
            volumes.append(image_mount)

        # Build the command with translated paths
        cmd = build_passthrough_command(command, translated_args)

        logger.info(
            f"Running {backend} backend: {' '.join(cmd)}"
        )
        logger.debug(f"Container name: {container_name}")

        # Create run config
        run_config = RunConfig(
            image=image_name,
            command=cmd,
            name=container_name,
            volumes=volumes,
            environment=self._prepare_environment(),
            user=f"{os.getuid()}:{os.getgid()}",
            detach=False,  # Wait for completion
            remove=True,  # Clean up after running
        )

        try:
            # Run container
            container_id = self.engine.containers.run(run_config)
            logger.debug(f"Container started: {container_id}")

            # Get logs
            logs = self.engine.containers.logs(container_id)
            logger.info(f"Container output:\n{logs}")

            return logs

        except Exception as e:
            logger.error(f"Failed to run backend container: {e}")
            raise RuntimeError(
                f"Backend execution failed: {e}"
            ) from e

    def install_backends(
        self,
        backends: Optional[list[str]] = None,
        force_rebuild: bool = False,
    ) -> dict[str, str]:
        """
        Install/initialize specified backends.

        Args:
            backends: List of backends to install.
                     If None, uses config defaults.
            force_rebuild: Force rebuild of images

        Returns:
            Dictionary mapping backend name to installation status

        Raises:
            RuntimeError: If installation fails
        """
        if backends is None:
            backends = self.config.backends

        results = {}

        for backend in backends:
            try:
                logger.info(f"Installing backend: {backend}")
                output = self.run_backend(
                    backend,
                    "install",
                    [],
                )
                results[backend] = "success"
                logger.info(f"Successfully installed {backend}")
            except Exception as e:
                results[backend] = f"failed: {e}"
                logger.error(f"Failed to install {backend}: {e}")

        return results

    def generate_scheme(
        self,
        backend: str,
        args: list[str],
    ) -> str:
        """
        Generate a color scheme using a backend.

        Args:
            backend: Backend to use
            args: Arguments for the backend

        Returns:
            Generated color scheme output

        Raises:
            RuntimeError: If generation fails
        """
        logger.info(f"Generating scheme with {backend}")
        return self.run_backend(backend, "generate", args)

    def _extract_and_mount_image(
        self, args: list[str]
    ) -> tuple[list[str], Optional[VolumeMount]]:
        """
        Extract image path from args and prepare volume mount.

        Args:
            args: Command arguments that may contain an image path

        Returns:
            Tuple of (translated_args, volume_mount) where translated_args
            has the image path replaced with the container path, and
            volume_mount is the mount for the image directory (or None)
        """
        from pathlib import Path

        # Look for image path in args (it's the first positional argument)
        image_path = None
        image_arg_index = None

        for i, arg in enumerate(args):
            # Skip flags and their values
            if arg.startswith("-"):
                continue
            # Found a positional argument - assume it's the image path
            if not arg.startswith("-"):
                image_path = arg
                image_arg_index = i
                break

        if not image_path or image_arg_index is None or not Path(image_path).exists():
            # No image path found or doesn't exist - return args unchanged
            return args, None

        # Expand and resolve the path
        host_path = Path(image_path).expanduser().resolve()

        # Mount the parent directory
        mount_source = str(host_path.parent)
        mount_target = "/workspace/input"

        # Translate the path for the container
        container_path = f"{mount_target}/{host_path.name}"

        # Replace the image path in args with the container path
        translated_args = args.copy()
        translated_args[image_arg_index] = container_path

        logger.debug(f"Mounting image directory: {mount_source} -> {mount_target}")
        logger.debug(f"Translated image path: {host_path} -> {container_path}")

        return translated_args, VolumeMount(
            source=mount_source,
            target=mount_target,
            read_only=True,
        )

    def _prepare_volume_mounts(self) -> list[VolumeMount]:
        """
        Prepare volume mounts for container.

        Returns:
            List of VolumeMount objects
        """
        mounts = []

        # Mount output directory
        if self.config.output_dir:
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            mounts.append(
                VolumeMount(
                    source=str(self.config.output_dir),
                    target="/tmp/color-schemes",
                    read_only=False,
                )
            )

        # Mount cache directory
        if self.config.cache_dir:
            self.config.cache_dir.mkdir(parents=True, exist_ok=True)
            mounts.append(
                VolumeMount(
                    source=str(self.config.cache_dir),
                    target="/home/colorscheme/.cache",
                    read_only=False,
                )
            )

        # Mount config directory - mount entire .config to allow backends to write their own subdirs
        if self.config.config_dir:
            # Create parent .config directory
            config_parent = self.config.config_dir.parent
            config_parent.mkdir(parents=True, exist_ok=True)
            self.config.config_dir.mkdir(parents=True, exist_ok=True)
            mounts.append(
                VolumeMount(
                    source=str(config_parent),
                    target="/home/colorscheme/.config",
                    read_only=False,
                )
            )

        logger.debug(f"Volume mounts: {[m.target for m in mounts]}")
        return mounts

    def _prepare_environment(self) -> dict[str, str]:
        """
        Prepare environment variables for container.

        Returns:
            Dictionary of environment variables
        """
        env = {
            "HOME": "/home/colorscheme",
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }

        # Pass through relevant environment variables
        passthrough_vars = [
            "DISPLAY",
            "WAYLAND_DISPLAY",
            "XDG_RUNTIME_DIR",
        ]

        for var in passthrough_vars:
            if var in os.environ:
                env[var] = os.environ[var]

        if self.config.verbose:
            env["VERBOSE"] = "1"

        if self.config.debug:
            env["DEBUG"] = "1"

        logger.debug(f"Environment variables: {list(env.keys())}")
        return env

    def cleanup_container(self, container_name: str) -> None:
        """
        Clean up a container by name.

        Args:
            container_name: Name of container to remove
        """
        try:
            # Find container by name
            containers = self.engine.containers.list()
            container_id = None

            for container in containers:
                if container_name in str(container):
                    container_id = container
                    break

            if container_id:
                self.engine.containers.stop(container_id)
                self.engine.containers.remove(container_id)
                logger.info(f"Cleaned up container: {container_name}")
        except Exception as e:
            logger.warning(f"Failed to cleanup container: {e}")
