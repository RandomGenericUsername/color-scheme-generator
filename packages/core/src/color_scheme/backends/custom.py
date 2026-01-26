"""Custom backend for color scheme generation using PIL."""

import logging
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans  # type: ignore[import-untyped]

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import ColorAlgorithm
from color_scheme.core.base import ColorSchemeGenerator
from color_scheme.core.exceptions import (
    ColorExtractionError,
    InvalidImageError,
)
from color_scheme.core.types import Color, ColorScheme, GeneratorConfig

logger = logging.getLogger(__name__)


class CustomGenerator(ColorSchemeGenerator):
    """Custom backend for color extraction using PIL and K-means.

    Attributes:
        settings: Application configuration
        algorithm: Color extraction algorithm to use
        n_clusters: Number of color clusters
    """

    def __init__(self, settings: AppConfig):
        """Initialize CustomGenerator."""
        self.settings = settings
        self.algorithm = ColorAlgorithm(settings.backends.custom.algorithm)
        self.n_clusters = settings.backends.custom.n_clusters
        logger.debug(
            "Initialized CustomGenerator with algorithm=%s, n_clusters=%d",
            self.algorithm.value,
            self.n_clusters,
        )

    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "custom"

    def is_available(self) -> bool:
        """Check if custom backend is available."""
        return True  # PIL is a required dependency

    def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
        """Generate color scheme using K-means clustering.

        Args:
            image_path: Path to source image
            config: Runtime configuration

        Returns:
            ColorScheme object with extracted colors

        Raises:
            InvalidImageError: If image is invalid
            ColorExtractionError: If color extraction fails
        """
        logger.info("Generating color scheme with custom backend from %s", image_path)

        # Validate image
        image_path = image_path.expanduser().resolve()
        logger.debug("Resolved image path: %s", image_path)

        if not image_path.exists():
            logger.error("Image file does not exist: %s", image_path)
            raise InvalidImageError(str(image_path), "File does not exist")

        if not image_path.is_file():
            logger.error("Path is not a file: %s", image_path)
            raise InvalidImageError(str(image_path), "Not a file")

        try:
            # Load and process image
            img = Image.open(image_path)
            img = img.convert("RGB")
            logger.debug("Loaded image: %s", img.size)

            # Extract colors using K-means
            colors = self._extract_colors_kmeans(img)
            logger.debug("Extracted %d colors", len(colors))

            # Apply saturation adjustment if specified
            saturation = config.saturation_adjustment or 1.0
            if saturation != 1.0:
                colors = [c.adjust_saturation(saturation) for c in colors]
                logger.debug("Applied saturation adjustment: %.2f", saturation)

            # Ensure we have exactly 16 colors
            if len(colors) < 16:
                # Duplicate colors if we have less than 16
                while len(colors) < 16:
                    colors.append(colors[len(colors) % len(colors)])
            elif len(colors) > 16:
                colors = colors[:16]

            # Create color scheme
            scheme = ColorScheme(
                background=colors[0],  # Darkest color
                foreground=colors[-1],  # Brightest color
                cursor=colors[1],  # Second color
                colors=colors,
                source_image=image_path,
                backend=self.backend_name,
            )

            logger.info("Successfully generated color scheme")
            return scheme

        except (OSError, ValueError) as e:
            logger.error("Failed to load image: %s", e)
            raise InvalidImageError(str(image_path), str(e)) from e
        except Exception as e:
            logger.error("Color extraction failed: %s", e)
            raise ColorExtractionError(self.backend_name, str(e)) from e

    def _extract_colors_kmeans(self, img: Image.Image) -> list[Color]:
        """Extract colors using K-means clustering."""
        # Resize image for faster processing
        img_resized = img.copy()
        img_resized.thumbnail((200, 200))

        # Convert to numpy array
        pixels = np.array(img_resized).reshape(-1, 3)

        # Run K-means clustering
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        kmeans.fit(pixels)

        # Get cluster centers (colors)
        centers = kmeans.cluster_centers_.astype(int)

        # Convert to Color objects
        colors = []
        for rgb in centers:
            r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
            hex_color = f"#{r:02X}{g:02X}{b:02X}"
            colors.append(Color(hex=hex_color, rgb=(r, g, b)))

        # Sort by brightness (sum of RGB values)
        colors.sort(key=lambda c: sum(c.rgb))

        return colors
