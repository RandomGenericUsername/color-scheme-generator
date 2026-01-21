"""CLI entry point for color-scheme orchestrator.

This is a placeholder during Phase 1: Foundation.
Full orchestrator implementation will be added in later phases.
"""

import typer

app = typer.Typer(
    name="color-scheme",
    help="Color scheme generator with containerized backends (under development)",
    add_completion=False,
    no_args_is_help=True,
)


@app.command()
def version():
    """Show version information."""
    from color_scheme_orchestrator import __version__

    typer.echo(f"color-scheme-orchestrator version {__version__}")
    typer.echo("Phase 1: Foundation - Orchestrator under development")
    typer.echo("Container management features coming in later phases")


@app.command()
def generate():
    """Generate color scheme with containerized backend (coming in later phases)."""
    typer.echo("Command not yet implemented - coming in later phases")
    raise typer.Exit(1)


def main():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    main()
