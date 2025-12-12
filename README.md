# Color Scheme Generator

> **Extract beautiful color palettes from images and generate configuration files for various applications**

A comprehensive color scheme generation system with a modular architecture, supporting multiple backends and output formats.

## 🎨 Overview

The Color Scheme Generator project consists of two main components:

1. **[Core Tool](core/)** (`colorscheme-gen`) - The main color extraction engine
2. **[Orchestrator](orchestrator/)** (`color-scheme`) - Container-based backend wrapper

```
┌───────────────────────────────────────────────────────────────────┐
│                              User                                  │
└─────────────────────────────────┬─────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌───────────────────────────────┐  ┌───────────────────────────────┐
│         Orchestrator          │  │       Standalone Tool         │
│        (color-scheme)         │  │      (colorscheme-gen)        │
│  • Containerized execution    │  │  • Direct execution           │
│  • Docker/Podman support      │  │  • Local backend deps         │
└───────────────────────────────┘  └───────────────────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                         Backend Layer                              │
│       pywal  •  wallust  •  custom (built-in)                     │
└───────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker or Podman (for orchestrator)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

```bash
# Install everything
make install

# Build Docker images (for orchestrator)
make docker-build
```

### Usage

**Orchestrator (containerized):**
```bash
cd orchestrator
uv run color-scheme generate ~/Pictures/wallpaper.png
```

**Standalone tool (direct):**
```bash
cd core
uv run colorscheme-gen generate ~/Pictures/wallpaper.png
```

**Output location:** `~/.config/color-scheme/output/`

## 📚 Documentation

All documentation is centralized in the [`docs/`](docs/) directory:

| Section | Description |
|---------|-------------|
| [Getting Started](docs/getting-started/) | Installation, prerequisites, quick start |
| [Guides](docs/guides/) | How-to guides for common tasks |
| [Configuration](docs/configuration/) | All configuration options |
| [Architecture](docs/architecture/) | System design and internals |
| [API Reference](docs/api/) | CLI and Python library reference |
| [Examples](docs/examples/) | Code examples and integrations |
| [Troubleshooting](docs/troubleshooting/) | Common issues and solutions |
| [Development](docs/development/) | Contributing and development setup |

**Start here:** [docs/README.md](docs/README.md)

## ✨ Features

### Core Tool Features

- **Multiple Backends**: pywal, wallust, or custom Python backends
- **8+ Output Formats**: JSON, CSS, shell scripts, YAML, GTK themes, etc.
- **Configurable**: TOML configuration with Pydantic validation
- **Type-Safe**: Full Python type hints and mypy support
- **Extensible**: Plugin architecture for custom backends

### Orchestrator Features

- **🔒 Security**: Backends run in isolated containers
- **🐳 Container Management**: Runtime-agnostic (Docker/Podman)
- **⚙️ Smart Defaults**: Auto-detection and sensible configuration
- **🔄 Transparent**: Dynamic argument passthrough to core tool
- **📦 Easy Installation**: Single package install

## 🏗️ Project Structure

```
color-scheme-generator/
├── core/                           # Standalone tool (colorscheme-gen)
│   ├── src/colorscheme_generator/  # Main package
│   └── tests/                      # Core tests
│
├── orchestrator/                   # Container orchestrator (color-scheme)
│   ├── src/color_scheme/           # Orchestrator package
│   ├── docker/                     # Dockerfile definitions
│   └── tests/                      # Orchestrator tests
│
├── docs/                           # Centralized documentation
│
└── README.md                       # This file
```

## 🎯 Use Cases

- **Desktop Theming**: Generate terminal and window manager color schemes
- **Web Design**: Extract color palettes for websites
- **Creative Workflows**: Dynamic themes from wallpapers or artwork
- **Automated Theming**: Batch process images for consistent color schemes

## 📋 Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker or Podman (for orchestrator)

## 🛠️ Development

```bash
# Install with dev dependencies
make install-dev

# Run tests
make test

# Run linting
make lint
```

See [Development Guide](docs/development/setup.md) for complete setup.

### Core Tool Development

```bash
cd core
make install-dev  # Install with dev dependencies
make test         # Run tests
make lint         # Run linter
make format       # Format code
```

### Orchestrator Development

```bash
cd orchestrator
make install-dev     # Install with dev dependencies
make test            # Run tests
make docker-build    # Build Docker images
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! See [Contributing Guide](docs/development/contributing.md).

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/RandomGenericUsername/color-scheme-generator/issues)
