"""Wallust backend for color scheme generation.

This backend uses wallust (Rust binary) to extract colors from images.
Wallust writes JSON files to a cache directory, which we read from.
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


class WallustGenerator(ColorSchemeGenerator):
    """Wallust backend for color extraction.

    Uses wallust (Rust binary) to generate colors. Wallust writes to a
    cache directory (~/.cache/wallust/), which we read from to extract
    the ColorScheme.

    Attributes:
        settings: Application configuration
        cache_dir: Directory where wallust writes its output
        backend_type: Wallust backend type (resized, full, thumb)
    """

    def __init__(self, settings: AppConfig):
        """Initialize WallustGenerator.

        Args:
            settings: Application configuration
        """
        self.settings = settings
        self.cache_dir = Path.home() / ".cache" / "wallust"
        self.backend_type = settings.backends.wallust.backend_type
        logger.debug(
            "Initialized WallustGenerator with cache_dir=%s, backend_type=%s",
            self.cache_dir,
            self.backend_type,
        )

    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "wallust"

    def is_available(self) -> bool:
        """Check if wallust is available.

        Returns:
            True if wallust binary is in PATH
        """
        available = shutil.which("wallust") is not None
        logger.debug("Wallust availability check: %s", available)
        return available

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
            BackendNotAvailableError: If wallust is not available
            InvalidImageError: If image is invalid
            ColorExtractionError: If color extraction fails
        """
        logger.info("Generating color scheme with wallust from %s", image_path)

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

        # Run wallust (writes to cache)
        try:
            self._run_wallust(image_path, config)
        except Exception as e:
            logger.error("Failed to run wallust: %s", e)
            raise ColorExtractionError(
                f"Failed to run wallust on {image_path}: {e}"
            ) from e

        # Find and read the cache file
        try:
            cache_file = self._find_cache_file(image_path, config)
            logger.debug("Found wallust cache file: %s", cache_file)
        except Exception as e:
            logger.error("Failed to find wallust cache file: %s", e)
            raise ColorExtractionError(
                f"Failed to find wallust cache file for {image_path}: {e}"
            ) from e

        if not cache_file.exists():
            logger.error("Wallust cache file not found: %s", cache_file)
            raise ColorExtractionError(
                f"Wallust cache file not found: {cache_file}"
            )

        # Parse JSON from cache file
        try:
            with cache_file.open() as f:
                wallust_colors = json.load(f)
            logger.debug("Successfully parsed wallust JSON output")
        except Exception as e:
            logger.error("Failed to read wallust output: %s", e)
            raise ColorExtractionError(
                f"Failed to read wallust output from {cache_file}: {e}"
            ) from e

        # Convert to ColorScheme
        scheme = self._parse_wallust_output(wallust_colors, image_path)
        logger.info("Successfully generated color scheme with wallust")
        return scheme

    def _run_wallust(
        self,
        image_path: Path,
        config: GeneratorConfig,  # noqa: ARG002
    ) -> None:
        """Run wallust command to generate colors (writes to cache).

        Args:
            image_path: Path to source image
            config: Runtime configuration (reserved for future use)

        Raises:
            ColorExtractionError: If wallust command fails
            BackendNotAvailableError: If wallust is not installed
        """
        cmd = [
            "wallust",
            "run",
            str(image_path),
            "--backend",
            self.backend_type,
            "-s",  # Skip terminal sequences
            "-T",  # Skip templates
            "-N",  # No config file
            "-q",  # Quiet mode
        ]

        # Add saturation adjustment if configured
        # Our scale: 0.0-2.0, Wallust scale: 1-100
        # Convert: 1.0 -> 50, 0.0 (grayscale) -> 1, 2.0 (max) -> 100
        saturation_factor = self.settings.generation.saturation_adjustment
        if saturation_factor != 1.0:
            # Map 0.0-2.0 to 1-100 (50 is neutral)
            wallust_saturation = int(saturation_factor * 50)
            wallust_saturation = max(1, min(100, wallust_saturation))
            cmd.extend(["--saturation", str(wallust_saturation)])
            logger.debug("Using saturation adjustment: %d", wallust_saturation)

        logger.debug("Running wallust command: %s", " ".join(cmd))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout:
                logger.debug("Wallust stdout: %s", result.stdout)
            if result.stderr:
                logger.debug("Wallust stderr: %s", result.stderr)
        except subprocess.CalledProcessError as e:
            logger.error(
                "Wallust command failed with code %d: %s",
                e.returncode,
                e.stderr,
            )
            raise ColorExtractionError(
                f"Wallust command failed: {e.stderr}"
            ) from e
        except FileNotFoundError as e:
            logger.error("Wallust binary not found in PATH")
            raise BackendNotAvailableError(
                self.backend_name,
                "wallust command not found. "
                "Install with: cargo install wallust",
            ) from e

    def _find_cache_file(
        self,
        image_path: Path,  # noqa: ARG002
        config: GeneratorConfig,  # noqa: ARG002
    ) -> Path:
        """Find the wallust cache file for the given image.

        Args:
            image_path: Path to source image
            config: Runtime configuration (reserved for future use)

        Returns:
            Path to the cache file

        Raises:
            FileNotFoundError: If cache file cannot be found
        """
        if not self.cache_dir.exists():
            raise FileNotFoundError(
                f"Wallust cache directory not found: {self.cache_dir}"
            )

        # Get all cache directories
        cache_dirs = [d for d in self.cache_dir.iterdir() if d.is_dir()]
        if not cache_dirs:
            raise FileNotFoundError(
                f"No cache directories found in {self.cache_dir}"
            )

        # Get the most recently modified directory (handles the hash)
        latest_cache_dir = max(cache_dirs, key=lambda d: d.stat().st_mtime)

        # Build expected filename: <Backend>_<Colorspace>_<Threshold>_<Palette>
        backend = self.backend_type.capitalize()
        colorspace = "Lch"  # Default colorspace
        threshold = "auto"  # Default threshold
        palette = "Dark"  # Default palette

        filename = f"{backend}_{colorspace}_{threshold}_{palette}"
        cache_file = latest_cache_dir / filename

        # Fallback: if exact filename doesn't exist, try to find any
        # Dark palette file
        if not cache_file.exists():
            dark_files = list(latest_cache_dir.glob("*_Dark"))
            if dark_files:
                cache_file = dark_files[0]
            else:
                raise FileNotFoundError(
                    f"No cache file found in {latest_cache_dir}"
                )

        return cache_file

    def _parse_wallust_output(
        self, wallust_colors: dict, image_path: Path
    ) -> ColorScheme:
        """Parse wallust JSON output into ColorScheme.

        Args:
            wallust_colors: Wallust colors dict from JSON output
            image_path: Source image path

        Returns:
            ColorScheme object
        """
        # Wallust format (flat structure):
        # {
        #   "background": "#...",
        #   "foreground": "#...",
        #   "cursor": "#...",
        #   "color0": "#...", "color1": "#...", ...
        # }

        # Extract special colors directly from root
        background = self._parse_color(
            wallust_colors.get("background", "#000000")
        )
        foreground = self._parse_color(
            wallust_colors.get("foreground", "#ffffff")
        )
        cursor = self._parse_color(
            wallust_colors.get("cursor", foreground.hex)
        )

        # Extract terminal colors (0-15) directly from root
        colors = []
        for i in range(16):
            color_key = f"color{i}"
            if color_key in wallust_colors:
                colors.append(self._parse_color(wallust_colors[color_key]))
            else:
                # Fallback if color missing
                colors.append(Color(hex="#000000", rgb=(0, 0, 0)))

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
