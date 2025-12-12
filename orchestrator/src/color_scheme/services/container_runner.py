"""Container execution service for running color-scheme commands."""

import logging
import os
import uuid
from typing import Optional

from container_manager import (
    ContainerEngine,
    RunConfig,
    VolumeMount,
)

from color_scheme.config.config import OrchestratorConfig
from color_scheme.config.constants import CONTAINER_OUTPUT_DIR
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
            Container output/logs with container paths translated to host paths

        Raises:
            RuntimeError: If container execution fails
        """
        if image_name is None:
            image_name = f"color-scheme-{backend}:latest"

        container_name = f"color-scheme-{backend}-{uuid.uuid4().hex[:8]}"

        # Extract and mount image path if present in args
        translated_args, image_mount = self._extract_and_mount_image(args)

        # For generate command, process --output-dir argument BEFORE volume mounts
        # This updates config.output_dir if user specified a custom path
        if command == "generate":
            translated_args = self._process_output_dir_arg(translated_args)

        # Build volume mounts (uses potentially updated config.output_dir)
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
            # When detach=False, run() returns the container stdout directly
            # and the container is already removed (remove=True)
            output = self.engine.containers.run(run_config)
            logger.info(f"Container output:\n{output}")

            # Translate container paths back to host paths in output
            output = self._translate_output_paths(output)

            return output

        except Exception as e:
            logger.error(f"Failed to run backend container: {e}")
            raise RuntimeError(
                f"Backend execution failed: {e}"
            ) from e

    def _process_output_dir_arg(self, args: list[str]) -> list[str]:
        """
        Process --output-dir argument: extract user-specified path, update config,
        and replace with container path.

        Args:
            args: Current argument list

        Returns:
            Updated argument list with --output-dir pointing to container path
        """
        from pathlib import Path

        new_args = []
        i = 0

        while i < len(args):
            arg = args[i]
            if arg in ("--output-dir", "-o"):
                # Get the value (next arg)
                if i + 1 < len(args):
                    user_path = Path(args[i + 1]).expanduser().resolve()
                    # Update config to mount this directory
                    self.config.output_dir = user_path
                    # Skip both the flag and its value
                    i += 2
                    continue
                else:
                    # Flag without value - skip it
                    i += 1
                    continue
            new_args.append(arg)
            i += 1

        # Always add --output-dir pointing to container path
        new_args.extend(["--output-dir", CONTAINER_OUTPUT_DIR])

        return new_args

    def _translate_output_paths(self, output: str) -> str:
        """
        Translate container paths in output to host paths.

        Args:
            output: Container output string

        Returns:
            Output with container paths replaced by host paths
        """
        # Replace container output path with host output path
        host_output_dir = str(self.config.output_dir)
        output = output.replace(CONTAINER_OUTPUT_DIR, host_output_dir)

        return output

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

        # Mount output directory (host output_dir -> container /output)
        if self.config.output_dir:
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            mounts.append(
                VolumeMount(
                    source=str(self.config.output_dir),
                    target=CONTAINER_OUTPUT_DIR,
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
