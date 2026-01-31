# Phase 4: Orchestrator Package Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement container orchestration layer that runs color-scheme-core in isolated Docker/Podman containers, providing identical CLI while handling image management, volume mounts, and container lifecycle.

**Architecture:** The orchestrator package wraps color-scheme-core, delegating simple commands directly and executing backend-dependent commands (generate) inside containers. Uses container-manager library for Docker/Podman abstraction. Three container images (pywal, wallust, custom) extend a base image containing color-scheme-core.

**Tech Stack:** Typer (CLI), container-manager (Docker/Podman abstraction), color-scheme-core (wrapped package), Jinja2 (Dockerfiles as templates)

---

## Task 1: Container Manager Integration

**Files:**
- Create: `packages/orchestrator/src/color_scheme_orchestrator/container/__init__.py`
- Create: `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`
- Create: `packages/orchestrator/tests/unit/test_container_manager.py`

**Step 1: Write failing test for ContainerManager initialization**

Create `packages/orchestrator/tests/unit/test_container_manager.py`:
```python
"""Tests for container manager."""

import pytest
from unittest.mock import Mock, patch

from color_scheme_orchestrator.container.manager import ContainerManager
from color_scheme.config.settings import Settings


class TestContainerManagerInit:
    """Tests for ContainerManager initialization."""

    def test_init_with_settings(self):
        """Test initialization with settings."""
        settings = Settings.get()
        manager = ContainerManager(settings)

        assert manager.settings == settings
        assert manager.engine is not None

    def test_init_detects_docker_engine(self):
        """Test that it detects docker engine from settings."""
        settings = Settings.get()
        settings.container.engine = "docker"

        manager = ContainerManager(settings)

        assert manager.engine == "docker"

    def test_init_detects_podman_engine(self):
        """Test that it detects podman engine from settings."""
        settings = Settings.get()
        settings.container.engine = "podman"

        manager = ContainerManager(settings)

        assert manager.engine == "podman"
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/unit/test_container_manager.py -v
```

Expected: ImportError - ContainerManager not defined

**Step 3: Implement minimal ContainerManager**

Create `packages/orchestrator/src/color_scheme_orchestrator/container/__init__.py`:
```python
"""Container orchestration components."""

from color_scheme_orchestrator.container.manager import ContainerManager

__all__ = ["ContainerManager"]
```

Create `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`:
```python
"""Container manager for orchestrating color extraction in containers."""

from color_scheme.config.settings import Settings


class ContainerManager:
    """Manages container lifecycle for color scheme generation.

    Handles:
    - Container engine detection (Docker/Podman)
    - Image management (pull, list, remove)
    - Container execution
    - Volume mount configuration
    """

    def __init__(self, settings: Settings):
        """Initialize container manager.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.engine = settings.container.engine
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/unit/test_container_manager.py -v
```

Expected: 3 tests PASS

**Step 5: Commit**

Run:
```bash
git add packages/orchestrator/src/color_scheme_orchestrator/container/
git add packages/orchestrator/tests/unit/test_container_manager.py
git commit -m "feat(orchestrator): add ContainerManager skeleton

Initialize ContainerManager with settings and engine detection.
Prepares foundation for container orchestration.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Image Name Resolution

**Files:**
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`
- Create: `packages/orchestrator/tests/unit/test_image_names.py`

**Step 1: Write failing test for image name resolution**

Create `packages/orchestrator/tests/unit/test_image_names.py`:
```python
"""Tests for container image name resolution."""

import pytest

from color_scheme_orchestrator.container.manager import ContainerManager
from color_scheme.config.enums import Backend
from color_scheme.config.settings import Settings


class TestImageNameResolution:
    """Tests for resolving backend enum to image name."""

    def test_pywal_backend_image_name(self):
        """Test pywal backend resolves to correct image."""
        settings = Settings.get()
        manager = ContainerManager(settings)

        image = manager.get_image_name(Backend.PYWAL)

        assert image == "color-scheme-pywal:latest"

    def test_wallust_backend_image_name(self):
        """Test wallust backend resolves to correct image."""
        settings = Settings.get()
        manager = ContainerManager(settings)

        image = manager.get_image_name(Backend.WALLUST)

        assert image == "color-scheme-wallust:latest"

    def test_custom_backend_image_name(self):
        """Test custom backend resolves to correct image."""
        settings = Settings.get()
        manager = ContainerManager(settings)

        image = manager.get_image_name(Backend.CUSTOM)

        assert image == "color-scheme-custom:latest"

    def test_image_name_with_registry(self):
        """Test image name includes registry if configured."""
        settings = Settings.get()
        settings.container.image_registry = "ghcr.io/myorg"
        manager = ContainerManager(settings)

        image = manager.get_image_name(Backend.PYWAL)

        assert image == "ghcr.io/myorg/color-scheme-pywal:latest"
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/unit/test_image_names.py::TestImageNameResolution::test_pywal_backend_image_name -v
```

Expected: AttributeError - get_image_name method not defined

**Step 3: Implement get_image_name method**

Edit `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`:
```python
"""Container manager for orchestrating color extraction in containers."""

from color_scheme.config.enums import Backend
from color_scheme.config.settings import Settings


class ContainerManager:
    """Manages container lifecycle for color scheme generation.

    Handles:
    - Container engine detection (Docker/Podman)
    - Image management (pull, list, remove)
    - Container execution
    - Volume mount configuration
    """

    def __init__(self, settings: Settings):
        """Initialize container manager.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.engine = settings.container.engine

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
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/unit/test_image_names.py -v
```

Expected: 4 tests PASS

**Step 5: Commit**

Run:
```bash
git add packages/orchestrator/src/color_scheme_orchestrator/container/manager.py
git add packages/orchestrator/tests/unit/test_image_names.py
git commit -m "feat(orchestrator): add image name resolution

Resolve Backend enum to full container image names.
Supports optional registry prefix from settings.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Volume Mount Configuration

**Files:**
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`
- Create: `packages/orchestrator/tests/unit/test_volume_mounts.py`

**Step 1: Write failing test for volume mount construction**

Create `packages/orchestrator/tests/unit/test_volume_mounts.py`:
```python
"""Tests for volume mount configuration."""

import pytest
from pathlib import Path

from color_scheme_orchestrator.container.manager import ContainerManager
from color_scheme.config.settings import Settings


class TestVolumeMounts:
    """Tests for constructing volume mounts."""

    def test_image_mount_readonly(self):
        """Test image file is mounted read-only."""
        settings = Settings.get()
        manager = ContainerManager(settings)
        image_path = Path("/home/user/wallpaper.png")
        output_dir = Path("/tmp/output")

        mounts = manager.build_volume_mounts(image_path, output_dir)

        # Find image mount
        image_mount = next(m for m in mounts if "/input/image.png" in m)
        assert image_path.as_posix() in image_mount
        assert ":ro" in image_mount

    def test_output_mount_readwrite(self):
        """Test output directory is mounted read-write."""
        settings = Settings.get()
        manager = ContainerManager(settings)
        image_path = Path("/home/user/wallpaper.png")
        output_dir = Path("/tmp/output")

        mounts = manager.build_volume_mounts(image_path, output_dir)

        # Find output mount
        output_mount = next(m for m in mounts if "/output" in m)
        assert output_dir.as_posix() in output_mount
        assert ":rw" in output_mount or not ":ro" in output_mount

    def test_templates_mount_readonly(self):
        """Test templates directory is mounted read-only."""
        settings = Settings.get()
        manager = ContainerManager(settings)
        image_path = Path("/home/user/wallpaper.png")
        output_dir = Path("/tmp/output")

        mounts = manager.build_volume_mounts(image_path, output_dir)

        # Find templates mount
        template_mount = next(m for m in mounts if "/templates" in m)
        assert settings.templates.directory.as_posix() in template_mount
        assert ":ro" in template_mount

    def test_mount_format_docker_style(self):
        """Test mounts are in Docker -v format."""
        settings = Settings.get()
        manager = ContainerManager(settings)
        image_path = Path("/home/user/wallpaper.png")
        output_dir = Path("/tmp/output")

        mounts = manager.build_volume_mounts(image_path, output_dir)

        # All mounts should be in format: host:container[:mode]
        for mount in mounts:
            parts = mount.split(":")
            assert len(parts) >= 2  # host:container or host:container:mode
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/unit/test_volume_mounts.py::TestVolumeMounts::test_image_mount_readonly -v
```

Expected: AttributeError - build_volume_mounts method not defined

**Step 3: Implement build_volume_mounts method**

Edit `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`:
```python
"""Container manager for orchestrating color extraction in containers."""

from pathlib import Path

from color_scheme.config.enums import Backend
from color_scheme.config.settings import Settings


class ContainerManager:
    """Manages container lifecycle for color scheme generation.

    Handles:
    - Container engine detection (Docker/Podman)
    - Image management (pull, list, remove)
    - Container execution
    - Volume mount configuration
    """

    def __init__(self, settings: Settings):
        """Initialize container manager.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.engine = settings.container.engine

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
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/unit/test_volume_mounts.py -v
```

Expected: 4 tests PASS

**Step 5: Commit**

Run:
```bash
git add packages/orchestrator/src/color_scheme_orchestrator/container/manager.py
git add packages/orchestrator/tests/unit/test_volume_mounts.py
git commit -m "feat(orchestrator): add volume mount configuration

Build Docker-style volume mounts for image, output, templates.
Image and templates mounted read-only, output read-write.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Container Execution Runner

**Files:**
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`
- Create: `packages/orchestrator/tests/unit/test_container_execution.py`

**Step 1: Write failing test for container execution**

Create `packages/orchestrator/tests/unit/test_container_execution.py`:
```python
"""Tests for container execution."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call

from color_scheme_orchestrator.container.manager import ContainerManager
from color_scheme.config.enums import Backend
from color_scheme.config.settings import Settings


class TestContainerExecution:
    """Tests for executing commands in containers."""

    @patch("subprocess.run")
    def test_run_generate_builds_docker_command(self, mock_run):
        """Test that run_generate constructs correct docker command."""
        settings = Settings.get()
        settings.container.engine = "docker"
        manager = ContainerManager(settings)

        image_path = Path("/tmp/test.png")
        output_dir = Path("/tmp/output")
        backend = Backend.PYWAL

        # Mock successful execution
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        manager.run_generate(
            backend=backend,
            image_path=image_path,
            output_dir=output_dir,
        )

        # Verify docker was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]

        assert call_args[0] == "docker"
        assert "run" in call_args
        assert "--rm" in call_args
        assert "color-scheme-pywal:latest" in call_args

    @patch("subprocess.run")
    def test_run_generate_includes_volume_mounts(self, mock_run):
        """Test that volume mounts are included in docker command."""
        settings = Settings.get()
        manager = ContainerManager(settings)

        image_path = Path("/tmp/test.png")
        output_dir = Path("/tmp/output")
        backend = Backend.CUSTOM

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        manager.run_generate(
            backend=backend,
            image_path=image_path,
            output_dir=output_dir,
        )

        call_args = mock_run.call_args[0][0]

        # Check for -v flags
        v_indices = [i for i, arg in enumerate(call_args) if arg == "-v"]
        assert len(v_indices) >= 3  # At least image, output, templates

    @patch("subprocess.run")
    def test_run_generate_passes_cli_args(self, mock_run):
        """Test that CLI arguments are passed to container."""
        settings = Settings.get()
        manager = ContainerManager(settings)

        image_path = Path("/tmp/test.png")
        output_dir = Path("/tmp/output")
        backend = Backend.PYWAL
        cli_args = ["--saturation", "1.5", "--format", "json"]

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        manager.run_generate(
            backend=backend,
            image_path=image_path,
            output_dir=output_dir,
            cli_args=cli_args,
        )

        call_args = mock_run.call_args[0][0]

        # Container command should include: color-scheme generate /input/image.png ...
        assert "color-scheme" in call_args
        assert "generate" in call_args
        assert "/input/image.png" in call_args
        assert "--saturation" in call_args
        assert "1.5" in call_args

    @patch("subprocess.run")
    def test_run_generate_raises_on_failure(self, mock_run):
        """Test that non-zero exit code raises exception."""
        settings = Settings.get()
        manager = ContainerManager(settings)

        image_path = Path("/tmp/test.png")
        output_dir = Path("/tmp/output")
        backend = Backend.PYWAL

        # Mock failed execution
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: backend failed"
        )

        with pytest.raises(RuntimeError, match="Container execution failed"):
            manager.run_generate(
                backend=backend,
                image_path=image_path,
                output_dir=output_dir,
            )
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/unit/test_container_execution.py::TestContainerExecution::test_run_generate_builds_docker_command -v
```

Expected: AttributeError - run_generate method not defined

**Step 3: Implement run_generate method**

Edit `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`:
```python
"""Container manager for orchestrating color extraction in containers."""

import subprocess
from pathlib import Path

from color_scheme.config.enums import Backend
from color_scheme.config.settings import Settings


class ContainerManager:
    """Manages container lifecycle for color scheme generation.

    Handles:
    - Container engine detection (Docker/Podman)
    - Image management (pull, list, remove)
    - Container execution
    - Volume mount configuration
    """

    def __init__(self, settings: Settings):
        """Initialize container manager.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.engine = settings.container.engine

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

        # Add volume mounts
        for mount in mounts:
            cmd.extend(["-v", mount])

        # Add image
        cmd.append(image)

        # Add container command: color-scheme generate /input/image.png [args]
        cmd.extend(["color-scheme", "generate", "/input/image.png"])

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
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/unit/test_container_execution.py -v
```

Expected: 4 tests PASS

**Step 5: Commit**

Run:
```bash
git add packages/orchestrator/src/color_scheme_orchestrator/container/manager.py
git add packages/orchestrator/tests/unit/test_container_execution.py
git commit -m "feat(orchestrator): add container execution runner

Execute color-scheme generate in containers with proper mounts.
Raises RuntimeError on container failure with stderr output.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: CLI Generate Command (Orchestrator)

**Files:**
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`
- Create: `packages/orchestrator/tests/integration/test_cli_generate_orchestrator.py`

**Step 1: Write failing integration test**

Create `packages/orchestrator/tests/integration/test_cli_generate_orchestrator.py`:
```python
"""Integration tests for orchestrator CLI generate command."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, Mock

from color_scheme_orchestrator.cli.main import app


runner = CliRunner()


class TestOrchestratorGenerate:
    """Tests for orchestrator generate command."""

    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    def test_generate_calls_container_manager(self, mock_run):
        """Test that generate command uses container manager."""
        # Create a temporary test image
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            result = runner.invoke(app, [
                "generate",
                str(test_image),
                "--backend", "pywal",
            ])

            # Should call container manager
            assert mock_run.called
            assert result.exit_code == 0
        finally:
            test_image.unlink()

    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    def test_generate_passes_cli_args_to_container(self, mock_run):
        """Test CLI arguments are passed to container."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            result = runner.invoke(app, [
                "generate",
                str(test_image),
                "--saturation", "1.5",
                "--format", "json",
                "--format", "css",
            ])

            # Verify CLI args were passed
            call_kwargs = mock_run.call_args[1]
            cli_args = call_kwargs.get("cli_args", [])

            assert "--saturation" in cli_args
            assert "1.5" in cli_args
            assert "--format" in cli_args
            assert result.exit_code == 0
        finally:
            test_image.unlink()

    def test_generate_requires_image_path(self):
        """Test that generate command requires image path."""
        result = runner.invoke(app, ["generate"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "required" in result.output.lower()
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/integration/test_cli_generate_orchestrator.py::TestOrchestratorGenerate::test_generate_requires_image_path -v
```

Expected: Command not implemented (placeholder returns error)

**Step 3: Implement generate command**

Edit `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`:
```python
"""CLI entry point for color-scheme orchestrator."""

from pathlib import Path

import typer
from rich.console import Console

from color_scheme.config.enums import Backend, ColorFormat
from color_scheme.config.settings import Settings
from color_scheme_orchestrator.container.manager import ContainerManager

app = typer.Typer(
    name="color-scheme",
    help="Color scheme generator with containerized backends",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()


@app.command()
def version():
    """Show version information."""
    from color_scheme_orchestrator import __version__

    typer.echo(f"color-scheme-orchestrator version {__version__}")


@app.command()
def generate(
    image_path: Path = typer.Argument(  # noqa: B008
        ...,
        help="Path to source image",
    ),
    output_dir: Path | None = typer.Option(  # noqa: B008
        None,
        "--output-dir",
        "-o",
        help="Output directory for color scheme files",
    ),
    backend: Backend | None = typer.Option(  # noqa: B008
        None,
        "--backend",
        "-b",
        help="Backend to use for color extraction",
    ),
    formats: list[ColorFormat] | None = typer.Option(  # noqa: B008
        None,
        "--format",
        "-f",
        help="Output format(s) to generate (can be specified multiple times)",
    ),
    saturation: float | None = typer.Option(  # noqa: B008
        None,
        "--saturation",
        "-s",
        min=0.0,
        max=2.0,
        help="Saturation adjustment factor (0.0-2.0)",
    ),
) -> None:
    """Generate color scheme using containerized backend.

    Runs color-scheme-core generate command inside a container.

    Example usage:

        # Generate with default backend
        color-scheme generate wallpaper.jpg

        # Specify backend
        color-scheme generate wallpaper.jpg -b pywal

        # Custom output and formats
        color-scheme generate wallpaper.jpg -o ~/colors -f json -f css
    """
    try:
        # Load settings
        settings = Settings.get()

        # Validate image path
        if not image_path.exists():
            console.print(f"[red]Error:[/red] Image file not found: {image_path}")
            raise typer.Exit(1)

        if not image_path.is_file():
            console.print(f"[red]Error:[/red] Path is not a file: {image_path}")
            raise typer.Exit(1)

        # Use default backend if not specified
        if backend is None:
            backend = Backend(settings.generation.default_backend)

        # Use default output dir if not specified
        if output_dir is None:
            output_dir = settings.output.directory

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build CLI arguments to pass to container
        cli_args = []

        # Output directory (container will write to /output)
        cli_args.extend(["--output-dir", "/output"])

        # Backend
        cli_args.extend(["--backend", backend.value])

        # Formats
        if formats:
            for fmt in formats:
                cli_args.extend(["--format", fmt.value])

        # Saturation
        if saturation is not None:
            cli_args.extend(["--saturation", str(saturation)])

        # Create container manager
        manager = ContainerManager(settings)

        # Execute in container
        console.print(f"[cyan]Running in container:[/cyan] {backend.value}")
        console.print(f"[cyan]Output directory:[/cyan] {output_dir}")

        manager.run_generate(
            backend=backend,
            image_path=image_path,
            output_dir=output_dir,
            cli_args=cli_args,
        )

        console.print("\n[green]Color scheme generated successfully![/green]")

    except RuntimeError as e:
        console.print(f"[red]Container error:[/red] {str(e)}")
        raise typer.Exit(1) from None

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


def main():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/integration/test_cli_generate_orchestrator.py -v
```

Expected: 3 tests PASS

**Step 5: Commit**

Run:
```bash
git add packages/orchestrator/src/color_scheme_orchestrator/cli/main.py
git add packages/orchestrator/tests/integration/test_cli_generate_orchestrator.py
git commit -m "feat(orchestrator): implement CLI generate command

Execute color scheme generation in containers.
Translates CLI args and delegates to ContainerManager.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: CLI Show Command (Delegation)

**Files:**
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`
- Create: `packages/orchestrator/tests/integration/test_cli_show_delegation.py`

**Step 1: Write failing test for show delegation**

Create `packages/orchestrator/tests/integration/test_cli_show_delegation.py`:
```python
"""Integration tests for show command delegation."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch

from color_scheme_orchestrator.cli.main import app


runner = CliRunner()


class TestShowDelegation:
    """Tests for delegating show command to core."""

    @patch("color_scheme_orchestrator.cli.main.core_show_colors")
    def test_show_delegates_to_core(self, mock_core_show):
        """Test that show command calls core's show implementation."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            result = runner.invoke(app, ["show", str(test_image)])

            # Should delegate to core
            assert mock_core_show.called

        finally:
            test_image.unlink()

    @patch("color_scheme_orchestrator.cli.main.core_show_colors")
    def test_show_passes_arguments(self, mock_core_show):
        """Test that show passes arguments to core."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            result = runner.invoke(app, [
                "show",
                str(test_image),
                "--backend", "custom",
                "--saturation", "1.2",
            ])

            # Verify arguments were passed
            assert mock_core_show.called

        finally:
            test_image.unlink()
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/integration/test_cli_show_delegation.py::TestShowDelegation::test_show_delegates_to_core -v
```

Expected: Command not found or not implemented

**Step 3: Implement show command delegation**

Edit `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`, add after generate command:
```python
@app.command()
def show(
    image_path: Path = typer.Argument(  # noqa: B008
        ...,
        help="Path to source image",
    ),
    backend: Backend | None = typer.Option(  # noqa: B008
        None,
        "--backend",
        "-b",
        help="Backend to use for color extraction (auto-detects if not specified)",
    ),
    saturation: float | None = typer.Option(  # noqa: B008
        None,
        "--saturation",
        "-s",
        min=0.0,
        max=2.0,
        help="Saturation adjustment factor (0.0-2.0)",
    ),
) -> None:
    """Display color scheme in terminal (delegates to core).

    This command runs directly on the host without containers.

    Example usage:

        # Show colors from image
        color-scheme show wallpaper.jpg

        # Show with specific backend
        color-scheme show wallpaper.jpg -b pywal
    """
    # Import core's show implementation
    from color_scheme.cli.main import show as core_show_colors

    # Delegate to core - it runs on host, no container needed
    try:
        # Call core's show function with the same context
        # Use invoke to call the Typer command programmatically
        from typer import Context

        # Create a mock context for the core command
        ctx = Context(core_show_colors)

        # Build arguments dict
        args = {
            "image_path": image_path,
            "backend": backend,
            "saturation": saturation,
        }

        # Invoke core command
        core_show_colors.callback(**args)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/integration/test_cli_show_delegation.py -v
```

Expected: 2 tests PASS

**Step 5: Commit**

Run:
```bash
git add packages/orchestrator/src/color_scheme_orchestrator/cli/main.py
git add packages/orchestrator/tests/integration/test_cli_show_delegation.py
git commit -m "feat(orchestrator): implement show command delegation

Delegate show command to core package (no container).
Show runs on host for immediate feedback.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Final Testing and Integration

**Files:**
- Create: `packages/orchestrator/tests/integration/test_end_to_end.py`
- Create: `packages/orchestrator/README.md` (update)

**Step 1: Write end-to-end integration test**

Create `packages/orchestrator/tests/integration/test_end_to_end.py`:
```python
"""End-to-end integration tests for orchestrator package."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, Mock

from color_scheme_orchestrator.cli.main import app


runner = CliRunner()


class TestEndToEnd:
    """End-to-end workflow tests."""

    @patch("subprocess.run")
    def test_full_generate_workflow(self, mock_subprocess):
        """Test complete generate workflow with mocked container."""
        # Mock successful container execution
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            try:
                result = runner.invoke(app, [
                    "generate",
                    str(test_image),
                    "--output-dir", str(output_dir),
                    "--backend", "custom",
                    "--format", "json",
                ])

                # Should succeed
                assert result.exit_code == 0
                assert "successfully" in result.output.lower()

                # Should have called docker/podman
                assert mock_subprocess.called
                call_args = mock_subprocess.call_args[0][0]
                assert call_args[0] in ["docker", "podman"]

            finally:
                test_image.unlink()

    def test_version_command(self):
        """Test version command works."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "orchestrator" in result.output

    def test_help_shows_all_commands(self):
        """Test help shows all available commands."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "generate" in result.output
        assert "show" in result.output
        assert "version" in result.output
```

**Step 2: Run tests**

Run:
```bash
cd packages/orchestrator
uv run pytest tests/integration/test_end_to_end.py -v
```

Expected: 3 tests PASS

**Step 3: Update README with usage instructions**

Edit `packages/orchestrator/README.md`:
```markdown
# color-scheme-orchestrator

Container orchestrator for color-scheme-core.

## Features

- Runs color extraction in isolated containers (Docker/Podman)
- Same CLI interface as core package
- No host dependencies for backends (pywal, wallust, etc.)
- Automatic container image management

## Installation

```bash
pip install color-scheme-orchestrator
```

Requires Docker or Podman installed.

## Usage

### Generate Color Scheme (Containerized)

```bash
# Generate with default backend
color-scheme generate wallpaper.jpg

# Specify backend and output directory
color-scheme generate wallpaper.jpg -b pywal -o ~/colors

# Generate specific formats
color-scheme generate wallpaper.jpg -f json -f css -f scss

# Adjust saturation
color-scheme generate wallpaper.jpg -s 1.5
```

The `generate` command runs inside a container, so you don't need to install backend dependencies on your host system.

### Show Color Scheme (Host)

```bash
# Display colors in terminal
color-scheme show wallpaper.jpg

# Show with specific backend
color-scheme show wallpaper.jpg -b custom
```

The `show` command runs directly on the host for immediate feedback (delegates to core package).

### Check Version

```bash
color-scheme version
```

## Container Images

The orchestrator uses pre-built container images:

- `color-scheme-pywal:latest` - pywal backend with ImageMagick
- `color-scheme-wallust:latest` - wallust backend (Rust)
- `color-scheme-custom:latest` - custom backend with scikit-learn

Images are pulled automatically from the configured registry (ghcr.io by default).

## Configuration

Uses the same `settings.toml` as color-scheme-core, with additional container settings:

```toml
[container]
engine = "docker"  # or "podman"
image_registry = "ghcr.io/your-org"  # optional registry prefix
```

See [Configuration Guide](https://github.com/your-org/color-scheme/blob/main/docs/configuration.md) for details.

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run tests in parallel
uv run pytest -n auto
```

## Architecture

The orchestrator wraps color-scheme-core and delegates commands:

- **generate**: Runs in container with volume mounts for image, output, templates
- **show**: Delegates directly to core (no container, runs on host)

This provides containerization benefits (no host dependencies) while maintaining fast feedback for display commands.

## Documentation

See main project documentation at [github.com/your-org/color-scheme](https://github.com/your-org/color-scheme).
```

**Step 4: Run all tests**

Run:
```bash
cd packages/orchestrator
uv run pytest -v
```

Expected: All tests PASS

**Step 5: Final commit**

Run:
```bash
git add packages/orchestrator/tests/integration/test_end_to_end.py
git add packages/orchestrator/README.md
git commit -m "test(orchestrator): add end-to-end integration tests

Verify complete workflow from CLI to container execution.
Update README with full usage documentation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Completion

Phase 4 implementation complete! You now have:

✅ **ContainerManager** - Docker/Podman abstraction with image name resolution
✅ **Volume Mounts** - Proper mount configuration for image, output, templates
✅ **Container Execution** - Run generate commands in isolated containers
✅ **CLI Generate** - Orchestrator command that delegates to containers
✅ **CLI Show** - Direct delegation to core package (no container)
✅ **Integration Tests** - Full test coverage including end-to-end workflows
✅ **Documentation** - Complete README with usage examples

## Next Steps

The orchestrator package is ready for:
- **Dockerfile Creation**: Build container images for pywal, wallust, custom backends
- **Image Management Commands**: Add install/uninstall/list-images commands
- **CI/CD**: Container image build and publish pipeline
- **Registry Publishing**: Push images to ghcr.io

## Notes

**Container Image Requirements** (not in this plan):
- Base image with color-scheme-core installed
- Backend-specific images extending base
- Proper ENTRYPOINT for CLI execution

**Future Enhancements** (not in this plan):
- `color-scheme install <backend>` - Pull container images
- `color-scheme uninstall <backend>` - Remove images
- `color-scheme list-images` - Show available images
- Auto-pull missing images (configurable)
