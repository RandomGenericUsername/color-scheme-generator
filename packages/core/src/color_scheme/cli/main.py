"""CLI entry point for color-scheme."""

import logging
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from color_scheme.config.enums import Backend, ColorFormat
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    ColorSchemeError,
    InvalidImageError,
    OutputWriteError,
    TemplateRenderError,
)
from color_scheme.core.types import GeneratorConfig
from color_scheme.factory import BackendFactory
from color_scheme.output.manager import OutputManager

app = typer.Typer(
    name="color-scheme",
    help="Generate color schemes from images",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()
logger = logging.getLogger(__name__)


@app.command()
def version():
    """Show version information."""
    from color_scheme import __version__

    typer.echo(f"color-scheme-core version {__version__}")


@app.command()
def generate(
    image_path: Path = typer.Argument(
        ...,
        help="Path to source image",
    ),
    output_dir: Path = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for color scheme files",
    ),
    backend: Backend = typer.Option(
        None,
        "--backend",
        "-b",
        help="Backend to use for color extraction (auto-detects if not specified)",
    ),
    formats: list[ColorFormat] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format(s) to generate (can be specified multiple times)",
    ),
    saturation: float = typer.Option(
        None,
        "--saturation",
        "-s",
        min=0.0,
        max=2.0,
        help="Saturation adjustment factor (0.0-2.0, default from settings)",
    ),
):
    """Generate color scheme from an image.

    Extracts colors from an image and generates color scheme files in various formats.

    Example usage:

        # Generate with auto-detected backend and default formats
        color-scheme generate wallpaper.jpg

        # Specify backend and output directory
        color-scheme generate wallpaper.jpg -b pywal -o ~/colors

        # Generate specific formats
        color-scheme generate wallpaper.jpg -f json -f css -f scss

        # Adjust saturation
        color-scheme generate wallpaper.jpg -s 1.5
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

        # Create backend factory
        factory = BackendFactory(settings)

        # Auto-detect backend if not specified
        if backend is None:
            backend = factory.auto_detect()
            console.print(f"[cyan]Auto-detected backend:[/cyan] {backend.value}")
        else:
            console.print(f"[cyan]Using backend:[/cyan] {backend.value}")

        # Build GeneratorConfig with overrides
        overrides = {}
        if output_dir is not None:
            overrides["output_dir"] = output_dir
        if saturation is not None:
            overrides["saturation_adjustment"] = saturation
        if formats is not None:
            overrides["formats"] = formats

        config = GeneratorConfig.from_settings(settings, **overrides)

        # Create generator
        console.print("[cyan]Creating generator...[/cyan]")
        generator = factory.create(backend)

        # Generate color scheme
        console.print(f"[cyan]Extracting colors from:[/cyan] {image_path}")
        color_scheme = generator.generate(image_path, config)

        # Apply saturation adjustment if specified
        if config.saturation_adjustment is not None and config.saturation_adjustment != 1.0:
            console.print(
                f"[cyan]Adjusting saturation:[/cyan] {config.saturation_adjustment}"
            )
            # Adjust all colors
            color_scheme.background = color_scheme.background.adjust_saturation(
                config.saturation_adjustment
            )
            color_scheme.foreground = color_scheme.foreground.adjust_saturation(
                config.saturation_adjustment
            )
            color_scheme.cursor = color_scheme.cursor.adjust_saturation(
                config.saturation_adjustment
            )
            color_scheme.colors = [
                c.adjust_saturation(config.saturation_adjustment)
                for c in color_scheme.colors
            ]

        # Write output files
        output_manager = OutputManager(settings)
        console.print(f"[cyan]Writing output files to:[/cyan] {config.output_dir}")
        output_manager.write_outputs(
            color_scheme,
            config.output_dir,
            config.formats,
        )

        # Display success message with file list
        console.print("\n[green]Generated color scheme successfully![/green]\n")

        # Create table of generated files
        table = Table(title="Generated Files")
        table.add_column("Format", style="cyan")
        table.add_column("File Path", style="green")

        for fmt in config.formats:
            file_path = config.output_dir / f"colors.{fmt.value}"
            table.add_row(fmt.value, str(file_path))

        console.print(table)

    except InvalidImageError as e:
        console.print(f"[red]Error:[/red] Invalid image: {e.reason}")
        logger.error("Invalid image: %s", e)
        raise typer.Exit(1)

    except BackendNotAvailableError as e:
        console.print(f"[red]Error:[/red] Backend '{e.backend}' not available: {e.reason}")
        console.print("\n[yellow]Tip:[/yellow] Try auto-detection or use a different backend")
        logger.error("Backend not available: %s", e)
        raise typer.Exit(1)

    except ColorExtractionError as e:
        console.print(f"[red]Error:[/red] Color extraction failed: {e.reason}")
        logger.error("Color extraction failed: %s", e)
        raise typer.Exit(1)

    except TemplateRenderError as e:
        console.print(f"[red]Error:[/red] Template rendering failed: {e.reason}")
        console.print(f"Template: {e.template_name}")
        logger.error("Template rendering failed: %s", e)
        raise typer.Exit(1)

    except OutputWriteError as e:
        console.print(f"[red]Error:[/red] Failed to write output file: {e.reason}")
        console.print(f"File: {e.file_path}")
        logger.error("Output write failed: %s", e)
        raise typer.Exit(1)

    except ColorSchemeError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error("Color scheme error: %s", e)
        raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        logger.exception("Unexpected error in generate command")
        raise typer.Exit(1)


def main():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    main()
