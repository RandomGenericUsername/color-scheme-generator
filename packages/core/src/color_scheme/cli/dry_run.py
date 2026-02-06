"""Dry-run reporting for CLI commands.

Provides DryRunReporter and command-specific reporters that format
and display configuration resolution results without executing.
"""

from pathlib import Path
from typing import Any

from color_scheme_settings.models import ResolvedConfig
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class DryRunReporter:
    """Base dry-run reporter for displaying resolved configuration.

    Formats and displays the configuration sources, resolved values,
    and execution plan for a dry-run.
    """

    def __init__(
        self,
        command: str,
        resolved_config: ResolvedConfig,
        context: dict[str, Any] | None = None,
    ):
        """Initialize the reporter.

        Args:
            command: Command name (e.g., "color-scheme-core generate")
            resolved_config: ResolvedConfig with all resolved values
            context: Additional context (image path, etc.)
        """
        self.command = command
        self.config = resolved_config
        self.context = context or {}
        self.console = Console()

    def run(self) -> None:
        """Execute complete dry-run report."""
        self.print_header()
        self.print_resolved_config_section()
        self.print_footer()

    def print_header(self) -> None:
        """Print command header with decoration."""
        header_text = f"DRY-RUN: {self.command}"
        self.console.print(Panel(header_text, style="bold cyan"))

    def print_resolved_config_section(self) -> None:
        """Print resolved configuration with sources."""
        table = Table(title="Resolved Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Source", style="yellow")

        for key, resolved in sorted(self.config.items()):
            source_name = resolved.source.value
            if resolved.overrides:
                source_name += " ⚠"
            table.add_row(key, str(resolved.value), source_name)

        self.console.print(table)

        # Show overrides if any
        overrides = [
            (key, resolved)
            for key, resolved in self.config.items()
            if resolved.overrides
        ]
        if overrides:
            self.print_overrides_section(overrides)

    def print_overrides_section(
        self,
        overrides: list[tuple[str, Any]],
    ) -> None:
        """Print information about overridden settings."""
        self.console.print("\n[yellow]⚠ Overridden Settings:[/yellow]")
        for key, resolved in overrides:
            self.console.print(f"\n  {key}:")
            self.console.print(f"    Final value: {resolved.value}")
            self.console.print(f"    From: {resolved.source.value}")
            for override_source, override_value in resolved.overrides:
                self.console.print(
                    f"    Overridden: {override_source.value} = {override_value}"
                )

    def print_footer(self) -> None:
        """Print footer message."""
        self.console.print(
            "\n[cyan]This is a dry-run.[/cyan] "
            "[green]No files were created or modified.[/green]"
        )


class GenerateDryRunReporter(DryRunReporter):
    """Dry-run reporter for generate command."""

    def run(self) -> None:
        """Execute complete dry-run report for generate."""
        self.print_header()
        self.print_input_section()
        self.print_resolved_config_section()
        self.print_execution_plan()
        self.print_footer()

    def print_input_section(self) -> None:
        """Print input validation information."""
        if "image_path" not in self.context:
            return

        image_path = self.context["image_path"]
        table = Table(title="Input Files")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="green")

        exists = Path(image_path).exists()
        status = "✓ Found" if exists else "✗ Not found"
        table.add_row(str(image_path), status)

        self.console.print(table)

    def print_execution_plan(self) -> None:
        """Print execution plan for generate command."""
        backend = self._get_config_value("generation.default_backend")
        output_dir = self._get_config_value("output.directory")
        formats = self._get_config_value("output.formats")
        saturation = self._get_config_value("generation.saturation_adjustment")

        plan_lines = [
            "[cyan]Step 1: Load Image[/cyan]",
            f"  • Path: {self.context.get('image_path', 'N/A')}",
            "",
            "[cyan]Step 2: Extract Colors[/cyan]",
            f"  • Backend: {backend}",
            "",
        ]

        if saturation and saturation != 1.0:
            percentage = (saturation - 1.0) * 100
            direction = "increase" if percentage > 0 else "decrease"
            plan_lines.extend(
                [
                    "[cyan]Step 3: Apply Adjustments[/cyan]",
                    f"  • Saturation: {saturation}x "
                    f"({direction} by {abs(percentage):.0f}%)",
                    "",
                ]
            )

        plan_lines.extend(
            [
                "[cyan]Step 4: Render Templates[/cyan]",
                "  • Templates to render:",
            ]
        )
        if formats:
            for fmt in formats:
                plan_lines.append(f"    - colors.{fmt}")

        plan_lines.extend(
            [
                "",
                "[cyan]Step 5: Write Files[/cyan]",
                f"  • Output directory: {output_dir}",
                "  • Files to create:",
            ]
        )
        if formats:
            for fmt in formats:
                plan_lines.append(f"    - {Path(output_dir) / f'colors.{fmt}'}")

        self.console.print("\n[bold]Execution Plan:[/bold]")
        for line in plan_lines:
            self.console.print(line)

    def _get_config_value(self, key: str) -> Any:
        """Get a configuration value safely."""
        resolved = self.config.get(key)
        if resolved:
            return resolved.value
        return None


class ShowDryRunReporter(DryRunReporter):
    """Dry-run reporter for show command."""

    def run(self) -> None:
        """Execute complete dry-run report for show."""
        self.print_header()
        self.print_input_section()
        self.print_resolved_config_section()
        self.print_execution_plan()
        self.print_footer()

    def print_input_section(self) -> None:
        """Print input validation information."""
        if "image_path" not in self.context:
            return

        image_path = self.context["image_path"]
        table = Table(title="Input Files")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="green")

        exists = Path(image_path).exists()
        status = "✓ Found" if exists else "✗ Not found"
        table.add_row(str(image_path), status)

        self.console.print(table)

    def print_execution_plan(self) -> None:
        """Print execution plan for show command."""
        backend = self._get_config_value("generation.default_backend")
        saturation = self._get_config_value("generation.saturation_adjustment")

        plan_lines = [
            "[cyan]Step 1: Load Image[/cyan]",
            f"  • Path: {self.context.get('image_path', 'N/A')}",
            "",
            "[cyan]Step 2: Extract Colors[/cyan]",
            f"  • Backend: {backend}",
            "",
        ]

        if saturation and saturation != 1.0:
            percentage = (saturation - 1.0) * 100
            direction = "increase" if percentage > 0 else "decrease"
            plan_lines.extend(
                [
                    "[cyan]Step 3: Apply Adjustments[/cyan]",
                    f"  • Saturation: {saturation}x "
                    f"({direction} by {abs(percentage):.0f}%)",
                    "",
                ]
            )

        plan_lines.extend(
            [
                "[cyan]Step 4: Display in Terminal[/cyan]",
                "  • Output format: Terminal colors",
                "  • Color count: 16 + background/foreground/cursor",
            ]
        )

        self.console.print("\n[bold]Execution Plan:[/bold]")
        for line in plan_lines:
            self.console.print(line)

    def _get_config_value(self, key: str) -> Any:
        """Get a configuration value safely."""
        resolved = self.config.get(key)
        if resolved:
            return resolved.value
        return None
