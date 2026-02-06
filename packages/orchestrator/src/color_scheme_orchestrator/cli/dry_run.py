"""Dry-run reporting for orchestrator commands with container information."""

from typing import Any

from color_scheme.cli.dry_run import (
    DryRunReporter,
    GenerateDryRunReporter,
    ShowDryRunReporter,
)
from color_scheme_settings.models import ResolvedConfig
from rich.table import Table


class ContainerDryRunReporter(DryRunReporter):
    """Base dry-run reporter for container-based commands."""

    def __init__(
        self,
        command: str,
        resolved_config: ResolvedConfig,
        context: dict[str, Any] | None = None,
    ):
        """Initialize the container reporter.

        Args:
            command: Command name (e.g., "color-scheme generate")
            resolved_config: ResolvedConfig with all resolved values
            context: Additional context (image path, engine, etc.)
        """
        super().__init__(command, resolved_config, context)

    def print_container_info_section(self) -> None:
        """Print container-specific information."""
        engine = self._get_config_value("orchestrator.engine")

        table = Table(title="Container Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Container Engine", engine or "docker")
        table.add_row(
            "Image Prefix",
            self._get_config_value("orchestrator.image_prefix") or "color-scheme",
        )

        self.console.print(table)

    def _get_config_value(self, key: str) -> Any:
        """Get a configuration value safely."""
        resolved = self.config.get(key)
        if resolved:
            return resolved.value
        return None


class ContainerGenerateDryRunReporter(ContainerDryRunReporter, GenerateDryRunReporter):
    """Dry-run reporter for orchestrator generate command."""

    def run(self) -> None:
        """Execute complete dry-run report for container generate."""
        self.print_header()
        self.print_input_section()
        self.print_container_info_section()
        self.print_resolved_config_section()
        self.print_execution_plan()
        self.print_footer()


class ContainerShowDryRunReporter(ContainerDryRunReporter, ShowDryRunReporter):
    """Dry-run reporter for orchestrator show command."""

    def run(self) -> None:
        """Execute complete dry-run report for container show."""
        self.print_header()
        self.print_input_section()
        self.print_container_info_section()
        self.print_resolved_config_section()
        self.print_execution_plan()
        self.print_footer()


class InstallDryRunReporter(DryRunReporter):
    """Dry-run reporter for install command."""

    def run(self) -> None:
        """Execute complete dry-run report for install."""
        self.print_header()
        self.print_backend_info()
        self.print_resolved_config_section()
        self.print_build_plan()
        self.print_footer()

    def print_backend_info(self) -> None:
        """Print backend information."""
        backend = self.context.get("backend", "all")
        table = Table(title="Backend Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Backend(s) to Build", str(backend))

        engine = self._get_config_value("orchestrator.engine")
        table.add_row("Container Engine", engine or "docker")

        self.console.print(table)

    def print_build_plan(self) -> None:
        """Print build plan."""
        self.console.print("\n[bold]Build Plan:[/bold]")
        backend = self.context.get("backend", "all")
        engine = self._get_config_value("orchestrator.engine") or "docker"

        if backend == "all":
            backends = ["pywal", "wallust", "custom"]
        else:
            backends = [backend]

        for b in backends:
            image_name = f"color-scheme-{b}"
            self.console.print(f"\n  [cyan]Building:[/cyan] {image_name}")
            self.console.print(f"    • Engine: {engine}")
            self.console.print(f"    • Dockerfile: ./Dockerfile.{b}")
            self.console.print("    • Tags: latest, dev")

    def _get_config_value(self, key: str) -> Any:
        """Get a configuration value safely."""
        resolved = self.config.get(key)
        if resolved:
            return resolved.value
        return None


class UninstallDryRunReporter(DryRunReporter):
    """Dry-run reporter for uninstall command."""

    def run(self) -> None:
        """Execute complete dry-run report for uninstall."""
        self.print_header()
        self.print_backend_info()
        self.print_resolved_config_section()
        self.print_removal_plan()
        self.print_footer()

    def print_backend_info(self) -> None:
        """Print backend information."""
        backend = self.context.get("backend", "all")
        table = Table(title="Backend Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Backend(s) to Remove", str(backend))

        engine = self._get_config_value("orchestrator.engine")
        table.add_row("Container Engine", engine or "docker")

        self.console.print(table)

    def print_removal_plan(self) -> None:
        """Print removal plan."""
        self.console.print("\n[bold]Removal Plan:[/bold]")
        backend = self.context.get("backend", "all")
        engine = self._get_config_value("orchestrator.engine") or "docker"

        if backend == "all":
            backends = ["pywal", "wallust", "custom"]
        else:
            backends = [backend]

        for b in backends:
            image_name = f"color-scheme-{b}"
            self.console.print(f"\n  [cyan]Removing:[/cyan] {image_name}")
            self.console.print(f"    • Engine: {engine}")
            self.console.print(f"    • Command: {engine} rmi {image_name}:latest")

    def _get_config_value(self, key: str) -> Any:
        """Get a configuration value safely."""
        resolved = self.config.get(key)
        if resolved:
            return resolved.value
        return None
