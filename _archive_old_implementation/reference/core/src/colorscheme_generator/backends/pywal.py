"""Pywal backend for color scheme generation.

This backend uses pywal (Python library or CLI) to extract colors from images.
Pywal always writes to ~/.cache/wal/, which we read from.
"""

import json
import logging
import shutil
import subprocess
from pathlib import Path

from colorscheme_generator.config.config import AppConfig
from colorscheme_generator.core.base import ColorSchemeGenerator
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
)
from colorscheme_generator.core.types import (
    Color,
    ColorScheme,
    GeneratorConfig,
)

logger = logging.getLogger(__name__)


class PywalGenerator(ColorSchemeGenerator):
    """Pywal backend for color extraction.

    Uses pywal to generate colors. Pywal writes to a fixed location
    (~/.cache/wal/), which we read from to extract the ColorScheme.

    Attributes:
        settings: Application configuration
        cache_dir: Directory where pywal writes its output
        use_library: Whether to use pywal as library vs CLI
    """

    def __init__(self, settings: AppConfig):
        """Initialize PywalGenerator.

        Args:
            settings: Application configuration
        """
        self.settings = settings
        # Pywal hardcodes this location - cannot be configured
        self.cache_dir = Path.home() / ".cache" / "wal"
        logger.debug(
            "Initialized PywalGenerator with cache_dir=%s, algorithm=%s",
            self.cache_dir,
            settings.backends.pywal.backend_algorithm,
        )

    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "pywal"

    def is_available(self) -> bool:
        """Check if pywal CLI is available.

        Returns:
            True if pywal CLI is available
        """
        available = shutil.which("wal") is not None
        logger.debug("Pywal availability check: %s", available)
        return available

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
            BackendNotAvailableError: If pywal is not available
            InvalidImageError: If image is invalid
            ColorExtractionError: If color extraction fails
        """
        logger.info("Generating color scheme with pywal from %s", image_path)

        # Ensure backend is available
        self.ensure_available()

        # Validate image
        image_path = image_path.expanduser().resolve()
        logger.debug("Resolved image path: %s", image_path)
        if not image_path.exists():
            logger.error("Image file does not exist: %s", image_path)
            raise InvalidImageError(str(image_path), "File does not exist")
        if not image_path.is_file():
            logger.error("Path is not a file: %s", image_path)
            raise InvalidImageError(str(image_path), "Not a file")

        # Run pywal CLI
        try:
            self._run_pywal_cli(image_path, config)
        except Exception as e:
            logger.error("Failed to run pywal: %s", e)
            raise ColorExtractionError(
                f"Failed to run pywal on {image_path}: {e}"
            ) from e

        # Read colors from pywal's output
        colors_file = self.cache_dir / "colors.json"
        logger.debug("Reading pywal output from %s", colors_file)
        if not colors_file.exists():
            logger.error("Pywal output file not found: %s", colors_file)
            raise ColorExtractionError(
                f"Pywal output file not found: {colors_file}"
            )

        try:
            with Path(colors_file).open() as f:
                pywal_colors = json.load(f)
            logger.debug("Successfully parsed pywal JSON output")
        except Exception as e:
            logger.error("Failed to read pywal output: %s", e)
            raise ColorExtractionError(
                f"Failed to read pywal output: {e}"
            ) from e

        # Convert to ColorScheme
        scheme = self._parse_pywal_output(pywal_colors, image_path)
        logger.info("Successfully generated color scheme with pywal")
        return scheme

    def _run_pywal_cli(
        self,
        image_path: Path,
        config: GeneratorConfig,  # noqa: ARG002
    ) -> None:
        """Run pywal as CLI command.

        Args:
            image_path: Path to source image
            config: Runtime configuration (reserved for future use)
        """
        cmd = ["wal", "-i", str(image_path), "-n"]

        # Add backend algorithm selection
        backend_algorithm = self.settings.backends.pywal.backend_algorithm
        if backend_algorithm != "wal":  # wal is the default
            cmd.extend(["--backend", backend_algorithm])

        logger.debug("Running pywal command: %s", " ".join(cmd))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug("Pywal stdout: %s", result.stdout)
            if result.stderr:
                logger.debug("Pywal stderr: %s", result.stderr)
        except subprocess.CalledProcessError as e:
            logger.error(
                "Pywal command failed with code %d: %s", e.returncode, e.stderr
            )
            raise ColorExtractionError(
                f"Pywal command failed: {e.stderr}"
            ) from e
        except FileNotFoundError as e:
            logger.error("Pywal binary not found in PATH")
            raise BackendNotAvailableError(
                self.backend_name,
                "wal command not found. Install pywal.",
            ) from e

    def _parse_pywal_output(
        self, pywal_colors: dict, image_path: Path
    ) -> ColorScheme:
        """Parse pywal JSON output into ColorScheme.

        Args:
            pywal_colors: Pywal colors dict from colors.json
            image_path: Source image path

        Returns:
            ColorScheme object
        """
        # Pywal format:
        # {
        #   "special": {
        #     "background": "#...", "foreground": "#...", "cursor": "#..."
        #   },
        #   "colors": {"color0": "#...", "color1": "#...", ...}
        # }

        special = pywal_colors.get("special", {})
        colors_dict = pywal_colors.get("colors", {})

        # Extract special colors
        background = self._parse_color(special.get("background", "#000000"))
        foreground = self._parse_color(special.get("foreground", "#ffffff"))
        cursor = self._parse_color(special.get("cursor", foreground.hex))

        # Extract terminal colors (0-15)
        colors = []
        for i in range(16):
            color_key = f"color{i}"
            if color_key in colors_dict:
                colors.append(self._parse_color(colors_dict[color_key]))
            else:
                # Fallback if color missing
                colors.append(Color(hex="#000000", rgb=(0, 0, 0)))

        # Apply saturation adjustment if configured
        saturation_factor = self.settings.generation.saturation_adjustment
        if saturation_factor != 1.0:
            background = background.adjust_saturation(saturation_factor)
            foreground = foreground.adjust_saturation(saturation_factor)
            cursor = cursor.adjust_saturation(saturation_factor)
            colors = [
                color.adjust_saturation(saturation_factor) for color in colors
            ]

        return ColorScheme(
            background=background,
            foreground=foreground,
            cursor=cursor,
            colors=colors,
            source_image=image_path,
            backend=self.backend_name,
        )

    def _parse_color(self, hex_color: str) -> Color:
        """Parse hex color string to Color object.

        Args:
            hex_color: Hex color string (e.g., "#1a1a1a")

        Returns:
            Color object
        """
        # Remove '#' if present
        hex_color = hex_color.lstrip("#")

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        return Color(hex=f"#{hex_color}", rgb=(r, g, b))
