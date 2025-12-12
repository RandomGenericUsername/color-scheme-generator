# Color Scheme Generator - Standalone Tool

> **Extract color palettes from images and generate configuration files**

The standalone tool (`colorscheme-gen`) is the core color extraction engine that supports multiple backends and output formats.

## 🚀 Quick Start

```bash
# Install
make install

# Generate color scheme
uv run colorscheme-gen generate ~/Pictures/wallpaper.png

# Show generated colors
uv run colorscheme-gen show ~/.config/color-scheme/output/colors.json
```

**Output location:** `~/.config/color-scheme/output/`

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

```bash
# Generate with default backend
uv run colorscheme-gen generate ~/Pictures/wallpaper.png

# Specify backend
uv run colorscheme-gen generate ~/Pictures/wallpaper.png --backend wallust

# Custom output directory
uv run colorscheme-gen generate ~/Pictures/wallpaper.png --output-dir ~/my-colors

# Show generated colors
uv run colorscheme-gen show ~/.config/color-scheme/output/colors.json

# List available backends
uv run colorscheme-gen backends
```

## ⚙️ Configuration

Configure via `settings.toml`:

```toml
[colorscheme]
backend = "pywal"
output_dir = "~/.config/color-scheme/output"

[backends.pywal]
saturation = 0.5
```

See [Configuration Guide](docs/configuration/settings.md) for all options.

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

