# color-scheme-settings

Shared layered configuration system for color-scheme packages.

## Overview

This package provides a unified settings system that:

- **Merges multiple layers**: defaults → project → user → environment → CLI
- **Validates with Pydantic**: Type-safe configuration models
- **Supports namespaces**: Each package registers its own schema
- **Handles overrides**: Dot-notation CLI overrides (`--set logging.level=DEBUG`)

## Installation

```bash
pip install color-scheme-settings
```

Or install from source:

```bash
cd packages/settings
uv sync
```

## Quick Start

```python
from pydantic import BaseModel
from color_scheme_settings import (
    SchemaRegistry,
    configure,
    load_config,
    apply_overrides,
)

# Define package schemas
class LoggingSettings(BaseModel):
    level: str = "INFO"
    show_time: bool = True

class OutputSettings(BaseModel):
    directory: str = "~/.local/share/color-scheme"
    format: str = "json"

# Register schemas
SchemaRegistry.register("logging", LoggingSettings)
SchemaRegistry.register("output", OutputSettings)

# Build unified model (composes all namespaces)
class UnifiedConfig(BaseModel):
    logging: LoggingSettings = LoggingSettings()
    output: OutputSettings = OutputSettings()

# Configure and load
configure(UnifiedConfig)
config = load_config()

print(config.logging.level)  # "INFO"
print(config.output.format)  # "json"
```

## API Reference

### `SchemaRegistry`

Register package configuration schemas.

```python
from color_scheme_settings import SchemaRegistry

# Register a namespace
SchemaRegistry.register("my_namespace", MySettingsModel)

# Get registered schema
model = SchemaRegistry.get("my_namespace")

# List all namespaces
namespaces = SchemaRegistry.list_namespaces()
```

### `configure()`

Configure the settings system before loading.

```python
from color_scheme_settings import configure

configure(
    unified_model=UnifiedConfig,
    project_root=Path("/path/to/project"),
    user_config_path=Path("~/.config/color-scheme/settings.toml"),
)
```

### `load_config()`

Load and merge all configuration layers. Cached after first call.

```python
from color_scheme_settings import load_config

config = load_config()
```

### `reload_config()`

Force reload configuration (useful for testing).

```python
from color_scheme_settings import reload_config

config = reload_config()
```

### `get_config()`

Load config with optional CLI overrides.

```python
from color_scheme_settings import get_config

config = get_config(overrides=["logging.level=DEBUG", "output.format=yaml"])
```

### `apply_overrides()`

Apply dot-notation overrides to a config model.

```python
from color_scheme_settings import apply_overrides

config = load_config()
updated = apply_overrides(config, ["logging.level=WARNING"])
```

## Configuration Layers

Settings are loaded and merged in this order (later layers override earlier):

1. **Defaults** - Hardcoded in Pydantic models
2. **Project** - `settings.toml` in project root
3. **User** - `~/.config/color-scheme/settings.toml`
4. **Environment** - `COLOR_SCHEME_*` environment variables
5. **CLI** - `--set key=value` overrides

## Error Handling

```python
from color_scheme_settings import (
    SettingsError,           # Base exception
    SettingsFileError,       # File read/parse errors
    SettingsValidationError, # Pydantic validation failures
    SettingsOverrideError,   # Invalid override syntax
    SettingsRegistryError,   # Schema registration errors
)
```

## Development

```bash
cd packages/settings

# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/color_scheme_settings
```

## Related Documentation

- [Settings Layer Architecture](../../docs/explanations/settings-layers.md)
- [Configuration Reference](../../docs/reference/configuration/settings-model.md)
