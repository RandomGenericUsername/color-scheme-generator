# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

color-scheme is a CLI tool for extracting and generating color schemes from images. It supports multiple color extraction backends (pywal, wallust, custom) and outputs colors in various formats (JSON, CSS, SCSS, YAML, shell scripts, GTK CSS, rofi rasi, terminal sequences).

## Commands

```bash
# Install dependencies
uv sync

# Run the CLI
uv run color-scheme <command>

# Run tests
uv run pytest

# Run tests in parallel
uv run pytest -n auto

# Linting and formatting
uv run ruff check .
uv run ruff format .
uv run black .
uv run isort .

# Type checking
uv run mypy src/

# Security scanning
uv run bandit -r src/
```

## Architecture

### Entry Point
- `src/color_scheme/main.py` - Creates logger and invokes CLI app
- CLI entry point registered as `color-scheme` in pyproject.toml

### CLI Structure (Typer-based)
- `cli/main.py` - Typer app with registered commands
- `cli/commands/` - Individual command implementations (install, uninstall)
- `cli/utils/reusable_cli_options.py` - Type aliases for shared CLI options (ConfigOption, VerboseOption, LogDirOption, LogLevelOption)
- `cli/config/settings.py` - Verbosity to log level mapping

### Shared Utilities
- `shared/config/logging.py` - Logger factory using rich-logging library

### Templates
- `templates/` - Jinja2 templates for color output formats
- Template variables: `source_image`, `backend`, `generated_at`, `background`, `foreground`, `cursor`, `colors` (list)
- Color objects have `.hex` and `.rgb` properties

## External Dependencies (from GitHub)
- `rich-logging` - Logging with rich console output
- `task-pipeline` - Task orchestration
- `container-manager` - Container (Docker/Podman) management

## Configuration
- `settings.toml` - Runtime configuration for logging, container engine, output formats, template directory, and backend-specific settings
