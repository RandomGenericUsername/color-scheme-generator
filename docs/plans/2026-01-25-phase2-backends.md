# Phase 2: Core Backends Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement all three color extraction backends (custom, pywal, wallust) with full test coverage

**Architecture:** TDD approach - implement core types first, then backends one by one (custom → pywal → wallust), then factory pattern. Each backend inherits from abstract base class and implements color extraction logic.

**Tech Stack:** Python 3.12+, PIL/Pillow, scikit-learn, pywal (optional), pytest, pytest-cov

---

## Task 1: Core Types and Base Classes

**Files:**
- Create: `packages/core/src/color_scheme/core/__init__.py`
- Create: `packages/core/src/color_scheme/core/types.py`
- Create: `packages/core/src/color_scheme/core/base.py`
- Create: `packages/core/src/color_scheme/core/exceptions.py`
- Create: `packages/core/tests/unit/test_types.py`

**Step 1: Write test for Color type**

Create `packages/core/tests/unit/test_types.py`:
```python
"""Tests for core type definitions."""

from pathlib import Path

import pytest

from color_scheme.core.types import Color, ColorScheme
from color_scheme.config.enums import Backend


class TestColor:
    """Tests for Color type."""

    def test_color_creation(self):
        """Test creating a Color."""
        color = Color(hex="#FF5733", rgb=(255, 87, 51))
        assert color.hex == "#FF5733"
        assert color.rgb == (255, 87, 51)

    def test_color_validation(self):
        """Test Color validation."""
        with pytest.raises(ValueError):
            Color(hex="invalid", rgb=(255, 87, 51))

    def test_adjust_saturation(self):
        """Test saturation adjustment."""
        color = Color(hex="#FF5733", rgb=(255, 87, 51))

        # Test desaturation
        desaturated = color.adjust_saturation(0.5)
        assert desaturated.hex != color.hex

        # Test no change
        unchanged = color.adjust_saturation(1.0)
        assert unchanged.hex == color.hex


class TestColorScheme:
    """Tests for ColorScheme type."""

    def test_colorscheme_creation(self):
        """Test creating a ColorScheme."""
        colors = [
            Color(hex=f"#{i:02x}{i:02x}{i:02x}", rgb=(i, i, i))
            for i in range(16)
        ]

        scheme = ColorScheme(
            background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
            foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
            cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
            colors=colors,
            source_image=Path("/tmp/test.png"),
            backend="custom"
        )

        assert len(scheme.colors) == 16
        assert scheme.backend == "custom"

    def test_colorscheme_validation(self):
        """Test ColorScheme validation."""
        colors = [Color(hex="#000000", rgb=(0, 0, 0)) for _ in range(15)]

        with pytest.raises(ValueError):
            ColorScheme(
                background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
                foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
                cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
                colors=colors,  # Only 15 colors, needs 16
                source_image=Path("/tmp/test.png"),
                backend="custom"
            )
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_types.py -v
```

Expected: ImportError - module 'color_scheme.core.types' not found

**Step 3: Create core types module**

Create `packages/core/src/color_scheme/core/__init__.py`:
```python
"""Core types and base classes for color scheme generation."""

from color_scheme.core.base import ColorSchemeGenerator
from color_scheme.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    ColorSchemeError,
    InvalidImageError,
)
from color_scheme.core.types import Color, ColorScheme, GeneratorConfig

__all__ = [
    "Color",
    "ColorScheme",
    "GeneratorConfig",
    "ColorSchemeGenerator",
    "ColorSchemeError",
    "InvalidImageError",
    "ColorExtractionError",
    "BackendNotAvailableError",
]
```

Create `packages/core/src/color_scheme/core/types.py`:
```python
"""Core type definitions for colorscheme generator."""

import colorsys
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend, ColorFormat


class Color(BaseModel):
    """Single color in multiple formats.

    Attributes:
        hex: Hex color code (e.g., "#FF5733")
        rgb: RGB tuple (0-255 for each channel)
        hsl: Optional HSL tuple (hue: 0-360, saturation: 0-1, lightness: 0-1)
    """

    hex: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    rgb: tuple[int, int, int]
    hsl: tuple[float, float, float] | None = None

    def adjust_saturation(self, factor: float) -> "Color":
        """Adjust color saturation by a multiplier.

        Args:
            factor: Saturation multiplier (0.0-2.0)

        Returns:
            New Color with adjusted saturation
        """
        # Convert RGB (0-255) to RGB (0-1)
        r, g, b = self.rgb[0] / 255.0, self.rgb[1] / 255.0, self.rgb[2] / 255.0

        # Convert to HLS (Hue, Lightness, Saturation)
        h, l, s = colorsys.rgb_to_hls(r, g, b)

        # Adjust saturation
        s = max(0.0, min(1.0, s * factor))  # Clamp to [0, 1]

        # Convert back to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)

        # Convert to 0-255 range
        new_rgb = (
            int(round(r * 255)),
            int(round(g * 255)),
            int(round(b * 255)),
        )

        # Convert to hex
        new_hex = f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"

        # Create new Color with adjusted values
        return Color(
            hex=new_hex,
            rgb=new_rgb,
            hsl=(h * 360, s, l) if self.hsl else None,
        )


class ColorScheme(BaseModel):
    """Complete color scheme from image.

    Attributes:
        background: Background color
        foreground: Foreground/text color
        cursor: Cursor color
        colors: List of 16 terminal colors (ANSI colors 0-15)
        source_image: Path to source image
        backend: Backend used for generation
        generated_at: Timestamp of generation
        output_files: Dict of format -> path (populated by OutputManager)
    """

    background: Color
    foreground: Color
    cursor: Color
    colors: list[Color] = Field(..., min_length=16, max_length=16)

    # Metadata
    source_image: Path
    backend: str
    generated_at: datetime = Field(default_factory=datetime.now)

    # Output files (populated by OutputManager after writing)
    output_files: dict[str, Path] = Field(default_factory=dict)


class GeneratorConfig(BaseModel):
    """Runtime configuration for color scheme generation.

    Attributes:
        backend: Backend to use
        color_count: Number of colors (fixed at 16)
        saturation_adjustment: Saturation adjustment factor
        output_dir: Output directory
        formats: Output formats
        backend_options: Backend-specific options
    """

    # Color extraction settings (for backends)
    backend: Backend | None = None
    color_count: int = 16  # Hardcoded, not configurable

    saturation_adjustment: float | None = None

    # File output settings (for OutputManager)
    output_dir: Path | None = None
    formats: list[ColorFormat] | None = None

    # Backend-specific options (merged with settings)
    backend_options: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_settings(
        cls, settings: AppConfig, **overrides: Any
    ) -> "GeneratorConfig":
        """Create config from settings with optional overrides."""
        return cls(
            backend=overrides.get("backend")
            or Backend(settings.generation.default_backend),
            color_count=16,
            saturation_adjustment=overrides.get("saturation_adjustment")
            or settings.generation.saturation_adjustment,
            output_dir=overrides.get("output_dir") or settings.output.directory,
            formats=overrides.get("formats")
            or [ColorFormat(f) for f in settings.output.formats],
            backend_options=overrides.get("backend_options", {}),
        )

    def get_backend_settings(self, settings: AppConfig) -> dict[str, Any]:
        """Get backend-specific settings merged with runtime options."""
        backend = self.backend or Backend(settings.generation.default_backend)

        if backend == Backend.PYWAL:
            base_settings = settings.backends.pywal.model_dump()
        elif backend == Backend.WALLUST:
            base_settings = settings.backends.wallust.model_dump()
        elif backend == Backend.CUSTOM:
            base_settings = settings.backends.custom.model_dump()
        else:
            base_settings = {}

        return {**base_settings, **self.backend_options}
```

Create `packages/core/src/color_scheme/core/exceptions.py`:
```python
"""Exceptions for color scheme generation."""


class ColorSchemeError(Exception):
    """Base exception for color scheme generation errors."""

    pass


class InvalidImageError(ColorSchemeError):
    """Raised when image is invalid or cannot be read."""

    def __init__(self, image_path: str, reason: str):
        self.image_path = image_path
        self.reason = reason
        super().__init__(f"Invalid image '{image_path}': {reason}")


class ColorExtractionError(ColorSchemeError):
    """Raised when color extraction fails."""

    def __init__(self, backend: str, reason: str):
        self.backend = backend
        self.reason = reason
        super().__init__(f"Color extraction failed ({backend}): {reason}")


class BackendNotAvailableError(ColorSchemeError):
    """Raised when backend is not available."""

    def __init__(self, backend: str, reason: str):
        self.backend = backend
        self.reason = reason
        super().__init__(f"Backend '{backend}' not available: {reason}")
```

Create `packages/core/src/color_scheme/core/base.py`:
```python
"""Abstract base class for color scheme generators."""

from abc import ABC, abstractmethod
from pathlib import Path

from color_scheme.core.types import ColorScheme, GeneratorConfig


class ColorSchemeGenerator(ABC):
    """Abstract base class for color scheme generators.

    All backend implementations must inherit from this class.
    """

    @abstractmethod
    def generate(
        self, image_path: Path, config: GeneratorConfig
    ) -> ColorScheme:
        """Generate color scheme from image.

        Args:
            image_path: Path to the source image
            config: Runtime configuration for generation

        Returns:
            ColorScheme object with extracted colors

        Raises:
            InvalidImageError: If image cannot be read or is invalid
            ColorExtractionError: If color extraction fails
            BackendNotAvailableError: If backend is not available
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on the system.

        Returns:
            True if backend is available, False otherwise
        """
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Get the backend name.

        Returns:
            Backend name (e.g., "pywal", "wallust", "custom")
        """
        pass

    def ensure_available(self) -> None:
        """Ensure backend is available, raise error if not.

        Raises:
            BackendNotAvailableError: If backend is not available
        """
        from color_scheme.core.exceptions import BackendNotAvailableError

        if not self.is_available():
            raise BackendNotAvailableError(
                self.backend_name,
                f"{self.backend_name} is not installed or not in PATH",
            )
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_types.py -v
```

Expected: All tests pass

**Step 5: Check coverage**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_types.py --cov=src/color_scheme/core --cov-report=term
```

Expected: Coverage ≥ 90%

**Step 6: Commit**

Run:
```bash
git add packages/core/src/color_scheme/core/ packages/core/tests/unit/test_types.py
git commit -m "feat(core): add core types and base classes

Implements:
- Color type with hex, RGB, HSL and saturation adjustment
- ColorScheme type with 16 terminal colors
- GeneratorConfig for runtime configuration
- ColorSchemeGenerator abstract base class
- Custom exceptions for error handling

All types fully tested with 90%+ coverage.

Part of Phase 2: Core Backends.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Custom Backend Implementation

**Files:**
- Create: `packages/core/src/color_scheme/backends/__init__.py`
- Create: `packages/core/src/color_scheme/backends/custom.py`
- Create: `packages/core/tests/unit/test_custom_backend.py`
- Create: `packages/core/tests/fixtures/test_image.png` (test fixture)

**Step 1: Create test fixture image**

Run:
```bash
cd packages/core
mkdir -p tests/fixtures
python3 << 'EOF'
from PIL import Image
import numpy as np

# Create a simple 100x100 test image with gradient colors
img = Image.new('RGB', (100, 100))
pixels = []
for y in range(100):
    for x in range(100):
        r = int((x / 100) * 255)
        g = int((y / 100) * 255)
        b = 128
        pixels.append((r, g, b))
img.putdata(pixels)
img.save('tests/fixtures/test_image.png')
print("Created test image: tests/fixtures/test_image.png")
EOF
```

Expected: Test image created

**Step 2: Write failing test for CustomGenerator**

Create `packages/core/tests/unit/test_custom_backend.py`:
```python
"""Tests for custom backend."""

from pathlib import Path

import pytest

from color_scheme.backends.custom import CustomGenerator
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import InvalidImageError
from color_scheme.core.types import GeneratorConfig


class TestCustomGenerator:
    """Tests for CustomGenerator."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def generator(self, settings):
        """Create CustomGenerator."""
        return CustomGenerator(settings)

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    @pytest.fixture
    def config(self):
        """Create GeneratorConfig."""
        return GeneratorConfig()

    def test_backend_name(self, generator):
        """Test backend name."""
        assert generator.backend_name == "custom"

    def test_is_available(self, generator):
        """Test is_available."""
        assert generator.is_available() is True

    def test_generate_success(self, generator, test_image, config):
        """Test successful color generation."""
        scheme = generator.generate(test_image, config)

        assert scheme.backend == "custom"
        assert len(scheme.colors) == 16
        assert scheme.source_image == test_image.resolve()

        # Check color format
        assert scheme.background.hex.startswith("#")
        assert len(scheme.background.hex) == 7

    def test_generate_invalid_image(self, generator, config):
        """Test generation with invalid image."""
        invalid_path = Path("/nonexistent/image.png")

        with pytest.raises(InvalidImageError) as exc_info:
            generator.generate(invalid_path, config)

        assert "does not exist" in str(exc_info.value).lower()

    def test_generate_not_a_file(self, generator, config, tmp_path):
        """Test generation with directory instead of file."""
        with pytest.raises(InvalidImageError) as exc_info:
            generator.generate(tmp_path, config)

        assert "not a file" in str(exc_info.value).lower()
```

**Step 3: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_custom_backend.py -v
```

Expected: ImportError - module 'color_scheme.backends.custom' not found

**Step 4: Implement CustomGenerator**

Create `packages/core/src/color_scheme/backends/__init__.py`:
```python
"""Color extraction backends."""

from color_scheme.backends.custom import CustomGenerator

__all__ = ["CustomGenerator"]
```

Create `packages/core/src/color_scheme/backends/custom.py`:
```python
"""Custom backend for color scheme generation using PIL."""

import logging
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

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

    def generate(
        self, image_path: Path, config: GeneratorConfig
    ) -> ColorScheme:
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
        logger.info(
            "Generating color scheme with custom backend from %s", image_path
        )

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
            raise InvalidImageError(str(image_path), str(e))
        except Exception as e:
            logger.error("Color extraction failed: %s", e)
            raise ColorExtractionError(self.backend_name, str(e))

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
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            colors.append(Color(hex=hex_color, rgb=(r, g, b)))

        # Sort by brightness (sum of RGB values)
        colors.sort(key=lambda c: sum(c.rgb))

        return colors
```

**Step 5: Run tests to verify they pass**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_custom_backend.py -v
```

Expected: All tests pass

**Step 6: Check coverage**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_custom_backend.py --cov=src/color_scheme/backends --cov-report=term
```

Expected: Coverage ≥ 90%

**Step 7: Commit**

Run:
```bash
git add packages/core/src/color_scheme/backends/ packages/core/tests/unit/test_custom_backend.py packages/core/tests/fixtures/
git commit -m "feat(backends): implement custom backend with K-means

Implements CustomGenerator using PIL and scikit-learn K-means:
- K-means clustering for color extraction
- Automatic sorting by brightness
- Saturation adjustment support
- Comprehensive error handling

Includes test fixture image and full test coverage (90%+).

Part of Phase 2: Core Backends.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: PyWal Backend Implementation

**Files:**
- Create: `packages/core/src/color_scheme/backends/pywal.py`
- Create: `packages/core/tests/unit/test_pywal_backend.py`

**Step 1: Write failing test for PywalGenerator**

Create `packages/core/tests/unit/test_pywal_backend.py`:
```python
"""Tests for pywal backend."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from color_scheme.backends.pywal import PywalGenerator
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import BackendNotAvailableError, InvalidImageError
from color_scheme.core.types import GeneratorConfig


class TestPywalGenerator:
    """Tests for PywalGenerator."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def generator(self, settings):
        """Create PywalGenerator."""
        return PywalGenerator(settings)

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    @pytest.fixture
    def config(self):
        """Create GeneratorConfig."""
        return GeneratorConfig()

    def test_backend_name(self, generator):
        """Test backend name."""
        assert generator.backend_name == "pywal"

    @patch("shutil.which")
    def test_is_available_true(self, mock_which, generator):
        """Test is_available when pywal is installed."""
        mock_which.return_value = "/usr/bin/wal"
        assert generator.is_available() is True

    @patch("shutil.which")
    def test_is_available_false(self, mock_which, generator):
        """Test is_available when pywal is not installed."""
        mock_which.return_value = None
        assert generator.is_available() is False

    @patch("shutil.which")
    def test_ensure_available_raises(self, mock_which, generator):
        """Test ensure_available raises when not available."""
        mock_which.return_value = None

        with pytest.raises(BackendNotAvailableError) as exc_info:
            generator.ensure_available()

        assert "pywal" in str(exc_info.value).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_success(self, mock_which, mock_run, generator, test_image, config, tmp_path):
        """Test successful color generation."""
        mock_which.return_value = "/usr/bin/wal"

        # Mock pywal cache file
        cache_file = tmp_path / "colors.json"
        cache_file.write_text('''{
            "special": {
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "cursor": "#ff0000"
            },
            "colors": {
                "color0": "#000000",
                "color1": "#111111",
                "color2": "#222222",
                "color3": "#333333",
                "color4": "#444444",
                "color5": "#555555",
                "color6": "#666666",
                "color7": "#777777",
                "color8": "#888888",
                "color9": "#999999",
                "color10": "#aaaaaa",
                "color11": "#bbbbbb",
                "color12": "#cccccc",
                "color13": "#dddddd",
                "color14": "#eeeeee",
                "color15": "#ffffff"
            }
        }''')

        with patch.object(generator, '_get_cache_file', return_value=cache_file):
            scheme = generator.generate(test_image, config)

        assert scheme.backend == "pywal"
        assert len(scheme.colors) == 16
        assert scheme.background.hex == "#1a1a1a"
        assert scheme.foreground.hex == "#ffffff"

    def test_generate_invalid_image(self, generator, config):
        """Test generation with invalid image."""
        invalid_path = Path("/nonexistent/image.png")

        with pytest.raises(InvalidImageError):
            generator.generate(invalid_path, config)
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_pywal_backend.py -v
```

Expected: ImportError - module 'color_scheme.backends.pywal' not found

**Step 3: Implement PywalGenerator**

Update `packages/core/src/color_scheme/backends/__init__.py`:
```python
"""Color extraction backends."""

from color_scheme.backends.custom import CustomGenerator
from color_scheme.backends.pywal import PywalGenerator

__all__ = ["CustomGenerator", "PywalGenerator"]
```

Create `packages/core/src/color_scheme/backends/pywal.py`:
```python
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
        self.cache_dir = settings.backends.pywal.cache_dir
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
            )
        except subprocess.TimeoutExpired:
            logger.error("Pywal command timed out")
            raise ColorExtractionError(
                self.backend_name,
                "Pywal timed out after 30 seconds"
            )
        except Exception as e:
            logger.error("Color extraction failed: %s", e)
            raise ColorExtractionError(self.backend_name, str(e))

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
            )

    def _parse_colors(self, data: dict, image_path: Path) -> ColorScheme:
        """Parse colors from pywal cache data."""
        special = data.get("special", {})
        colors_dict = data.get("colors", {})

        # Extract special colors
        bg_hex = special.get("background", "#000000")
        fg_hex = special.get("foreground", "#ffffff")
        cursor_hex = special.get("cursor", "#ff0000")

        # Extract 16 colors
        colors = []
        for i in range(16):
            color_hex = colors_dict.get(f"color{i}", "#000000")
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
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_pywal_backend.py -v
```

Expected: All tests pass

**Step 5: Check coverage**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_pywal_backend.py --cov=src/color_scheme/backends/pywal --cov-report=term
```

Expected: Coverage ≥ 90%

**Step 6: Commit**

Run:
```bash
git add packages/core/src/color_scheme/backends/ packages/core/tests/unit/test_pywal_backend.py
git commit -m "feat(backends): implement pywal backend

Implements PywalGenerator using pywal CLI:
- Subprocess execution with timeout
- JSON cache file parsing
- Backend algorithm selection
- Saturation adjustment support
- Comprehensive error handling

Fully tested with mocks (90%+ coverage).

Part of Phase 2: Core Backends.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Wallust Backend Implementation

**Files:**
- Create: `packages/core/src/color_scheme/backends/wallust.py`
- Create: `packages/core/tests/unit/test_wallust_backend.py`

**Step 1: Write failing test for WallustGenerator**

Create `packages/core/tests/unit/test_wallust_backend.py`:
```python
"""Tests for wallust backend."""

from pathlib import Path
from unittest.mock import patch

import pytest

from color_scheme.backends.wallust import WallustGenerator
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import BackendNotAvailableError, InvalidImageError
from color_scheme.core.types import GeneratorConfig


class TestWallustGenerator:
    """Tests for WallustGenerator."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def generator(self, settings):
        """Create WallustGenerator."""
        return WallustGenerator(settings)

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    @pytest.fixture
    def config(self):
        """Create GeneratorConfig."""
        return GeneratorConfig()

    def test_backend_name(self, generator):
        """Test backend name."""
        assert generator.backend_name == "wallust"

    @patch("shutil.which")
    def test_is_available_true(self, mock_which, generator):
        """Test is_available when wallust is installed."""
        mock_which.return_value = "/usr/bin/wallust"
        assert generator.is_available() is True

    @patch("shutil.which")
    def test_is_available_false(self, mock_which, generator):
        """Test is_available when wallust is not installed."""
        mock_which.return_value = None
        assert generator.is_available() is False

    @patch("shutil.which")
    def test_ensure_available_raises(self, mock_which, generator):
        """Test ensure_available raises when not available."""
        mock_which.return_value = None

        with pytest.raises(BackendNotAvailableError) as exc_info:
            generator.ensure_available()

        assert "wallust" in str(exc_info.value).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_success(self, mock_which, mock_run, generator, test_image, config):
        """Test successful color generation."""
        mock_which.return_value = "/usr/bin/wallust"

        # Mock wallust JSON output
        mock_run.return_value.stdout = '''{
            "background": "#1a1a1a",
            "foreground": "#ffffff",
            "cursor": "#ff0000",
            "color0": "#000000",
            "color1": "#111111",
            "color2": "#222222",
            "color3": "#333333",
            "color4": "#444444",
            "color5": "#555555",
            "color6": "#666666",
            "color7": "#777777",
            "color8": "#888888",
            "color9": "#999999",
            "color10": "#aaaaaa",
            "color11": "#bbbbbb",
            "color12": "#cccccc",
            "color13": "#dddddd",
            "color14": "#eeeeee",
            "color15": "#ffffff"
        }'''

        scheme = generator.generate(test_image, config)

        assert scheme.backend == "wallust"
        assert len(scheme.colors) == 16
        assert scheme.background.hex == "#1a1a1a"
        assert scheme.foreground.hex == "#ffffff"

    def test_generate_invalid_image(self, generator, config):
        """Test generation with invalid image."""
        invalid_path = Path("/nonexistent/image.png")

        with pytest.raises(InvalidImageError):
            generator.generate(invalid_path, config)
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_wallust_backend.py -v
```

Expected: ImportError - module 'color_scheme.backends.wallust' not found

**Step 3: Implement WallustGenerator**

Update `packages/core/src/color_scheme/backends/__init__.py`:
```python
"""Color extraction backends."""

from color_scheme.backends.custom import CustomGenerator
from color_scheme.backends.pywal import PywalGenerator
from color_scheme.backends.wallust import WallustGenerator

__all__ = ["CustomGenerator", "PywalGenerator", "WallustGenerator"]
```

Create `packages/core/src/color_scheme/backends/wallust.py`:
```python
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
            )
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
            )
        except Exception as e:
            logger.error("Color extraction failed: %s", e)
            raise ColorExtractionError(self.backend_name, str(e))

    def _parse_colors(self, data: dict, image_path: Path) -> ColorScheme:
        """Parse colors from wallust JSON output."""
        # Extract special colors
        bg_hex = data.get("background", "#000000")
        fg_hex = data.get("foreground", "#ffffff")
        cursor_hex = data.get("cursor", "#ff0000")

        # Extract 16 colors
        colors = []
        for i in range(16):
            color_hex = data.get(f"color{i}", "#000000")
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
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_wallust_backend.py -v
```

Expected: All tests pass

**Step 5: Check coverage**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_wallust_backend.py --cov=src/color_scheme/backends/wallust --cov-report=term
```

Expected: Coverage ≥ 90%

**Step 6: Commit**

Run:
```bash
git add packages/core/src/color_scheme/backends/ packages/core/tests/unit/test_wallust_backend.py
git commit -m "feat(backends): implement wallust backend

Implements WallustGenerator using wallust CLI:
- JSON output parsing
- Backend type selection
- Subprocess execution with timeout
- Saturation adjustment support
- Comprehensive error handling

Fully tested with mocks (90%+ coverage).

Part of Phase 2: Core Backends.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Factory Pattern Implementation

**Files:**
- Create: `packages/core/src/color_scheme/factory.py`
- Create: `packages/core/tests/unit/test_factory.py`

**Step 1: Write failing test for factory**

Create `packages/core/tests/unit/test_factory.py`:
```python
"""Tests for backend factory."""

from unittest.mock import patch

import pytest

from color_scheme.backends.custom import CustomGenerator
from color_scheme.backends.pywal import PywalGenerator
from color_scheme.backends.wallust import WallustGenerator
from color_scheme.config.enums import Backend
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import BackendNotAvailableError
from color_scheme.factory import BackendFactory


class TestBackendFactory:
    """Tests for BackendFactory."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def factory(self, settings):
        """Create BackendFactory."""
        return BackendFactory(settings)

    def test_create_custom_backend(self, factory):
        """Test creating custom backend."""
        generator = factory.create(Backend.CUSTOM)
        assert isinstance(generator, CustomGenerator)
        assert generator.backend_name == "custom"

    @patch("shutil.which")
    def test_create_pywal_backend(self, mock_which, factory):
        """Test creating pywal backend."""
        mock_which.return_value = "/usr/bin/wal"

        generator = factory.create(Backend.PYWAL)
        assert isinstance(generator, PywalGenerator)
        assert generator.backend_name == "pywal"

    @patch("shutil.which")
    def test_create_wallust_backend(self, mock_which, factory):
        """Test creating wallust backend."""
        mock_which.return_value = "/usr/bin/wallust"

        generator = factory.create(Backend.WALLUST)
        assert isinstance(generator, WallustGenerator)
        assert generator.backend_name == "wallust"

    @patch("shutil.which")
    def test_create_unavailable_backend_raises(self, mock_which, factory):
        """Test creating unavailable backend raises error."""
        mock_which.return_value = None

        with pytest.raises(BackendNotAvailableError):
            factory.create(Backend.PYWAL)

    @patch.object(PywalGenerator, "is_available", return_value=True)
    @patch.object(WallustGenerator, "is_available", return_value=False)
    def test_detect_available_backends(self, mock_wallust, mock_pywal, factory):
        """Test detecting available backends."""
        available = factory.detect_available()

        assert Backend.CUSTOM in available  # Always available
        assert Backend.PYWAL in available
        assert Backend.WALLUST not in available

    @patch.object(PywalGenerator, "is_available", return_value=True)
    @patch.object(WallustGenerator, "is_available", return_value=True)
    def test_auto_detect_all_available(self, mock_wallust, mock_pywal, factory):
        """Test auto-detect with all backends available."""
        # Prefer order: wallust > pywal > custom
        backend = factory.auto_detect()
        assert backend == Backend.WALLUST

    @patch.object(PywalGenerator, "is_available", return_value=True)
    @patch.object(WallustGenerator, "is_available", return_value=False)
    def test_auto_detect_pywal_only(self, mock_wallust, mock_pywal, factory):
        """Test auto-detect with pywal only."""
        backend = factory.auto_detect()
        assert backend == Backend.PYWAL

    @patch.object(PywalGenerator, "is_available", return_value=False)
    @patch.object(WallustGenerator, "is_available", return_value=False)
    def test_auto_detect_fallback_to_custom(self, mock_wallust, mock_pywal, factory):
        """Test auto-detect fallback to custom."""
        backend = factory.auto_detect()
        assert backend == Backend.CUSTOM
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_factory.py -v
```

Expected: ImportError - module 'color_scheme.factory' not found

**Step 3: Implement BackendFactory**

Create `packages/core/src/color_scheme/factory.py`:
```python
"""Factory for creating backend generators."""

import logging

from color_scheme.backends.custom import CustomGenerator
from color_scheme.backends.pywal import PywalGenerator
from color_scheme.backends.wallust import WallustGenerator
from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend
from color_scheme.core.base import ColorSchemeGenerator
from color_scheme.core.exceptions import BackendNotAvailableError

logger = logging.getLogger(__name__)


class BackendFactory:
    """Factory for creating backend generators.

    Provides methods to:
    - Create generators for specific backends
    - Detect available backends
    - Auto-detect the best available backend

    Attributes:
        settings: Application configuration
    """

    def __init__(self, settings: AppConfig):
        """Initialize BackendFactory.

        Args:
            settings: Application configuration
        """
        self.settings = settings
        logger.debug("Initialized BackendFactory")

    def create(self, backend: Backend) -> ColorSchemeGenerator:
        """Create a generator for the specified backend.

        Args:
            backend: Backend to create

        Returns:
            ColorSchemeGenerator instance

        Raises:
            BackendNotAvailableError: If backend is not available

        Example:
            >>> factory = BackendFactory(settings)
            >>> generator = factory.create(Backend.PYWAL)
            >>> scheme = generator.generate(image_path, config)
        """
        logger.debug("Creating generator for backend: %s", backend.value)

        if backend == Backend.CUSTOM:
            generator = CustomGenerator(self.settings)
        elif backend == Backend.PYWAL:
            generator = PywalGenerator(self.settings)
        elif backend == Backend.WALLUST:
            generator = WallustGenerator(self.settings)
        else:
            raise ValueError(f"Unknown backend: {backend}")

        # Ensure backend is available
        generator.ensure_available()

        logger.info("Created %s generator", backend.value)
        return generator

    def detect_available(self) -> list[Backend]:
        """Detect all available backends.

        Returns:
            List of available backends

        Example:
            >>> factory = BackendFactory(settings)
            >>> available = factory.detect_available()
            >>> print(available)
            [<Backend.CUSTOM: 'custom'>, <Backend.PYWAL: 'pywal'>]
        """
        available = []

        for backend in Backend:
            try:
                if backend == Backend.CUSTOM:
                    generator = CustomGenerator(self.settings)
                elif backend == Backend.PYWAL:
                    generator = PywalGenerator(self.settings)
                elif backend == Backend.WALLUST:
                    generator = WallustGenerator(self.settings)
                else:
                    continue

                if generator.is_available():
                    available.append(backend)
                    logger.debug("Backend %s is available", backend.value)
                else:
                    logger.debug("Backend %s is not available", backend.value)

            except Exception as e:
                logger.debug(
                    "Failed to check backend %s: %s", backend.value, e
                )

        logger.info("Available backends: %s", [b.value for b in available])
        return available

    def auto_detect(self) -> Backend:
        """Auto-detect the best available backend.

        Preference order: wallust > pywal > custom

        Returns:
            Best available backend (always returns at least CUSTOM)

        Example:
            >>> factory = BackendFactory(settings)
            >>> backend = factory.auto_detect()
            >>> generator = factory.create(backend)
        """
        logger.debug("Auto-detecting best available backend")

        # Check in preference order
        for backend in [Backend.WALLUST, Backend.PYWAL, Backend.CUSTOM]:
            try:
                if backend == Backend.CUSTOM:
                    generator = CustomGenerator(self.settings)
                elif backend == Backend.PYWAL:
                    generator = PywalGenerator(self.settings)
                elif backend == Backend.WALLUST:
                    generator = WallustGenerator(self.settings)
                else:
                    continue

                if generator.is_available():
                    logger.info("Auto-detected backend: %s", backend.value)
                    return backend

            except Exception as e:
                logger.debug(
                    "Failed to check backend %s: %s", backend.value, e
                )

        # Fallback to custom (always available)
        logger.info("Falling back to custom backend")
        return Backend.CUSTOM
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_factory.py -v
```

Expected: All tests pass

**Step 5: Check coverage**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_factory.py --cov=src/color_scheme/factory --cov-report=term
```

Expected: Coverage ≥ 90%

**Step 6: Commit**

Run:
```bash
git add packages/core/src/color_scheme/factory.py packages/core/tests/unit/test_factory.py
git commit -m "feat(core): implement backend factory pattern

Implements BackendFactory with:
- create() - Create specific backend generator
- detect_available() - Find all available backends
- auto_detect() - Auto-select best backend (wallust > pywal > custom)

Comprehensive tests with mocks (90%+ coverage).

Part of Phase 2: Core Backends.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Final Testing and Verification

**Step 1: Run all tests**

Run:
```bash
cd packages/core
uv run pytest tests/unit/ -v
```

Expected: All tests pass

**Step 2: Check overall coverage**

Run:
```bash
cd packages/core
uv run pytest tests/unit/ --cov=src/color_scheme --cov-report=term --cov-report=html
```

Expected: Coverage ≥ 95%

**Step 3: Run linting**

Run:
```bash
cd packages/core
uv run ruff check src/ tests/
uv run black --check src/ tests/
uv run isort --check src/ tests/
```

Expected: No linting errors

**Step 4: Run type checking**

Run:
```bash
cd packages/core
uv run mypy src/color_scheme/
```

Expected: No type errors (or minimal warnings)

**Step 5: Run verification scripts**

Run:
```bash
./scripts/verify-design-compliance.sh
./scripts/verify-documentation.sh
```

Expected: Show improved compliance (backends implemented)

**Step 6: Update documentation progress**

Edit `docs/implementation-progress.md`:
- Mark Phase 2 tasks as complete
- Update phase status to ✅ COMPLETE
- Add completion date

**Step 7: Final commit**

Run:
```bash
git add docs/implementation-progress.md
git commit -m "docs(progress): mark Phase 2 core backends as complete

All three backends implemented and tested:
- Custom backend (K-means, always available)
- Pywal backend (subprocess, conditional)
- Wallust backend (subprocess, conditional)
- Factory pattern with auto-detection

Test coverage: 95%+
All backends fully functional.

Phase 2 complete. Ready for Phase 3: Output Generation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Completion

Phase 2 implementation complete! You now have:

✅ **Core Types** - Color, ColorScheme, GeneratorConfig with full validation
✅ **Base Classes** - Abstract ColorSchemeGenerator interface
✅ **Custom Backend** - K-means color extraction (always available)
✅ **Pywal Backend** - pywal integration (conditional availability)
✅ **Wallust Backend** - wallust integration (conditional availability)
✅ **Factory Pattern** - Backend creation and auto-detection
✅ **Test Coverage** - 95%+ coverage across all backends
✅ **Error Handling** - Custom exceptions for all failure modes

## Next Steps

Ready to proceed to **Phase 3: Core Package - Output Generation** which involves:
1. OutputManager for file generation
2. Jinja2 templates for 8 formats (JSON, CSS, SCSS, YAML, shell scripts, GTK CSS, rofi rasi, terminal sequences)
3. CLI commands (generate, show)

Execute this plan with: `superpowers:executing-plans`
