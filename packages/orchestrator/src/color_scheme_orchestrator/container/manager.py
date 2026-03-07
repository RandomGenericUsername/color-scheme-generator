"""Container manager for orchestrating color extraction in containers."""

import os
import pty
import select
import subprocess
import sys
import threading
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

        Streams container output directly to the terminal. Allocates a
        pseudo-TTY (-t) only when the host stdout is a terminal so Rich
        inside the container renders colours and tables interactively,
        and falls back to plain line streaming when piped or scripted.

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

        if sys.stdout.isatty():
            cmd.append("-t")
            for var in ("TERM", "COLORTERM"):
                val = os.environ.get(var)
                if val:
                    cmd.extend(["-e", f"{var}={val}"])
            cmd.extend(["-e", "FORCE_COLOR=1"])

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

        # Inject display-path overrides so the core shows real host paths
        cmd.extend(["--display-image-path", image_path.as_posix()])
        cmd.extend(["--display-output-dir", output_dir.as_posix()])

        # Add CLI arguments
        cmd.extend(cli_args)

        # Execute container with streaming output
        result = self._run_streaming(cmd)

        if result.returncode != 0:
            error_msg = f"Container execution failed with exit code {result.returncode}"
            if result.stderr:
                error_msg += f": {result.stderr}"
            raise RuntimeError(error_msg)

    def _run_streaming(self, cmd: list[str]) -> subprocess.CompletedProcess[str]:
        """Run a command, streaming output live.

        Uses PTY when -t flag is present (for Rich colours and animations),
        otherwise uses PIPE for plain line streaming.

        Args:
            cmd: Command and arguments to execute.

        Returns:
            CompletedProcess with returncode and stderr (if available).
            stdout is streamed directly to the terminal.
        """
        if "-t" in cmd:
            return self._run_streaming_pty(cmd)
        return self._run_streaming_pipe(cmd)

    def _run_streaming_pipe(self, cmd: list[str]) -> subprocess.CompletedProcess[str]:
        """PIPE-based streaming.

        Args:
            cmd: Command and arguments to execute.

        Returns:
            CompletedProcess with returncode and accumulated stderr.
            stdout is streamed directly to the terminal.
        """
        proc = subprocess.Popen(  # nosec: B603
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stderr_lines: list[str] = []

        def _drain_stderr() -> None:
            if proc.stderr is None:
                raise RuntimeError("stderr pipe unexpectedly None")
            for line in proc.stderr:
                stderr_lines.append(line)

        stderr_thread = threading.Thread(target=_drain_stderr, daemon=True)
        stderr_thread.start()

        if proc.stdout is None:
            raise RuntimeError("stdout pipe unexpectedly None")
        for line in proc.stdout:
            print(line, end="", flush=True)

        proc.wait()
        stderr_thread.join()

        return subprocess.CompletedProcess(
            args=cmd,
            returncode=proc.returncode,
            stdout="",
            stderr="".join(stderr_lines),
        )

    def _run_streaming_pty(self, cmd: list[str]) -> subprocess.CompletedProcess[str]:
        """PTY-based streaming for Rich colours and animations.

        When -t flag is present, use PTY so Rich inside the container
        detects a terminal and renders colours, tables, and animations.
        stdout and stderr are merged in PTY mode.

        Args:
            cmd: Command and arguments to execute.

        Returns:
            CompletedProcess with returncode. stderr is empty (merged into
            the PTY stream, already visible on the terminal).
        """
        master_fd, slave_fd = pty.openpty()

        proc = subprocess.Popen(  # nosec: B603
            cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
        )
        os.close(slave_fd)

        while True:
            try:
                r, _, _ = select.select([master_fd], [], [], 0.1)
            except (ValueError, OSError):
                break

            if r:
                try:
                    chunk = os.read(master_fd, 1024)
                except OSError:
                    break

                if not chunk:
                    break

                sys.stdout.buffer.write(chunk)
                sys.stdout.flush()

            elif proc.poll() is not None:
                # Process finished — do one final read to flush remaining output
                try:
                    chunk = os.read(master_fd, 1024)
                    if chunk:
                        sys.stdout.buffer.write(chunk)
                        sys.stdout.flush()
                except OSError:
                    pass
                break

        proc.wait()
        os.close(master_fd)

        # PTY mode: stderr is merged into the PTY stream, not separately available
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=proc.returncode,
            stdout="",
            stderr="",
        )

    def run_show(
        self,
        backend: Backend,
        image_path: Path,
        cli_args: list[str] | None = None,
    ) -> None:
        """Execute show command in container.

        Stdout flows directly to the terminal. Allocates a pseudo-TTY (-t)
        only when the host stdout is a terminal, so Rich inside the container
        renders color tables interactively and falls back to a plain bullet
        list when piped or scripted.

        Args:
            backend: Backend to use
            image_path: Path to source image
            cli_args: Additional CLI arguments to pass

        Raises:
            RuntimeError: If container execution fails
        """
        if cli_args is None:
            cli_args = []

        image = self.get_image_name(backend)
        image_mount = f"{image_path.as_posix()}:/input/image.png:ro"

        cmd = [self.engine, "run", "--rm"]

        if sys.stdout.isatty():
            cmd.append("-t")
            for var in ("TERM", "COLORTERM"):
                val = os.environ.get(var)
                if val:
                    cmd.extend(["-e", f"{var}={val}"])
            cmd.extend(["-e", "FORCE_COLOR=1"])

        user_id = os.getuid()
        group_id = os.getgid()
        cmd.extend(["--user", f"{user_id}:{group_id}"])

        cmd.extend(["-v", image_mount])
        cmd.append(image)

        cmd.extend(["show", "/input/image.png"])
        cmd.extend(["--display-image-path", image_path.as_posix()])
        cmd.extend(cli_args)

        result = subprocess.run(cmd)

        if result.returncode != 0:
            raise RuntimeError(
                f"Container execution failed with exit code {result.returncode}"
            )
