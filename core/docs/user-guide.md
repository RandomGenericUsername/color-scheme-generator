# User Guide

Complete guide to using colorscheme-generator for extracting and generating color schemes.

---

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Backends](#backends)
- [Output Formats](#output-formats)
- [Customization](#customization)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python ≥3.12
- pip or pipx

### Install from Source

```bash
# Clone repository
git clone https://github.com/yourusername/colorscheme-generator.git
cd colorscheme-generator/core

# Install in development mode
pip install -e .

# Verify installation
colorscheme-gen --help
```

### Optional Dependencies

#### Pywal Backend

```bash
# Install pywal
pip install pywal

# Or with the package
pip install -e ".[pywal]"
```

#### Wallust Backend

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install wallust
cargo install wallust

# Verify
wallust --version
```

---

## Basic Usage

### Generate Color Scheme

```bash
# Auto-detect backend
colorscheme-gen generate wallpaper.png

# Specify backend
colorscheme-gen generate wallpaper.png --backend pywal
colorscheme-gen generate wallpaper.png --backend wallust
colorscheme-gen generate wallpaper.png --backend custom

# Specify output directory
colorscheme-gen generate wallpaper.png --output-dir ~/my-colors

# Specify output formats
colorscheme-gen generate wallpaper.png --formats json css sh
```

### Show Color Scheme

```bash
# Show from JSON file
colorscheme-gen show ~/.cache/colorscheme/colors.json

# Show with color preview (if terminal supports)
colorscheme-gen show ~/.cache/colorscheme/colors.json --preview
```

### List Available Backends

```bash
colorscheme-gen generate --list-backends
```

Output:
```
Available backends:
  ✓ pywal   - Python-based color extraction (multiple algorithms)
  ✓ wallust - Rust-based color extraction (fast and accurate)
  ✓ custom  - Built-in PIL + scikit-learn clustering
```

---

## Backends

### Pywal Backend

**Description**: Uses the pywal tool for color extraction. Supports multiple algorithms.

**Installation**: `pip install pywal`

**Algorithms**:
- `wal` (default): Fast, balanced quality
- `colorz`: Good for vibrant colors
- `colorthief`: Accurate, slower
- `haishoku`: Good for pastel colors
- `schemer2`: Experimental

**Usage**:
```bash
# Use default algorithm (wal)
colorscheme-gen generate image.png --backend pywal

# Use specific algorithm
colorscheme-gen generate image.png --backend pywal --pywal-algorithm colorz
colorscheme-gen generate image.png --backend pywal --pywal-algorithm colorthief
```

**Configuration** (`settings.toml`):
```toml
[backends.pywal]
backend_algorithm = "wal"  # Options: wal, colorz, colorthief, haishoku, schemer2
```

### Wallust Backend

**Description**: Rust-based color extraction. Fast and high-quality.

**Installation**: `cargo install wallust`

**Backend Types**:
- `resized` (default): Fast, resizes image first
- `full`: Highest quality, processes full image
- `thumb`: Very fast, uses thumbnail
- `fastresize`: Balanced speed/quality
- `wal`: Compatible with pywal

**Usage**:
```bash
# Use default backend type (resized)
colorscheme-gen generate image.png --backend wallust

# Use specific backend type
colorscheme-gen generate image.png --backend wallust --wallust-backend full
colorscheme-gen generate image.png --backend wallust --wallust-backend thumb
```

**Configuration** (`settings.toml`):
```toml
[backends.wallust]
backend_type = "resized"  # Options: resized, full, thumb, fastresize, wal
```

### Custom Backend

**Description**: Built-in backend using PIL and scikit-learn. No external dependencies.

**Algorithms**:
- `kmeans` (default): K-means clustering
- `minibatch`: Mini-batch K-means (faster for large images)

**Usage**:
```bash
# Use default algorithm (kmeans)
colorscheme-gen generate image.png --backend custom

# Use specific algorithm
colorscheme-gen generate image.png --backend custom --custom-algorithm minibatch

# Adjust cluster count
colorscheme-gen generate image.png --backend custom --custom-clusters 20
```

**Configuration** (`settings.toml`):
```toml
[backends.custom]
algorithm = "kmeans"  # Options: kmeans, minibatch
n_clusters = 16
```

### Backend Comparison

| Feature | Pywal | Wallust | Custom |
|---------|-------|---------|--------|
| **Speed** | Medium | Fast | Medium |
| **Quality** | Good | Excellent | Good |
| **Dependencies** | pywal package | wallust binary | Built-in |
| **Algorithms** | 5 options | 5 options | 2 options |
| **Best For** | Compatibility | Performance | No dependencies |

---

## Output Formats

### Available Formats

| Format | Extension | Description | Use Case |
|--------|-----------|-------------|----------|
| **JSON** | `.json` | Structured data | Programmatic use |
| **Shell** | `.sh` | Shell variables | Shell scripts |
| **CSS** | `.css` | CSS variables | Web styling |
| **GTK.CSS** | `.gtk.css` | GTK theme | GTK applications |
| **YAML** | `.yaml` | YAML format | Configuration files |
| **TOML** | `.toml` | TOML format | Configuration files |
| **Sequences** | `.sequences` | Terminal escapes | Terminal theming |
| **RASI** | `.rasi` | Rofi theme | Rofi launcher |

### Format Examples

#### JSON Format
```json
{
  "special": {
    "background": "#1a1b26",
    "foreground": "#c0caf5",
    "cursor": "#c0caf5"
  },
  "colors": {
    "color0": "#15161e",
    "color1": "#f7768e",
    "color2": "#9ece6a",
    ...
  }
}
```

#### Shell Format
```bash
# Shell variables
background='#1a1b26'
foreground='#c0caf5'
cursor='#c0caf5'
color0='#15161e'
color1='#f7768e'
...
```

#### CSS Format
```css
:root {
  --background: #1a1b26;
  --foreground: #c0caf5;
  --cursor: #c0caf5;
  --color0: #15161e;
  --color1: #f7768e;
  ...
}
```

### Specifying Output Formats

```bash
# Single format
colorscheme-gen generate image.png --formats json

# Multiple formats
colorscheme-gen generate image.png --formats json css sh yaml

# All formats (default from settings.toml)
colorscheme-gen generate image.png
```

---

## Customization

### Saturation Adjustment

Adjust color saturation after extraction:

```bash
# Increase saturation (more vibrant)
colorscheme-gen generate image.png --saturation 1.5

# Decrease saturation (more muted)
colorscheme-gen generate image.png --saturation 0.7

# Grayscale
colorscheme-gen generate image.png --saturation 0.0

# Maximum saturation
colorscheme-gen generate image.png --saturation 2.0
```

**Scale**: 0.0 (grayscale) → 1.0 (unchanged) → 2.0 (maximum)

**Configuration** (`settings.toml`):
```toml
[generation]
saturation_adjustment = 1.0  # 0.0-2.0
```

### Custom Templates

Use your own Jinja2 templates:

```bash
# Specify custom template directory
colorscheme-gen generate image.png --template-dir ~/.config/colorscheme/templates
```

**Template Structure**:
```
~/.config/colorscheme/templates/
├── colors.json.j2
├── colors.css.j2
├── colors.sh.j2
└── my-custom-format.j2
```

See **[Templates Guide](templates.md)** for details.

### Strict Template Mode

Enable strict undefined variable checking:

```bash
colorscheme-gen generate image.png --strict-templates
```

**Configuration** (`settings.toml`):
```toml
[templates]
strict_mode = true
```

---

## Advanced Usage

### CLI Options

```
usage: colorscheme-gen generate [-h] [--backend {pywal,wallust,custom}]
                                [--pywal-algorithm {wal,colorz,colorthief,haishoku,schemer2}]
                                [--wallust-backend {resized,full,thumb,fastresize,wal}]
                                [--custom-algorithm {kmeans,minibatch}]
                                [--custom-clusters N] [--saturation SATURATION]
                                [--output-dir DIR]
                                [--formats {json,sh,css,gtk.css,yaml,toml,sequences,rasi} [{json,sh,css,gtk.css,yaml,toml,sequences,rasi} ...]]
                                [--template-dir DIR] [--strict-templates]
                                [-v] [--list-backends]
                                [image]
```

### Combining Options

```bash
# Full customization
colorscheme-gen generate wallpaper.png \
  --backend wallust \
  --wallust-backend full \
  --saturation 1.3 \
  --output-dir ~/themes/current \
  --formats json css sh sequences \
  --verbose
```

### Using with Shell Scripts

```bash
#!/bin/bash
# Auto-theme from wallpaper

WALLPAPER="$HOME/Pictures/wallpaper.jpg"
OUTPUT_DIR="$HOME/.config/colors"

# Generate color scheme
colorscheme-gen generate "$WALLPAPER" \
  --backend wallust \
  --saturation 1.2 \
  --output-dir "$OUTPUT_DIR" \
  --formats json sh

# Source colors
source "$OUTPUT_DIR/colors.sh"

# Apply to terminal (example)
echo -e "\033]10;$foreground\007"  # Set foreground
echo -e "\033]11;$background\007"  # Set background

# Apply to other tools
# ... (i3, polybar, rofi, etc.)
```

### Python API Usage

```python
from pathlib import Path
from colorscheme_generator import ColorSchemeGeneratorFactory
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.core.types import GeneratorConfig
from colorscheme_generator.core.managers.output_manager import OutputManager

# Load settings
settings = Settings.get()

# Create backend
generator = ColorSchemeGeneratorFactory.create_auto(settings)

# Generate color scheme
config = GeneratorConfig.from_settings(settings)
colorscheme = generator.generate(Path("wallpaper.png"), config)

# Access colors
print(f"Background: {colorscheme.background.hex}")
print(f"Foreground: {colorscheme.foreground.hex}")
print(f"Cursor: {colorscheme.cursor.hex}")

for i, color in enumerate(colorscheme.colors):
    print(f"Color {i}: {color.hex} RGB{color.rgb}")

# Write output files
output_manager = OutputManager(settings)
output_manager.write_all(colorscheme)
```

### Programmatic Saturation Adjustment

```python
from colorscheme_generator.core.types import Color

# Create color
color = Color(hex="#ff5733", rgb=(255, 87, 51))

# Adjust saturation
vibrant = color.adjust_saturation(1.5)  # More saturated
muted = color.adjust_saturation(0.7)    # Less saturated
gray = color.adjust_saturation(0.0)     # Grayscale

print(f"Original: {color.hex}")
print(f"Vibrant:  {vibrant.hex}")
print(f"Muted:    {muted.hex}")
print(f"Gray:     {gray.hex}")
```

---

## Troubleshooting

### Backend Not Available

**Problem**: `BackendNotAvailableError: No backends available`

**Solutions**:
1. Install at least one backend:
   ```bash
   pip install pywal  # OR
   cargo install wallust
   ```
2. Use built-in custom backend:
   ```bash
   colorscheme-gen generate image.png --backend custom
   ```

### Invalid Image Error

**Problem**: `InvalidImageError: Cannot open image`

**Solutions**:
1. Check file exists: `ls -l image.png`
2. Verify file format: `file image.png`
3. Supported formats: PNG, JPEG, BMP, GIF, TIFF
4. Try converting: `convert image.webp image.png`

### Permission Denied

**Problem**: `PermissionError: Cannot write to output directory`

**Solutions**:
1. Check directory permissions: `ls -ld ~/.cache/colorscheme`
2. Create directory: `mkdir -p ~/.cache/colorscheme`
3. Use different directory: `--output-dir ~/my-colors`

### Pywal Algorithm Not Found

**Problem**: `ValueError: Invalid backend_algorithm`

**Solutions**:
1. Check available algorithms: `wal --help`
2. Install missing dependencies:
   ```bash
   pip install colorz colorthief haishoku
   ```
3. Use default algorithm: `--pywal-algorithm wal`

### Template Rendering Error

**Problem**: `TemplateError: Undefined variable`

**Solutions**:
1. Disable strict mode: Remove `--strict-templates`
2. Check template syntax
3. Use built-in templates: Remove `--template-dir`

### Colors Look Wrong

**Problem**: Colors don't match image

**Solutions**:
1. Try different backend:
   ```bash
   colorscheme-gen generate image.png --backend wallust
   ```
2. Try different algorithm:
   ```bash
   colorscheme-gen generate image.png --backend pywal --pywal-algorithm colorthief
   ```
3. Adjust saturation:
   ```bash
   colorscheme-gen generate image.png --saturation 1.3
   ```
4. Use full-resolution processing:
   ```bash
   colorscheme-gen generate image.png --backend wallust --wallust-backend full
   ```

### Verbose Output

Enable verbose logging for debugging:

```bash
colorscheme-gen generate image.png --verbose
```

---

## Best Practices

### 1. Choose the Right Backend

- **Wallust**: Best for most use cases (fast + high quality)
- **Pywal**: Good for compatibility with existing pywal setups
- **Custom**: When you can't install external dependencies

### 2. Optimize for Your Use Case

**For Speed**:
```bash
colorscheme-gen generate image.png --backend wallust --wallust-backend thumb
```

**For Quality**:
```bash
colorscheme-gen generate image.png --backend wallust --wallust-backend full
```

**For Vibrant Colors**:
```bash
colorscheme-gen generate image.png --saturation 1.5
```

**For Muted Colors**:
```bash
colorscheme-gen generate image.png --saturation 0.7
```

### 3. Automate with Scripts

Create a script to auto-theme your desktop:

```bash
#!/bin/bash
# ~/.local/bin/auto-theme

WALLPAPER="$1"
COLORS_DIR="$HOME/.config/colors"

# Generate colors
colorscheme-gen generate "$WALLPAPER" \
  --backend wallust \
  --saturation 1.2 \
  --output-dir "$COLORS_DIR" \
  --formats json sh css

# Reload applications
source "$COLORS_DIR/colors.sh"
i3-msg reload
polybar-msg cmd restart
# ... etc
```

Usage:
```bash
auto-theme ~/Pictures/new-wallpaper.jpg
```

### 4. Version Control Your Settings

Keep your `settings.toml` in version control:

```bash
# Copy default settings
cp ~/.config/colorscheme-generator/settings.toml ~/dotfiles/

# Symlink
ln -s ~/dotfiles/settings.toml ~/.config/colorscheme-generator/settings.toml
```

---

## Next Steps

- **[Configuration Guide](configuration.md)** - Detailed settings documentation
- **[Templates Guide](templates.md)** - Create custom output formats
- **[API Reference](api-reference.md)** - Python API documentation
- **[Development Guide](development.md)** - Contributing to the project


