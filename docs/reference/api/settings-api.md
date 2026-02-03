# Settings API Reference

**Scope:** Public API for the layered configuration system
**Extracted:** February 3, 2026
**Source:** `packages/settings/src/color_scheme_settings/` (public module)

Complete reference for the settings system: configuration loading, schema registration, validation, and CLI overrides.

---

## Overview

The settings system provides a **layered configuration** approach with automatic merging:

1. **Package Layer** - Built-in defaults (lowest priority)
2. **Project Layer** - Project-wide settings (`{project_root}/settings.toml`)
3. **User Layer** - User overrides (`~/.config/color-scheme/settings.toml`)
4. **CLI Layer** - Command-line argument overrides (highest priority)

---

## Module Exports

**Public API from `color_scheme_settings`:**

```python
from color_scheme_settings import (
    SchemaRegistry,     # Schema registration and retrieval
    load_config,        # Load all layers (cached)
    reload_config,      # Force reload (testing)
    get_config,         # Load with CLI overrides
    apply_overrides,    # Apply dotted-key overrides
    configure,          # Pre-configure the system
)

# Exception types
from color_scheme_settings import (
    SettingsError,              # Base exception
    SettingsFileError,          # File I/O problems
    SettingsValidationError,    # Validation failures
    SettingsOverrideError,      # Invalid override keys
    SettingsRegistryError,      # Registry issues
)
```

---

## Configuration

### `configure(unified_model, project_root=None, user_config_path=None) -> None`

Pre-configure the settings system before first load.

**Parameters:**
- `unified_model` (`type[BaseModel]`): Pydantic model that composes all namespaces
- `project_root` (`Path | None`): Path to project root (contains settings.toml)
- `user_config_path` (`Path | None`): Path to user settings file

**Raises:** None (raises on load_config if not configured)

**Example:**
```python
from color_scheme.config.config import AppConfig
from color_scheme_settings import configure

# Configure before loading
configure(
    unified_model=AppConfig,
    project_root=Path("."),
    user_config_path=Path.home() / ".config/color-scheme/settings.toml"
)

# Now load_config() will work
config = load_config()
```

**Note:** Usually called once at application startup.

---

## Loading and Reloading

### `load_config() -> BaseModel`

Loads, merges, and validates all settings layers.

**Returns:** Validated unified configuration object

**Raises:**
- `SettingsError` - System not configured (call `configure()` first)
- `SettingsFileError` - File reading or TOML parsing error
- `SettingsValidationError` - Pydantic validation failure

**Behavior:**
1. Discovers all layers (package → project → user)
2. Merges layers (later layers override earlier)
3. Validates merged config against unified model
4. Caches result for subsequent calls
5. Returns unified config object

**Caching:**
- Result is cached after first call
- Use `reload_config()` to force refresh (testing only)

**Example:**
```python
from color_scheme_settings import load_config

# First call: loads and validates
config = load_config()

# Second call: returns cached instance
config2 = load_config()
assert config is config2  # Same object

# Access configuration
print(config.generation.saturation_adjustment)
print(config.output.formats)
```

---

### `reload_config() -> BaseModel`

Forces a complete reload from all layers, clearing the cache.

**Parameters:** None

**Returns:** Freshly loaded and validated configuration

**Raises:** Same as `load_config()`

**Usage:** Testing and dynamic reloads

**Example:**
```python
from color_scheme_settings import reload_config

# Force a fresh load
fresh_config = reload_config()

# Changes to settings files are now reflected
```

---

### `get_config(**overrides) -> BaseModel`

Loads config with optional CLI argument overrides.

**Parameters:**
- `**overrides` (dict[str, Any]): Keyword arguments with dotted-key paths

**Returns:** Validated config with overrides applied

**Raises:**
- `SettingsOverrideError` - Invalid override key path
- Other `SettingsError` subclasses from load_config

**Example:**
```python
from color_scheme_settings import get_config

# Load with CLI overrides
config = get_config(
    **{
        "core.generation.saturation_adjustment": 1.5,
        "core.output.directory": "/custom/output",
        "core.output.formats": ["json", "sh"]
    }
)

# Access overridden values
print(config.generation.saturation_adjustment)  # 1.5
print(config.output.directory)  # /custom/output
```

---

## Schema Registration

### `SchemaRegistry` Class

Registry for all namespace schemas.

**Purpose:** Each package registers its namespace, Pydantic model, and defaults file.

#### Class Methods

##### `register(namespace: str, model: type[BaseModel], defaults_file: Path) -> None`

Register a package's configuration schema.

**Parameters:**
- `namespace` (`str`): Unique identifier (e.g., "core", "orchestrator")
- `model` (`type[BaseModel]`): Pydantic model for validation
- `defaults_file` (`Path`): Path to package's settings.toml (defaults)

**Raises:**
- `SettingsRegistryError` - Namespace already registered

**Example:**
```python
from color_scheme_settings import SchemaRegistry
from color_scheme.config.config import AppConfig
from pathlib import Path

# Register core package
SchemaRegistry.register(
    namespace="core",
    model=AppConfig,
    defaults_file=Path("packages/core/settings.toml")
)

# Register orchestrator package
SchemaRegistry.register(
    namespace="orchestrator",
    model=OrchestratorConfig,
    defaults_file=Path("packages/orchestrator/settings.toml")
)
```

##### `get(namespace: str) -> SchemaEntry`

Retrieve a registered schema by namespace.

**Parameters:**
- `namespace` (`str`): Namespace identifier

**Returns:** `SchemaEntry` with namespace, model, and defaults_file

**Raises:**
- `SettingsRegistryError` - Namespace not registered

**Example:**
```python
entry = SchemaRegistry.get("core")
print(entry.namespace)      # "core"
print(entry.model)          # <class 'AppConfig'>
print(entry.defaults_file)  # Path('packages/core/settings.toml')
```

##### `all_entries() -> list[SchemaEntry]`

Get all registered entries.

**Returns:** List of SchemaEntry objects

**Example:**
```python
for entry in SchemaRegistry.all_entries():
    print(f"{entry.namespace}: {entry.model.__name__}")
```

##### `all_namespaces() -> list[str]`

Get all registered namespace names.

**Returns:** List of namespace strings

**Example:**
```python
namespaces = SchemaRegistry.all_namespaces()
# ["core", "orchestrator", "settings"]
```

##### `clear() -> None`

Remove all registered schemas (testing only).

**Usage:** Reset registry between tests

**Example:**
```python
SchemaRegistry.clear()  # Back to empty state
```

---

## Override Application

### `apply_overrides(config: BaseModel, overrides: dict[str, Any]) -> BaseModel`

Apply CLI argument overrides to a validated config.

**Parameters:**
- `config` (`BaseModel`): Validated configuration object
- `overrides` (`dict[str, Any]`): Dotted-key paths and values

**Returns:** New config instance with overrides applied and re-validated

**Raises:**
- `SettingsOverrideError` - Invalid key path (doesn't exist in config)

**Dotted-Key Format:**
```python
# Format: "namespace.section.field"
overrides = {
    "core.generation.saturation_adjustment": 1.5,
    "core.output.directory": "/tmp/output",
    "core.output.formats": ["json", "sh"],
    "orchestrator.engine": "podman",
}
```

**Behavior:**
1. Splits each key by dots
2. Walks the config dictionary following the path
3. Sets the leaf value
4. Re-validates entire config through Pydantic
5. Returns new config instance

**Example:**
```python
from color_scheme_settings import load_config, apply_overrides

# Load base config
config = load_config()

# Apply overrides
overrides = {
    "core.generation.saturation_adjustment": 1.2,
    "core.output.directory": Path("/custom/out")
}

new_config = apply_overrides(config, overrides)

# Values are updated
print(new_config.generation.saturation_adjustment)  # 1.2
print(new_config.output.directory)  # /custom/out
```

---

## Configuration Layers

### Layer Discovery

The settings system discovers layers in this order (lowest to highest priority):

**Layer 1: Package Defaults**
- Source: Each package's defaults (TOML file)
- Registry: Registered in `SchemaRegistry`
- Section format: Flat (no namespace prefix)
- Example: `[generation]`, `[output]`

**Layer 2: Project Settings**
- Source: `{project_root}/settings.toml`
- Section format: Namespaced with dot notation
- Example: `[core.generation]`, `[orchestrator.engine]`

**Layer 3: User Settings**
- Source: `~/.config/color-scheme/settings.toml` (or custom path)
- Section format: Namespaced with dot notation
- Example: `[core.output]`, `[core.logging]`

**Layer 4: CLI Overrides** (Applied via `apply_overrides`)
- Source: Command-line arguments
- Format: Dotted-key paths
- Example: `core.output.directory`, `core.generation.saturation_adjustment`

### Merge Behavior

Later layers override earlier layers:

```
Package Defaults
    ↓ (override with)
Project Settings
    ↓ (override with)
User Settings
    ↓ (override with)
CLI Overrides
    ↓
Final Config
```

**Example:**
```toml
# packages/core/settings.toml (Package Layer)
[generation]
saturation_adjustment = 1.0
default_backend = "custom"

# project_root/settings.toml (Project Layer)
[core.generation]
saturation_adjustment = 1.2

# ~/.config/color-scheme/settings.toml (User Layer)
[core.output]
directory = "/home/user/colors"

# CLI (Overrides Layer)
core.generation.saturation_adjustment = 1.5
```

**Result:**
```python
config.generation.saturation_adjustment  # 1.5 (from CLI override)
config.generation.default_backend        # "custom" (from package default)
config.output.directory                  # /home/user/colors (from user layer)
```

---

## Loading Process

### Complete Load Flow

```python
from color_scheme.config.config import AppConfig
from color_scheme_settings import configure, load_config, apply_overrides

# Step 1: Configure system
configure(
    unified_model=AppConfig,
    project_root=Path("."),
)

# Step 2: Load all layers
config = load_config()
# Merges: packages/core/settings.toml
#       + ./settings.toml
#       + ~/.config/color-scheme/settings.toml

# Step 3: Apply CLI overrides
final_config = apply_overrides(
    config,
    {
        "core.output.directory": "/custom",
        "core.generation.saturation_adjustment": 1.2,
    }
)
```

### Validation

Each layer is validated when merged:

1. **Package Layer** - Validated by package's Pydantic model
2. **Project Layer** - Values validated by same model
3. **User Layer** - Values validated by same model
4. **Final Merge** - Entire unified config validated

**If validation fails:**
- `SettingsValidationError` is raised with details
- Cannot proceed until config is fixed

---

## Error Handling

### SettingsError (Base)

Base exception for all settings errors.

```python
from color_scheme_settings import SettingsError

try:
    config = load_config()
except SettingsError as e:
    print(f"Settings error: {e}")
```

### SettingsFileError

Raised when TOML files cannot be read or parsed.

```python
from color_scheme_settings import SettingsFileError

try:
    config = load_config()
except SettingsFileError as e:
    print(f"File: {e.file_path}")
    print(f"Reason: {e.reason}")
```

### SettingsValidationError

Raised when validation fails against Pydantic model.

```python
from color_scheme_settings import SettingsValidationError

try:
    config = load_config()
except SettingsValidationError as e:
    print(f"Namespace: {e.namespace}")
    print(f"Error: {e.validation_error}")
    print(f"Source: {e.source_layer}")
```

### SettingsOverrideError

Raised when override key path doesn't exist.

```python
from color_scheme_settings import apply_overrides, SettingsOverrideError

try:
    new_config = apply_overrides(config, {"invalid.key.path": "value"})
except SettingsOverrideError as e:
    print(f"Invalid key: {e.key}")
```

### SettingsRegistryError

Raised when registering duplicate or accessing unknown namespace.

```python
from color_scheme_settings import SchemaRegistry, SettingsRegistryError

try:
    SchemaRegistry.register("core", model, defaults)
    SchemaRegistry.register("core", model, defaults)  # Error!
except SettingsRegistryError as e:
    print(f"Namespace: {e.namespace}")
    print(f"Error: {e.reason}")
```

---

## Complete Example

```python
from pathlib import Path
from color_scheme.config.config import AppConfig
from color_scheme_settings import (
    SchemaRegistry,
    configure,
    load_config,
    apply_overrides,
)

# 1. Register core package schema
SchemaRegistry.register(
    namespace="core",
    model=AppConfig,
    defaults_file=Path("packages/core/settings.toml")
)

# 2. Configure settings system
configure(
    unified_model=AppConfig,
    project_root=Path("."),
)

# 3. Load all layers (cached)
config = load_config()
print(f"Saturation: {config.generation.saturation_adjustment}")
print(f"Formats: {config.output.formats}")

# 4. Apply CLI overrides
cli_args = {
    "core.generation.saturation_adjustment": 1.5,
    "core.output.directory": "/output"
}
final_config = apply_overrides(config, cli_args)

print(f"Final saturation: {final_config.generation.saturation_adjustment}")
print(f"Final directory: {final_config.output.directory}")
```

---

## Related Documentation

- [Settings Schema](../configuration/settings-schema.md) - Configuration fields and structure
- [Defaults Reference](../configuration/defaults.md) - Default values
- [CLI Commands](../cli/core-commands.md) - Using settings from CLI
- [Configuration](../configuration/) - Complete configuration guide
