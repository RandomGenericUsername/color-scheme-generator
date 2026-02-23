# Reference: Core Types

**Module:** `color_scheme.core.types`
**Source:** `packages/core/src/color_scheme/core/types.py`

---

## Color

```python
from color_scheme.core.types import Color
```

A Pydantic model representing a single color in hex and RGB formats.

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `hex` | `str` | Pattern `^#[0-9a-fA-F]{6}$` | Hex color code, e.g. `"#FF5733"`. Must be exactly 7 characters: `#` followed by 6 hexadecimal digits. Case-insensitive. |
| `rgb` | `tuple[int, int, int]` | Each value 0–255 | RGB tuple. Each channel must be an integer in the range 0 to 255 inclusive. |
| `hsl` | `tuple[float, float, float] \| None` | Hue 0–360, Saturation 0–1, Lightness 0–1 | Optional HSL representation. May be `None`. |

### Validation rules

1. **Hex pattern** — `hex` must match `^#[0-9a-fA-F]{6}$`. Any other string raises
   `ValueError`.

2. **RGB range** — each of the three integer values in `rgb` must be 0–255. Values
   outside this range raise `ValueError`.

3. **Hex-RGB consistency** — the hex and RGB values must encode the same color. A
   `Color(hex="#FF5733", rgb=(255, 255, 255))` raises `ValueError` with a message
   matching `"RGB .* does not match hex"`.

```python
# Valid
c = Color(hex="#FF5733", rgb=(255, 87, 51))

# Invalid: hex out of pattern
Color(hex="FF5733", rgb=(255, 87, 51))    # ValueError

# Invalid: RGB value out of range
Color(hex="#FF5733", rgb=(256, 87, 51))   # ValueError

# Invalid: mismatch
Color(hex="#FF5733", rgb=(255, 255, 255)) # ValueError
```

### adjust_saturation

```python
Color.adjust_saturation(factor: float) -> Color
```

Returns a new `Color` with the saturation multiplied by `factor`.

| Factor | Effect |
|--------|--------|
| `0.0` | Fully desaturated (grayscale) |
| `1.0` | No change — returns color with the same hex |
| `2.0` | Double saturation |

The saturation is clamped to [0.0, 1.0] in HLS space before converting back to RGB.
A factor of 1.0 returns a color with an identical hex value.

```python
c = Color(hex="#FF5733", rgb=(255, 87, 51))

same = c.adjust_saturation(1.0)
# same.hex == c.hex

muted = c.adjust_saturation(0.5)
# muted.hex differs from c.hex
```

---

## ColorScheme

```python
from color_scheme.core.types import ColorScheme
```

A Pydantic model representing a complete 16-color palette extracted from an image.

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `background` | `Color` | Required | Primary background color. |
| `foreground` | `Color` | Required | Primary foreground/text color. |
| `cursor` | `Color` | Required | Cursor or selection color. |
| `colors` | `list[Color]` | Exactly 16 items | ANSI terminal colors, indices 0–15. |
| `source_image` | `Path` | Required | Path to the source image. |
| `backend` | `str` | Required | Name of the backend that produced this scheme (`"custom"`, `"pywal"`, or `"wallust"`). |
| `generated_at` | `datetime` | Default: `datetime.now()` | Generation timestamp. |
| `output_files` | `dict[str, Path]` | Default: `{}` | Map of format name to file path, populated by the output manager after writing. |

### Validation rules

The `colors` list must contain **exactly 16** `Color` objects. Providing fewer or more
than 16 raises `ValueError`.

```python
# Invalid: only 15 colors
ColorScheme(
    background=..., foreground=..., cursor=...,
    colors=[c] * 15,  # ValueError
    source_image=Path("image.jpg"), backend="custom",
)
```

### Accessing colors

```python
# Special colors
bg_hex = scheme.background.hex           # e.g. "#1A1A1A"
fg_rgb = scheme.foreground.rgb           # e.g. (232, 232, 232)

# ANSI palette (0–15)
color0 = scheme.colors[0]               # darkest color
color15 = scheme.colors[15]             # brightest color

# All hex values
hex_list = [c.hex for c in scheme.colors]

# Output files (after generation)
if "json" in scheme.output_files:
    json_path = scheme.output_files["json"]
```

---

## GeneratorConfig

```python
from color_scheme.core.types import GeneratorConfig
```

A Pydantic model that holds runtime configuration for a single generation run.

### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `backend` | `Backend \| None` | `None` | Backend enum value. `None` triggers auto-detection. |
| `color_count` | `int` | `16` | Number of colors. Hardcoded to 16; not configurable at runtime. |
| `saturation_adjustment` | `float \| None` | `None` | Saturation factor. `None` means use the value from settings. |
| `output_dir` | `Path \| None` | `None` | Output directory. `None` means use the value from settings. |
| `formats` | `list[ColorFormat] \| None` | `None` | Formats to generate. `None` means use the value from settings. |
| `backend_options` | `dict[str, Any]` | `{}` | Backend-specific options that override settings values. |

### GeneratorConfig.from_settings

```python
@classmethod
GeneratorConfig.from_settings(settings: AppConfig) -> GeneratorConfig
```

Construct a `GeneratorConfig` from an `AppConfig` object. All fields are populated
from the settings object:

- `color_count` is always 16 (hardcoded).
- `backend`, `output_dir`, `formats`, and `saturation_adjustment` come from the
  corresponding settings fields.

```python
from color_scheme.core.types import GeneratorConfig
from color_scheme_settings import load_config

settings = load_config()
config = GeneratorConfig.from_settings(settings)

assert config.color_count == 16
assert config.backend is not None
assert config.output_dir is not None
```

---

## Backend enum

```python
from color_scheme.config.enums import Backend
```

| Value | String | Description |
|-------|--------|-------------|
| `Backend.PYWAL` | `"pywal"` | Pywal backend (requires `wal` binary in PATH) |
| `Backend.WALLUST` | `"wallust"` | Wallust backend (requires `wallust` binary in PATH) |
| `Backend.CUSTOM` | `"custom"` | Built-in Python backend, always available |

---

## ColorFormat enum

```python
from color_scheme.config.enums import ColorFormat
```

| Value | String | Output filename |
|-------|--------|-----------------|
| `ColorFormat.JSON` | `"json"` | `colors.json` |
| `ColorFormat.SH` | `"sh"` | `colors.sh` |
| `ColorFormat.CSS` | `"css"` | `colors.css` |
| `ColorFormat.GTK_CSS` | `"gtk.css"` | `colors.gtk.css` |
| `ColorFormat.YAML` | `"yaml"` | `colors.yaml` |
| `ColorFormat.SEQUENCES` | `"sequences"` | `colors.sequences` |
| `ColorFormat.RASI` | `"rasi"` | `colors.rasi` |
| `ColorFormat.SCSS` | `"scss"` | `colors.scss` |

---

## Verification reference

| BHV | Behavior |
|-----|---------|
| BHV-0012 | `Color` rejects invalid hex pattern and out-of-range RGB |
| BHV-0013 | `Color` rejects mismatched hex and RGB |
| BHV-0014 | `adjust_saturation(1.0)` returns same hex; other factors change hex |
| BHV-0015 | `ColorScheme` requires exactly 16 colors |
| BHV-0016 | `GeneratorConfig.from_settings` populates all fields; `color_count == 16` |
