"""Install command to build backend container images."""

import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from color_scheme.config.enums import Backend
from color_scheme.config.settings import Settings

console = Console()

# Map backends to their Dockerfile names
DOCKERFILE_MAP = {
    Backend.PYWAL: "Dockerfile.pywal",
    Backend.WALLUST: "Dockerfile.wallust",
    Backend.CUSTOM: "Dockerfile.custom",
}


def install(
    backend: Backend | None = typer.Argument(  # noqa: B008
        None,
        help="Backend to install (pywal, wallust, or custom). If not specified, installs all backends.",
    ),
    engine: str | None = typer.Option(  # noqa: B008
        None,
        "--engine",
        "-e",
        help="Container engine to use (docker or podman). Uses config default if not specified.",
    ),
) -> None:
    """Build container images for color extraction backends.

    This command builds Docker/Podman images for the specified backend(s).
    Each image contains color-scheme-core plus the backend-specific dependencies.

    Examples:

        # Install all backends
        color-scheme install

        # Install specific backend
        color-scheme install pywal

        # Use podman instead of docker
        color-scheme install --engine podman
    """
    try:
        # Load settings
        settings = Settings.get()

        # Determine container engine
        if engine is None:
            # Get from settings, but since we removed container settings from core,
            # we need to default to docker
            container_engine = "docker"
        else:
            container_engine = engine.lower()
            if container_engine not in ["docker", "podman"]:
                console.print(
                    f"[red]Error:[/red] Invalid engine '{container_engine}'. "
                    "Must be 'docker' or 'podman'."
                )
                raise typer.Exit(1)

        # Determine which backends to install
        if backend is None:
            backends_to_install = list(Backend)
        else:
            backends_to_install = [backend]

        # Find project root (where packages/ directory is)
        # This file is at: packages/orchestrator/src/color_scheme_orchestrator/cli/commands/install.py
        # Project root is: ../../../../../../../
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent.parent.parent.parent
        docker_dir = project_root / "packages" / "orchestrator" / "docker"

        if not docker_dir.exists():
            console.print(
                f"[red]Error:[/red] Docker directory not found: {docker_dir}"
            )
            raise typer.Exit(1)

        # Build each backend
        console.print(
            f"[cyan]Building {len(backends_to_install)} backend(s) using {container_engine}...[/cyan]\n"
        )

        success_count = 0
        failed_backends = []

        for backend_enum in backends_to_install:
            dockerfile_name = DOCKERFILE_MAP[backend_enum]
            dockerfile_path = docker_dir / dockerfile_name
            image_name = f"color-scheme-{backend_enum.value}:latest"

            if not dockerfile_path.exists():
                console.print(
                    f"[red]✗[/red] {backend_enum.value}: Dockerfile not found at {dockerfile_path}"
                )
                failed_backends.append(backend_enum.value)
                continue

            console.print(f"[cyan]Building {backend_enum.value}...[/cyan]")

            # Build docker command
            cmd = [
                container_engine,
                "build",
                "-f",
                str(dockerfile_path),
                "-t",
                image_name,
                str(project_root),
            ]

            # Show progress while building
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Building {image_name}...",
                    total=None,
                )

                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=project_root,
                    )

                    if result.returncode == 0:
                        progress.update(task, description=f"✓ Built {image_name}")
                        console.print(f"[green]✓[/green] {backend_enum.value}: Built successfully")
                        success_count += 1
                    else:
                        progress.update(task, description=f"✗ Failed to build {image_name}")
                        console.print(f"[red]✗[/red] {backend_enum.value}: Build failed")
                        console.print(f"[dim]{result.stderr}[/dim]")
                        failed_backends.append(backend_enum.value)

                except subprocess.SubprocessError as e:
                    progress.update(task, description=f"✗ Error building {image_name}")
                    console.print(f"[red]✗[/red] {backend_enum.value}: {str(e)}")
                    failed_backends.append(backend_enum.value)

            console.print()  # Empty line for readability

        # Print summary
        console.print("[bold]Build Summary:[/bold]")
        console.print(f"  [green]Success:[/green] {success_count}/{len(backends_to_install)}")

        if failed_backends:
            console.print(f"  [red]Failed:[/red] {', '.join(failed_backends)}")
            raise typer.Exit(1)
        else:
            console.print("\n[green]All backend images built successfully![/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None
