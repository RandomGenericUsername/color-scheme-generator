# color-scheme

CLI tool for extracting and generating color schemes from images.

## Features

- **Multiple Backends**: pywal, wallust, custom Python algorithm
- **Multiple Formats**: JSON, CSS, SCSS, YAML, shell scripts, GTK, rofi, terminal sequences
- **Flexible Deployment**: Run on host or in containers
- **Configurable**: Settings file with CLI overrides
- **Type-Safe**: Pydantic validation throughout

## Quick Start

### Installation

```bash
# Core package (host installation)
pip install color-scheme-core

# Orchestrator (containerized)
pip install color-scheme-orchestrator
```

### Usage

```bash
# Generate color scheme
color-scheme generate wallpaper.png

# Show color scheme
color-scheme show

# Use specific backend
color-scheme generate wallpaper.png --backend wallust
```

## Documentation

- [Installation Guide](docs/user-guide/installation.md)
- [Configuration Guide](docs/user-guide/configuration.md)
- [CLI Reference](docs/user-guide/cli-reference.md)
- [Backend Documentation](docs/user-guide/backends.md)
- [Contributing Guide](docs/development/contributing.md)

## Development

```bash
# Clone repository
git clone https://github.com/your-org/color-scheme.git
cd color-scheme

# Run setup script
./scripts/dev-setup.sh

# Run tests
cd packages/core
uv run pytest
```

See [Contributing Guide](docs/development/contributing.md) for full workflow.

## Architecture

This is a monorepo with two packages:

- **color-scheme-core**: Standalone color extraction and generation
- **color-scheme-orchestrator**: Container orchestration layer

Both expose the same `color-scheme` CLI. Choose based on your needs:
- Core: Direct installation, you manage dependencies
- Orchestrator: Containerized, isolated execution

See [Architecture Design](docs/plans/2026-01-18-monorepo-architecture-design.md) for details.

## Project Status

Current version: **Phase 1 (Foundation)** - v0.1.0

See [Implementation Progress](docs/implementation-progress.md) for roadmap.

## License

MIT
