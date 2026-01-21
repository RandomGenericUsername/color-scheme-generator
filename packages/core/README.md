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

## Usage

```bash
# Generate color scheme
color-scheme generate image.png

# Show color scheme
color-scheme show
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
