"""Uninstall command to remove backend container images."""

import subprocess

import typer
from color_scheme.config.enums import Backend
from rich.console import Console

console = Console()


def uninstall(
    backend: Backend | None = typer.Argument(  # noqa: B008
        None,
        help="Backend to uninstall (pywal, wallust, or custom). "
        "If not specified, removes all backends.",
    ),
    yes: bool = typer.Option(  # noqa: B008
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
    engine: str | None = typer.Option(  # noqa: B008
        None,
        "--engine",
        "-e",
        help="Container engine to use (docker or podman). "
        "Uses config default if not specified.",
    ),
) -> None:
    """Remove container images for color extraction backends.

    This command removes Docker/Podman images for the specified backend(s).
    Use with caution as this will delete the images from your system.

    Examples:

        # Remove all backends (with confirmation)
        color-scheme uninstall

        # Remove specific backend without confirmation
        color-scheme uninstall pywal --yes

        # Use podman instead of docker
        color-scheme uninstall --engine podman
    """
    try:
        # Determine container engine
        if engine is None:
            # Default to docker since we removed container settings from core
            container_engine = "docker"
        else:
            container_engine = engine.lower()
            if container_engine not in ["docker", "podman"]:
                console.print(
                    f"[red]Error:[/red] Invalid engine '{container_engine}'. "
                    "Must be 'docker' or 'podman'."
                )
                raise typer.Exit(1)

        # Determine which backends to uninstall
        if backend is None:
            backends_to_remove = list(Backend)
        else:
            backends_to_remove = [backend]

        # Build image names
        image_names = [f"color-scheme-{b.value}:latest" for b in backends_to_remove]

        # Confirm deletion
        if not yes:
            console.print(
                "[yellow]Warning:[/yellow] This will remove the following images:"
            )
            for image in image_names:
                console.print(f"  - {image}")
            console.print()

            confirm = typer.confirm("Are you sure you want to continue?")
            if not confirm:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

        # Remove each image
        console.print(f"[cyan]Removing {len(image_names)} image(s)...[/cyan]\n")

        success_count = 0
        failed_images = []

        for backend_enum, image_name in zip(backends_to_remove, image_names):
            # Build docker rmi command
            cmd = [container_engine, "rmi", image_name]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    console.print(
                        f"[green]✓[/green] {backend_enum.value}: Removed {image_name}"
                    )
                    success_count += 1
                else:
                    # Image might not exist, which is fine
                    if (
                        "no such image" in result.stderr.lower()
                        or "not found" in result.stderr.lower()
                    ):
                        console.print(
                            f"[dim]○[/dim] {backend_enum.value}: "
                            "Image not found (already removed)"
                        )
                        success_count += 1
                    else:
                        console.print(
                            f"[red]✗[/red] {backend_enum.value}: Failed to remove"
                        )
                        console.print(f"[dim]{result.stderr}[/dim]")
                        failed_images.append(image_name)

            except subprocess.SubprocessError as e:
                console.print(f"[red]✗[/red] {backend_enum.value}: {str(e)}")
                failed_images.append(image_name)

        # Print summary
        console.print("\n[bold]Removal Summary:[/bold]")
        console.print(f"  [green]Success:[/green] {success_count}/{len(image_names)}")

        if failed_images:
            console.print(f"  [red]Failed:[/red] {', '.join(failed_images)}")
            raise typer.Exit(1)
        else:
            console.print("\n[green]All images removed successfully![/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None
