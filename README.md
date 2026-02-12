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

- [Quick Start Tutorial](docs/tutorials/quick-start.md)
- [CLI Reference](docs/reference/cli/core-commands.md)
- [Configuration Reference](docs/reference/configuration/settings-model.md)
- [Backend Documentation](docs/reference/backends/pywal.md)
- [How to Contribute](docs/how-to/contribute.md)

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

See [Developer Setup Tutorial](docs/tutorials/developer-setup.md) for full environment setup.

## Architecture

This is a monorepo with three packages:

- **color-scheme-core**: Standalone color extraction and generation
- **color-scheme-orchestrator**: Container orchestration layer
- **color-scheme-settings**: Shared configuration system

Both core and orchestrator expose the same `color-scheme` CLI. Choose based on your needs:
- Core: Direct installation, you manage dependencies
- Orchestrator: Containerized, isolated execution

See [Architecture Explanation](docs/explanations/architecture.md) for details.

## Project Status

Current version: **v0.1.0**

## License

MIT
