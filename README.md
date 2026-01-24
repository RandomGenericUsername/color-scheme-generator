# color-scheme

[![Core Package CI](https://github.com/your-org/color-scheme/workflows/Core%20Package%20CI/badge.svg)](https://github.com/your-org/color-scheme/actions)
[![codecov](https://codecov.io/gh/your-org/color-scheme/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/color-scheme)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful CLI tool for extracting color palettes from images and generating color schemes in multiple formats.

## Features

- **Multiple Backends**: Choose from pywal, wallust, or custom Python-based color extraction
- **Multiple Output Formats**: JSON, CSS, SCSS, YAML, shell scripts, GTK CSS, rofi, terminal sequences
- **Flexible Deployment**: Run directly on host or in isolated containers
- **Type-Safe Configuration**: Pydantic-validated settings with sensible defaults
- **Template-Based Output**: Customizable Jinja2 templates for all output formats
- **High Test Coverage**: 95%+ test coverage with comprehensive test suite

## Quick Start

### Installation

Choose the package that fits your needs:

**Core Package** (host installation):
```bash
pip install color-scheme-core

# Optional: Install backends
pip install pywal  # For pywal backend
# Install wallust from: https://github.com/dharmx/wallust
```

**Orchestrator Package** (containerized):
```bash
pip install color-scheme-orchestrator

# Requires Docker or Podman
# Backends run in containers, no separate installation needed
```

### Basic Usage

```bash
# Generate color scheme from image (Phase 2+)
color-scheme generate wallpaper.png

# Show current color scheme (Phase 2+)
color-scheme show

# Use specific backend
color-scheme generate image.png --backend wallust

# Specify output formats
color-scheme generate image.png --formats json,css,scss

# Show version
color-scheme version
```

## Current Status

**Version**: 0.1.0 (Phase 1: Foundation)

Phase 1 is complete with:
- Monorepo structure with core and orchestrator packages
- Configuration system (dynaconf + Pydantic)
- CI/CD pipeline
- Development automation
- Comprehensive documentation

**Coming Soon**:
- Phase 2: Backend implementations (pywal, wallust, custom)
- Phase 3: Output generation and templates
- Phase 4: Container orchestration
- Phase 5: Advanced features

See [Implementation Progress](docs/implementation-progress.md) for detailed roadmap.

## Documentation

### User Documentation
- [Installation Guide](docs/user-guide/installation.md) - Detailed installation instructions
- Configuration Guide (Coming in Phase 2)
- CLI Reference (Coming in Phase 2)
- Backend Documentation (Coming in Phase 2)

### Developer Documentation
- [Getting Started](docs/development/getting-started.md) - Set up your development environment
- [Testing Guide](docs/development/testing.md) - How to write and run tests
- [Contributing Guide](docs/development/contributing.md) - Contribution workflow and standards

### Architecture Documentation
- [Architecture Overview](docs/architecture/overview.md) - System design and components
- [Monorepo Design](docs/plans/2026-01-18-monorepo-architecture-design.md) - Detailed architecture decisions

### Additional Resources
- [Documentation Index](docs/README.md) - Complete documentation navigation
- [Troubleshooting](docs/troubleshooting/error-database.md) - Known errors and solutions
- [Changelog](CHANGELOG.md) - Project changelog

## Development

### Prerequisites

- Python 3.12 or higher
- Git
- Docker or Podman (optional, for orchestrator development)

### Quick Setup

```bash
# Clone repository
git clone https://github.com/your-org/color-scheme.git
cd color-scheme

# Run automated setup
./scripts/setup-dev.sh
```

The setup script will:
1. Check prerequisites
2. Install uv package manager
3. Install all dependencies
4. Set up pre-commit hooks
5. Verify installation

### Manual Development Setup

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup core package
cd packages/core
uv sync --dev

# Setup orchestrator package
cd ../orchestrator
uv sync --dev

# Return to root
cd ../..
```

### Running Tests

```bash
cd packages/core

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/color_scheme --cov-report=term

# Run in parallel (faster)
uv run pytest -n auto

# Ensure 95%+ coverage
uv run pytest --cov=src/color_scheme --cov-fail-under=95
```

### Code Quality

```bash
cd packages/core

# Format code
uv run black .
uv run isort .

# Lint code
uv run ruff check .
uv run ruff check --fix .  # Auto-fix

# Type check
uv run mypy src/

# Security scan
uv run bandit -r src/
```

### Development Commands

```bash
# Run CLI (core)
cd packages/core
uv run color-scheme --help

# Run CLI (orchestrator)
cd packages/orchestrator
uv run color-scheme --help

# Add dependency
uv add <package-name>

# Update dependencies
uv sync --upgrade
```

## Architecture

This project uses a **monorepo** structure with two independent packages:

```
color-scheme/
├── packages/
│   ├── core/              # Standalone color extraction
│   └── orchestrator/      # Container orchestration
├── templates/             # Shared Jinja2 templates
├── scripts/               # Development automation
├── docs/                  # Comprehensive documentation
└── .github/              # CI/CD workflows
```

### Core Package

**Purpose**: Standalone color extraction and scheme generation

- Direct installation on host system
- Multiple backend support (pywal, wallust, custom)
- Full CLI interface
- Template-based output generation

**Use for**: Direct control, development, custom backends

### Orchestrator Package

**Purpose**: Containerized execution layer

- Runs core in isolated containers
- No backend installation required
- Same CLI as core package
- Docker/Podman support

**Use for**: Isolation, automated environments, multiple backend versions

Both packages expose the same `color-scheme` CLI. Install one, not both.

See [Architecture Overview](docs/architecture/overview.md) for detailed design.

## Technology Stack

**Core Technologies**:
- Python 3.12+
- uv (package management)
- Typer (CLI framework)
- Pydantic (data validation)
- dynaconf (configuration)
- Jinja2 (templates)

**Development Tools**:
- pytest (testing)
- black, ruff, isort (code quality)
- mypy (type checking)
- GitHub Actions (CI/CD)

**External Dependencies** (from GitHub):
- rich-logging
- task-pipeline
- container-manager

See [Architecture Overview](docs/architecture/overview.md) for complete stack.

## Configuration

Configuration is managed via `settings.toml`:

```toml
# Logging
[logging]
level = "INFO"
show_time = true
show_path = false

# Output
[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]

# Generation
[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

# Backend-specific settings
[backends.pywal]
backend_algorithm = "haishoku"

[backends.wallust]
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16
```

Configuration priority (highest to lowest):
1. CLI flags
2. Environment variables
3. User config (`~/.config/color-scheme/settings.toml`)
4. Package defaults
5. Pydantic defaults

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/development/contributing.md) for:

- Development workflow
- Code standards
- Commit message conventions
- Pull request process
- Code review expectations

### Quick Contribution Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/core/your-feature`
3. Make changes and add tests (95%+ coverage required)
4. Run quality checks: `black`, `ruff`, `mypy`, `pytest`
5. Commit with conventional commit format
6. Push and create pull request

## Design Principles

- **YAGNI**: Only implement what's needed
- **Type Safety**: Pydantic models throughout
- **Testability**: 95%+ coverage requirement
- **Configuration over Code**: Prefer settings files
- **Template-Driven**: Jinja2 for all output formats

## Project Status

### Completed (Phase 1)
- ✅ Monorepo structure
- ✅ Configuration system with dynaconf + Pydantic
- ✅ CI/CD pipeline
- ✅ Development automation
- ✅ Comprehensive documentation

### In Progress
- 📝 Phase 2: Backend implementations

### Planned
- 📋 Phase 3: Output generation
- 📋 Phase 4: Container orchestration
- 📋 Phase 5: Advanced features

See [Implementation Progress](docs/implementation-progress.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Documentation](docs/README.md)
- [Contributing Guide](docs/development/contributing.md)
- [Architecture Overview](docs/architecture/overview.md)
- [Issue Tracker](https://github.com/your-org/color-scheme/issues)
- [Changelog](CHANGELOG.md)

## Acknowledgments

Built with:
- [Python](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) by Astral
- [Typer](https://typer.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [dynaconf](https://www.dynaconf.com/)
- [Jinja2](https://jinja.palletsprojects.com/)

Inspired by:
- [pywal](https://github.com/dylanaraps/pywal)
- [wallust](https://github.com/dharmx/wallust)
