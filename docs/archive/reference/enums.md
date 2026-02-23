# Enumeration Reference

**Scope:** All enumeration values used throughout color-scheme
**Extracted:** February 2, 2026
**Source:** `packages/core/src/color_scheme/config/enums.py`

Complete reference for all enum types and their values.

---

## Quick Reference

| Enum | Values | Purpose |
|------|--------|---------|
| `Backend` | `pywal`, `wallust`, `custom` | Color extraction backend selection |
| `ColorAlgorithm` | `kmeans`, `dominant` | Custom backend algorithms |
| `ColorFormat` | 8 values (json, sh, css, etc.) | Output format selection |

---

## Backend Enum

### Purpose
Specifies which color extraction backend to use for analyzing images.

### Values

| Value | Python Constant | Availability | Description |
|-------|-----------------|--------------|-------------|
| `pywal` | `Backend.PYWAL` | If installed | Python-based color extraction using multiple algorithms |
| `wallust` | `Backend.WALLUST` | If installed | Rust-based color extraction utility |
| `custom` | `Backend.CUSTOM` | Always | Built-in Python K-means clustering |

### Implementation

```python
class Backend(str, Enum):
    """Available color extraction backends."""
    PYWAL = "pywal"
    WALLUST = "wallust"
    CUSTOM = "custom"
```

### Usage

**In configuration:**
```toml
[generation]
default_backend = "pywal"
```

**In CLI:**
```bash
color-scheme-core generate image.jpg -b wallust
color-scheme-core generate image.jpg -b custom
```

**In Python:**
```python
from color_scheme.config.enums import Backend

backend = Backend.PYWAL
if backend == Backend.PYWAL:
    # Handle pywal backend
    pass
```

### Backend Characteristics

| Backend | External Dependency | Performance | Color Quality | Notes |
|---------|-------------------|-------------|---------------|-------|
| **pywal** | Yes (pywal binary) | Medium | Excellent | Multiple algorithms available, requires installation |
| **wallust** | Yes (wallust binary) | Fast | Good | Rust-based, CLI-only |
| **custom** | No | Medium | Good | K-means clustering, always available |

### Auto-Detection Order

When backend is not specified, tried in this order:

1. `pywal` - if `wal` binary is in PATH and executable
2. `wallust` - if `wallust` binary is in PATH and executable
3. `custom` - always available (built-in Python implementation)

### Backend Availability

**Check availability:**
```bash
# Pywal
which wal && wal --version

# Wallust
which wallust && wallust --version

# Custom
# Always available, no check needed
```

### Backend Installation

| Backend | Installation |
|---------|--------------|
| pywal | `pip install pywal` or package manager |
| wallust | `cargo install wallust` or package manager |
| custom | Built-in, no installation needed |

---

## ColorAlgorithm Enum

### Purpose
Specifies the color extraction algorithm for the custom backend.

### Values

| Value | Python Constant | Status | Description |
|-------|-----------------|--------|-------------|
| `kmeans` | `ColorAlgorithm.KMEANS` | ✅ **Implemented** | K-means clustering to find dominant color groups |
| `dominant` | `ColorAlgorithm.DOMINANT` | ⚠️ **NOT IMPLEMENTED** | Dominant color extraction (not available) |

### Implementation

```python
class ColorAlgorithm(str, Enum):
    """Custom backend color extraction algorithms."""
    KMEANS = "kmeans"
    DOMINANT = "dominant"
```

### Important Notes

⚠️ **WARNING:** The `dominant` algorithm is **NOT IMPLEMENTED**. Attempting to use it will raise an error:

```python
# This will raise an error
ColorAlgorithm.DOMINANT  # Valid enum value, but not implemented in backend
```

### Usage

**In configuration:**
```toml
[backends.custom]
algorithm = "kmeans"  # Only valid value
```

**In CLI:**
The algorithm is not directly selectable from CLI. Use configuration.

**In Python:**
```python
from color_scheme.config.enums import ColorAlgorithm

algorithm = ColorAlgorithm.KMEANS
if algorithm == ColorAlgorithm.KMEANS:
    # Handle k-means clustering
    pass
```

### K-means Clustering Details

The **only implemented** algorithm uses K-means clustering:

- **What it does:** Identifies `n_clusters` dominant color groups in the image
- **How it works:** Iteratively groups similar colors together
- **Parameter:** `backends.custom.n_clusters` (default: 16)
- **Output:** Up to 16 ANSI terminal colors plus background/foreground/cursor

### Why Dominant Not Implemented

The `dominant` algorithm was planned but not implemented in the current version. Use `kmeans` instead, which provides similar results.

---

## ColorFormat Enum

### Purpose
Specifies output file formats for generated color schemes.

### Values

| Value | Python Constant | File | Use Case | Content Type |
|-------|-----------------|------|----------|--------------|
| `json` | `ColorFormat.JSON` | `colors.json` | API/programmatic access | JSON object |
| `sh` | `ColorFormat.SH` | `colors.sh` | Shell scripts/bash | Shell variables |
| `css` | `ColorFormat.CSS` | `colors.css` | Web CSS | CSS custom properties |
| `gtk.css` | `ColorFormat.GTK_CSS` | `colors.gtk.css` | GTK theming | GTK definitions |
| `yaml` | `ColorFormat.YAML` | `colors.yaml` | Configuration files | YAML format |
| `sequences` | `ColorFormat.SEQUENCES` | `colors.sequences` | Terminal escape codes | OSC sequences |
| `rasi` | `ColorFormat.RASI` | `colors.rasi` | Rofi theming | Rofi variables |
| `scss` | `ColorFormat.SCSS` | `colors.scss` | Sass/SCSS | Sass variables |

### Implementation

```python
class ColorFormat(str, Enum):
    """Output format types."""
    JSON = "json"
    SH = "sh"
    CSS = "css"
    GTK_CSS = "gtk.css"
    YAML = "yaml"
    SEQUENCES = "sequences"
    RASI = "rasi"
    SCSS = "scss"
```

### Total Formats

**8 output formats** are defined and all are implemented.

### Usage

**In configuration:**
```toml
[output]
formats = ["json", "sh", "css"]  # Partial list
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]  # All
```

**In CLI:**
```bash
# Multiple formats
color-scheme-core generate image.jpg -f json -f css -f scss

# Default (all formats)
color-scheme-core generate image.jpg
```

**In Python:**
```python
from color_scheme.config.enums import ColorFormat

formats = [ColorFormat.JSON, ColorFormat.CSS]
```

### File Output Mapping

| Format | Template | Output File | Example Content |
|--------|----------|------------|---|
| `json` | `colors.json.j2` | `colors.json` | `{"colors": [...], "metadata": {...}}` |
| `sh` | `colors.sh.j2` | `colors.sh` | `export COLOR_0="#FF5733"` |
| `css` | `colors.css.j2` | `colors.css` | `:root { --color-0: #FF5733; }` |
| `gtk.css` | `colors.gtk.css.j2` | `colors.gtk.css` | `@define-color color0 #FF5733;` |
| `yaml` | `colors.yaml.j2` | `colors.yaml` | `colors:\n  0: "#FF5733"` |
| `sequences` | `colors.sequences.j2` | `colors.sequences` | `\x1b]4;0;#FF5733\x1b\\` |
| `rasi` | `colors.rasi.j2` | `colors.rasi` | `color0: #FF5733;` |
| `scss` | `colors.scss.j2` | `colors.scss` | `$color-0: #FF5733;` |

### All Templates Available

All 8 template files exist in the `templates/` directory and are **100% implemented**.

### Format Details

#### JSON (`json`)
- **Use case:** APIs, programmatic access, data interchange
- **Features:** Includes metadata (source, backend, generation time), all color modes
- **Example:**
```json
{
  "source_image": "/path/to/image.jpg",
  "backend": "pywal",
  "colors": [
    {"hex": "#FF5733", "rgb": [255, 87, 51]}
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

#### Shell (`sh`)
- **Use case:** Bash scripts, shell environments
- **Features:** Bash variables with `export` for environment injection
- **Example:**
```bash
export COLOR_0="#FF5733"
export COLOR_1="#33FF57"
export BACKGROUND="#1A1A1A"
```

#### CSS (`css`)
- **Use case:** Web CSS, CSS frameworks
- **Features:** CSS custom properties (variables) for modern browsers
- **Example:**
```css
:root {
  --color-0: #FF5733;
  --color-1: #33FF57;
  --background: #1A1A1A;
}
```

#### GTK CSS (`gtk.css`)
- **Use case:** GTK application theming, GNOME desktops
- **Features:** GTK `@define-color` syntax for theme definitions
- **Example:**
```css
@define-color color0 #FF5733;
@define-color color1 #33FF57;
@define-color background #1A1A1A;
```

#### YAML (`yaml`)
- **Use case:** Configuration files, data serialization
- **Features:** YAML format for structured data
- **Example:**
```yaml
colors:
  0: "#FF5733"
  1: "#33FF57"
background: "#1A1A1A"
```

#### Terminal Sequences (`sequences`)
- **Use case:** Terminal color configuration, iTerm2, alacritty
- **Features:** OSC (Operating System Command) escape sequences
- **Format:** `\x1b]<command>;<color>\x1b\\`
- **Example:**
```
\x1b]4;0;#FF5733\x1b\\
\x1b]4;1;#33FF57\x1b\\
\x1b]10;#FF5733\x1b\\
```

#### Rofi Configuration (`rasi`)
- **Use case:** Rofi/dmenu theming, application launcher styling
- **Features:** Rofi theme variable syntax
- **Example:**
```rasi
color0: #FF5733;
color1: #33FF57;
background: #1A1A1A;
```

#### Sass/SCSS (`scss`)
- **Use case:** Sass stylesheets, SCSS variable imports
- **Features:** Sass `$variable` syntax
- **Example:**
```scss
$color-0: #FF5733;
$color-1: #33FF57;
$background: #1A1A1A;
```

### Format Selection Guidance

| Use Case | Recommended Format | Alternative |
|----------|-------------------|------------|
| Shell scripting | `sh` | `json` |
| Web development | `css` | `scss` |
| GTK/GNOME theming | `gtk.css` | `css` |
| Terminal emulator | `sequences` | `sh` |
| Application launcher | `rasi` | `sh` |
| Configuration files | `yaml` | `json` |
| Sass project | `scss` | `css` |
| General purpose | `json` | `yaml` |

---

## Enum to String Conversion

All enums inherit from `str`, allowing direct string comparisons:

```python
from color_scheme.config.enums import Backend, ColorFormat

# Direct string comparison
backend_str = "pywal"
if backend_str == Backend.PYWAL.value:
    print("Using pywal")

# Enum comparison
backend = Backend.PYWAL
if backend == Backend.PYWAL:
    print("Using pywal")

# Both work identically
assert Backend.PYWAL.value == "pywal"
assert str(Backend.PYWAL) == "pywal"
```

---

## Enum String Values

### Backend String Values
```python
Backend.PYWAL.value     # → "pywal"
Backend.WALLUST.value   # → "wallust"
Backend.CUSTOM.value    # → "custom"
```

### ColorAlgorithm String Values
```python
ColorAlgorithm.KMEANS.value     # → "kmeans"
ColorAlgorithm.DOMINANT.value   # → "dominant"
```

### ColorFormat String Values
```python
ColorFormat.JSON.value          # → "json"
ColorFormat.SH.value            # → "sh"
ColorFormat.CSS.value           # → "css"
ColorFormat.GTK_CSS.value       # → "gtk.css"
ColorFormat.YAML.value          # → "yaml"
ColorFormat.SEQUENCES.value     # → "sequences"
ColorFormat.RASI.value          # → "rasi"
ColorFormat.SCSS.value          # → "scss"
```

---

## Enum Validation

All enum fields in configuration and CLI are validated against these definitions:

```python
# Valid
Backend("pywal")                    # → Backend.PYWAL
ColorFormat("css")                  # → ColorFormat.CSS

# Invalid (raises ValueError)
Backend("invalid")                  # ValueError: 'invalid' is not a valid Backend
ColorAlgorithm("nonexistent")       # ValueError: 'nonexistent' is not a valid ColorAlgorithm
```

---

## Enum to CLI Representation

In CLI help text, enums appear as choices:

```
--backend  -b  [pywal|wallust|custom]
--format   -f  [json|sh|css|gtk.css|yaml|sequences|rasi|scss]
```

The `|` separates valid options.

---

## Python Import Reference

```python
# Import individual enums
from color_scheme.config.enums import Backend
from color_scheme.config.enums import ColorAlgorithm
from color_scheme.config.enums import ColorFormat

# Import all
from color_scheme.config.enums import Backend, ColorAlgorithm, ColorFormat

# Iterate over all values
for backend in Backend:
    print(backend.value)  # pywal, wallust, custom

# Check if string is valid
if "pywal" in [b.value for b in Backend]:
    print("Valid backend")
```

---

## Case Sensitivity

All enum values are **lowercase** and **case-sensitive** in configuration/CLI:

| Valid | Invalid |
|-------|---------|
| `backend = "pywal"` | `backend = "PYWAL"` |
| `format = "json"` | `format = "JSON"` |
| `-b custom` | `-b CUSTOM` |

---

## Enum Count Summary

| Enum | Count | All Implemented |
|------|-------|-----------------|
| Backend | 3 | Yes (2 if dependencies missing) |
| ColorAlgorithm | 2 | No (1 implemented, 1 planned) |
| ColorFormat | 8 | Yes ✅ |
| **Total** | **13** | Mostly (12/13 ≈ 92%) |

---

## Version Information

These enumerations are stable in version **0.1.0** and beyond.

Future versions may add new enum values but will not remove existing ones (backward compatibility).

---

## Related Documentation

- [Settings Schema](settings-schema.md) - Using enums in configuration
- [Default Values](defaults.md) - Default enum selections
- [Core CLI Commands](../cli/core-commands.md) - CLI enum usage
- [Configuration Reference](../configuration/settings-schema.md) - Enum in config
