"""CLI entry point for color-scheme.

This is a placeholder during Phase 1: Foundation.
Full CLI implementation will be added in Phase 2.
"""

import typer

app = typer.Typer(
    name="color-scheme",
    help="Color scheme generator (under development)",
    add_completion=False,
    no_args_is_help=True,
)


@app.command()
def version():
    """Show version information."""
    from color_scheme import __version__

    typer.echo(f"color-scheme-core version {__version__}")
    typer.echo("Phase 1: Foundation - CLI under development")


@app.command()
def generate():
    """Generate color scheme from an image (coming in Phase 2)."""
    typer.echo("Command not yet implemented - coming in Phase 2")
    raise typer.Exit(1)


def main():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    main()
