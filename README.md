# Color Scheme Generator

> **Extract beautiful color palettes from images and generate configuration files for various applications**

A comprehensive color scheme generation system with a modular architecture, supporting multiple backends and output formats.

## 🎨 Overview

The Color Scheme Generator project consists of two main components:

1. **[Core Tool](core/)** - The main color extraction engine
2. **[Orchestrator](orchestrator/)** - Container-based backend wrapper

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator                              │
│  • Container management (Docker/Podman)                      │
│  • Backend isolation and execution                           │
│  • Argument passthrough                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                     Core Tool                                │
│  • Color extraction (pywal, wallust, custom)                 │
│  • Multiple output formats (JSON, CSS, YAML, etc.)           │
│  • Configuration management                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker or Podman (for orchestrator)

Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Option 1: Using the Orchestrator (Recommended)

The orchestrator provides containerized backend execution for security and consistency:

```bash
# Install both components using Makefile
make install

# Build backend Docker images
make docker-build

# Generate color scheme
cd orchestrator
uv run color-scheme generate -i /path/to/image.jpg
```

**Documentation**: [orchestrator/docs/](orchestrator/docs/)

### Option 2: Using the Core Tool Directly

For direct usage without containers:

```bash
# Install core tool using Makefile
cd core
make install

# Generate color scheme
uv run colorscheme-gen generate -i /path/to/image.jpg --backend pywal
```

**Documentation**: [core/docs/](core/docs/)

## 📚 Documentation

### Orchestrator Documentation

Complete documentation for the container-based orchestrator:

- **[Quick Start](orchestrator/docs/quick-start.md)** - Get started in 30 seconds
- **[Architecture](orchestrator/docs/architecture.md)** - System design and components
- **[CLI Reference](orchestrator/docs/cli-reference.md)** - Complete command documentation
- **[Configuration](orchestrator/docs/configuration.md)** - Configuration options
- **[Developer Guide](orchestrator/docs/developer-guide.md)** - Development workflows
- **[API Reference](orchestrator/docs/api-reference.md)** - Python API documentation

**Start here**: [orchestrator/docs/index.md](orchestrator/docs/index.md)

### Core Tool Documentation

Documentation for the core color extraction engine:

- **[Core README](core/README.md)** - Core tool overview
- **[Core Documentation](core/docs/)** - Detailed core tool docs

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
├── core/                           # Core color extraction tool
│   ├── src/colorscheme_generator/  # Main package
│   │   ├── domain/                 # Domain models (ColorScheme, Color)
│   │   ├── application/            # Application layer (factories, settings)
│   │   ├── infrastructure/         # Infrastructure (backends, templates)
│   │   └── cli.py                  # CLI entry point
│   ├── docs/                       # Core documentation
│   ├── tests/                      # Core tests
│   └── pyproject.toml              # Core package configuration
│
├── orchestrator/                   # Container orchestrator
│   ├── src/color_scheme/           # Orchestrator package
│   │   ├── cli.py                  # CLI entry point
│   │   ├── commands/               # Command implementations
│   │   ├── services/               # Container services
│   │   ├── config/                 # Configuration management
│   │   └── utils/                  # Utilities
│   ├── docker/                     # Dockerfile definitions
│   │   ├── Dockerfile.pywal        # Pywal backend
│   │   ├── Dockerfile.wallust      # Wallust backend
│   │   └── Dockerfile.custom       # Custom backend template
│   ├── docs/                       # Orchestrator documentation
│   ├── tests/                      # Orchestrator tests
│   └── pyproject.toml              # Orchestrator package configuration
│
└── README.md                       # This file
```

## 🎯 Use Cases

- **Desktop Theming**: Generate terminal and window manager color schemes
- **Web Design**: Extract color palettes for websites
- **Creative Workflows**: Dynamic themes from wallpapers or artwork
- **Automated Theming**: Batch process images for consistent color schemes

## 📋 Requirements

### Core Tool
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Backend dependencies (pywal, wallust, or custom)

### Orchestrator
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker or Podman
- Core tool (auto-installed)

## 🛠️ Development

### Quick Development Setup

```bash
# Install both components with dev dependencies
make install-dev

# Run all tests
make test

# Run linting
make lint

# Build distribution packages
make build
```

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

See respective documentation for detailed development guides.

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please see the respective component documentation for contribution guidelines:

- [Orchestrator Developer Guide](orchestrator/docs/developer-guide.md)
- [Core Tool Documentation](core/docs/)

## 📞 Support

- **Orchestrator Documentation**: [orchestrator/docs/](orchestrator/docs/)
- **Core Documentation**: [core/docs/](core/docs/)
- **Issues**: [GitHub Issues](https://github.com/RandomGenericUsername/color-scheme-generator/issues)

