# color-scheme-orchestrator

Container orchestrator for color-scheme-core.

## Features

- Runs color extraction in isolated containers
- Same CLI as core package
- Automatic container image management
- Supports Docker and Podman

## Installation

```bash
pip install color-scheme-orchestrator
```

Requires Docker or Podman.

## Usage (Phase 1 - Under Development)

Once fully implemented:

```bash
# Install backend container images
color-scheme install pywal

# Generate color scheme (containerized)
color-scheme generate image.png

# Show color scheme (delegates to core, no container)
color-scheme show
```

Currently available:

```bash
# Show version
color-scheme version
```

Full containerization functionality coming in later phases.

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest
```

## Documentation

See main project documentation in repository root.
