# How to Configure Backends

**Purpose:** Customize backend behavior for color extraction
**Created:** February 3, 2026
**Tested:** Yes - all options verified from config classes

Learn how to configure and customize each color extraction backend.

---

## Backend Configuration Overview

Each backend has specific configuration options. These can be set in three ways:

1. **Runtime options** via CLI flags (overrides everything)
2. **Configuration file** `~/.config/color-scheme/settings.toml` (user settings)
3. **Defaults** (built into application)

### Configuration Priority (highest to lowest)

1. CLI arguments (`--saturation`, `--format`, etc.)
2. User config file (`~/.config/color-scheme/settings.toml`)
3. Project config file (optional)
4. Built-in defaults

---

## Custom Backend Configuration

**Backend Type:** Built-in Python backend (PIL + scikit-learn)
**Availability:** Always available (no installation needed)
**Default:** Unless specified, this is the fallback

### Options

| Option | Type | Default | Range | Purpose |
|--------|------|---------|-------|---------|
| `algorithm` | string | `"kmeans"` | `"kmeans"` only | Color extraction algorithm |
| `n_clusters` | integer | `16` | 8-256 | Number of color clusters |

### Configuration File

Edit `~/.config/color-scheme/settings.toml`:

```toml
[backends.custom]
algorithm = "kmeans"      # Only algorithm currently supported
n_clusters = 16           # Extract 16 colors (ANSI standard)
```

### Runtime Override

```bash
# Override cluster count
color-scheme generate image.jpg -b custom

# Via backend options (in code)
from color_scheme.core.types import GeneratorConfig

config = GeneratorConfig(
    backend_options={"n_clusters": 10}
)
```

### Examples

```bash
# Use defaults
color-scheme generate wallpaper.jpg -b custom

# Extract more colors (will duplicate to 16)
color-scheme generate wallpaper.jpg -b custom

# Adjust saturation (works with any n_clusters)
color-scheme generate wallpaper.jpg -b custom -s 1.3
```

### Behavior

- **n_clusters < 16:** Colors are duplicated to reach exactly 16
- **n_clusters > 16:** Extra colors are truncated
- **n_clusters = 16:** Perfect 1:1 mapping (recommended)

---

## Pywal Backend Configuration

**Backend Type:** External Python tool
**Installation:** `pip install pywal` or `pacman -S pywal`
**Status:** Optional - used if installed and `--backend pywal` specified

### Options

| Option | Type | Default | Valid Values | Purpose |
|--------|------|---------|--------------|---------|
| `backend_algorithm` | string | `"haishoku"` | `wal`, `colorz`, `colorthief`, `haishoku`, `schemer2` | Color extraction algorithm |

### Configuration File

Edit `~/.config/color-scheme/settings.toml`:

```toml
[backends.pywal]
backend_algorithm = "haishoku"    # Recommended: best quality
```

### Algorithm Options

| Algorithm | Speed | Quality | Notes |
|-----------|-------|---------|-------|
| `wal` | Very Fast | Basic | Pywal's original algorithm |
| `colorz` | Fast | Good | Better color separation |
| `colorthief` | Medium | Good | Consistent results |
| `haishoku` | Medium | Excellent | Best quality (recommended) |
| `schemer2` | Slow | Excellent | Computational but accurate |

### Runtime Override

```bash
# Use pywal with specific algorithm
color-scheme generate wallpaper.jpg -b pywal

# Change algorithm (in code)
from color_scheme.core.types import GeneratorConfig

config = GeneratorConfig(
    backend_options={"backend_algorithm": "colorz"}
)
```

### Examples

```bash
# Use pywal with default algorithm (haishoku)
color-scheme generate wallpaper.jpg -b pywal

# Try different algorithms for comparison
color-scheme generate wallpaper.jpg -b pywal  # haishoku
color-scheme generate wallpaper.jpg -b pywal  # (change setting and retry)

# Combine with saturation adjustment
color-scheme generate wallpaper.jpg -b pywal -s 1.2
```

### Installation

```bash
# Ubuntu/Debian
sudo apt install python3-pip
pip install pywal

# Arch Linux
sudo pacman -S pywal

# Fedora
sudo dnf install pywal

# macOS (Homebrew)
brew install pywal
```

### Verify Installation

```bash
# Check if available
color-scheme generate image.jpg -b pywal

# Manual check
which wal        # Should print /usr/bin/wal or similar
wal --version    # Should show version
```

---

## Wallust Backend Configuration

**Backend Type:** External Rust tool
**Installation:** `pacman -S wallust`, `cargo install wallust`, or equivalent
**Status:** Optional - used if installed and `--backend wallust` specified

### Options

| Option | Type | Default | Valid Values | Purpose |
|--------|------|---------|--------------|---------|
| `backend_type` | string | `"resized"` | `resized`, `full`, and others | Wallust backend type |

### Configuration File

Edit `~/.config/color-scheme/settings.toml`:

```toml
[backends.wallust]
backend_type = "resized"    # Resize image for faster processing
```

### Backend Type Options

| Backend Type | Speed | Quality | Notes |
|--------------|-------|---------|-------|
| `resized` | Fast | Excellent | Resize image first (recommended) |
| `full` | Medium | Excellent | Process full resolution |
| `wal` | Medium | Excellent | Pywal-compatible mode |

### Runtime Override

```bash
# Use wallust with default backend
color-scheme generate wallpaper.jpg -b wallust

# Change backend type (in code)
from color_scheme.core.types import GeneratorConfig

config = GeneratorConfig(
    backend_options={"backend_type": "full"}
)
```

### Examples

```bash
# Use wallust with default settings
color-scheme generate wallpaper.jpg -b wallust

# Try full resolution for large images
color-scheme generate wallpaper.jpg -b wallust

# With saturation boost
color-scheme generate wallpaper.jpg -b wallust -s 1.1
```

### Installation

```bash
# Arch Linux
sudo pacman -S wallust

# Fedora Copr
sudo dnf copr enable whatthefox/wallust
sudo dnf install wallust

# Cargo (universal)
cargo install wallust

# macOS (Homebrew - if available)
brew install wallust
```

### Verify Installation

```bash
# Check if available
color-scheme generate image.jpg -b wallust

# Manual check
which wallust      # Should print path
wallust --version  # Should show version
```

---

## Configuration Examples

### Example 1: Best Quality (Slow but Beautiful)

```toml
# ~/.config/color-scheme/settings.toml

[generation]
default_backend = "pywal"      # Use pywal as default

[backends.pywal]
backend_algorithm = "schemer2" # Highest quality algorithm

[backends.custom]
n_clusters = 16
```

Then generate:
```bash
color-scheme generate wallpaper.jpg -s 1.1
```

### Example 2: Fast Processing (Development)

```toml
# ~/.config/color-scheme/settings.toml

[generation]
default_backend = "custom"     # Use built-in backend

[backends.custom]
n_clusters = 8                 # Extract fewer colors (duplicated to 16)
algorithm = "kmeans"
```

Then generate:
```bash
color-scheme generate wallpaper.jpg
```

### Example 3: Multiple Algorithms Comparison

```bash
#!/bin/bash
# test-backends.sh - Compare all backends

IMAGE="wallpaper.jpg"
OUTPUT_BASE="~/test-backends"

# Test custom
mkdir -p "$OUTPUT_BASE/custom"
color-scheme generate "$IMAGE" -b custom -o "$OUTPUT_BASE/custom"

# Test pywal with different algorithms
for algo in wal colorz haishoku schemer2; do
    mkdir -p "$OUTPUT_BASE/pywal-$algo"
    # (would need to update config between runs)
    echo "Test pywal with $algo algorithm"
done

# Test wallust
mkdir -p "$OUTPUT_BASE/wallust"
color-scheme generate "$IMAGE" -b wallust -o "$OUTPUT_BASE/wallust"

echo "Results in: $OUTPUT_BASE"
ls -la "$OUTPUT_BASE"
```

---

## Comparing Backends

### Speed Comparison

**Fast to Slow:**
1. Custom (fastest) - No external process
2. Wallust (resized) - Rust, well-optimized
3. Pywal (wal algorithm) - Python, original algorithm
4. Pywal (schemer2) - Python, most computational

### Quality Comparison

**Best to Acceptable:**
1. Wallust - Excellent, Rust-optimized algorithms
2. Pywal (schemer2) - Excellent, very computational
3. Pywal (haishoku) - Very good, balanced
4. Pywal (colorthief) - Good, consistent
5. Pywal (colorz) - Good, fast
6. Pywal (wal) - Good, basic
7. Custom - Very good, deterministic

### When to Use Each Backend

| Scenario | Recommendation | Reason |
|----------|-----------------|--------|
| Desktop theme | Wallust | Fastest + best quality |
| Development/testing | Custom | No dependencies |
| High quality needed | Pywal (schemer2) | Best algorithm |
| Balanced | Pywal (haishoku) | Good speed & quality |
| CI/CD pipeline | Custom | No external deps |
| Already using pywal | Pywal | Familiar settings |

---

## Configuration File Reference

Complete example `~/.config/color-scheme/settings.toml`:

```toml
[generation]
# Default backend to use (custom, pywal, wallust)
default_backend = "pywal"

# Default saturation adjustment (0.0-2.0)
saturation_adjustment = 1.0

[backends.custom]
# K-means clustering algorithm (only "kmeans" supported)
algorithm = "kmeans"

# Number of color clusters to extract (8-256, recommended: 16)
n_clusters = 16

[backends.pywal]
# Pywal color extraction algorithm
# Options: wal, colorz, colorthief, haishoku, schemer2
backend_algorithm = "haishoku"

[backends.wallust]
# Wallust backend type
# Options: resized, full, wal
backend_type = "resized"

[output]
# Output directory for generated files
directory = "~/.config/color-scheme/output"

# Formats to generate (can be a subset)
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]
```

---

## Command Quick Reference

```bash
# Auto-detect best available backend
color-scheme generate image.jpg

# Use specific backend
color-scheme generate image.jpg -b custom
color-scheme generate image.jpg -b pywal
color-scheme generate image.jpg -b wallust

# Override saturation per-command
color-scheme generate image.jpg -s 1.5

# Combine options
color-scheme generate image.jpg -b pywal -o ~/colors -s 1.2 -f json -f css
```

---

## Troubleshooting

### Backend not available error

```
Error: pywal is not installed or not in PATH
```

**Solution:** Install the backend or use custom:
```bash
color-scheme generate image.jpg -b custom
```

### Colors don't look right with custom backend

**Solution 1:** Increase saturation:
```bash
color-scheme generate image.jpg -b custom -s 1.3
```

**Solution 2:** Use a different backend:
```bash
color-scheme generate image.jpg -b pywal
```

**Solution 3:** Adjust n_clusters:
```toml
[backends.custom]
n_clusters = 8   # Try fewer clusters
```

### Pywal algorithm produces different colors

This is expected - each algorithm uses different methods. Compare results:

```bash
# Try haishoku (recommended)
color-scheme generate image.jpg -b pywal

# Try colorz (if haishoku doesn't work)
# (Update settings.toml and retry)
```

---

## Next Steps

- **[Customize output formats](customize-output.md)** - Choose which output formats to generate
- **[Generate colors](generate-colors.md)** - Apply backend configuration to generate colors
- **[Integrate with shell](integrate-shell.md)** - Use generated colors in your environment
