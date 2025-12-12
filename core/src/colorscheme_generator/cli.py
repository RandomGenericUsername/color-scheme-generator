"""Command-line interface for colorscheme generator using Typer."""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from colorscheme_generator import ColorSchemeGeneratorFactory
from colorscheme_generator.config.enums import Backend, ColorFormat
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
    OutputWriteError,
)
from colorscheme_generator.core.managers import OutputManager
from colorscheme_generator.core.types import (
    Color,
    ColorScheme,
    GeneratorConfig,
)

# Create Typer app
app = typer.Typer(
    name="colorscheme-gen",
    help="Generate color schemes from images using multiple backends",
    add_completion=False,
)

# Rich console for pretty output
console = Console()


def _ansi_color_block(color: Color, width: int = 8) -> str:
    """Create an ANSI colored block for terminal display.

    Args:
        color: Color to display
        width: Width of the color block in characters

    Returns:
        ANSI escape sequence for colored block
    """
    r, g, b = color.rgb
    # Use 24-bit true color ANSI escape codes
    return f"\033[48;2;{r};{g};{b}m{' ' * width}\033[0m"


def _load_colorscheme_from_json(path: Path) -> ColorScheme:
    """Load ColorScheme from JSON file.

    Args:
        path: Path to JSON file

    Returns:
        ColorScheme object

    Raises:
        ValueError: If file format is invalid
    """
    with path.open() as f:
        data = json.load(f)

    # Parse metadata
    metadata = data.get("metadata", {})
    source_image = Path(metadata.get("source_image", "unknown"))
    backend = metadata.get("backend", "unknown")

    # Parse special colors
    special = data.get("special", {})
    rgb_data = data.get("rgb", {})

    background = Color(
        hex=special["background"],
        rgb=tuple(rgb_data["background"]),  # type: ignore
    )
    foreground = Color(
        hex=special["foreground"],
        rgb=tuple(rgb_data["foreground"]),  # type: ignore
    )
    cursor = Color(
        hex=special["cursor"],
        rgb=tuple(rgb_data["cursor"]),  # type: ignore
    )

    # Parse colors - RGB data is in a nested array
    colors_dict = data.get("colors", {})
    rgb_colors = rgb_data.get("colors", [])

    colors = []
    for i in range(16):
        color_key = f"color{i}"
        if color_key not in colors_dict:
            raise ValueError(f"Missing {color_key} in colors")
        if i >= len(rgb_colors):
            raise ValueError(f"Missing RGB data for {color_key}")

        colors.append(
            Color(
                hex=colors_dict[color_key],
                rgb=tuple(rgb_colors[i]),  # type: ignore
            )
        )

    return ColorScheme(
        background=background,
        foreground=foreground,
        cursor=cursor,
        colors=colors,
        source_image=source_image,
        backend=backend,
    )


def _show_colorscheme(scheme: ColorScheme) -> None:
    """Display a color scheme with colored blocks.

    Args:
        scheme: ColorScheme to display
    """
    console.print("\n[bold]Color Scheme[/bold]")
    console.print(f"Source: {scheme.source_image}")
    console.print(f"Backend: {scheme.backend}\n")

    # Special colors
    console.print("[bold]Special Colors:[/bold]")
    console.print(
        f"Background: {_ansi_color_block(scheme.background)} {scheme.background.hex}"
    )
    console.print(
        f"Foreground: {_ansi_color_block(scheme.foreground)} {scheme.foreground.hex}"
    )
    console.print(
        f"Cursor:     {_ansi_color_block(scheme.cursor)} {scheme.cursor.hex}"
    )

    # Regular colors
    console.print("\n[bold]Colors:[/bold]")
    for i, color in enumerate(scheme.colors):
        console.print(
            f"Color {i:2d}:   {_ansi_color_block(color)} {color.hex}"
        )


def _find_last_colorscheme() -> Path | None:
    """Find the most recently generated colorscheme file.

    Looks in the default output directory from settings.

    Returns:
        Path to most recent colors.json file, or None if not found
    """
    try:
        settings = Settings.get()
        output_dir = settings.output.directory

        # Look for colors.json in output directory
        json_file = output_dir / "colors.json"
        if json_file.exists():
            return json_file

        return None
    except Exception:
        return None


@app.command()
def show(
    file: Annotated[
        Optional[Path],
        typer.Option(
            "--file",
            "-f",
            help="Path to color scheme JSON file",
            exists=True,
            dir_okay=False,
        ),
    ] = None,
    last: Annotated[
        bool,
        typer.Option(
            "--last",
            "-l",
            help="Show last generated color scheme",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Verbose output",
        ),
    ] = False,
) -> None:
    """Display a color scheme with colored blocks.

    Examples:
        colorscheme-gen show --file colors.json
        colorscheme-gen show --last
    """
    # Determine which file to use
    if last:
        colors_file = _find_last_colorscheme()
        if not colors_file:
            console.print(
                "[red]Error:[/red] No recent colorscheme found. "
                "Generate one first or specify a file."
            )
            raise typer.Exit(1)
        if verbose:
            console.print(f"Using last generated: {colors_file}")
    else:
        colors_file = file
        if not colors_file:
            console.print(
                "[red]Error:[/red] Either --file or --last must be specified"
            )
            raise typer.Exit(1)

    # Check file exists
    if not colors_file.exists():
        console.print(
            f"[red]Error:[/red] File not found: {colors_file}"
        )
        raise typer.Exit(1)

    # Load and display colorscheme
    try:
        scheme = _load_colorscheme_from_json(colors_file)
        _show_colorscheme(scheme)
    except Exception as e:
        console.print(
            f"[red]Error:[/red] Failed to load colorscheme: {e}"
        )
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def generate(
    image: Annotated[
        Optional[Path],
        typer.Argument(
            help="Path to source image",
            exists=True,
            dir_okay=False,
        ),
    ] = None,
    backend: Annotated[
        str,
        typer.Option(
            "--backend",
            "-b",
            help="Backend to use for color extraction",
        ),
    ] = "auto",
    formats: Annotated[
        Optional[list[str]],
        typer.Option(
            "--formats",
            "-f",
            help="Output formats (can specify multiple)",
        ),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            "-o",
            help="Output directory for generated files",
        ),
    ] = None,
    saturation: Annotated[
        Optional[float],
        typer.Option(
            "--saturation",
            "-s",
            help="Saturation multiplier (0.0=grayscale, 1.0=unchanged, 2.0=max)",
        ),
    ] = None,
    pywal_algorithm: Annotated[
        Optional[str],
        typer.Option(
            "--pywal-algorithm",
            help="Pywal color extraction algorithm",
        ),
    ] = None,
    wallust_backend: Annotated[
        Optional[str],
        typer.Option(
            "--wallust-backend",
            help="Wallust backend type",
        ),
    ] = None,
    custom_algorithm: Annotated[
        Optional[str],
        typer.Option(
            "--custom-algorithm",
            help="Custom backend algorithm",
        ),
    ] = None,
    custom_clusters: Annotated[
        Optional[int],
        typer.Option(
            "--custom-clusters",
            help="Number of color clusters for custom backend",
        ),
    ] = None,
    template_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--template-dir",
            help="Custom template directory",
            exists=True,
            dir_okay=True,
        ),
    ] = None,
    list_backends: Annotated[
        bool,
        typer.Option(
            "--list-backends",
            help="List available backends and exit",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Verbose output",
        ),
    ] = False,
) -> None:
    """Generate color scheme from an image.

    Examples:
        colorscheme-gen generate wallpaper.png
        colorscheme-gen generate wallpaper.png --backend pywal
        colorscheme-gen generate wallpaper.png -o ~/.config/colors -f json css
    """
    # Load settings
    try:
        settings = Settings.get()
    except Exception as e:
        console.print(
            f"[red]Error loading settings:[/red] {e}"
        )
        raise typer.Exit(1)

    # List backends if requested
    if list_backends:
        available = ColorSchemeGeneratorFactory.list_available(settings)
        console.print("[bold]Available backends:[/bold]")
        for backend_name in available:
            console.print(f"  • {backend_name}")
        return

    # Require image argument
    if not image:
        console.print(
            "[red]Error:[/red] image argument is required"
        )
        raise typer.Exit(1)

    # Create runtime config
    config_kwargs = {}

    if backend != "auto":
        try:
            config_kwargs["backend"] = Backend(backend)
        except ValueError:
            console.print(
                f"[red]Error:[/red] Invalid backend: {backend}"
            )
            console.print(
                "Valid backends: pywal, wallust, custom, auto"
            )
            raise typer.Exit(1)
    else:
        # When backend is "auto", use the default backend from settings
        config_kwargs["backend"] = Backend(settings.generation.default_backend)

    if output_dir:
        config_kwargs["output_dir"] = output_dir.expanduser()

    if formats:
        try:
            config_kwargs["formats"] = [ColorFormat(f) for f in formats]
        except ValueError as e:
            console.print(
                f"[red]Error:[/red] Invalid format: {e}"
            )
            raise typer.Exit(1)

    # Build overrides dictionary from CLI args
    overrides = {}

    if saturation is not None:
        overrides["saturation"] = saturation

    # Backend-specific overrides
    if pywal_algorithm:
        overrides["pywal_algorithm"] = pywal_algorithm
    if wallust_backend:
        overrides["wallust_backend"] = wallust_backend
    if custom_algorithm:
        overrides["custom_algorithm"] = custom_algorithm
    if custom_clusters:
        overrides["custom_clusters"] = custom_clusters

    # Template directory
    if template_dir:
        overrides["template_dir"] = template_dir

    # Create runtime config
    try:
        config = GeneratorConfig(**config_kwargs)
    except Exception as e:
        console.print(
            f"[red]Error creating config:[/red] {e}"
        )
        raise typer.Exit(1)

    # Apply overrides to settings
    if overrides:
        # Manually apply overrides to settings
        if "saturation" in overrides:
            settings.generation.saturation_adjustment = overrides["saturation"]
        if "pywal_algorithm" in overrides:
            settings.backends.pywal.backend_algorithm = overrides["pywal_algorithm"]
        if "wallust_backend" in overrides:
            settings.backends.wallust.backend_type = overrides["wallust_backend"]
        if "custom_algorithm" in overrides:
            settings.backends.custom.algorithm = overrides["custom_algorithm"]
        if "custom_clusters" in overrides:
            settings.backends.custom.n_clusters = overrides["custom_clusters"]
        if "template_dir" in overrides:
            settings.templates.directory = Path(overrides["template_dir"])

    if verbose:
        console.print(f"[dim]Image:[/dim] {image}")
        console.print(f"[dim]Backend:[/dim] {config.backend.value}")
        console.print(f"[dim]Output dir:[/dim] {config.output_dir}")
        formats_str = [f.value for f in config.formats] if config.formats else "default"
        console.print(f"[dim]Formats:[/dim] {formats_str}")

    # Create generator
    try:
        generator = ColorSchemeGeneratorFactory.create(
            backend=config.backend,
            settings=settings,
        )
    except BackendNotAvailableError as e:
        console.print(
            f"[red]Error:[/red] Backend not available: {e}"
        )
        console.print(
            "\nAvailable backends:"
        )
        available = ColorSchemeGeneratorFactory.list_available(settings)
        for backend_name in available:
            console.print(f"  • {backend_name}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(
            f"[red]Error creating generator:[/red] {e}"
        )
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)

    # Generate color scheme
    try:
        if verbose:
            console.print(f"\n[dim]Extracting colors from {image}...[/dim]")

        scheme = generator.generate(image, config)

        if verbose:
            console.print("[green]✓[/green] Color extraction successful")

    except InvalidImageError as e:
        console.print(
            f"[red]Error:[/red] Invalid image: {e}"
        )
        raise typer.Exit(1)
    except ColorExtractionError as e:
        console.print(
            f"[red]Error:[/red] Color extraction failed: {e}"
        )
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)
    except Exception as e:
        console.print(
            f"[red]Error:[/red] Unexpected error: {e}"
        )
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)

    # Write output files
    try:
        # Use default output directory if not specified
        output_dir = config.output_dir if config.output_dir else settings.output.directory
        # Use default formats if not specified
        formats = config.formats if config.formats else [ColorFormat(f) for f in settings.output.formats]

        if verbose:
            console.print(f"\n[dim]Writing output to: {output_dir}[/dim]")

        output_manager = OutputManager(settings)
        output_files = output_manager.write_outputs(
            scheme,
            output_dir,
            formats,
        )

        console.print("\n[bold green]✓ Generated files:[/bold green]")
        for format_name, file_path in output_files.items():
            console.print(f"  • {format_name}: {file_path}")

    except OutputWriteError as e:
        console.print(
            f"[red]Error writing output:[/red] {e}"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(
            f"[red]Error:[/red] Unexpected error writing output: {e}"
        )
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
