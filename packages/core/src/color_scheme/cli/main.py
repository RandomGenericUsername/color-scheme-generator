"""CLI entry point for color-scheme."""

import logging
from pathlib import Path
from typing import Any, Protocol, cast

import typer
from color_scheme_settings import configure, get_config
from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend, ColorFormat
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


class CoreOnlyConfig(BaseModel):
    """Configuration for standalone core usage (without orchestrator)."""

    model_config = ConfigDict(frozen=True)
    core: AppConfig = Field(default_factory=AppConfig)


class HasCoreConfig(Protocol):
    """Protocol for configs that have a .core attribute."""

    core: AppConfig


# Bootstrap settings for standalone core usage
configure(CoreOnlyConfig)

app = typer.Typer(
    name="color-scheme",
    help="Generate color schemes from images",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()
logger = logging.getLogger(__name__)


@app.command()
def version() -> None:
    """Show version information."""
    from color_scheme import __version__

    typer.echo(f"color-scheme-core version {__version__}")


@app.command()
def generate(
    image_path: Path = typer.Argument(
        ...,
        help="Path to source image",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for color scheme files",
    ),
    backend: Backend | None = typer.Option(
        None,
        "--backend",
        "-b",
        help="Backend to use for color extraction (auto-detects if not specified)",
    ),
    formats: list[ColorFormat] | None = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format(s) to generate (can be specified multiple times)",
    ),
    saturation: float | None = typer.Option(
        None,
        "--saturation",
        "-s",
        min=0.0,
        max=2.0,
        help="Saturation adjustment factor (0.0-2.0, default from settings)",
    ),
) -> None:
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
        config = cast(HasCoreConfig, get_config())

        # Validate image path
        if not image_path.exists():
            console.print(f"[red]Error:[/red] Image file not found: {image_path}")
            raise typer.Exit(1)

        if not image_path.is_file():
            console.print(f"[red]Error:[/red] Path is not a file: {image_path}")
            raise typer.Exit(1)

        # Create backend factory
        factory = BackendFactory(config.core)

        # Auto-detect backend if not specified
        if backend is None:
            backend = factory.auto_detect()
            console.print(f"[cyan]Auto-detected backend:[/cyan] {backend.value}")
        else:
            console.print(f"[cyan]Using backend:[/cyan] {backend.value}")

        # Build GeneratorConfig with overrides
        overrides: dict[str, Any] = {}
        if output_dir is not None:
            overrides["output_dir"] = output_dir
        if saturation is not None:
            overrides["saturation_adjustment"] = saturation
        if formats is not None:
            overrides["formats"] = formats

        generator_config = GeneratorConfig.from_settings(config.core, **overrides)

        # Create generator
        console.print("[cyan]Creating generator...[/cyan]")
        generator = factory.create(backend)

        # Generate color scheme
        console.print(f"[cyan]Extracting colors from:[/cyan] {image_path}")
        color_scheme = generator.generate(image_path, generator_config)

        # Apply saturation adjustment if specified
        if (
            generator_config.saturation_adjustment is not None
            and generator_config.saturation_adjustment != 1.0
        ):
            sat = generator_config.saturation_adjustment
            console.print(f"[cyan]Adjusting saturation:[/cyan] {sat}")
            # Adjust all colors
            color_scheme.background = color_scheme.background.adjust_saturation(sat)
            color_scheme.foreground = color_scheme.foreground.adjust_saturation(sat)
            color_scheme.cursor = color_scheme.cursor.adjust_saturation(sat)
            color_scheme.colors = [
                c.adjust_saturation(sat) for c in color_scheme.colors
            ]

        # Write output files
        output_manager = OutputManager(config.core)
        if generator_config.output_dir is None:
            raise ValueError("output_dir must be configured for generate command")
        if generator_config.formats is None:
            raise ValueError("formats must be configured for generate command")
        console.print(
            f"[cyan]Writing output files to:[/cyan] {generator_config.output_dir}"
        )
        output_manager.write_outputs(
            color_scheme,
            generator_config.output_dir,
            generator_config.formats,
        )

        # Display success message with file list
        console.print("\n[green]Generated color scheme successfully![/green]\n")

        # Create table of generated files
        table = Table(title="Generated Files")
        table.add_column("Format", style="cyan")
        table.add_column("File Path", style="green")

        for fmt in generator_config.formats:
            file_path = generator_config.output_dir / f"colors.{fmt.value}"
            table.add_row(fmt.value, str(file_path))

        console.print(table)

    except InvalidImageError as e:
        console.print(f"[red]Error:[/red] Invalid image: {e.reason}")
        logger.error("Invalid image: %s", e)
        raise typer.Exit(1)

    except BackendNotAvailableError as e:
        console.print(
            f"[red]Error:[/red] Backend '{e.backend}' not available: {e.reason}"
        )
        console.print(
            "\n[yellow]Tip:[/yellow] Try auto-detection or use a different backend"
        )
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

    except typer.Exit:
        # Re-raise typer.Exit to avoid catching it in Exception handler
        raise

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        logger.exception("Unexpected error in generate command")
        raise typer.Exit(1)


@app.command()
def show(
    image_path: Path = typer.Argument(
        ...,
        help="Path to source image",
    ),
    backend: Backend | None = typer.Option(
        None,
        "--backend",
        "-b",
        help="Backend to use for color extraction (auto-detects if not specified)",
    ),
    saturation: float | None = typer.Option(
        None,
        "--saturation",
        "-s",
        min=0.0,
        max=2.0,
        help="Saturation adjustment factor (0.0-2.0, default from settings)",
    ),
) -> None:
    """Display color scheme from an image in the terminal.

    Extracts colors from an image and displays them in a formatted table
    without writing any files.

    Example usage:

        # Show colors with auto-detected backend
        color-scheme show wallpaper.jpg

        # Specify backend
        color-scheme show wallpaper.jpg -b pywal

        # Adjust saturation
        color-scheme show wallpaper.jpg -s 1.5
    """
    try:
        # Load settings
        config = cast(HasCoreConfig, get_config())

        # Validate image path
        if not image_path.exists():
            console.print(f"[red]Error:[/red] Image file not found: {image_path}")
            raise typer.Exit(1)

        if not image_path.is_file():
            console.print(f"[red]Error:[/red] Path is not a file: {image_path}")
            raise typer.Exit(1)

        # Create backend factory
        factory = BackendFactory(config.core)

        # Auto-detect backend if not specified
        if backend is None:
            backend = factory.auto_detect()
            console.print(f"[cyan]Auto-detected backend:[/cyan] {backend.value}")
        else:
            console.print(f"[cyan]Using backend:[/cyan] {backend.value}")

        # Build GeneratorConfig with overrides
        overrides = {}
        if saturation is not None:
            overrides["saturation_adjustment"] = saturation

        generator_config = GeneratorConfig.from_settings(config.core, **overrides)

        # Create generator
        generator = factory.create(backend)

        # Generate color scheme
        console.print(f"[cyan]Extracting colors from:[/cyan] {image_path}")
        color_scheme = generator.generate(image_path, generator_config)

        # Apply saturation adjustment if specified
        if (
            generator_config.saturation_adjustment is not None
            and generator_config.saturation_adjustment != 1.0
        ):
            sat = generator_config.saturation_adjustment
            console.print(f"[cyan]Adjusting saturation:[/cyan] {sat}")
            # Adjust all colors
            color_scheme.background = color_scheme.background.adjust_saturation(sat)
            color_scheme.foreground = color_scheme.foreground.adjust_saturation(sat)
            color_scheme.cursor = color_scheme.cursor.adjust_saturation(sat)
            color_scheme.colors = [
                c.adjust_saturation(sat) for c in color_scheme.colors
            ]

        # Display color scheme information
        console.print()

        # Create info panel
        info_lines = [
            f"[cyan]Source Image:[/cyan] {image_path}",
            f"[cyan]Backend:[/cyan] {backend.value}",
        ]
        if (
            generator_config.saturation_adjustment is not None
            and generator_config.saturation_adjustment != 1.0
        ):
            info_lines.append(
                f"[cyan]Saturation:[/cyan] {generator_config.saturation_adjustment}"
            )

        info_panel = Panel(
            "\n".join(info_lines),
            title="Color Scheme Information",
            border_style="cyan",
        )
        console.print(info_panel)
        console.print()

        # Create table for special colors
        special_table = Table(title="Special Colors", show_header=True)
        special_table.add_column("Color", style="cyan")
        special_table.add_column("Preview", width=10)
        special_table.add_column("Hex", style="white")
        special_table.add_column("RGB", style="white")

        # Add special colors
        special_colors = [
            ("Background", color_scheme.background),
            ("Foreground", color_scheme.foreground),
            ("Cursor", color_scheme.cursor),
        ]

        for name, color in special_colors:
            preview = f"[on {color.hex}]          [/]"
            rgb_str = f"rgb({color.rgb[0]}, {color.rgb[1]}, {color.rgb[2]})"
            special_table.add_row(name, preview, color.hex, rgb_str)

        console.print(special_table)
        console.print()

        # Create table for terminal colors
        terminal_table = Table(title="Terminal Colors (ANSI)", show_header=True)
        terminal_table.add_column("Index", style="cyan", width=6)
        terminal_table.add_column("Name", style="cyan")
        terminal_table.add_column("Preview", width=10)
        terminal_table.add_column("Hex", style="white")
        terminal_table.add_column("RGB", style="white")

        # ANSI color names
        color_names = [
            "Black",
            "Red",
            "Green",
            "Yellow",
            "Blue",
            "Magenta",
            "Cyan",
            "White",
            "Bright Black",
            "Bright Red",
            "Bright Green",
            "Bright Yellow",
            "Bright Blue",
            "Bright Magenta",
            "Bright Cyan",
            "Bright White",
        ]

        # Add terminal colors
        for idx, (name, color) in enumerate(zip(color_names, color_scheme.colors)):
            preview = f"[on {color.hex}]          [/]"
            rgb_str = f"rgb({color.rgb[0]}, {color.rgb[1]}, {color.rgb[2]})"
            terminal_table.add_row(str(idx), name, preview, color.hex, rgb_str)

        console.print(terminal_table)

    except InvalidImageError as e:
        console.print(f"[red]Error:[/red] Invalid image: {e.reason}")
        logger.error("Invalid image: %s", e)
        raise typer.Exit(1)

    except BackendNotAvailableError as e:
        console.print(
            f"[red]Error:[/red] Backend '{e.backend}' not available: {e.reason}"
        )
        console.print(
            "\n[yellow]Tip:[/yellow] Try auto-detection or use a different backend"
        )
        logger.error("Backend not available: %s", e)
        raise typer.Exit(1)

    except ColorExtractionError as e:
        console.print(f"[red]Error:[/red] Color extraction failed: {e.reason}")
        logger.error("Color extraction failed: %s", e)
        raise typer.Exit(1)

    except ColorSchemeError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.error("Color scheme error: %s", e)
        raise typer.Exit(1)

    except typer.Exit:
        # Re-raise typer.Exit to avoid catching it in Exception handler
        raise

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        logger.exception("Unexpected error in show command")
        raise typer.Exit(1)


def main():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    main()
