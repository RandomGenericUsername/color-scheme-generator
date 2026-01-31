# Color Scheme Generator - Standalone Tool

> **Extract color palettes from images and generate configuration files**

The standalone tool (`color-scheme`) is the core color extraction engine that supports multiple backends and output formats.

## 🚀 Quick Start

```bash
# Install
make install

# Generate color scheme (outputs to ~/.config/color-scheme/output)
uv run color-scheme generate ~/Pictures/wallpaper.png

# Show last generated colors
uv run color-scheme show --last

# Show specific color scheme file
uv run color-scheme show --file ~/.config/color-scheme/output/colors.json
```

**Default output location:** `~/.config/color-scheme/output/`
**Default format:** JSON (configurable in settings.toml)

## ✨ Key Features

- **Multiple Backends**: pywal, wallust, or custom Python backends
- **8+ Output Formats**: JSON, CSS, shell scripts, YAML, GTK themes, etc.
- **Configurable**: TOML configuration with Pydantic validation
- **Type-Safe**: Full Python type hints and mypy support
- **Extensible**: Plugin architecture for custom backends

## 📚 Documentation

Full documentation is in the [`docs/`](docs/) directory:

| Section | Description |
|---------|-------------|
| [Getting Started](docs/getting-started/) | Installation and quick start |
| [Guides](docs/guides/) | Usage guides and workflows |
| [Configuration](docs/configuration/) | settings.toml reference |
| [API Reference](docs/api/) | CLI and Python API |
| [Architecture](docs/architecture/) | System design |
| [Development](docs/development/) | Contributing and development |
| [Troubleshooting](docs/troubleshooting/) | Common issues and solutions |

**Start here:** [docs/README.md](docs/README.md)

## 📋 Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Backend dependencies (pywal, wallust, or none for custom)

## 🎯 Basic Usage

### Generate Color Schemes

```bash
# Generate with default backend (auto-detected from settings)
uv run color-scheme generate ~/Pictures/wallpaper.png

# Specify backend explicitly
uv run color-scheme generate ~/Pictures/wallpaper.png --backend wallust

# Use custom backend
uv run color-scheme generate ~/Pictures/wallpaper.png --backend custom

# Custom output directory
uv run color-scheme generate ~/Pictures/wallpaper.png --output-dir ~/my-colors

# Multiple output formats
uv run color-scheme generate ~/Pictures/wallpaper.png --formats json css

# Adjust saturation (0=grayscale, 1=unchanged, 2=max)
uv run color-scheme generate ~/Pictures/wallpaper.png --saturation 1.2

# List available backends
uv run color-scheme generate --list-backends

# Debug mode (verbose output)
uv run color-scheme generate ~/Pictures/wallpaper.png --debug

# Quiet mode (only errors)
uv run color-scheme generate ~/Pictures/wallpaper.png --quiet
```

### View Generated Colors

```bash
# Show last generated color scheme
uv run color-scheme show --last

# Show specific color scheme file
uv run color-scheme show --file ~/my-colors/colors.json

# Verbose output (show file path)
uv run color-scheme show --last --verbose
```

## ⚙️ Configuration

### Environment Variables

None currently used by core. Configuration is via `settings.toml`.

### Settings File

Configure via `settings.toml` (located in `$XDG_CONFIG_HOME/color-scheme/` or `~/.config/color-scheme/`):

```toml
[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

[output]
directory = "~/.config/color-scheme/output"
formats = ["json", "css"]

[backends.pywal]
use_library = false
cache_dir = "$HOME/.cache/wal"
backend_algorithm = "default"

[backends.wallust]
binary_path = "wallust"
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16

[logging]
level = "INFO"
show_time = true
```

See [Configuration Guide](docs/configuration/settings.md) for complete reference.

### Backend-Specific Options

**Pywal Options:**
- `--pywal-algorithm`: Color extraction algorithm (e.g., "default", "colorz")

**Wallust Options:**
- `--wallust-backend`: Backend type ("resized", "mean", etc.)

**Custom Options:**
- `--custom-algorithm`: Algorithm ("kmeans", "kmeans-fast", etc.)
- `--custom-clusters`: Number of color clusters (default: 16)

## 🛠️ Development

```bash
make install-dev   # Install with dev dependencies
make test          # Run tests
make lint          # Lint code
make format        # Format code
```

See [Development Guide](docs/development/setup.md) for complete setup.

## 📄 License

MIT License - see LICENSE file for details.

