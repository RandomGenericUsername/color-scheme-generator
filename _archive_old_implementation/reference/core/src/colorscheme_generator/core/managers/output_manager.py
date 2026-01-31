"""Output manager for writing color schemes to files.

This module provides the OutputManager class that writes ColorScheme objects
to files using Jinja2 templates. This is separate from backends - backends
extract colors, OutputManager writes them to files.
"""

import logging
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound,
    UndefinedError,
)

from colorscheme_generator.config.config import AppConfig
from colorscheme_generator.config.enums import ColorFormat
from colorscheme_generator.core.exceptions import (
    OutputWriteError,
    TemplateRenderError,
)
from colorscheme_generator.core.types import ColorScheme

logger = logging.getLogger(__name__)


class OutputManager:
    """Manages writing ColorScheme objects to files.

    This class is responsible for:
    1. Loading Jinja2 templates
    2. Rendering templates with ColorScheme data
    3. Writing rendered content to files

    It's completely independent of backends - it just takes a ColorScheme
    object and writes it to files in various formats.

    Attributes:
        settings: Application configuration
        template_env: Jinja2 environment for template rendering

    Example:
        >>> from colorscheme_generator.config.settings import Settings
        >>> manager = OutputManager(Settings.get())
        >>> output_files = manager.write_outputs(
        ...     scheme=color_scheme,
        ...     output_dir=Path("~/.cache/colorscheme"),
        ...     formats=[ColorFormat.JSON, ColorFormat.CSS]
        ... )
    """

    def __init__(self, settings: AppConfig):
        """Initialize OutputManager.

        Args:
            settings: Application configuration
        """
        self.settings = settings

        # Set up Jinja2 environment
        template_dir = settings.templates.directory
        if not template_dir.is_absolute():
            # Relative to package root (templates are now inside the package)
            package_root = Path(__file__).parent.parent.parent
            template_dir = package_root / template_dir

        logger.debug("Template directory: %s", template_dir)

        # Import Jinja2 undefined classes
        from jinja2 import StrictUndefined

        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        )
        logger.debug("Initialized OutputManager with Jinja2 environment")

    def write_outputs(
        self,
        scheme: ColorScheme,
        output_dir: Path,
        formats: list[ColorFormat],
    ) -> dict[str, Path]:
        """Write ColorScheme to files in specified formats.

        Args:
            scheme: ColorScheme object to write
            output_dir: Directory to write files to
            formats: List of output formats to generate

        Returns:
            Dictionary mapping format name to output file path

        Raises:
            TemplateRenderError: If template rendering fails
            OutputWriteError: If writing file fails

        Example:
            >>> output_files = manager.write_outputs(
            ...     scheme=color_scheme,
            ...     output_dir=Path("~/.cache/colorscheme"),
            ...     formats=[ColorFormat.JSON, ColorFormat.CSS]
            ... )
            >>> print(output_files)
            {
                'json': PosixPath('/home/user/.cache/colorscheme/colors.json'),
                'css': PosixPath('/home/user/.cache/colorscheme/colors.css')
            }
        """
        logger.info("Writing color scheme outputs to %s", output_dir)
        logger.debug("Output formats: %s", [f.value for f in formats])

        # Ensure output directory exists
        output_dir = output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Resolved output directory: %s", output_dir)

        output_files = {}

        for fmt in formats:
            try:
                # Render template
                logger.debug("Rendering template for format: %s", fmt.value)
                content = self._render_template(scheme, fmt)

                # Write to file
                output_path = output_dir / f"colors.{fmt.value}"

                # Special handling for sequences format (binary file)
                if fmt == ColorFormat.SEQUENCES:
                    binary_content = self._convert_to_escape_sequences(content)
                    self._write_binary_file(output_path, binary_content)
                else:
                    # Text file (existing behavior)
                    self._write_file(output_path, content)

                output_files[fmt.value] = output_path
                logger.debug("Wrote %s", output_path)

            except (TemplateRenderError, OutputWriteError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                logger.error("Unexpected error writing %s: %s", fmt.value, e)
                # Wrap unexpected errors
                raise OutputWriteError(
                    str(output_dir / f"colors.{fmt.value}"),
                    f"Unexpected error: {e}",
                ) from e

        logger.info("Successfully wrote %d output files", len(output_files))
        return output_files

    def _render_template(self, scheme: ColorScheme, fmt: ColorFormat) -> str:
        """Render template for given format.

        Args:
            scheme: ColorScheme object
            fmt: Output format

        Returns:
            Rendered template content

        Raises:
            TemplateRenderError: If rendering fails
        """
        template_name = f"colors.{fmt.value}.j2"

        try:
            template = self.template_env.get_template(template_name)
            logger.debug("Loaded template: %s", template_name)
        except TemplateNotFound:
            logger.error(
                "Template not found: %s in %s",
                template_name,
                self.settings.templates.directory,
            )
            raise TemplateRenderError(
                template_name,
                f"Template not found in {self.settings.templates.directory}",
            ) from None

        # Prepare template context
        context = {
            "background": scheme.background,
            "foreground": scheme.foreground,
            "cursor": scheme.cursor,
            "colors": scheme.colors,
            "source_image": str(scheme.source_image),
            "backend": scheme.backend,
            "generated_at": scheme.generated_at.isoformat(),
        }

        try:
            rendered = template.render(**context)
            logger.debug("Successfully rendered template: %s", template_name)
            return rendered
        except UndefinedError as e:
            logger.error(
                "Undefined variable in template %s: %s", template_name, e
            )
            raise TemplateRenderError(
                template_name, f"Undefined variable: {e}"
            ) from e
        except Exception as e:
            logger.error("Template render error in %s: %s", template_name, e)
            raise TemplateRenderError(template_name, str(e)) from e

    def _convert_to_escape_sequences(self, content: str) -> bytes:
        """Convert template output to actual ANSI escape sequences.

        Replaces placeholder characters with actual escape codes:
        - ']' → ESC + ']' (OSC start)
        - '\\' → ESC (sequence terminator)

        Args:
            content: Template-rendered content with placeholders

        Returns:
            Binary content with actual escape sequences

        Example:
            >>> content = "]4;0;#282A23\\]10;#F8F8F8\\"
            >>> binary = self._convert_to_escape_sequences(content)
            >>> assert b'\\x1b]4;0;#282A23' in binary
        """
        # Replace ] with ESC + ]
        content = content.replace("]", "\x1b]")
        # Replace \ with ESC
        content = content.replace("\\", "\x1b\\")

        return content.encode("utf-8")

    def _write_binary_file(self, path: Path, content: bytes) -> None:
        """Write binary content to file.

        Args:
            path: File path
            content: Binary content to write

        Raises:
            OutputWriteError: If writing fails

        Example:
            >>> binary_content = b'\\x1b]4;0;#282A23\\x1b\\\\'
            >>> path = Path("colors.sequences")
            >>> self._write_binary_file(path, binary_content)
        """
        try:
            path.write_bytes(content)
        except PermissionError:
            raise OutputWriteError(str(path), "Permission denied") from None
        except OSError as e:
            raise OutputWriteError(str(path), str(e)) from e

    def _write_file(self, path: Path, content: str) -> None:
        """Write content to file.

        Args:
            path: File path
            content: Content to write

        Raises:
            OutputWriteError: If writing fails
        """
        try:
            path.write_text(content)
        except PermissionError:
            raise OutputWriteError(str(path), "Permission denied") from None
        except OSError as e:
            raise OutputWriteError(str(path), str(e)) from e
