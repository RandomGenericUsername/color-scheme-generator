# Color Scheme Orchestrator

> **Container-based backend orchestration for the colorscheme-generator tool**

The orchestrator (`color-scheme`) wraps the standalone tool to run backends (pywal, wallust, custom) in isolated Docker/Podman containers, providing security, consistency, and simplicity.

## 🚀 Quick Start

```bash
# Install
make install

# Build backend Docker images
make docker-build

# Generate color scheme
uv run color-scheme generate ~/Pictures/wallpaper.png
```

**Output location:** `~/.config/color-scheme/output/`

## ✨ Key Features

- **🔒 Security**: Backends run in sandboxed containers
- **🐳 Container Management**: Runtime-agnostic (Docker/Podman)
- **⚙️ Smart Defaults**: Auto-detection and sensible configuration
- **🔄 Transparent**: Dynamic argument passthrough to core tool

## 📚 Documentation

Full documentation is in the [`docs/`](docs/) directory:

| Section | Description |
|---------|-------------|
| [Getting Started](docs/getting-started/) | Installation and quick start |
| [Guides](docs/guides/) | Usage guides and workflows |
| [Configuration](docs/configuration/) | Environment variables and settings |
| [API Reference](docs/api/) | CLI reference |
| [Architecture](docs/architecture/) | System design |
| [Development](docs/development/) | Contributing and development |
| [Troubleshooting](docs/troubleshooting/) | Container issues and solutions |

**Start here:** [docs/README.md](docs/README.md)

## 📋 Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker or Podman

## 🎯 Basic Usage

```bash
# Generate with default backend
uv run color-scheme generate ~/Pictures/wallpaper.png

# Specify backend
uv run color-scheme generate ~/Pictures/wallpaper.png --backend wallust

# Check status
uv run color-scheme status

# Show available backends
uv run color-scheme show backends
```

## ⚙️ Configuration

Configure via environment variables:

```bash
export COLOR_SCHEME_RUNTIME=docker
export COLOR_SCHEME_OUTPUT_DIR=~/color-schemes
export COLOR_SCHEME_VERBOSE=true
```

See [Configuration Guide](docs/configuration/settings.md) for all options.

## 🛠️ Development

```bash
make install-dev   # Install with dev dependencies
make test          # Run tests
make lint          # Lint code
make docker-build  # Build Docker images
```

See [Development Guide](docs/development/setup.md) for complete setup.

## 📄 License

MIT License - see LICENSE file for details.
