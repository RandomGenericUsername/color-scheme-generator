# Backend API Reference

**Scope:** Complete backend API documentation
**Extracted:** February 3, 2026
**Source:** `packages/core/src/color_scheme/core/base.py` and backend implementations

Complete reference for color scheme backends: abstract base class and three implementations (Custom, Pywal, Wallust).

---

## Overview

All backends inherit from `ColorSchemeGenerator`, implementing a standardized interface for color extraction. The project includes three backends:

1. **Custom** - Built-in K-means clustering (always available)
2. **Pywal** - Python-based external tool (optional, must be installed)
3. **Wallust** - Rust-based external tool (optional, must be installed)

---

## Abstract Base Class: ColorSchemeGenerator

**Module:** `color_scheme.core.base`
**Type:** Abstract base class (ABC)
**Purpose:** Defines interface all backends must implement

### Definition

```python
from abc import ABC, abstractmethod
from pathlib import Path
from color_scheme.core.types import ColorScheme, GeneratorConfig

class ColorSchemeGenerator(ABC):
    """Abstract base class for color scheme generators."""
    # All backends inherit from this
```

### Abstract Methods

All subclasses **must** implement these methods:

#### `generate(image_path: Path, config: GeneratorConfig) -> ColorScheme`

Generates a color scheme from an image.

**Parameters:**
- `image_path` (`Path`): Path to source image file
- `config` (`GeneratorConfig`): Runtime configuration

**Returns:** `ColorScheme` object with 16 colors

**Raises:**
- `InvalidImageError` - Image cannot be read or is invalid
- `ColorExtractionError` - Color extraction fails
- `BackendNotAvailableError` - Backend not available (called in subclass)

**Must validate:**
- Image file exists
- Image is actually a file (not a directory)
- Image is readable

---

#### `is_available() -> bool`

Checks if backend is available on the system.

**Returns:** `True` if backend is available, `False` otherwise

**Examples:**
- Custom: Always `True` (PIL is required dependency)
- Pywal: Checks if `wal` command is in PATH
- Wallust: Checks if `wallust` command is in PATH

---

#### `backend_name` (Property)

Gets the backend's identifier.

**Returns:** Backend name as string

**Valid values:**
- `"custom"` - Custom K-means backend
- `"pywal"` - Pywal backend
- `"wallust"` - Wallust backend

**Example:**
```python
def backend_name(self) -> str:
    return "custom"
```

---

### Instance Methods

#### `ensure_available() -> None`

Ensures backend is available, raises error if not.

**Raises:** `BackendNotAvailableError` if `is_available()` returns `False`

**Implementation:**
```python
def ensure_available(self) -> None:
    """Ensure backend is available, raise error if not."""
    if not self.is_available():
        raise BackendNotAvailableError(
            self.backend_name,
            f"{self.backend_name} is not installed or not in PATH",
        )
```

**Usage:**
```python
backend = PywalGenerator(settings)
backend.ensure_available()  # Raises BackendNotAvailableError if pywal not installed
```

---

## Custom Backend

**Class:** `color_scheme.backends.custom.CustomGenerator`
**Module:** `packages/core/src/color_scheme/backends/custom.py`
**Algorithm:** K-means clustering (scikit-learn)
**Availability:** Always (PIL and scikit-learn are required dependencies)

### Definition

```python
from color_scheme.backends.custom import CustomGenerator
from color_scheme.config.config import AppConfig

# Initialize
settings = AppConfig()
backend = CustomGenerator(settings)
```

### Attributes

| Attribute | Type | Source | Description |
|-----------|------|--------|-------------|
| `settings` | `AppConfig` | Constructor | Application configuration |
| `algorithm` | `ColorAlgorithm` | `settings.backends.custom.algorithm` | Algorithm enum value |
| `n_clusters` | `int` | `settings.backends.custom.n_clusters` | Number of color clusters |

### Methods

#### `generate(image_path: Path, config: GeneratorConfig) -> ColorScheme`

Generates color scheme using K-means clustering.

**Algorithm:**
1. Load image with PIL
2. Convert to RGB
3. Resize to 200x200 for faster processing
4. Extract n_clusters colors using K-means
5. Sort by brightness (sum of RGB values)
6. Apply saturation adjustment if specified
7. Ensure exactly 16 colors (duplicate/truncate as needed)
8. Return ColorScheme with:
   - `background` = darkest color (index 0)
   - `foreground` = brightest color (index -1)
   - `cursor` = second color (index 1)
   - `colors` = all 16 colors

**Parameters:**
- `image_path` (`Path`): Path to image
- `config` (`GeneratorConfig`): Configuration with optional `saturation_adjustment`

**Returns:** `ColorScheme` with 16 colors

**Raises:**
- `InvalidImageError` - File doesn't exist or isn't a valid image
- `ColorExtractionError` - K-means extraction fails

**Example:**
```python
from color_scheme.backends.custom import CustomGenerator
from color_scheme.core.types import GeneratorConfig
from pathlib import Path

backend = CustomGenerator(settings)
config = GeneratorConfig(saturation_adjustment=1.2)

scheme = backend.generate(
    Path("/path/to/image.jpg"),
    config
)

print(f"Background: {scheme.background.hex}")
print(f"Colors: {[c.hex for c in scheme.colors]}")
```

#### `is_available() -> bool`

Always returns `True` (built-in backend).

```python
assert backend.is_available() is True
```

#### `backend_name` (Property)

Returns `"custom"`

```python
assert backend.backend_name == "custom"
```

#### `_extract_colors_kmeans(img: Image.Image) -> list[Color]` (Private)

Internal method that performs K-means clustering.

**Process:**
1. Resize image to 200x200
2. Convert to numpy array
3. Run KMeans(n_clusters=self.n_clusters, random_state=42)
4. Extract cluster centers as RGB tuples
5. Convert to Color objects with hex format
6. Sort by brightness

**Returns:** List of Color objects

---

## Pywal Backend

**Class:** `color_scheme.backends.pywal.PywalGenerator`
**Module:** `packages/core/src/color_scheme/backends/pywal.py`
**Tool:** External Python-based tool (pywal)
**Availability:** Only if `wal` command is in PATH

### Definition

```python
from color_scheme.backends.pywal import PywalGenerator

settings = AppConfig()
backend = PywalGenerator(settings)

# Check availability before use
if backend.is_available():
    scheme = backend.generate(image_path, config)
else:
    print("Pywal not installed")
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `settings` | `AppConfig` | Application configuration |
| `cache_dir` | `Path` | Pywal cache directory (always `~/.cache/wal/`) |

### Methods

#### `generate(image_path: Path, config: GeneratorConfig) -> ColorScheme`

Generates color scheme using pywal tool.

**Process:**
1. Validate image file exists and is readable
2. Get backend-specific settings from config
3. Run: `wal -i <image> -n -q --backend <algorithm>`
   - `-i` = input image
   - `-n` = skip setting wallpaper
   - `-q` = quiet mode
   - `--backend` = color extraction algorithm
4. Read colors from pywal cache directory (`~/.cache/wal/colorscheme.json`)
5. Parse JSON output
6. Convert to ColorScheme object
7. Return ColorScheme

**Parameters:**
- `image_path` (`Path`): Path to image file
- `config` (`GeneratorConfig`): Configuration (includes backend_algorithm setting)

**Returns:** `ColorScheme` with 16 colors

**Raises:**
- `BackendNotAvailableError` - `wal` command not found
- `InvalidImageError` - Image file invalid
- `ColorExtractionError` - Pywal extraction fails

**Backend Algorithm:**
- Controlled by `config.backend_options.get("backend_algorithm")` or `settings.backends.pywal.backend_algorithm`
- Default: `"wal"`
- Other options: Pywal supports multiple algorithms

**Example:**
```python
backend = PywalGenerator(settings)

if backend.is_available():
    config = GeneratorConfig(backend_options={"backend_algorithm": "colorz"})
    scheme = backend.generate(Path("/path/to/image.jpg"), config)
else:
    raise BackendNotAvailableError("pywal", "wal command not found")
```

#### `is_available() -> bool`

Checks if `wal` command is in PATH.

```python
import shutil
return shutil.which("wal") is not None
```

#### `backend_name` (Property)

Returns `"pywal"`

---

## Wallust Backend

**Class:** `color_scheme.backends.wallust.WallustGenerator`
**Module:** `packages/core/src/color_scheme/backends/wallust.py`
**Tool:** External Rust-based tool (wallust)
**Availability:** Only if `wallust` command is in PATH

### Definition

```python
from color_scheme.backends.wallust import WallustGenerator

settings = AppConfig()
backend = WallustGenerator(settings)

if backend.is_available():
    scheme = backend.generate(image_path, config)
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `settings` | `AppConfig` | Application configuration |

### Methods

#### `generate(image_path: Path, config: GeneratorConfig) -> ColorScheme`

Generates color scheme using wallust tool.

**Process:**
1. Validate image file exists and is readable
2. Get backend-specific settings from config
3. Run: `wallust run <image> --backend <type> -s -T -q`
   - `run` = generate colors
   - `--backend` = color extraction backend
   - `-s` = skip setting terminal sequences
   - `-T` = skip templating
   - `-q` = quiet mode
4. Read colors from wallust cache directory (`~/.cache/wallust/`)
5. Parse color file output
6. Convert to ColorScheme object
7. Return ColorScheme

**Parameters:**
- `image_path` (`Path`): Path to image file
- `config` (`GeneratorConfig`): Configuration (includes backend_type setting)

**Returns:** `ColorScheme` with 16 colors

**Raises:**
- `BackendNotAvailableError` - `wallust` command not found
- `InvalidImageError` - Image file invalid
- `ColorExtractionError` - Wallust extraction fails

**Backend Type:**
- Controlled by `config.backend_options.get("backend_type")` or `settings.backends.wallust.backend_type`
- Default: `"resized"`
- Other options: Wallust supports multiple backends

**Example:**
```python
backend = WallustGenerator(settings)

if backend.is_available():
    config = GeneratorConfig(backend_options={"backend_type": "colorz"})
    scheme = backend.generate(Path("/path/to/image.jpg"), config)
else:
    raise BackendNotAvailableError("wallust", "wallust command not found")
```

#### `is_available() -> bool`

Checks if `wallust` command is in PATH.

```python
import shutil
return shutil.which("wallust") is not None
```

#### `backend_name` (Property)

Returns `"wallust"`

---

## Backend Comparison

| Feature | Custom | Pywal | Wallust |
|---------|--------|-------|---------|
| **Availability** | Always (built-in) | Conditional (external) | Conditional (external) |
| **Language** | Python (PIL + scikit-learn) | Python | Rust |
| **Algorithm** | K-means clustering | Multiple algorithms | Multiple backends |
| **Dependencies** | PIL, scikit-learn | wal CLI tool | wallust CLI tool |
| **Speed** | Fast (200px resize) | Medium | Fast (compiled) |
| **Configurability** | n_clusters, algorithm | backend_algorithm | backend_type |
| **Output** | In-memory | Cache (~/.cache/wal/) | Cache (~/.cache/wallust/) |

---

## Using Backends

### Selecting a Backend

```python
from color_scheme.backends.custom import CustomGenerator
from color_scheme.backends.pywal import PywalGenerator
from color_scheme.backends.wallust import WallustGenerator
from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend

settings = AppConfig()

# By enum
backend_enum = Backend.CUSTOM  # or PYWAL, WALLUST

# Get the right backend class
if backend_enum == Backend.CUSTOM:
    backend = CustomGenerator(settings)
elif backend_enum == Backend.PYWAL:
    backend = PywalGenerator(settings)
elif backend_enum == Backend.WALLUST:
    backend = WallustGenerator(settings)

# Verify it's available before using
backend.ensure_available()
```

### Checking Availability

```python
backends_to_try = [
    PywalGenerator(settings),
    WallustGenerator(settings),
    CustomGenerator(settings),  # Fallback (always available)
]

for backend in backends_to_try:
    if backend.is_available():
        scheme = backend.generate(image_path, config)
        break
```

### Generating Colors

```python
from pathlib import Path
from color_scheme.core.types import GeneratorConfig

backend = CustomGenerator(settings)

config = GeneratorConfig(
    saturation_adjustment=1.2,
    backend_options={"n_clusters": 10}
)

try:
    scheme = backend.generate(
        Path("/path/to/image.jpg"),
        config
    )
    print(f"Generated {len(scheme.colors)} colors")
    print(f"Background: {scheme.background.hex}")
except InvalidImageError as e:
    print(f"Image error: {e}")
except ColorExtractionError as e:
    print(f"Extraction failed: {e}")
```

---

## Error Handling

### InvalidImageError

Raised when image file is invalid.

```python
from color_scheme.core.exceptions import InvalidImageError
from pathlib import Path

try:
    backend.generate(Path("/nonexistent/image.jpg"), config)
except InvalidImageError as e:
    print(f"Invalid image: {e.image_path}")
    print(f"Reason: {e.reason}")
```

### ColorExtractionError

Raised when color extraction fails.

```python
from color_scheme.core.exceptions import ColorExtractionError

try:
    backend.generate(image_path, config)
except ColorExtractionError as e:
    print(f"Backend: {e.backend}")
    print(f"Reason: {e.reason}")
```

### BackendNotAvailableError

Raised when backend is not installed.

```python
from color_scheme.core.exceptions import BackendNotAvailableError

backend = PywalGenerator(settings)
try:
    backend.ensure_available()
except BackendNotAvailableError as e:
    print(f"Backend {e.backend} not available: {e.reason}")
```

---

## Testing

See `packages/core/tests/unit/test_*_backend.py` for implementation examples:

```python
from color_scheme.backends.custom import CustomGenerator
from color_scheme.core.types import GeneratorConfig
from pathlib import Path

# Test generation
backend = CustomGenerator(app_config)
scheme = backend.generate(Path("tests/fixtures/test_image.png"), GeneratorConfig())

assert len(scheme.colors) == 16
assert scheme.backend == "custom"
assert scheme.background.hex.startswith("#")
```

---

## Related Documentation

- [Core Types](types.md) - ColorScheme and Color classes
- [Factory Pattern](factory.md) - How backends are instantiated
- [Settings Schema](../configuration/settings-schema.md) - Backend configuration options
- [CLI Commands](../cli/core-commands.md) - Using backends from CLI
