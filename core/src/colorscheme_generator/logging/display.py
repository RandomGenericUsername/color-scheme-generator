"""Rich display for color schemes.

Provides beautiful terminal output for generated color schemes.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from colorscheme_generator.core.types import Color, ColorScheme


class ColorSchemeDisplay:
    """Display color schemes with rich formatting."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize display.

        Args:
            console: Rich console to use (creates new if not provided)
        """
        self.console = console or Console()

    def _color_block(self, color: Color, width: int = 2) -> Text:
        """Create a colored block using Rich Text.

        Args:
            color: Color to display
            width: Width of block in characters

        Returns:
            Rich Text with colored background
        """
        text = Text(" " * width)
        text.stylize(f"on {color.hex}")
        return text

    def _color_row(self, name: str, color: Color, name_width: int = 12) -> Text:
        """Create a row with color name, block, and hex value.

        Args:
            name: Color name (e.g., "background", "color0")
            color: Color to display
            name_width: Width for name column

        Returns:
            Formatted text line
        """
        line = Text()
        line.append(f"{name:<{name_width}}", style="dim")
        line.append(" ")
        line.append(self._color_block(color, width=8))
        line.append(f"  {color.hex}", style="bold")
        return line

    def show_summary(
        self,
        scheme: ColorScheme,
        elapsed_time: Optional[float] = None,
        output_files: Optional[dict[str, Path]] = None,
    ) -> None:
        """Display a complete color scheme summary.

        Args:
            scheme: Generated color scheme
            elapsed_time: Time taken to generate (seconds)
            output_files: Dictionary of format -> file path
        """
        # Header panel
        header_lines = []
        header_lines.append(f"🖼️  [bold]Wallpaper:[/bold] {scheme.source_image.name}")
        header_lines.append(f"📁 [bold]Path:[/bold] {scheme.source_image}")
        header_lines.append(f"🔧 [bold]Backend:[/bold] {scheme.backend}")
        if elapsed_time is not None:
            header_lines.append(f"⏱️  [bold]Time:[/bold] {elapsed_time:.2f}s")

        self.console.print(Panel(
            "\n".join(header_lines),
            title="[bold green]Color Scheme Generated[/bold green]",
            border_style="green",
        ))

        # Special colors table
        special_table = Table(
            show_header=False,
            box=None,
            padding=(0, 2),
        )
        special_table.add_column("Name", style="dim", width=12)
        special_table.add_column("Color", width=10)
        special_table.add_column("Hex", style="bold")

        for name, color in [
            ("background", scheme.background),
            ("foreground", scheme.foreground),
            ("cursor", scheme.cursor),
        ]:
            special_table.add_row(
                name,
                self._color_block(color, width=8),
                color.hex,
            )

        self.console.print(Panel(
            special_table,
            title="[bold]Special Colors[/bold]",
            border_style="blue",
        ))

        # Color palette (0-15) in two columns
        palette_table = Table(
            show_header=False,
            box=None,
            padding=(0, 1),
        )
        # Left column (0-7)
        palette_table.add_column("N1", width=3, style="dim")
        palette_table.add_column("C1", width=10)
        palette_table.add_column("H1", width=9)
        # Spacer
        palette_table.add_column("", width=4)
        # Right column (8-15)
        palette_table.add_column("N2", width=3, style="dim")
        palette_table.add_column("C2", width=10)
        palette_table.add_column("H2", width=9)

        for i in range(8):
            left_color = scheme.colors[i]
            right_color = scheme.colors[i + 8]
            palette_table.add_row(
                f"{i}",
                self._color_block(left_color, width=8),
                left_color.hex,
                "",
                f"{i + 8}",
                self._color_block(right_color, width=8),
                right_color.hex,
            )

        self.console.print(Panel(
            palette_table,
            title="[bold]Palette (0-15)[/bold]",
            border_style="blue",
        ))

        # Output files
        if output_files:
            self.console.print(
                f"\n[bold green]✅ Output files written to:[/bold green] "
                f"{list(output_files.values())[0].parent}"
            )
            for fmt, path in output_files.items():
                self.console.print(f"   • {path.name}")

