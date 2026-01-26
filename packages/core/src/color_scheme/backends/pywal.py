"""Pywal backend for color scheme generation."""

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


class PywalGenerator(ColorSchemeGenerator):
    """Pywal backend for color extraction.

    Uses pywal (Python-based wallpaper color extractor) to generate colors.

    Attributes:
        settings: Application configuration
        cache_dir: Pywal cache directory
    """

    def __init__(self, settings: AppConfig):
        """Initialize PywalGenerator."""
        self.settings = settings
        # Pywal always writes to ~/.cache/wal/ (hardcoded)
        self.cache_dir = Path.home() / ".cache" / "wal"
        logger.debug("Initialized PywalGenerator with cache_dir=%s", self.cache_dir)

    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "pywal"

    def is_available(self) -> bool:
        """Check if pywal is available."""
        return shutil.which("wal") is not None

    def generate(
        self, image_path: Path, config: GeneratorConfig
    ) -> ColorScheme:
        """Generate color scheme using pywal.

        Args:
            image_path: Path to source image
            config: Runtime configuration

        Returns:
            ColorScheme object with extracted colors

        Raises:
            InvalidImageError: If image is invalid
            ColorExtractionError: If color extraction fails
            BackendNotAvailableError: If pywal is not available
        """
        self.ensure_available()

        logger.info(
            "Generating color scheme with pywal backend from %s", image_path
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
            # Run pywal
            backend_settings = config.get_backend_settings(self.settings)
            backend_arg = backend_settings.get("backend_algorithm", "wal")

            cmd = [
                "wal",
                "-i", str(image_path),
                "-n",  # Skip setting wallpaper
                "-q",  # Quiet mode
                "--backend", backend_arg,
            ]

            logger.debug("Running pywal command: %s", " ".join(cmd))
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            logger.debug("Pywal completed successfully")

            # Read colors from cache
            cache_file = self._get_cache_file()
            colors_data = self._read_cache_file(cache_file)

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
            logger.error("Pywal command failed: %s", e.stderr)
            raise ColorExtractionError(
                self.backend_name,
                f"Pywal failed: {e.stderr}"
            ) from e
        except subprocess.TimeoutExpired as e:
            logger.error("Pywal command timed out")
            raise ColorExtractionError(
                self.backend_name,
                "Pywal timed out after 30 seconds"
            ) from e
        except Exception as e:
            logger.error("Color extraction failed: %s", e)
            raise ColorExtractionError(self.backend_name, str(e)) from e

    def _get_cache_file(self) -> Path:
        """Get path to pywal cache file."""
        return self.cache_dir / "colors.json"

    def _read_cache_file(self, cache_file: Path) -> dict:
        """Read pywal cache file."""
        if not cache_file.exists():
            raise ColorExtractionError(
                self.backend_name,
                f"Cache file not found: {cache_file}"
            )

        try:
            with open(cache_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ColorExtractionError(
                self.backend_name,
                f"Invalid JSON in cache file: {e}"
            ) from e

    def _parse_colors(self, data: dict, image_path: Path) -> ColorScheme:
        """Parse colors from pywal cache data."""
        special = data.get("special", {})
        colors_dict = data.get("colors", {})

        # Extract special colors (normalize to uppercase)
        bg_hex = special.get("background", "#000000").upper()
        fg_hex = special.get("foreground", "#ffffff").upper()
        cursor_hex = special.get("cursor", "#ff0000").upper()

        # Extract 16 colors
        colors = []
        for i in range(16):
            color_hex = colors_dict.get(f"color{i}", "#000000").upper()
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
