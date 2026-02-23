# Core Types API

**Scope:** Public API types for color-scheme
**Extracted:** February 3, 2026
**Source:** `packages/core/src/color_scheme/core/types.py`

Complete reference for core data types: `Color`, `ColorScheme`, and `GeneratorConfig`.

---

## Color

**Class:** `color_scheme.core.types.Color`
**Base:** `pydantic.BaseModel`
**Purpose:** Represents a single color in multiple formats (hex, RGB, HSL)

### Definition

```python
from color_scheme.core.types import Color

color = Color(
    hex="#FF5733",
    rgb=(255, 87, 51),
    hsl=None  # Optional, can be calculated
)
```

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-----------|-------------|
| `hex` | `str` | Pattern: `^#[0-9a-fA-F]{6}$` | Hex color code (e.g., "#FF5733") |
| `rgb` | `tuple[int, int, int]` | Each value: 0-255 | RGB tuple with 3 channels |
| `hsl` | `tuple[float, float, float] \| None` | Hue: 0-360, Saturation: 0-1, Lightness: 0-1 | Optional HSL representation |

### Validation

The `Color` class performs automatic validation:

1. **RGB Range Validation** - Each RGB component must be 0-255
   ```python
   # ✓ Valid
   Color(hex="#FF5733", rgb=(255, 87, 51))

   # ✗ Invalid - RGB out of range
   Color(hex="#FF5733", rgb=(256, 87, 51))  # Raises ValueError
   ```

2. **Hex-RGB Consistency** - Hex and RGB values must match
   ```python
   # ✓ Valid - hex and RGB match
   Color(hex="#FF5733", rgb=(255, 87, 51))

   # ✗ Invalid - mismatch
   Color(hex="#FF5733", rgb=(100, 100, 100))  # Raises ValueError
   ```

### Methods

#### `adjust_saturation(factor: float) -> Color`

Adjusts the color's saturation by a multiplier, returning a new `Color` object.

**Parameters:**
- `factor` (`float`): Saturation multiplier
  - `0.0` → fully desaturated (grayscale)
  - `1.0` → original saturation
  - `2.0` → double saturation

**Returns:** New `Color` with adjusted saturation

**Example:**
```python
from color_scheme.core.types import Color

# Original color
color = Color(hex="#FF5733", rgb=(255, 87, 51))

# Increase saturation by 50%
boosted = color.adjust_saturation(1.5)
print(boosted.hex)  # "#FF5733" (adjusted)
print(boosted.rgb)  # Different RGB values due to saturation change

# Decrease saturation by 50%
muted = color.adjust_saturation(0.5)
print(muted.hex)    # Desaturated version
```

**Behavior:**
- Converts RGB (0-255) to HLS (0-1)
- Adjusts saturation component
- Clamps saturation to [0.0, 1.0]
- Converts back to RGB (0-255)
- Returns new `Color` with updated hex and RGB

---

## ColorScheme

**Class:** `color_scheme.core.types.ColorScheme`
**Base:** `pydantic.BaseModel`
**Purpose:** Represents a complete color scheme extracted from an image

### Definition

```python
from color_scheme.core.types import Color, ColorScheme
from pathlib import Path
from datetime import datetime

scheme = ColorScheme(
    background=Color(hex="#1A1A1A", rgb=(26, 26, 26)),
    foreground=Color(hex="#E8E8E8", rgb=(232, 232, 232)),
    cursor=Color(hex="#33FF57", rgb=(51, 255, 87)),
    colors=[
        Color(hex="#000000", rgb=(0, 0, 0)),
        # ... 15 more colors ...
    ],
    source_image=Path("/path/to/image.jpg"),
    backend="custom",
    generated_at=datetime.now(),
)
```

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-----------|-------------|
| `background` | `Color` | Required | Background color |
| `foreground` | `Color` | Required | Foreground/text color |
| `cursor` | `Color` | Required | Cursor/selection color |
| `colors` | `list[Color]` | Exactly 16 items | ANSI terminal colors 0-15 |
| `source_image` | `Path` | Required | Path to source image file |
| `backend` | `str` | Required | Name of backend used ("custom", "pywal", "wallust") |
| `generated_at` | `datetime` | Default: now | Timestamp of generation |
| `output_files` | `dict[str, Path]` | Default: {} | Format → file path (set by OutputManager) |

### Usage

**Accessing colors:**
```python
# Special colors
bg = scheme.background.hex      # "#1A1A1A"
fg = scheme.foreground.rgb      # (232, 232, 232)

# Terminal colors (indexed 0-15)
red = scheme.colors[1]          # ANSI red color
white = scheme.colors[15]       # ANSI white color

# Get all colors in hex format
hex_colors = [c.hex for c in scheme.colors]

# Get all colors in RGB format
rgb_colors = [c.rgb for c in scheme.colors]
```

**Checking output files:**
```python
# Check what formats were generated
if "json" in scheme.output_files:
    json_path = scheme.output_files["json"]
    print(f"JSON output: {json_path}")

# Get all generated files
for format_name, filepath in scheme.output_files.items():
    print(f"{format_name}: {filepath}")
```

### Example Output

```python
ColorScheme(
    background=Color(hex='#1A1A1A', rgb=(26, 26, 26), hsl=None),
    foreground=Color(hex='#E8E8E8', rgb=(232, 232, 232), hsl=None),
    cursor=Color(hex='#33FF57', rgb=(51, 255, 87), hsl=None),
    colors=[
        Color(hex='#000000', rgb=(0, 0, 0), hsl=None),
        Color(hex='#FF0000', rgb=(255, 0, 0), hsl=None),
        # ... 14 more colors ...
    ],
    source_image=PosixPath('/path/to/image.jpg'),
    backend='custom',
    generated_at=datetime.datetime(2024, 2, 3, 14, 30, 45, 123456),
    output_files={
        'json': PosixPath('/output/colors.json'),
        'sh': PosixPath('/output/colors.sh'),
        # ... other formats ...
    }
)
```

---

## GeneratorConfig

**Class:** `color_scheme.core.types.GeneratorConfig`
**Base:** `pydantic.BaseModel`
**Purpose:** Runtime configuration for color scheme generation

### Definition

```python
from color_scheme.core.types import GeneratorConfig
from color_scheme.config.enums import Backend, ColorFormat
from pathlib import Path

config = GeneratorConfig(
    backend=Backend.CUSTOM,
    color_count=16,
    saturation_adjustment=1.0,
    output_dir=Path("/output"),
    formats=[ColorFormat.JSON, ColorFormat.SH, ColorFormat.CSS],
    backend_options={"n_clusters": 8}
)
```

### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `backend` | `Backend \| None` | None | Backend to use (pywal, wallust, custom) |
| `color_count` | `int` | 16 | Number of colors (hardcoded, not configurable) |
| `saturation_adjustment` | `float \| None` | None | Saturation adjustment factor |
| `output_dir` | `Path \| None` | None | Output directory for generated files |
| `formats` | `list[ColorFormat] \| None` | None | Output formats to generate |
| `backend_options` | `dict[str, Any]` | {} | Backend-specific options (overrides settings) |

### Class Methods

#### `from_settings(settings: AppConfig, **overrides: Any) -> GeneratorConfig`

Creates a `GeneratorConfig` from `AppConfig` settings with optional runtime overrides.

**Parameters:**
- `settings` (`AppConfig`): Application configuration object
- `**overrides`: Keyword arguments to override settings values

**Returns:** `GeneratorConfig` instance

**Example:**
```python
from color_scheme.config.config import AppConfig
from color_scheme.core.types import GeneratorConfig
from color_scheme.config.enums import Backend, ColorFormat

# Load settings
settings = AppConfig()

# Create config from settings with overrides
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.PYWAL,
    saturation_adjustment=1.2,
    formats=[ColorFormat.JSON]
)
```

**Behavior:**
- Uses `settings.generation.default_backend` if backend not specified
- Uses `settings.generation.saturation_adjustment` if not overridden
- Uses `settings.output.directory` if output_dir not specified
- Uses `settings.output.formats` if formats not specified
- color_count is always 16 (hardcoded)

#### `get_backend_settings(settings: AppConfig) -> dict[str, Any]`

Retrieves backend-specific settings merged with runtime backend options.

**Parameters:**
- `settings` (`AppConfig`): Application configuration object

**Returns:** Dictionary of merged backend settings

**Example:**
```python
# Get settings for the configured backend
config = GeneratorConfig(
    backend=Backend.CUSTOM,
    backend_options={"n_clusters": 8}
)

merged = config.get_backend_settings(settings)
# Returns: {
#     "algorithm": "kmeans",     # from settings.backends.custom
#     "n_clusters": 8,            # from backend_options (overrides)
#     ... other settings ...
# }
```

**Behavior:**
- Looks up backend-specific settings from AppConfig
- For PYWAL: uses `settings.backends.pywal`
- For WALLUST: uses `settings.backends.wallust`
- For CUSTOM: uses `settings.backends.custom`
- Merges base settings with backend_options (options take precedence)
- Returns empty dict if backend not recognized

---

## Color Format Details

### Hex Format

- **Pattern:** `^#[0-9a-fA-F]{6}$`
- **Example:** `#FF5733`
- **Length:** 7 characters (# + 6 hex digits)
- **Case:** Uppercase or lowercase accepted (uppercase recommended)

### RGB Format

- **Type:** `tuple[int, int, int]`
- **Range:** Each value 0-255
- **Components:** (Red, Green, Blue)
- **Example:** `(255, 87, 51)`

### HSL Format

- **Type:** `tuple[float, float, float]`
- **Components:** (Hue, Saturation, Lightness)
- **Hue Range:** 0-360 degrees
- **Saturation Range:** 0.0-1.0 (0% to 100%)
- **Lightness Range:** 0.0-1.0 (0% to 100%)
- **Example:** `(10.0, 1.0, 0.5)`

---

## Usage Patterns

### Creating Colors Programmatically

```python
from color_scheme.core.types import Color

# From hex
color = Color(hex="#FF5733", rgb=(255, 87, 51))

# Validating user input
try:
    user_color = Color(hex=user_input_hex, rgb=user_input_rgb)
except ValueError as e:
    print(f"Invalid color: {e}")
```

### Working with ColorScheme

```python
from color_scheme.core.types import ColorScheme

# Accessing special colors
background_rgb = scheme.background.rgb
foreground_hex = scheme.foreground.hex

# Iterating through palette
for i, color in enumerate(scheme.colors):
    print(f"Color {i}: {color.hex}")

# Finding output files
if "json" in scheme.output_files:
    with open(scheme.output_files["json"]) as f:
        data = json.load(f)
```

### Building GeneratorConfig

```python
from color_scheme.core.types import GeneratorConfig
from color_scheme.config.enums import Backend, ColorFormat

# Method 1: From settings
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.CUSTOM
)

# Method 2: Direct instantiation
config = GeneratorConfig(
    backend=Backend.PYWAL,
    output_dir=Path("/custom/output"),
    formats=[ColorFormat.JSON, ColorFormat.SH],
    backend_options={"palette": "dark"}
)

# Get backend settings
backend_config = config.get_backend_settings(settings)
```

---

## Testing

See `packages/core/tests/unit/test_custom_backend.py` for usage examples in tests:

```python
from color_scheme.core.types import GeneratorConfig, Color

# Generate from image
generator = CustomGenerator(app_config)
scheme = generator.generate(test_image_path, GeneratorConfig())

# Verify structure
assert len(scheme.colors) == 16
assert scheme.background.hex.startswith("#")
assert scheme.backend == "custom"
```

---

## Related Documentation

- [ColorScheme Backends](backends.md) - How backends generate ColorScheme
- [Output Manager](output.md) - How ColorScheme is written to files
- [Settings Schema](../configuration/settings-schema.md) - AppConfig structure
