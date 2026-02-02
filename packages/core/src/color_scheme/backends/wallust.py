"""Wallust backend for color scheme generation."""

import json
import logging
import shutil
import subprocess  # nosec B404 - Required for external tool invocation
from pathlib import Path
from typing import Any

from color_scheme.config.config import AppConfig
from color_scheme.core.base import ColorSchemeGenerator
from color_scheme.core.exceptions import ColorExtractionError, InvalidImageError
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

    def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
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

        logger.info("Generating color scheme with wallust backend from %s", image_path)

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

            # Run wallust
            # Note: wallust doesn't output JSON to stdout,
            # it writes to ~/.cache/wallust/
            cmd = [
                "wallust",
                "run",
                str(image_path),
                "--backend",
                backend_type,
                "-s",  # Skip setting terminal sequences
                "-T",  # Skip templating
                "-q",  # Quiet mode
            ]

            logger.debug("Running wallust command: %s", " ".join(cmd))
            # Security: command hardcoded, image_path validated, shell=False, timeout set
            subprocess.run(  # nosec B603
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            logger.debug("Wallust completed successfully")

            # Find and read the palette file from cache
            cache_dir = Path.home() / ".cache" / "wallust"
            if not cache_dir.exists():
                raise ColorExtractionError(
                    self.backend_name, "Wallust cache directory not found"
                )

            # Find the subdirectory (wallust creates a hash-based subdir)
            subdirs = [d for d in cache_dir.iterdir() if d.is_dir()]
            if not subdirs:
                raise ColorExtractionError(
                    self.backend_name, "No cache subdirectory found"
                )

            # Use the most recently created subdirectory
            subdir = max(subdirs, key=lambda d: d.stat().st_mtime)

            # Find the palette file (usually the one with the longest name)
            palette_files = [
                f for f in subdir.iterdir() if f.is_file() and f.stat().st_size < 10000
            ]
            if not palette_files:
                raise ColorExtractionError(
                    self.backend_name, "No palette file found in cache"
                )

            # Use the file with the longest name (the full palette file)
            palette_file = max(palette_files, key=lambda f: len(f.name))

            logger.debug("Reading palette from: %s", palette_file)
            with palette_file.open() as f:
                colors_data = json.load(f)

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
                self.backend_name, f"Wallust failed: {e.stderr}"
            ) from e
        except subprocess.TimeoutExpired as e:
            logger.error("Wallust command timed out")
            raise ColorExtractionError(
                self.backend_name, "Wallust timed out after 30 seconds"
            ) from e
        except json.JSONDecodeError as e:
            logger.error("Failed to parse wallust output: %s", e)
            raise ColorExtractionError(
                self.backend_name, f"Invalid JSON output: {e}"
            ) from e
        except Exception as e:
            logger.error("Color extraction failed: %s", e)
            raise ColorExtractionError(self.backend_name, str(e)) from e

    def _parse_colors(self, data: dict[str, Any], image_path: Path) -> ColorScheme:
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
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
