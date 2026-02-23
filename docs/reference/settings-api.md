# Reference: Settings API

**Package:** `color-scheme-settings`
**Module:** `color_scheme_settings`
**Source:** `packages/settings/src/color_scheme_settings/`

---

## Module exports

```python
from color_scheme_settings import (
    # Configuration functions
    configure,          # Pre-configure the system before first load
    load_config,        # Load all layers (result is cached)
    reload_config,      # Force a fresh load (clears cache)
    get_config,         # Load with optional CLI overrides
    apply_overrides,    # Apply dotted-key overrides to a loaded config

    # Registry
    SchemaRegistry,     # Register and retrieve per-namespace schemas

    # Exceptions
    SettingsError,          # Base exception
    SettingsFileError,      # TOML file I/O or parse error
    SettingsValidationError,# Pydantic validation failure
    SettingsOverrideError,  # Invalid override key path
    SettingsRegistryError,  # Duplicate or unknown namespace
)
```

---

## configure

```python
configure(
    unified_model: type[BaseModel],
    project_root: Path | None = None,
    user_config_path: Path | None = None,
) -> None
```

Pre-configure the settings system before the first `load_config()` call.

| Parameter | Type | Description |
|-----------|------|-------------|
| `unified_model` | `type[BaseModel]` | Pydantic model that composes all registered namespaces. |
| `project_root` | `Path \| None` | Directory containing `settings.toml` (project layer). |
| `user_config_path` | `Path \| None` | Path to user settings file (user layer). |

Call once at application startup before loading config.

---

## load_config

```python
load_config() -> BaseModel
```

Load, merge, and validate all settings layers. The result is cached; subsequent calls
return the same object identity.

**Layer order (lowest to highest priority):**

1. Package defaults (registered in `SchemaRegistry`)
2. Project config (`{project_root}/settings.toml`)
3. User config (`~/.config/color-scheme/settings.toml` or custom path)

**Raises:**
- `SettingsError` — system not yet configured (call `configure()` first)
- `SettingsFileError` — file exists but cannot be read or parsed
- `SettingsValidationError` — merged values fail Pydantic validation

**Caching behavior:** After the first successful call, the validated config object is
cached. Every subsequent call to `load_config()` returns the same object. To clear the
cache, call `reload_config()`.

```python
config1 = load_config()
config2 = load_config()
assert config1 is config2  # True
```

---

## reload_config

```python
reload_config() -> BaseModel
```

Clears the internal cache and performs a fresh load from all layers. Returns the new
config object.

Raises the same exceptions as `load_config()`.

Intended for use in tests where settings files are modified between calls.

---

## get_config

```python
get_config(overrides: dict[str, Any] | None = None) -> BaseModel
```

Load config and apply optional CLI-level overrides on top. The overrides take
precedence over all other layers, including environment variables and user config.

| Parameter | Type | Description |
|-----------|------|-------------|
| `overrides` | `dict[str, Any] \| None` | Mapping of dotted-key paths to values. `None` or empty dict means no overrides. |

**Raises:**
- `SettingsOverrideError` — a key path in the dict does not exist in the schema
- Other `SettingsError` subclasses from `load_config()`

```python
config = get_config({
    "core.generation.saturation_adjustment": 0.5,
    "core.output.directory": "/custom/output",
    "core.output.formats": ["json", "sh"],
})
```

Key format: `"<namespace>.<section>.<field>"`.

---

## apply_overrides

```python
apply_overrides(config: BaseModel, overrides: dict[str, Any]) -> BaseModel
```

Apply a dict of dotted-key overrides to an already-loaded config object. Returns a new
validated config instance.

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | `BaseModel` | Validated config from `load_config()` or `get_config()`. |
| `overrides` | `dict[str, Any]` | Dotted-key paths to values. |

**Raises:** `SettingsOverrideError` if a key path does not exist.

```python
config = load_config()
new_config = apply_overrides(config, {
    "core.generation.saturation_adjustment": 1.2,
})
```

---

## SchemaRegistry

Class for per-namespace schema registration. Each package registers its own namespace,
Pydantic model, and defaults file before `load_config()` is called.

### SchemaRegistry.register

```python
SchemaRegistry.register(
    namespace: str,
    model: type[BaseModel],
    defaults_file: Path,
) -> None
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `namespace` | `str` | Unique identifier, e.g. `"core"` or `"orchestrator"`. |
| `model` | `type[BaseModel]` | Pydantic model for this namespace. |
| `defaults_file` | `Path` | Path to the package's `settings.toml` defaults file. |

**Raises:** `SettingsRegistryError` if the namespace is already registered.

```python
SchemaRegistry.register(
    namespace="core",
    model=AppConfig,
    defaults_file=Path("packages/core/settings.toml"),
)
```

### SchemaRegistry.get

```python
SchemaRegistry.get(namespace: str) -> SchemaEntry
```

Retrieve a registered schema by namespace name.

**Raises:** `SettingsRegistryError` if the namespace is not registered.

```python
entry = SchemaRegistry.get("core")
print(entry.namespace)     # "core"
print(entry.model)         # <class 'AppConfig'>
print(entry.defaults_file) # PosixPath('packages/core/settings.toml')
```

### SchemaRegistry.all_entries

```python
SchemaRegistry.all_entries() -> list[SchemaEntry]
```

Returns all registered `SchemaEntry` objects.

### SchemaRegistry.all_namespaces

```python
SchemaRegistry.all_namespaces() -> list[str]
```

Returns all registered namespace names as a list of strings.

### SchemaRegistry.clear

```python
SchemaRegistry.clear() -> None
```

Removes all registered schemas. For use in tests only.

---

## Configuration file format

### Package defaults (`settings.toml` per package)

Flat section names without namespace prefix:

```toml
[generation]
saturation_adjustment = 1.0
default_backend = "custom"

[output]
directory = "~/.config/color-scheme/output"
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]
```

### Project and user config

Section names are prefixed with the namespace:

```toml
[core.generation]
saturation_adjustment = 1.2
default_backend = "wallust"

[core.output]
formats = ["json", "sh"]
```

---

## Environment variable format

### COLORSCHEME_* prefix

Variables with the `COLORSCHEME_` prefix are resolved as config overrides. The
double-underscore (`__`) acts as a nesting separator between section and key names:

```
COLORSCHEME_<SECTION>__<KEY>=<value>
```

Examples:

```bash
export COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom
# → generation.default_backend = "custom"

export COLORSCHEME_GENERATION__SATURATION_ADJUSTMENT=1.5
# → generation.saturation_adjustment = 1.5 (parsed as float)

export COLORSCHEME_OUTPUT__DIRECTORY=/tmp/colors
# → output.directory = "/tmp/colors"
```

Environment variables have higher priority than user config but lower than
CLI overrides passed to `get_config()`.

### COLOR_SCHEME_TEMPLATES (special case)

```bash
export COLOR_SCHEME_TEMPLATES=/path/to/custom/templates
```

This single variable (different prefix) maps directly to `templates.directory`.

---

## Layer precedence summary

```
package defaults (SchemaRegistry)
    ↑ overridden by
project settings.toml
    ↑ overridden by
user ~/.config/color-scheme/settings.toml
    ↑ overridden by
COLORSCHEME_* environment variables
    ↑ overridden by
get_config(overrides) / CLI
```

---

## List merge behavior

When an override layer provides a list value for a key that is a list in a lower layer,
the lower layer's list is replaced entirely. Elements are not appended or merged.

```toml
# Package default
formats = ["json", "css", "yaml", "sh", "scss", "rasi", "sequences", "gtk.css"]

# User config — replaces the whole list
[core.output]
formats = ["json", "sh"]
```

Result: `formats == ["json", "sh"]`.

---

## Verification reference

| BHV | Behavior |
|-----|---------|
| BHV-0017 | Duplicate namespace in `SchemaRegistry.register` raises `SettingsRegistryError` |
| BHV-0018 | `SchemaRegistry.get` on unknown namespace raises `SettingsRegistryError` |
| BHV-0019 | Layer order: package < project < user < CLI |
| BHV-0020 | List values are replaced, not merged, when overridden |
| BHV-0021 | `get_config(overrides)` values take precedence over all layers |
| BHV-0022 | `load_config()` caches result; second call returns same object |
| BHV-0031 | `COLORSCHEME_SECTION__KEY` maps to `section.key` |
| BHV-0032 | `COLOR_SCHEME_TEMPLATES` maps to `templates.directory` |
