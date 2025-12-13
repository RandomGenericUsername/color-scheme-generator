"""Main CLI entry point for color-scheme orchestrator."""

import argparse
import logging
import sys
from typing import Optional

from color_scheme.commands import (
    generate_command,
    install_command,
    show_command,
    status_command,
)
from color_scheme.config.config import OrchestratorConfig
from color_scheme.logging import LoggingConfig, setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="color-scheme",
        description="Container orchestrator for color-scheme-generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  color-scheme install
  color-scheme generate -i image.jpg --backend pywal
  color-scheme show backends
  color-scheme status

Environment:
  COLOR_SCHEME_RUNTIME      Set container runtime (docker/podman)
  COLOR_SCHEME_OUTPUT_DIR   Set output directory
  COLOR_SCHEME_CONFIG_DIR   Set config directory
  COLOR_SCHEME_VERBOSE      Enable verbose output
  COLOR_SCHEME_DEBUG        Enable debug output
        """,
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to execute",
        required=True,
    )

    # install command
    install_parser = subparsers.add_parser(
        "install",
        help="Install and initialize backends",
    )
    install_parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild of images",
    )

    # generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a color scheme",
        description=(
            "Generate a color scheme using the specified backend. "
            "All unrecognized arguments are passed to the backend."
        ),
    )
    # Accept remaining arguments for passthrough
    generate_parser.add_argument(
        "passthrough",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to the core tool",
    )

    # show command
    show_parser = subparsers.add_parser(
        "show",
        help="Show information",
    )
    show_parser.add_argument(
        "resource",
        nargs="?",
        choices=["backends", "config", "help"],
        default="backends",
        help="What to show",
    )

    # status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show system status",
    )

    # Global options (added to all subparsers)
    all_subparsers = [
        install_parser, generate_parser, show_parser, status_parser
    ]
    for subparser in all_subparsers:
        subparser.add_argument(
            "--runtime",
            help="Container runtime to use (docker/podman)",
        )
        subparser.add_argument(
            "--output-dir",
            help="Output directory",
        )
        subparser.add_argument(
            "--config-dir",
            help="Configuration directory",
        )
        subparser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Verbose output",
        )
        subparser.add_argument(
            "--debug", "-d",
            action="store_true",
            help="Debug output",
        )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point.

    Args:
        argv: Command line arguments (for testing). Defaults to sys.argv[1:]

    Returns:
        Exit code
    """
    if argv is None:
        argv = sys.argv[1:]

    # Parse arguments
    parser = create_parser()

    try:
        # Try to parse with all args as-is
        args = parser.parse_args(argv)
    except SystemExit:
        # If parsing fails, might be due to generate command with
        # passthrough args. Try again with special handling.
        if argv and argv[0] == "generate":
            # Pass through remaining args for generate command
            argv_modified = argv[:2] + [argv[1]] + argv[2:]
            try:
                args = parser.parse_args(argv_modified)
            except Exception:
                parser.print_help()
                return 1
        else:
            return 1

    # Set up logging with Rich
    verbose = getattr(args, "verbose", False)
    debug = getattr(args, "debug", False)

    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    log_config = LoggingConfig(
        level=level,
        show_time=True,
        show_path=debug,
        rich_tracebacks=True,
    )
    setup_logging(log_config)

    # Create configuration
    config = OrchestratorConfig.default()

    # Override with CLI arguments
    if getattr(args, "runtime", None):
        config.runtime = args.runtime
    if getattr(args, "output_dir", None):
        config.output_dir = args.output_dir
    if getattr(args, "config_dir", None):
        config.config_dir = args.config_dir
    if getattr(args, "verbose", False):
        config.verbose = True
    if getattr(args, "debug", False):
        config.debug = True

    # Execute command
    try:
        if args.command == "install":
            force_rebuild = getattr(args, "force_rebuild", False)
            return install_command(
                config=config,
                force_rebuild=force_rebuild,
            )

        elif args.command == "generate":
            # Get passthrough arguments
            passthrough_args = getattr(args, "passthrough", [])
            return generate_command(
                args=passthrough_args,
                config=config,
            )

        elif args.command == "show":
            resource = getattr(args, "resource", None)
            return show_command(
                resource=resource,
                config=config,
            )

        elif args.command == "status":
            return status_command(config=config)

        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if config.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
