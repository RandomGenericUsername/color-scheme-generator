# Settings Layered Architecture Design

**Date:** 2026-01-30
**Status:** Design Complete
**Supersedes:** 2026-01-29-settings-layered-architecture.md

## Overview

A unified, layered configuration system for the color-scheme project. A new shared `settings` package owns all config infrastructure (loading, merging, overrides). Core and orchestrator register their schemas independently. Settings files are discovered from four layers and deep-merged in priority order, with CLI arguments applied on top.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Namespace style (root/user files) | Explicit: `[core.*]`, `[orchestrator.*]` | Makes ownership clear in shared files |
| Namespace style (package files) | Flat: `[logging]`, `[container]` | Package location implies ownership; loader wraps |
| Merge strategy | Deep merge | Individual fields override; everything else inherits |
| List handling | Replace (atomic) | If you specify a list, you own the whole list |
| Runtime config object | Unified composition | `config.core.*` and `config.orchestrator.*` — no inheritance |
| Config infrastructure ownership | New shared package | Neither core nor orchestrator owns the loader |
| CLI override mechanism | Shared package owns it | Single merge path, one source of truth |

## Layer Priority (Lowest to Highest)

```
1. Package defaults    packages/core/config/settings.toml         (flat sections)
                       packages/orchestrator/config/settings.toml  (flat sections)

2. Project root        settings.toml                               (namespaced: [core.*], [orchestrator.*])

3. User config         ~/.config/color-scheme/settings.toml        (namespaced: [core.*], [orchestrator.*])

4. CLI arguments       --saturation, --backend, --engine, etc.     (applied via overrides dict)
```

## Package Structure

```
packages/
├── settings/                          # NEW — shared config infrastructure
│   ├── src/color_scheme_settings/
│   │   ├── __init__.py                # Public API: load_config, get_config, reload_config
│   │   ├── loader.py                  # Layer discovery + TOML loading
│   │   ├── merger.py                  # Deep merge algorithm
│   │   ├── registry.py                # Schema registration system
│   │   ├── unified.py                 # UnifiedConfig model
│   │   ├── overrides.py               # CLI override application
│   │   └── errors.py                  # Error hierarchy
│   ├── tests/
│   │   ├── conftest.py                # Fixtures: temp TOML files, patched paths
│   │   ├── test_merger.py             # deep_merge unit tests
│   │   ├── test_registry.py           # Registration + retrieval tests
│   │   ├── test_overrides.py          # Dotted key resolution, re-validation
│   │   ├── test_loader.py             # File discovery integration tests
│   │   ├── test_pipeline.py           # End-to-end: files → merge → validate → override
│   │   └── test_errors.py             # Error context and attribution
│   └── pyproject.toml
│
├── core/
│   ├── src/color_scheme/config/
│   │   ├── __init__.py                # Registers schema with SchemaRegistry
│   │   ├── config.py                  # AppConfig + sub-models (UNCHANGED)
│   │   ├── defaults.py                # Hardcoded fallbacks (UNCHANGED)
│   │   ├── enums.py                   # Backend, ColorFormat enums (UNCHANGED)
│   │   └── settings.toml              # Core defaults, flat sections (UNCHANGED)
│   └── pyproject.toml                 # depends on color-scheme-settings
│
├── orchestrator/
│   ├── src/color_scheme_orchestrator/config/
│   │   ├── __init__.py                # Registers schema with SchemaRegistry
│   │   ├── settings.py                # ContainerSettings model (UNCHANGED)
│   │   └── settings.toml              # Orchestrator defaults, flat sections
│   └── pyproject.toml                 # depends on color-scheme-settings, color-scheme-core
```

**Dependency graph:**
```
settings  <── core  <── orchestrator
    ^                        |
    └────────────────────────┘
```

## Component Designs

### Schema Registry

Each package registers its namespace, Pydantic model, and defaults file. The shared package has zero knowledge of specific schemas.

```python
# packages/settings/src/color_scheme_settings/registry.py

class SchemaEntry:
    namespace: str           # "core" or "orchestrator"
    model: type[BaseModel]   # AppConfig or ContainerSettings
    defaults_file: Path      # Path to package's settings.toml

class SchemaRegistry:
    _entries: dict[str, SchemaEntry] = {}

    @classmethod
    def register(cls, namespace: str, model: type[BaseModel], defaults_file: Path) -> None:
        """Register a package's config schema. Raises SettingsRegistryError on duplicate."""

    @classmethod
    def get(cls, namespace: str) -> SchemaEntry:
        """Retrieve a registered schema by namespace."""

    @classmethod
    def all_entries(cls) -> list[SchemaEntry]:
        """Return all registered entries."""

    @classmethod
    def all_namespaces(cls) -> list[str]:
        """Return all registered namespace names."""
```

Registration happens at import time:

```python
# packages/core/src/color_scheme/config/__init__.py
from color_scheme_settings import SchemaRegistry
SchemaRegistry.register(
    namespace="core",
    model=AppConfig,
    defaults_file=Path(__file__).parent / "settings.toml",
)

# packages/orchestrator/src/color_scheme_orchestrator/config/__init__.py
from color_scheme_settings import SchemaRegistry
SchemaRegistry.register(
    namespace="orchestrator",
    model=ContainerSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)
```

### Layer Discovery and Loading

```python
# packages/settings/src/color_scheme_settings/loader.py

class LayerSource:
    layer: str          # "package", "project", "user"
    namespace: str      # "core", "orchestrator"
    file_path: Path     # Resolved absolute path
    data: dict          # Parsed TOML contents

class SettingsLoader:
    def discover_layers(self) -> list[LayerSource]:
        """Discover all settings files across all layers, lowest priority first."""
        layers = []

        # Layer 1: Package defaults (flat sections, wrapped into namespace)
        for entry in SchemaRegistry.all_entries():
            if entry.defaults_file.exists():
                data = load_toml(entry.defaults_file)
                layers.append(LayerSource(
                    layer="package", namespace=entry.namespace, data=data,
                ))

        # Layer 2: Project root (namespaced sections)
        project_file = find_project_root() / "settings.toml"
        if project_file.exists():
            data = load_toml(project_file)
            for ns in SchemaRegistry.all_namespaces():
                if ns in data:
                    layers.append(LayerSource(
                        layer="project", namespace=ns, data=data[ns],
                    ))

        # Layer 3: User config (namespaced sections)
        user_file = Path.home() / ".config" / "color-scheme" / "settings.toml"
        if user_file.exists():
            data = load_toml(user_file)
            for ns in SchemaRegistry.all_namespaces():
                if ns in data:
                    layers.append(LayerSource(
                        layer="user", namespace=ns, data=data[ns],
                    ))

        return layers
```

**Project root discovery:** Walk up from `cwd` looking for a `settings.toml` containing a `[core]` or `[orchestrator]` top-level key. Falls back to `cwd`.

**TOML parsing:** Uses `tomllib` (stdlib Python 3.11+) instead of dynaconf. We handle layering ourselves; dynaconf adds complexity without benefit. Pydantic stays for validation.

### Deep Merge Algorithm

```python
# packages/settings/src/color_scheme_settings/merger.py

def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Returns new dict.

    Rules:
    - Dicts: recurse into matching keys, base keys preserved if not overridden
    - Lists: replaced entirely (atomic)
    - Scalars: replaced entirely
    - Keys in override not in base: added
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def merge_layers(layers: list[LayerSource]) -> dict[str, dict]:
    """Merge all layers into one dict per namespace.

    Layers arrive in priority order (lowest first).
    Returns: {"core": {...merged...}, "orchestrator": {...merged...}}
    """
    merged: dict[str, dict] = {}
    for layer in layers:
        ns = layer.namespace
        if ns not in merged:
            merged[ns] = {}
        merged[ns] = deep_merge(merged[ns], layer.data)
    return merged
```

**Example:**
```
Package (core):  {"generation": {"default_backend": "pywal", "saturation_adjustment": 1.0}}
Project (core):  {"generation": {"saturation_adjustment": 1.3}}
User (core):     {"output": {"formats": ["json", "css"]}}

Result (core): {
    "generation": {"default_backend": "pywal", "saturation_adjustment": 1.3},
    "output": {"formats": ["json", "css"]}
}
```

### UnifiedConfig Model

```python
# packages/settings/src/color_scheme_settings/unified.py

class UnifiedConfig(BaseModel):
    """Root configuration composing all registered namespaces.

    Access:
        config.core.logging.level
        config.core.output.directory
        config.core.generation.default_backend
        config.core.backends.pywal.backend_algorithm
        config.core.templates.directory
        config.orchestrator.container.engine
        config.orchestrator.container.image_registry
    """
    model_config = ConfigDict(frozen=True)

    core: AppConfig
    orchestrator: ContainerSettings

    @classmethod
    def from_registry(cls, merged: dict[str, dict]) -> "UnifiedConfig":
        """Build from merged dicts using registered schemas.

        Resolves environment variables, lowercases keys,
        then validates each namespace through its Pydantic model.
        """
        validated = {}
        for entry in SchemaRegistry.all_entries():
            ns_data = merged.get(entry.namespace, {})
            ns_data = resolve_environment_variables(ns_data)
            ns_data = convert_keys_to_lowercase(ns_data)
            validated[entry.namespace] = entry.model(**ns_data)
        return cls(**validated)
```

The typed fields (`core: AppConfig`, `orchestrator: ContainerSettings`) provide IDE autocomplete and static analysis. The `from_registry()` factory is dynamic — adding a third package would only require adding a new field.

### CLI Override Mechanism

```python
# packages/settings/src/color_scheme_settings/overrides.py

def apply_overrides(config: UnifiedConfig, overrides: dict[str, object]) -> UnifiedConfig:
    """Apply CLI argument overrides to a validated config.

    Keys use dot notation with namespace prefix:
        "core.generation.saturation_adjustment" -> 1.5
        "core.output.directory" -> Path("/tmp/out")
        "core.output.formats" -> ["json", "css"]
        "orchestrator.container.engine" -> "podman"

    Returns a new UnifiedConfig instance (immutable pattern).
    Raises SettingsOverrideError if a key path doesn't exist in the schema.
    Re-validates through Pydantic to enforce constraints.
    """
    core_dict = config.core.model_dump()
    orchestrator_dict = config.orchestrator.model_dump()

    for dotted_key, value in overrides.items():
        parts = dotted_key.split(".")
        namespace = parts[0]
        path = parts[1:]

        target = core_dict if namespace == "core" else orchestrator_dict

        # Walk to the parent dict
        for segment in path[:-1]:
            if segment not in target:
                raise SettingsOverrideError(key=dotted_key)
            target = target[segment]

        if path[-1] not in target:
            raise SettingsOverrideError(key=dotted_key)
        target[path[-1]] = value

    return UnifiedConfig(
        core=AppConfig(**core_dict),
        orchestrator=ContainerSettings(**orchestrator_dict),
    )
```

### Public API

```python
# packages/settings/src/color_scheme_settings/__init__.py

_config: UnifiedConfig | None = None

def load_config() -> UnifiedConfig:
    """Load, merge, and validate all settings layers. Cached after first call."""
    global _config
    if _config is not None:
        return _config
    loader = SettingsLoader()
    layers = loader.discover_layers()
    merged = merge_layers(layers)
    _config = UnifiedConfig.from_registry(merged)
    return _config

def reload_config() -> UnifiedConfig:
    """Force reload from all layers. Useful for testing."""
    global _config
    _config = None
    return load_config()

def get_config(overrides: dict[str, object] | None = None) -> UnifiedConfig:
    """Load config with optional CLI overrides applied. Primary entry point."""
    config = load_config()
    if overrides:
        config = apply_overrides(config, overrides)
    return config
```

**Full pipeline:**
```
1. discover_layers()       → list[LayerSource]     (package, project, user files)
2. merge_layers(layers)    → dict per namespace     (deep merged dicts)
3. from_registry(merged)   → UnifiedConfig          (Pydantic validated)
4. apply_overrides(config) → UnifiedConfig          (CLI args on top)
```

### Error Hierarchy

```python
# packages/settings/src/color_scheme_settings/errors.py

class SettingsError(Exception):
    """Base for all settings errors."""

class SettingsFileError(SettingsError):
    """TOML file cannot be read or parsed.
    Raised for: malformed TOML syntax, file permissions issues.
    NOT raised for: missing files (silently skipped)."""
    file_path: Path
    reason: str

class SettingsValidationError(SettingsError):
    """Merged config fails Pydantic validation.
    Includes layer attribution — which file introduced the bad value."""
    namespace: str
    validation_error: ValidationError
    source_layer: str | None  # "package", "project", "user", "cli"

class SettingsOverrideError(SettingsError):
    """CLI override targets a nonexistent key path. Catches typos early."""
    key: str

class SettingsRegistryError(SettingsError):
    """Namespace conflict or missing registration."""
    namespace: str
```

**Key rule:** Missing files are not errors. Only package defaults are expected to exist. Project and user files are optional.

## CLI Usage After Migration

```python
# Core CLI command
from color_scheme_settings import get_config

def generate(image_path: Path, saturation: float | None = None, ...):
    overrides = {}
    if saturation is not None:
        overrides["core.generation.saturation_adjustment"] = saturation
    if output_dir is not None:
        overrides["core.output.directory"] = output_dir

    config = get_config(overrides)
    config.core.output.directory    # resolved value
    config.core.generation.default_backend

# Orchestrator CLI command
def generate(image_path: Path, engine: str | None = None, ...):
    overrides = {}
    if engine is not None:
        overrides["orchestrator.container.engine"] = engine

    config = get_config(overrides)
    config.orchestrator.container.engine
    config.core.output.directory    # orchestrator can read core settings
```

## Example Settings Files

**Package default — `packages/core/config/settings.toml` (flat):**
```toml
[logging]
level = "INFO"
show_time = true
show_path = false

[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]

[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

[backends.pywal]
backend_algorithm = "haishoku"

[backends.wallust]
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16
```

**Package default — `packages/orchestrator/config/settings.toml` (flat):**
```toml
[container]
engine = "docker"
```

**Project root — `settings.toml` (namespaced):**
```toml
[core.generation]
default_backend = "wallust"

[core.output]
formats = ["json", "css", "yaml"]

[orchestrator.container]
engine = "podman"
```

**User config — `~/.config/color-scheme/settings.toml` (namespaced):**
```toml
[core.generation]
saturation_adjustment = 1.3

[core.backends.custom]
n_clusters = 32
```

## Migration Path

**Removed:**
- `packages/core/src/color_scheme/config/settings.py` — `SettingsModel` class and dynaconf dependency
- `Settings` global singleton
- `OrchestratorConfig(AppConfig)` inheritance pattern
- `dynaconf` dependency (replaced by `tomllib` stdlib)
- `[container]` section from core's `settings.toml` (moves to orchestrator)

**Unchanged:**
- All Pydantic models in `config.py` (`AppConfig`, `LoggingSettings`, `OutputSettings`, etc.)
- `defaults.py` hardcoded fallbacks (stay as Pydantic field defaults)
- `enums.py`
- `ContainerSettings` model in orchestrator
- `settings.toml` content and format within each package

**Changed access patterns:**
```python
# Before
from color_scheme.config import Settings
settings = Settings.get()
settings.output.directory

# After
from color_scheme_settings import get_config
config = get_config(overrides)
config.core.output.directory
```

## Testing Strategy

**Unit tests (shared package):**
- `test_merger.py` — `deep_merge()` with nested dicts, list replacement, scalar override, empty dicts
- `test_registry.py` — Register, retrieve, duplicate rejection, ordering
- `test_overrides.py` — Dotted key resolution, nonexistent key error, re-validation, immutability
- `test_errors.py` — Error context and layer attribution

**Integration tests (shared package):**
- `test_loader.py` — File discovery across layers using `tmp_path`, missing files skipped, namespace wrapping
- `test_pipeline.py` — End-to-end: write TOML files to temp dirs, run `get_config()`, verify merge + override

**Edge cases:**
- Empty settings files at every layer
- User file with no relevant namespace keys
- Environment variable resolution (`$HOME`)
- Case-insensitive key handling
- Package registered but `settings.toml` missing (Pydantic defaults only)
- Only one package registered (core standalone without orchestrator)

**Fixtures:** `conftest.py` with helpers to write TOML to temp dirs and monkey-patch `find_project_root()` and user config path.
