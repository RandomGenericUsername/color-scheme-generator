"""OutputManager for writing color schemes to files."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import ColorFormat
from color_scheme.core.exceptions import OutputWriteError, TemplateRenderError
from color_scheme.core.types import ColorScheme


class OutputManager:
    """Manages writing color schemes to files using Jinja2 templates.

    This class handles:
    - Loading and rendering Jinja2 templates
    - Writing rendered content to output files
    - Special handling for binary formats (terminal sequences)
    - Directory creation and error handling

    Attributes:
        settings: Application configuration
        template_env: Jinja2 environment for template rendering
    """

    def __init__(self, settings: AppConfig):
        """Initialize OutputManager with settings.

        Args:
            settings: Application configuration containing template directory
        """
        self.settings = settings

        # Resolve template directory (handle relative paths from package root)
        template_dir = settings.templates.directory
        if not template_dir.is_absolute():
            # Get package root (color_scheme package directory)
            package_root = Path(__file__).parent.parent
            template_dir = package_root / template_dir

        # Setup Jinja2 environment with StrictUndefined
        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def write_outputs(
        self,
        color_scheme: ColorScheme,
        output_dir: Path,
        formats: list[ColorFormat],
    ) -> None:
        """Write color scheme to files in specified formats.

        Args:
            color_scheme: ColorScheme to write
            output_dir: Directory to write output files to
            formats: List of output formats to generate

        Raises:
            TemplateRenderError: If template rendering fails
            OutputWriteError: If file writing fails
        """
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write each format
        for fmt in formats:
            self._write_format(color_scheme, output_dir, fmt)

    def _write_format(
        self,
        color_scheme: ColorScheme,
        output_dir: Path,
        fmt: ColorFormat,
    ) -> None:
        """Write a single format.

        Args:
            color_scheme: ColorScheme to write
            output_dir: Directory to write to
            fmt: Format to write

        Raises:
            TemplateRenderError: If template rendering fails
            OutputWriteError: If file writing fails
        """
        # Render template
        content = self._render_template(color_scheme, fmt)

        # Determine output file path
        file_path = output_dir / f"colors.{fmt.value}"

        # Special handling for SEQUENCES format (binary)
        if fmt == ColorFormat.SEQUENCES:
            binary_content = self._convert_to_escape_sequences(content)
            self._write_binary_file(file_path, binary_content)
        else:
            self._write_file(file_path, content)

    def _render_template(
        self,
        color_scheme: ColorScheme,
        fmt: ColorFormat,
    ) -> str:
        """Render Jinja2 template for a format.

        Args:
            color_scheme: ColorScheme to render
            fmt: Format to render

        Returns:
            Rendered template content

        Raises:
            TemplateRenderError: If template rendering fails
        """
        template_name = f"colors.{fmt.value}.j2"

        try:
            template = self.template_env.get_template(template_name)
            content = template.render(
                source_image=str(color_scheme.source_image),
                backend=color_scheme.backend,
                generated_at=color_scheme.generated_at.isoformat(),
                background=color_scheme.background,
                foreground=color_scheme.foreground,
                cursor=color_scheme.cursor,
                colors=color_scheme.colors,
            )
            return content
        except TemplateNotFound as e:
            raise TemplateRenderError(
                template_name=template_name,
                reason="Template not found"
            ) from e
        except Exception as e:
            raise TemplateRenderError(
                template_name=template_name,
                reason=str(e)
            ) from e

    def _convert_to_escape_sequences(self, content: str) -> bytes:
        """Convert template placeholders to actual escape sequences.

        The template uses ] and \\ as placeholders. This converts them
        to actual ESC sequences for terminal consumption.

        Args:
            content: Template content with placeholders

        Returns:
            Binary content with actual escape sequences
        """
        # Replace ] with ESC] and \ with ESC\
        # ESC is \x1b (ASCII 27)
        content = content.replace("]", "\x1b]")
        content = content.replace("\\", "\x1b\\")
        return content.encode("utf-8")

    def _write_binary_file(self, file_path: Path, content: bytes) -> None:
        """Write binary content to file.

        Args:
            file_path: Path to write to
            content: Binary content

        Raises:
            OutputWriteError: If writing fails
        """
        try:
            file_path.write_bytes(content)
        except PermissionError as e:
            raise OutputWriteError(
                file_path=str(file_path),
                reason="Permission denied"
            ) from e
        except OSError as e:
            raise OutputWriteError(
                file_path=str(file_path),
                reason=str(e)
            ) from e

    def _write_file(self, file_path: Path, content: str) -> None:
        """Write text content to file.

        Args:
            file_path: Path to write to
            content: Text content

        Raises:
            OutputWriteError: If writing fails
        """
        try:
            file_path.write_text(content, encoding="utf-8")
        except PermissionError as e:
            raise OutputWriteError(
                file_path=str(file_path),
                reason="Permission denied"
            ) from e
        except OSError as e:
            raise OutputWriteError(
                file_path=str(file_path),
                reason=str(e)
            ) from e
