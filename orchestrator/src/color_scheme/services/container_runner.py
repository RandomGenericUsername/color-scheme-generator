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

        # Build volume mounts
        volumes = self._prepare_volume_mounts()

        # Build the command
        cmd = build_passthrough_command(command, args)

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
                    target="/root/.cache/color-scheme",
                    read_only=False,
                )
            )

        # Mount config directory
        if self.config.config_dir:
            self.config.config_dir.mkdir(parents=True, exist_ok=True)
            mounts.append(
                VolumeMount(
                    source=str(self.config.config_dir),
                    target="/root/.config/color-scheme",
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
            "HOME": "/root",
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
