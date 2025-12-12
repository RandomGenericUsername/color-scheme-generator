# Color Scheme Orchestrator

> **Container-based backend orchestration for the colorscheme-generator tool**

The orchestrator wraps the `colorscheme-generator` core tool to run backends (pywal, wallust, custom) in isolated Docker/Podman containers, providing security, consistency, and simplicity.

## 🚀 Quick Start

```bash
# 0. Install uv package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 1. Install the orchestrator using Makefile
cd orchestrator
make install

# 2. Build backend Docker images
make docker-build

# 3. Generate your first color scheme
uv run color-scheme generate -i /path/to/image.jpg
```

## ✨ Key Features

- **🔒 Security**: Backends run in sandboxed containers
- **🐳 Container Management**: Runtime-agnostic (Docker/Podman)
- **⚙️ Smart Defaults**: Auto-detection and sensible configuration
- **🔄 Transparent**: Dynamic argument passthrough to core tool
- **📦 Easy Installation**: Single package install

## 📚 Documentation

**Comprehensive documentation is available in the [`docs/`](docs/) directory:**

- **[Getting Started](docs/quick-start.md)** - Quick start guide and common commands
- **[Architecture](docs/architecture.md)** - System design and component interactions
- **[CLI Reference](docs/cli-reference.md)** - Complete command-line interface documentation
- **[Configuration](docs/configuration.md)** - Configuration options and environment variables
- **[Developer Guide](docs/developer-guide.md)** - Development setup and workflows
- **[API Reference](docs/api-reference.md)** - Python API documentation

**Start here:** [Documentation Index](docs/index.md)

## 📋 Requirements

- **Python** 3.12 or higher
- **[uv](https://docs.astral.sh/uv/)** package manager
- **Docker** or **Podman** (container runtime)
- The `colorscheme-generator` core tool (auto-installed)

## 🎯 Basic Usage

```bash
# Build backend Docker images
make docker-build

# Generate color scheme
uv run color-scheme generate -i image.jpg

# Check status
uv run color-scheme status

# Show available backends
uv run color-scheme show backends
```

See [CLI Reference](docs/cli-reference.md) for complete usage documentation.

## ⚙️ Configuration

Configure via environment variables:

```bash
export COLOR_SCHEME_RUNTIME=docker
export COLOR_SCHEME_OUTPUT_DIR=~/color-schemes
export COLOR_SCHEME_VERBOSE=true
```

See [Configuration Guide](docs/configuration.md) for all options.

## 🏗️ Architecture

```
User CLI → Orchestrator → Container Manager → Docker/Podman → Backend Containers
```

See [Architecture Documentation](docs/architecture.md) for detailed design.

## 🐛 Troubleshooting

**No container runtime found?**
```bash
sudo apt-get install docker.io  # Ubuntu/Debian
```

**Permission denied?**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

See [Quick Start Guide](docs/quick-start.md) for more troubleshooting.

## 🛠️ Development

```bash
# Install with dev dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Type checking
make type-check

# Lint code
make lint
```

See [Developer Guide](docs/developer-guide.md) for complete development documentation.

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/RandomGenericUsername/color-scheme-generator/issues)
- **Core Tool**: [../core/README.md](../core/README.md)

## 📄 License

MIT License - see LICENSE file for details
