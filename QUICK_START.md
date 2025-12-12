# Quick Start Guide

This guide shows you how to install and use the color-scheme-generator project using both `uv` and `make`.

## Prerequisites

- **Python 3.12+**
- **uv** - Fast Python package manager ([install instructions](https://docs.astral.sh/uv/getting-started/installation/))
- **Docker or Podman** - For running backend containers
- **Make** - Build automation tool (usually pre-installed on Linux/macOS)

## Installation

### Option 1: Using Make (Recommended)

Install everything from the project root:

```bash
# Clone the repository
git clone <repository-url>
cd color-scheme-generator

# Install both core and orchestrator
make install

# Build Docker images for backends
make docker-build
```

### Option 2: Using uv Directly

Install components individually:

```bash
# Install core tool
cd core
uv sync

# Install orchestrator
cd ../orchestrator
uv sync

# Build Docker images
cd ..
make docker-build
```

### Option 3: Install Individual Components

```bash
# Core only
cd core && make install

# Orchestrator only
cd orchestrator && make install
```

## Usage

### Using the Orchestrator (Containerized Backends)

The orchestrator runs color extraction backends in isolated Docker containers:

```bash
cd orchestrator

# Generate color scheme from an image
uv run color-scheme generate /path/to/wallpaper.png

# Specify a backend explicitly
uv run color-scheme generate /path/to/wallpaper.png --backend pywal

# Use wallust backend
uv run color-scheme generate /path/to/wallpaper.png --backend wallust

# Show available backends
uv run color-scheme install --list-backends
```

### Using the Core Tool Directly

The core tool runs backends locally without containers:

```bash
cd core

# Generate color scheme
uv run colorscheme-gen generate /path/to/wallpaper.png

# Specify backend and output format
uv run colorscheme-gen generate wallpaper.png --backend pywal --formats json css

# Show generated colors
uv run colorscheme-gen show ~/.cache/colorscheme/colors.json
```

### Using Make Shortcuts

```bash
# From core directory
make run ARGS="generate wallpaper.png"
make run ARGS="show ~/.cache/colorscheme/colors.json"

# From orchestrator directory
make run ARGS="generate wallpaper.png --backend pywal"
```

## Project Structure

```
color-scheme-generator/
├── core/                    # Core color extraction library
│   ├── src/colorscheme_generator/
│   ├── pyproject.toml
│   └── Makefile
├── orchestrator/            # Container orchestration layer
│   ├── src/color_scheme/
│   ├── docker/             # Backend Dockerfiles
│   ├── pyproject.toml
│   └── Makefile
├── Makefile                # Root Makefile (delegates to components)
└── QUICK_START.md          # This file
```

## Common Commands

### Development

```bash
# Run tests
make test

# Run linters
make lint

# Format code
make format

# Type check
make typecheck

# Clean build artifacts
make clean
```

### Docker Management

```bash
# Build all backend images
make docker-build

# Build specific backend
cd orchestrator
make docker-build-pywal
make docker-build-wallust

# Clean Docker images
make docker-clean
```

## Next Steps

- Read the [full documentation](README.md)
- Check [core documentation](core/docs/README.md)
- Check [orchestrator documentation](orchestrator/README.md)
- See [development guide](core/docs/development.md)

