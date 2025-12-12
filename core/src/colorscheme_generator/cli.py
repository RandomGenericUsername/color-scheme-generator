"""Command-line interface for colorscheme generator."""

import argparse
import json
import sys
from pathlib import Path

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
    """Display colorscheme in terminal with colored blocks.

    Args:
        scheme: ColorScheme to display
    """
    # Print header
    print("\n" + "=" * 60)
    print("Color Scheme")
    print("=" * 60)
    print(f"Source:  {scheme.source_image}")
    print(f"Backend: {scheme.backend}")
    print("=" * 60)

    # Print special colors
    print("\nSpecial Colors:")
    print("-" * 60)

    special_colors = [
        ("background", scheme.background),
        ("foreground", scheme.foreground),
        ("cursor", scheme.cursor),
    ]

    for name, color in special_colors:
        block = _ansi_color_block(color)
        print(f"{name:12} {block}  {color.hex}")

    # Print terminal colors
    print("\nTerminal Colors:")
    print("-" * 60)

    for i, color in enumerate(scheme.colors):
        block = _ansi_color_block(color)
        print(f"color{i:<7} {block}  {color.hex}")

    print("=" * 60 + "\n")


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


def cmd_show(args: argparse.Namespace) -> int:
    """Show colorscheme with colored blocks in terminal.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Determine which file to show
    if args.last:
        colors_file = _find_last_colorscheme()
        if not colors_file:
            print(
                "Error: No recent colorscheme found. "
                "Generate one first or specify a file.",
                file=sys.stderr,
            )
            return 1
        if args.verbose:
            print(f"Using last generated: {colors_file}")
    else:
        colors_file = args.file
        if not colors_file:
            print(
                "Error: Either --file or --last must be specified",
                file=sys.stderr,
            )
            return 1

    # Check file exists
    if not colors_file.exists():
        print(f"Error: File not found: {colors_file}", file=sys.stderr)
        return 1

    # Load and display colorscheme
    try:
        scheme = _load_colorscheme_from_json(colors_file)
        _show_colorscheme(scheme)
        return 0
    except Exception as e:
        print(f"Error: Failed to load colorscheme: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate colorscheme from image.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """

    # Load settings
    try:
        settings = Settings.get()
    except Exception as e:
        print(f"Error loading settings: {e}", file=sys.stderr)
        return 1

    # List backends if requested
    if hasattr(args, "list_backends") and args.list_backends:
        available = ColorSchemeGeneratorFactory.list_available(settings)
        print("Available backends:")
        for backend in available:
            print(f"  - {backend}")
        return 0

    # Require image argument
    if not args.image:
        print("Error: image argument is required", file=sys.stderr)
        return 1

    # Create runtime config
    config_kwargs = {}

    if args.backend != "auto":
        config_kwargs["backend"] = Backend(args.backend)
    if args.output_dir:
        config_kwargs["output_dir"] = args.output_dir.expanduser()

    if args.formats:
        config_kwargs["formats"] = [ColorFormat(f) for f in args.formats]

    # Build overrides dictionary from CLI args
    overrides = {}

    if args.saturation is not None:
        overrides["generation.saturation_adjustment"] = args.saturation

    if args.pywal_algorithm is not None:
        overrides["backends.pywal.backend_algorithm"] = args.pywal_algorithm

    if args.wallust_backend is not None:
        overrides["backends.wallust.backend_type"] = args.wallust_backend

    if args.custom_algorithm is not None:
        overrides["backends.custom.algorithm"] = args.custom_algorithm

    if args.custom_clusters is not None:
        overrides["backends.custom.n_clusters"] = args.custom_clusters

    if args.template_dir is not None:
        overrides["templates.directory"] = args.template_dir.expanduser().resolve()

    # Apply overrides
    if overrides:
        from colorscheme_generator.cli_overrides import SettingsOverrider

        settings = SettingsOverrider.apply_overrides(settings, overrides)

    # Build overrides dictionary from CLI args
    overrides = {}

    if args.saturation is not None:
        overrides["generation.saturation_adjustment"] = args.saturation

    if args.pywal_algorithm is not None:
        overrides["backends.pywal.backend_algorithm"] = args.pywal_algorithm

    if args.wallust_backend is not None:
        overrides["backends.wallust.backend_type"] = args.wallust_backend

    if args.custom_algorithm is not None:
        overrides["backends.custom.algorithm"] = args.custom_algorithm

    if args.custom_clusters is not None:
        overrides["backends.custom.n_clusters"] = args.custom_clusters

    if args.template_dir is not None:
        overrides["templates.directory"] = args.template_dir.expanduser().resolve()

    # Apply overrides
    if overrides:
        from colorscheme_generator.cli_overrides import SettingsOverrider

        settings = SettingsOverrider.apply_overrides(settings, overrides)

    # Create generator config
    config = GeneratorConfig.from_settings(
settings, **config_kwargs)

    # Create backend
    try:
        if args.backend == "auto":
            if args.verbose:
                print("Auto-detecting backend...")
            generator = ColorSchemeGeneratorFactory.create_auto(settings)
        else:
            generator = ColorSchemeGeneratorFactory.create(
                Backend(args.backend), settings
            )

        if args.verbose:
            print(f"Using backend: {generator.backend_name}")
    except BackendNotAvailableError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Generate color scheme
    try:
        if args.verbose:
            print(f"Extracting colors from: {args.image}")

        scheme = generator.generate(args.image, config)

        if args.verbose:
            print(f"Background: {scheme.background.hex}")
            print(f"Foreground: {scheme.foreground.hex}")
            print(f"Cursor: {scheme.cursor.hex}")
            print(f"Colors: {len(scheme.colors)}")
    except InvalidImageError as e:
        print(f"Error: Invalid image: {e}", file=sys.stderr)
        return 1
    except ColorExtractionError as e:
        print(f"Error: Color extraction failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    # Write output files
    try:
        if args.verbose:
            print(f"Writing output to: {config.output_dir}")

        output_manager = OutputManager(settings)
        output_files = output_manager.write_outputs(
            scheme,
            config.output_dir,
            config.formats,
        )

        print("Generated files:")
        for format_name, file_path in output_files.items():
            print(f"  {format_name}: {file_path}")
    except OutputWriteError as e:
        print(f"Error: Failed to write output: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    # Display the color scheme
    _show_colorscheme(scheme)

    return 0


def main() -> int:
    """Main CLI entry point with subcommands.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate and display color schemes from images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Create subparsers
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=False,
    )

    # Generate command (default)
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate color scheme from image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with auto-detected backend
  colorscheme-gen generate wallpaper.png

  # Use specific backend
  colorscheme-gen generate wallpaper.png --backend pywal

  # Custom output directory and formats
  colorscheme-gen generate wallpaper.png -o ~/.config/colors -f json css

  # List available backends
  colorscheme-gen generate --list-backends
        """,
    )

    generate_parser.add_argument(
        "image",
        type=Path,
        nargs="?",
        help="Path to source image",
    )

    generate_parser.add_argument(
        "-b",
        "--backend",
        type=str,
        choices=["pywal", "wallust", "custom", "auto"],
        default="auto",
        help="Backend to use (default: auto-detect)",
    )

    generate_parser.add_argument(
        "-f",
        "--formats",
        nargs="+",
        choices=["json", "sh", "css", "gtk.css", "yaml", "toml", "sequences"],
        help="Output formats (default: from settings)",
    )


    generate_parser.add_argument(
        "--list-backends",
        action="store_true",
        help="List available backends and exit",
    )

    # Generation settings
    generate_parser.add_argument(
        "-s",
        "--saturation",
        type=float,
        metavar="FACTOR",
        help="Saturation multiplier (0.0=grayscale, 1.0=unchanged, 2.0=max, default: 1.0)",
    )

    # Pywal backend settings
    generate_parser.add_argument(
        "--pywal-algorithm",
        type=str,
        choices=["wal", "colorz", "colorthief", "haishoku", "schemer2"],
        help="Pywal color extraction algorithm (default: wal)",
    )

    # Wallust backend settings
    generate_parser.add_argument(
        "--wallust-backend",
        type=str,
        choices=["resized", "full", "thumb", "fastresize", "wal"],
        help="Wallust backend type (default: resized)",
    )

    # Custom backend settings
    generate_parser.add_argument(
        "--custom-algorithm",
        type=str,
        choices=["kmeans", "minibatch"],
        help="Custom backend algorithm (default: kmeans)",
    )

    generate_parser.add_argument(
        "--custom-clusters",
        type=int,
        metavar="N",
        help="Number of color clusters for custom backend (default: 16)",
    )

    # Template settings
    generate_parser.add_argument(
        "--template-dir",
        type=Path,
        metavar="DIR",
        help="Custom template directory (default: built-in templates)",
    )

    generate_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    # Show command
    show_parser = subparsers.add_parser(
        "show",
        help="Display color scheme with colored blocks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show specific color scheme file
  colorscheme-gen show colors.json
  colorscheme-gen show --file ~/.config/colors/colors.json

  # Show last generated color scheme
  colorscheme-gen show --last
        """,
    )

    show_parser.add_argument(
        "file",
        type=Path,
        nargs="?",
        help="Path to color scheme JSON file",
    )

    show_parser.add_argument(
        "--last",
        action="store_true",
        help="Show last generated color scheme",
    )

    show_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    # Check if first arg is a file path (backward compatibility)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        first_arg = sys.argv[1]
        # If it's not a known command, treat as generate
        if first_arg not in ["generate", "show"]:
            sys.argv.insert(1, "generate")

    # Parse arguments
    args = parser.parse_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate command
    if args.command == "generate":
        return cmd_generate(args)
    elif args.command == "show":
        return cmd_show(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
