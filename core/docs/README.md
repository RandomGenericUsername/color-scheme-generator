# Colorscheme Generator Documentation

**Version:** 0.1.0  
**Python:** ≥3.12  
**License:** MIT

---

## 📖 What is Colorscheme Generator?

**Colorscheme Generator** is a powerful Python tool that extracts beautiful color schemes from images and generates configuration files for various applications. It supports multiple color extraction backends and can output to numerous formats.

### Key Features

- **🎨 Multiple Backends**: Choose from pywal, wallust, or custom PIL-based extraction
- **🔧 Flexible Output**: Generate JSON, shell scripts, CSS, YAML, TOML, and more
- **⚙️ Highly Configurable**: Fine-tune saturation, algorithms, and color counts
- **🎯 Template System**: Jinja2-powered templates for custom output formats
- **🚀 CLI & Library**: Use as a command-line tool or Python library
- **✅ Type-Safe**: Built with Pydantic for robust validation

### Use Cases

- **Desktop Theming**: Generate color schemes for terminals, window managers, and applications
- **Web Design**: Extract color palettes from images for websites
- **Design Workflows**: Automate color scheme generation from brand assets
- **Creative Projects**: Build dynamic themes based on wallpapers or artwork

---

## 🚀 Quick Start

### Installation

```bash
# Install uv package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install from source using Makefile
cd core
make install

# Or install with dev dependencies
make install-dev

# Optional: Install wallust (Rust-based, faster)
cargo install wallust
```

### Basic Usage

```bash
# Generate color scheme from an image (auto-detect backend)
uv run colorscheme-gen generate wallpaper.png

# Use specific backend
uv run colorscheme-gen generate wallpaper.png --backend pywal

# Customize saturation
uv run colorscheme-gen generate wallpaper.png --saturation 1.5

# Specify output directory and formats
uv run colorscheme-gen generate wallpaper.png \
  --output-dir ~/my-colors \
  --formats json css sh

# Show generated color scheme
uv run colorscheme-gen show ~/.cache/colorscheme/colors.json

# Or use the Makefile shortcut
make run ARGS="generate wallpaper.png"
```

### Python Library Usage

```python
from pathlib import Path
from colorscheme_generator import ColorSchemeGeneratorFactory
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.core.types import GeneratorConfig

# Load settings
settings = Settings.get()

# Create backend (auto-detect)
generator = ColorSchemeGeneratorFactory.create_auto(settings)

# Generate color scheme
config = GeneratorConfig.from_settings(settings)
colorscheme = generator.generate(Path("wallpaper.png"), config)

# Access colors
print(f"Background: {colorscheme.background.hex}")
print(f"Foreground: {colorscheme.foreground.hex}")
for i, color in enumerate(colorscheme.colors):
    print(f"Color {i}: {color.hex}")
```

---

## 📚 Documentation Index

### Getting Started
- **[Quick Start](#-quick-start)** - Get up and running in 5 minutes
- **[Installation Guide](installation.md)** - Detailed installation instructions
- **[Configuration](configuration.md)** - Configure settings.toml

### User Guides
- **[User Guide](user-guide.md)** - Comprehensive usage guide
- **[CLI Reference](cli-reference.md)** - Complete CLI documentation
- **[Backends Guide](backends.md)** - Understanding and choosing backends
- **[Templates Guide](templates.md)** - Customizing output templates

### Technical Documentation
- **[Architecture](architecture.md)** - System design and architecture
- **[API Reference](api-reference.md)** - Python API documentation
- **[Development Guide](development.md)** - Contributing and development

### Advanced Topics
- **[Custom Backends](backends.md#creating-custom-backends)** - Implement your own backend
- **[Custom Templates](templates.md#creating-custom-templates)** - Create custom output formats
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI / Python API                         │
│                    (colorscheme_generator.cli)                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Factory Pattern                             │
│              (ColorSchemeGeneratorFactory)                       │
│  - Auto-detection of available backends                         │
│  - Backend instantiation                                         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 ↓               ↓               ↓
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │   Pywal    │  │  Wallust   │  │   Custom   │
        │  Backend   │  │  Backend   │  │  Backend   │
        └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
               │                │                │
               └────────────────┼────────────────┘
                                ↓
                        ┌───────────────┐
                        │  ColorScheme  │
                        │   (16 colors) │
                        └───────┬───────┘
                                │
                                ↓
                        ┌───────────────┐
                        │ OutputManager │
                        │  (Jinja2)     │
                        └───────┬───────┘
                                │
                ┌───────────────┼───────────────┐
                ↓               ↓               ↓
            JSON            CSS/SCSS         Shell
            YAML             GTK.CSS        Sequences
            TOML              RASI
```

See **[Architecture Documentation](architecture.md)** for detailed diagrams and explanations.

---

## 🎯 Core Concepts

### Backends

**Backends** are responsible for extracting colors from images. Each backend uses different algorithms:

| Backend | Description | Speed | Quality | Dependencies |
|---------|-------------|-------|---------|--------------|
| **pywal** | Python-based, multiple algorithms | Medium | Good | `pywal` package |
| **wallust** | Rust-based, fast and accurate | Fast | Excellent | `wallust` binary |
| **custom** | PIL + scikit-learn clustering | Medium | Good | Built-in |

### Color Scheme Structure

Every color scheme contains:
- **Background**: Darkest color (for backgrounds)
- **Foreground**: Brightest color (for text)
- **Cursor**: Accent color (for cursors/highlights)
- **Colors 0-15**: 16 ANSI terminal colors

### Output Formats

Generated files can be in multiple formats:
- **JSON**: Structured data for programmatic use
- **Shell**: Source-able shell scripts (`colors.sh`)
- **CSS/SCSS**: Stylesheets with CSS variables
- **YAML/TOML**: Configuration file formats
- **Sequences**: Terminal escape sequences
- **GTK.CSS**: GTK theme files
- **RASI**: Rofi theme files

---

## 🔧 Configuration

Configuration is managed through `settings.toml` using Dynaconf + Pydantic:

```toml
# Generation defaults
[generation]
default_backend = "pywal"
default_color_count = 16
saturation_adjustment = 1.0  # 0.0=grayscale, 1.0=unchanged, 2.0=max

# Backend-specific settings
[backends.pywal]
backend_algorithm = "wal"  # Options: wal, colorz, colorthief, haishoku, schemer2

[backends.wallust]
backend_type = "resized"  # Options: resized, full, thumb, fastresize, wal

[backends.custom]
algorithm = "kmeans"  # Options: kmeans, minibatch
n_clusters = 16

# Output settings
[output]
directory = "$HOME/.cache/colorscheme"
formats = ["json", "sh", "css", "yaml"]

# Template settings
[templates]
directory = ""  # Empty = use built-in templates
strict_mode = false
```

See **[Configuration Guide](configuration.md)** for complete documentation.

---

## 📦 Project Structure

```
colorscheme-generator/
├── core/                           # Main package
│   ├── src/colorscheme_generator/
│   │   ├── backends/              # Color extraction backends
│   │   │   ├── pywal.py          # Pywal backend
│   │   │   ├── wallust.py        # Wallust backend
│   │   │   └── custom.py         # Custom PIL backend
│   │   ├── config/               # Configuration system
│   │   │   ├── settings.toml     # Default settings
│   │   │   ├── config.py         # Pydantic models
│   │   │   └── settings.py       # Dynaconf loader
│   │   ├── core/                 # Core types and managers
│   │   │   ├── types.py          # ColorScheme, Color, etc.
│   │   │   ├── base.py           # Abstract base classes
│   │   │   ├── exceptions.py     # Custom exceptions
│   │   │   └── managers/         # OutputManager
│   │   ├── templates/            # Jinja2 templates
│   │   │   ├── colors.json.j2
│   │   │   ├── colors.sh.j2
│   │   │   └── ...
│   │   ├── cli.py                # CLI entry point
│   │   └── factory.py            # Backend factory
│   ├── tests/                    # Test suite
│   └── pyproject.toml            # Package metadata
├── docs/                         # Documentation (you are here!)
└── CLI_SETTINGS_OVERRIDE_ARCHITECTURE.md  # CLI design spec
```

---

## 🤝 Contributing

We welcome contributions! See the **[Development Guide](development.md)** for:
- Setting up development environment
- Running tests
- Code style guidelines
- Submitting pull requests

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🔗 Links

- **GitHub**: [colorscheme-generator](https://github.com/yourusername/colorscheme-generator)
- **Issues**: [Report bugs](https://github.com/yourusername/colorscheme-generator/issues)
- **Discussions**: [Ask questions](https://github.com/yourusername/colorscheme-generator/discussions)

---

## 📝 Changelog

### v0.1.0 (2025-12-11)
- Initial release
- Support for pywal, wallust, and custom backends
- Saturation adjustment feature
- Pywal algorithm selection
- Multiple output formats
- Jinja2 template system
- Comprehensive test suite


