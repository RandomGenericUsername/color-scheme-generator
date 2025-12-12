# Configuration Guide

Complete reference for configuring colorscheme-generator via `settings.toml`.

---

## Table of Contents

- [Configuration File Location](#configuration-file-location)
- [Configuration Structure](#configuration-structure)
- [Generation Settings](#generation-settings)
- [Backend Settings](#backend-settings)
- [Output Settings](#output-settings)
- [Template Settings](#template-settings)
- [Environment Variables](#environment-variables)
- [Configuration Precedence](#configuration-precedence)

---

## Configuration File Location

### Default Location

```
~/.config/colorscheme-generator/settings.toml
```

### Custom Location

Set via environment variable:

```bash
export COLORSCHEME_SETTINGS_FILE=/path/to/custom/settings.toml
colorscheme-gen generate image.png
```

### Bundled Default

If no user config exists, the tool uses the bundled default:

```
core/src/colorscheme_generator/config/settings.toml
```

---

## Configuration Structure

```toml
# Generation defaults
[generation]
default_backend = "pywal"

saturation_adjustment = 1.0

# Backend-specific settings
[backends.pywal]
backend_algorithm = "wal"

[backends.wallust]
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16

# Output settings
[output]
directory = "$HOME/.cache/colorscheme"
formats = ["json", "sh", "css", "yaml"]

# Template settings
[templates]
directory = ""

```

---

## Generation Settings

### `[generation]`

Controls default behavior for color scheme generation.

#### `default_backend`

**Type**: String  
**Default**: `"pywal"`  
**Options**: `"pywal"`, `"wallust"`, `"custom"`, `"auto"`

**Description**: Default backend to use when not specified via CLI.

**Example**:
```toml
[generation]
default_backend = "wallust"  # Use wallust by default
```

**CLI Override**:
```bash
colorscheme-gen generate image.png --backend custom
```

---

#### `default_color_count`

**Note**: Color count is hardcoded at 16 (standard terminal ANSI colors) and cannot be configured.

---

#### `saturation_adjustment`

**Type**: Float  
**Default**: `1.0`  
**Range**: `0.0` - `2.0`

**Description**: Saturation multiplier applied to extracted colors.

**Values**:
- `0.0`: Grayscale (no saturation)
- `1.0`: Unchanged (original colors)
- `2.0`: Maximum saturation

**Example**:
```toml
[generation]
saturation_adjustment = 1.3  # Slightly more vibrant
```

**CLI Override**:
```bash
colorscheme-gen generate image.png --saturation 1.5
```

**Use Cases**:
- **Vibrant themes**: `1.3` - `1.8`
- **Muted themes**: `0.5` - `0.8`
- **Grayscale themes**: `0.0`

---

## Backend Settings

### `[backends.pywal]`

Settings for the pywal backend.

#### `backend_algorithm`

**Type**: String  
**Default**: `"wal"`  
**Options**: `"wal"`, `"colorz"`, `"colorthief"`, `"haishoku"`, `"schemer2"`

**Description**: Pywal color extraction algorithm.

**Algorithm Comparison**:

| Algorithm | Speed | Quality | Best For |
|-----------|-------|---------|----------|
| `wal` | Fast | Good | General use (default) |
| `colorz` | Medium | Good | Vibrant colors |
| `colorthief` | Slow | Excellent | Accuracy |
| `haishoku` | Fast | Good | Pastel colors |
| `schemer2` | Medium | Good | Experimental |

**Example**:
```toml
[backends.pywal]
backend_algorithm = "colorthief"  # Use colorthief for accuracy
```

**CLI Override**:
```bash
colorscheme-gen generate image.png --backend pywal --pywal-algorithm colorz
```

**Dependencies**:
```bash
# Install algorithm dependencies
pip install colorz colorthief haishoku
```

---

### `[backends.wallust]`

Settings for the wallust backend.

#### `backend_type`

**Type**: String  
**Default**: `"resized"`  
**Options**: `"resized"`, `"full"`, `"thumb"`, `"fastresize"`, `"wal"`

**Description**: Wallust backend processing type.

**Backend Type Comparison**:

| Type | Speed | Quality | Memory | Best For |
|------|-------|---------|--------|----------|
| `resized` | Fast | Good | Low | General use (default) |
| `full` | Slow | Excellent | High | Maximum quality |
| `thumb` | Very Fast | Fair | Very Low | Quick previews |
| `fastresize` | Fast | Good | Low | Balanced |
| `wal` | Medium | Good | Medium | Pywal compatibility |

**Example**:
```toml
[backends.wallust]
backend_type = "full"  # Maximum quality
```

**CLI Override**:
```bash
colorscheme-gen generate image.png --backend wallust --wallust-backend full
```

---

### `[backends.custom]`

Settings for the custom (built-in) backend.

#### `algorithm`

**Type**: String  
**Default**: `"kmeans"`  
**Options**: `"kmeans"`, `"minibatch"`

**Description**: Clustering algorithm for color extraction.

**Algorithm Comparison**:

| Algorithm | Speed | Quality | Best For |
|-----------|-------|---------|----------|
| `kmeans` | Medium | Good | General use (default) |
| `minibatch` | Fast | Good | Large images |

**Example**:
```toml
[backends.custom]
algorithm = "minibatch"  # Faster for large images
```

**CLI Override**:
```bash
colorscheme-gen generate image.png --backend custom --custom-algorithm minibatch
```

---

#### `n_clusters`

**Type**: Integer  
**Default**: `16`  
**Range**: `8` - `256`

**Description**: Number of color clusters for K-means algorithm.

**Example**:
```toml
[backends.custom]
n_clusters = 20  # Extract 20 colors, then select best 16
```

**CLI Override**:
```bash
colorscheme-gen generate image.png --backend custom --custom-clusters 20
```

**Note**: While you can extract more than 16 colors, the final color scheme will still contain exactly 16 colors (the best ones are selected).

---

## Output Settings

### `[output]`

Controls where and how color schemes are written.

#### `directory`

**Type**: String (path)  
**Default**: `"$HOME/.cache/colorscheme"`

**Description**: Output directory for generated files. Supports environment variable expansion.

**Example**:
```toml
[output]
directory = "$HOME/.config/colors"
```

**CLI Override**:
```bash
colorscheme-gen generate image.png --output-dir ~/my-colors
```

**Environment Variable Expansion**:
- `$HOME`: User home directory
- `$USER`: Username
- `$XDG_CONFIG_HOME`: XDG config directory
- Any other environment variable

---

#### `formats`

**Type**: Array of strings  
**Default**: `["json", "sh", "css", "yaml"]`  
**Options**: `"json"`, `"sh"`, `"css"`, `"gtk.css"`, `"yaml"`, `"toml"`, `"sequences"`, `"rasi"`

**Description**: Output file formats to generate.

**Example**:
```toml
[output]
formats = ["json", "css", "sh", "sequences"]
```

**CLI Override**:
```bash
colorscheme-gen generate image.png --formats json css sh
```

**Format Descriptions**:
- `json`: Structured JSON data
- `sh`: Shell script with variables
- `css`: CSS with custom properties
- `gtk.css`: GTK theme file
- `yaml`: YAML configuration
- `toml`: TOML configuration
- `sequences`: Terminal escape sequences
- `rasi`: Rofi theme file

---

## Template Settings

### `[templates]`

Controls template rendering behavior.

#### `directory`

**Type**: String (path)
**Default**: `""` (empty = use built-in templates)

**Description**: Custom template directory. If empty, uses built-in templates.

**Example**:
```toml
[templates]
directory = "$HOME/.config/colorscheme-generator/templates"
```

**CLI Override**:
```bash
colorscheme-gen generate image.png --template-dir ~/.config/templates
```

**Custom Template Structure**:
```
~/.config/colorscheme-generator/templates/
├── colors.json.j2
├── colors.css.j2
├── colors.sh.j2
└── my-custom-format.j2
```

See **[Templates Guide](templates.md)** for creating custom templates.

---

#### `strict_mode`

**Note**: Template strict mode is always enabled. Undefined variables in templates will raise an error. This ensures template errors are caught immediately rather than silently producing broken output.

---

## Environment Variables

### Supported Variables

All settings can be overridden via environment variables using the `COLORSCHEME_` prefix:

```bash
# Override backend
export COLORSCHEME_GENERATION__DEFAULT_BACKEND=wallust

# Override saturation
export COLORSCHEME_GENERATION__SATURATION_ADJUSTMENT=1.5

# Override output directory
export COLORSCHEME_OUTPUT__DIRECTORY=/tmp/colors

# Override pywal algorithm
export COLORSCHEME_BACKENDS__PYWAL__BACKEND_ALGORITHM=colorz
```

### Naming Convention

1. Prefix: `COLORSCHEME_`
2. Section: `GENERATION__`, `OUTPUT__`, `BACKENDS__`, `TEMPLATES__`
3. Subsection (if any): `PYWAL__`, `WALLUST__`, `CUSTOM__`
4. Setting: `DEFAULT_BACKEND`, `SATURATION_ADJUSTMENT`, etc.
5. Separator: Double underscore `__`

### Examples

```bash
# Generation settings
export COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom
export COLORSCHEME_GENERATION__SATURATION_ADJUSTMENT=1.3

# Backend settings
export COLORSCHEME_BACKENDS__PYWAL__BACKEND_ALGORITHM=colorthief
export COLORSCHEME_BACKENDS__WALLUST__BACKEND_TYPE=full
export COLORSCHEME_BACKENDS__CUSTOM__ALGORITHM=minibatch

# Output settings
export COLORSCHEME_OUTPUT__DIRECTORY=$HOME/colors
export COLORSCHEME_OUTPUT__FORMATS='["json","css","sh"]'

# Template settings

```

---

## Configuration Precedence

Settings are loaded in the following order (later overrides earlier):

```
1. Built-in defaults (defaults.py)
   ↓
2. User settings file (settings.toml)
   ↓
3. Environment variables (COLORSCHEME_*)
   ↓
4. CLI arguments (--backend, --saturation, etc.)
```

### Example

Given:
```toml
# settings.toml
[generation]
saturation_adjustment = 1.2
```

```bash
export COLORSCHEME_GENERATION__SATURATION_ADJUSTMENT=1.5
```

```bash
colorscheme-gen generate image.png --saturation 1.8
```

**Result**: Saturation = `1.8` (CLI wins)

---

## Complete Configuration Example

```toml
# ~/.config/colorscheme-generator/settings.toml

# ============================================================================
# Generation Settings
# ============================================================================
[generation]
# Backend to use by default
# Options: "pywal", "wallust", "custom", "auto"
default_backend = "wallust"


# Saturation adjustment multiplier
# 0.0 = grayscale, 1.0 = unchanged, 2.0 = maximum
saturation_adjustment = 1.3

# ============================================================================
# Backend Settings
# ============================================================================

# Pywal backend (requires: pip install pywal)
[backends.pywal]
# Color extraction algorithm
# Options: "wal", "colorz", "colorthief", "haishoku", "schemer2"
backend_algorithm = "colorthief"

# Wallust backend (requires: cargo install wallust)
[backends.wallust]
# Backend processing type
# Options: "resized", "full", "thumb", "fastresize", "wal"
backend_type = "full"

# Custom backend (built-in, no dependencies)
[backends.custom]
# Clustering algorithm
# Options: "kmeans", "minibatch"
algorithm = "kmeans"

# Number of color clusters
n_clusters = 16

# ============================================================================
# Output Settings
# ============================================================================
[output]
# Output directory (supports environment variables)
directory = "$HOME/.config/colors"

# Output formats to generate
# Options: "json", "sh", "css", "gtk.css", "yaml", "toml", "sequences", "rasi"
formats = ["json", "sh", "css", "yaml", "sequences"]

# ============================================================================
# Template Settings
# ============================================================================
[templates]
# Custom template directory (empty = use built-in templates)
directory = ""


```

---

## Validation Rules

### Saturation Adjustment

```python
# Must be between 0.0 and 2.0
0.0 <= saturation_adjustment <= 2.0
```

**Invalid**:
```toml
saturation_adjustment = 3.0  # ❌ Too high
saturation_adjustment = -0.5  # ❌ Negative
```

**Valid**:
```toml
saturation_adjustment = 0.0   # ✅ Grayscale
saturation_adjustment = 1.0   # ✅ Unchanged
saturation_adjustment = 2.0   # ✅ Maximum
```

### Backend Algorithm

```python
# Must be one of the allowed values
backend_algorithm in ["wal", "colorz", "colorthief", "haishoku", "schemer2"]
```

**Invalid**:
```toml
backend_algorithm = "invalid"  # ❌ Not allowed
```

**Valid**:
```toml
backend_algorithm = "wal"        # ✅
backend_algorithm = "colorthief" # ✅
```

### Output Directory

```python
# Must be a valid path (created if doesn't exist)
# Supports environment variable expansion
```

**Valid**:
```toml
directory = "$HOME/.cache/colorscheme"           # ✅
directory = "/tmp/colors"                        # ✅
directory = "$XDG_CONFIG_HOME/colors"            # ✅
directory = "~/colors"                           # ✅ (expanded)
```

### Output Formats

```python
# Must be a list of valid format names
formats in ["json", "sh", "css", "gtk.css", "yaml", "toml", "sequences", "rasi"]
```

**Invalid**:
```toml
formats = ["json", "invalid"]  # ❌ "invalid" not allowed
```

**Valid**:
```toml
formats = ["json"]                          # ✅ Single format
formats = ["json", "css", "sh"]             # ✅ Multiple formats
formats = ["json", "sh", "css", "yaml", "toml", "sequences"]  # ✅ Many formats
```

---

## Troubleshooting Configuration

### Configuration Not Loading

**Problem**: Changes to `settings.toml` not taking effect.

**Solutions**:
1. Check file location:
   ```bash
   ls -l ~/.config/colorscheme-generator/settings.toml
   ```
2. Verify TOML syntax:
   ```bash
   python -c "import tomli; tomli.load(open('settings.toml', 'rb'))"
   ```
3. Check for environment variable overrides:
   ```bash
   env | grep COLORSCHEME_
   ```

### Validation Errors

**Problem**: `ValidationError` when loading settings.

**Solutions**:
1. Check error message for specific field
2. Verify value is in allowed range/options
3. Check data type (string vs. number vs. boolean)
4. Use default settings as reference

### Path Expansion Not Working

**Problem**: `$HOME` not expanded in paths.

**Solutions**:
1. Ensure variable is set:
   ```bash
   echo $HOME
   ```
2. Use absolute path instead:
   ```toml
   directory = "/home/username/.cache/colorscheme"
   ```
3. Check Dynaconf version (should be ≥3.0)

---

## Best Practices

### 1. Use Version Control

Keep your settings in version control:

```bash
# Add to dotfiles
cp ~/.config/colorscheme-generator/settings.toml ~/dotfiles/
ln -s ~/dotfiles/settings.toml ~/.config/colorscheme-generator/settings.toml
```

### 2. Document Custom Settings

Add comments to explain your choices:

```toml
[generation]
# Using wallust for better performance on my system
default_backend = "wallust"

# Slightly more vibrant colors for my dark theme
saturation_adjustment = 1.3
```

### 3. Use Environment Variables for Secrets

Don't hardcode sensitive paths:

```toml
# ❌ Bad
directory = "/home/myusername/.cache/colorscheme"

# ✅ Good
directory = "$HOME/.cache/colorscheme"
```

### 4. Test Configuration Changes

After modifying settings, test with a sample image:

```bash
colorscheme-gen generate test-image.png --verbose
```

---

## Next Steps

- **[User Guide](user-guide.md)** - Learn how to use the tool
- **[Templates Guide](templates.md)** - Create custom output formats
- **[API Reference](api-reference.md)** - Python API documentation


