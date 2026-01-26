"""Wallust backend for color scheme generation."""

import json
import logging
import shutil
import subprocess
from pathlib import Path

from color_scheme.config.config import AppConfig
from color_scheme.core.base import ColorSchemeGenerator
from color_scheme.core.exceptions import (
    ColorExtractionError,
    InvalidImageError,
)
from color_scheme.core.types import Color, ColorScheme, GeneratorConfig

logger = logging.getLogger(__name__)


class WallustGenerator(ColorSchemeGenerator):
    """Wallust backend for color extraction.

    Uses wallust (Rust-based color extractor) to generate colors.

    Attributes:
        settings: Application configuration
    """

    def __init__(self, settings: AppConfig):
        """Initialize WallustGenerator."""
        self.settings = settings
        logger.debug("Initialized WallustGenerator")

    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "wallust"

    def is_available(self) -> bool:
        """Check if wallust is available."""
        return shutil.which("wallust") is not None

    def generate(
        self, image_path: Path, config: GeneratorConfig
    ) -> ColorScheme:
        """Generate color scheme using wallust.

        Args:
            image_path: Path to source image
            config: Runtime configuration

        Returns:
            ColorScheme object with extracted colors

        Raises:
            InvalidImageError: If image is invalid
            ColorExtractionError: If color extraction fails
            BackendNotAvailableError: If wallust is not available
        """
        self.ensure_available()

        logger.info(
            "Generating color scheme with wallust backend from %s", image_path
        )

        # Validate image
        image_path = image_path.expanduser().resolve()

        if not image_path.exists():
            logger.error("Image file does not exist: %s", image_path)
            raise InvalidImageError(str(image_path), "File does not exist")

        if not image_path.is_file():
            logger.error("Path is not a file: %s", image_path)
            raise InvalidImageError(str(image_path), "Not a file")

        try:
            # Get backend settings
            backend_settings = config.get_backend_settings(self.settings)
            backend_type = backend_settings.get("backend_type", "resized")

            # Run wallust with JSON output
            cmd = [
                "wallust",
                "run",
                str(image_path),
                "--backend", backend_type,
                "-s",  # Skip generating templates
                "-j",  # JSON output
            ]

            logger.debug("Running wallust command: %s", " ".join(cmd))
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            logger.debug("Wallust completed successfully")

            # Parse JSON output
            colors_data = json.loads(result.stdout)

            # Parse colors
            scheme = self._parse_colors(colors_data, image_path)

            # Apply saturation adjustment if specified
            saturation = config.saturation_adjustment or 1.0
            if saturation != 1.0:
                scheme.colors = [c.adjust_saturation(saturation) for c in scheme.colors]
                scheme.background = scheme.background.adjust_saturation(saturation)
                scheme.foreground = scheme.foreground.adjust_saturation(saturation)
                scheme.cursor = scheme.cursor.adjust_saturation(saturation)
                logger.debug("Applied saturation adjustment: %.2f", saturation)

            logger.info("Successfully generated color scheme")
            return scheme

        except subprocess.CalledProcessError as e:
            logger.error("Wallust command failed: %s", e.stderr)
            raise ColorExtractionError(
                self.backend_name,
                f"Wallust failed: {e.stderr}"
            ) from e
        except subprocess.TimeoutExpired:
            logger.error("Wallust command timed out")
            raise ColorExtractionError(
                self.backend_name,
                "Wallust timed out after 30 seconds"
            )
        except json.JSONDecodeError as e:
            logger.error("Failed to parse wallust output: %s", e)
            raise ColorExtractionError(
                self.backend_name,
                f"Invalid JSON output: {e}"
            ) from e
        except Exception as e:
            logger.error("Color extraction failed: %s", e)
            raise ColorExtractionError(self.backend_name, str(e)) from e

    def _parse_colors(self, data: dict, image_path: Path) -> ColorScheme:
        """Parse colors from wallust JSON output."""
        # Extract special colors (normalize to uppercase)
        bg_hex = data.get("background", "#000000").upper()
        fg_hex = data.get("foreground", "#ffffff").upper()
        cursor_hex = data.get("cursor", "#ff0000").upper()

        # Extract 16 colors
        colors = []
        for i in range(16):
            color_hex = data.get(f"color{i}", "#000000").upper()
            rgb = self._hex_to_rgb(color_hex)
            colors.append(Color(hex=color_hex, rgb=rgb))

        return ColorScheme(
            background=Color(hex=bg_hex, rgb=self._hex_to_rgb(bg_hex)),
            foreground=Color(hex=fg_hex, rgb=self._hex_to_rgb(fg_hex)),
            cursor=Color(hex=cursor_hex, rgb=self._hex_to_rgb(cursor_hex)),
            colors=colors,
            source_image=image_path,
            backend=self.backend_name,
        )

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
