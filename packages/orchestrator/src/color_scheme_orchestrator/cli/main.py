"""CLI entry point for color-scheme orchestrator."""

from pathlib import Path

import typer
from color_scheme.config.enums import Backend, ColorFormat
from color_scheme_settings import configure, get_config
from rich.console import Console

from color_scheme_orchestrator.cli.commands import install, uninstall
from color_scheme_orchestrator.config.unified import UnifiedConfig
from color_scheme_orchestrator.container.manager import ContainerManager

# Bootstrap settings for orchestrator (includes core + orchestrator namespaces)
configure(UnifiedConfig)

app = typer.Typer(
    name="color-scheme",
    help="Color scheme generator with containerized backends",
    add_completion=False,
    no_args_is_help=True,
)

# Register subcommands from commands module
app.command()(install)
app.command()(uninstall)

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
    dry_run: bool = typer.Option(  # noqa: B008
        False,
        "--dry-run",
        "-n",
        help="Show what would be done without executing",
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
        config = get_config()

        # Handle dry-run mode
        if dry_run:
            from color_scheme_orchestrator.cli.dry_run import ContainerGenerateDryRunReporter
            from color_scheme_settings.resolver import ConfigResolver
            
            # Build CLI args for resolver
            cli_args = {}
            if backend is not None:
                cli_args["backend"] = backend.value
            if output_dir is not None:
                cli_args["output_dir"] = str(output_dir)
            if formats is not None:
                cli_args["formats"] = [f.value for f in formats]
            if saturation is not None:
                cli_args["saturation"] = saturation
            
            # Resolve configuration
            resolver = ConfigResolver()
            resolved = resolver.resolve(
                cli_args=cli_args,
                command_ctx={"command": "generate"}
            )
            
            # Create reporter and run
            reporter = ContainerGenerateDryRunReporter(
                command="color-scheme generate",
                resolved_config=resolved,
                context={"image_path": image_path}
            )
            reporter.run()
            
            # Exit successfully without executing
            raise typer.Exit(0)

        # Validate image path
        if not image_path.exists():
            console.print(f"[red]Error:[/red] Image file not found: {image_path}")
            raise typer.Exit(1)

        if not image_path.is_file():
            console.print(f"[red]Error:[/red] Path is not a file: {image_path}")
            raise typer.Exit(1)

        # Use default backend if not specified
        if backend is None:
            backend = Backend(config.core.generation.default_backend)

        # Use default output dir if not specified
        if output_dir is None:
            output_dir = config.core.output.directory

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
        manager = ContainerManager(config)

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

    except typer.Exit:
        # Re-raise typer.Exit without catching it
        raise

    except RuntimeError as e:
        console.print(f"[red]Container error:[/red] {str(e)}")
        raise typer.Exit(1) from None

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


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
    dry_run: bool = typer.Option(  # noqa: B008
        False,
        "--dry-run",
        "-n",
        help="Show what would be done without executing",
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
    # Handle dry-run mode
    if dry_run:
        from color_scheme_orchestrator.cli.dry_run import ContainerShowDryRunReporter
        from color_scheme_settings.resolver import ConfigResolver
        
        # Build CLI args for resolver
        cli_args = {}
        if backend is not None:
            cli_args["backend"] = backend.value
        if saturation is not None:
            cli_args["saturation"] = saturation
        
        # Resolve configuration
        resolver = ConfigResolver()
        resolved = resolver.resolve(
            cli_args=cli_args,
            command_ctx={"command": "show"}
        )
        
        # Create reporter and run
        reporter = ContainerShowDryRunReporter(
            command="color-scheme show",
            resolved_config=resolved,
            context={"image_path": image_path}
        )
        reporter.run()
        
        # Exit successfully without executing
        raise typer.Exit(0)

    # Import core's show implementation
    from color_scheme.cli.main import show as core_show_colors

    # Delegate to core - it runs on host, no container needed
    try:
        # Call core's show function directly
        # Typer commands are regular functions, no .callback needed
        core_show_colors(
            image_path=image_path,
            backend=backend,
            saturation=saturation,
            dry_run=False,
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None


def main():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    main()
