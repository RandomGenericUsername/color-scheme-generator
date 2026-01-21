# color-scheme-core

Core color scheme generator with multiple backends.

## Features

- Multiple color extraction backends (pywal, wallust, custom)
- Multiple output formats (JSON, CSS, SCSS, YAML, shell scripts, etc.)
- Configurable via settings.toml
- CLI and Python API

## Installation

```bash
pip install color-scheme-core
```

## Usage (Phase 1 - Under Development)

Currently available:

```bash
# Show version
color-scheme version

# Show help
color-scheme --help
```

Coming in Phase 2:

```bash
# Generate color scheme (not yet implemented)
color-scheme generate image.png
```

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Check coverage
uv run pytest --cov
```

## Documentation

See main project documentation in repository root.
