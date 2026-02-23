# Reference: Exceptions

All public exception types raised by the color-scheme packages.

---

## Exception hierarchy

```
Exception (Python built-in)
├── ColorSchemeError               (core base)
│   ├── InvalidImageError
│   ├── ColorExtractionError
│   ├── BackendNotAvailableError
│   ├── TemplateRenderError
│   └── OutputWriteError
├── SettingsError                  (settings base)
│   ├── SettingsFileError
│   ├── SettingsValidationError
│   ├── SettingsOverrideError
│   └── SettingsRegistryError
└── TemplateError                  (templates base)
    ├── TemplateNotFoundError
    └── TemplateRegistryError
```

---

## Core exceptions

**Module:** `color_scheme.core.exceptions`

### ColorSchemeError

Base exception for all core errors.

```python
from color_scheme.core.exceptions import ColorSchemeError

try:
    generator.generate(image_path, config)
except ColorSchemeError as e:
    print(f"Core error: {e}")
```

### InvalidImageError

Raised when an image file cannot be read or processed.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `image_path` | `str` | Path to the invalid image file |
| `reason` | `str` | Specific reason |

**Message format:** `Invalid image '<image_path>': <reason>`

**When raised:**
- File does not exist
- File is not readable (permission denied)
- Format not supported by Pillow
- File is corrupted or truncated

```python
from color_scheme.core.exceptions import InvalidImageError

try:
    generator.generate("missing.jpg", config)
except InvalidImageError as e:
    print(e.image_path)  # "missing.jpg"
    print(e.reason)      # "File not found"
```

### ColorExtractionError

Raised when a backend fails to extract colors.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `backend` | `str` | Backend name that failed |
| `reason` | `str` | Specific reason |

**Message format:** `Color extraction failed (<backend>): <reason>`

**When raised:**
- Backend process exits with non-zero code
- Backend timeout
- Backend returns invalid color data

### BackendNotAvailableError

Raised when the requested backend is not available on the system.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `backend` | `str` | Requested backend name |
| `reason` | `str` | Specific reason |

**Message format:** `Backend '<backend>' not available: <reason>`

**When raised:**
- Backend binary not in PATH
- Container image not found (orchestrator)

```python
from color_scheme.core.exceptions import BackendNotAvailableError

try:
    generator = factory.create(Backend.PYWAL)
except BackendNotAvailableError as e:
    print(e.backend)  # "pywal"
    print(e.reason)   # "Binary 'wal' not found in PATH"
```

### TemplateRenderError

Raised when a Jinja2 template fails to render.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `template_name` | `str` | Name of the template file |
| `reason` | `str` | Jinja2 error detail |

**Message format:** `Template rendering failed ('<template_name>'): <reason>`

**When raised:**
- Template file not found
- Template syntax error
- Undefined template variable

### OutputWriteError

Raised when an output file cannot be written to disk.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `file_path` | `str` | Full path to the file that could not be written |
| `reason` | `str` | Specific reason |

**Message format:** `Failed to write '<file_path>': <reason>`

**When raised:**
- Permission denied
- Disk full
- Output directory is a file, not a directory

---

## Settings exceptions

**Module:** `color_scheme_settings`

```python
from color_scheme_settings import (
    SettingsError,
    SettingsFileError,
    SettingsValidationError,
    SettingsOverrideError,
    SettingsRegistryError,
)
```

### SettingsError

Base exception for all settings errors.

```python
from color_scheme_settings import SettingsError

try:
    config = load_config()
except SettingsError as e:
    print(f"Settings error: {e}")
```

### SettingsFileError

Raised when a TOML configuration file cannot be read or parsed.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `file_path` | `Path` | Path to the problematic file |
| `reason` | `str` | Parse or I/O error detail |

**Message format:** `Failed to load <file_path>: <reason>`

**Note:** Missing files are silently ignored. This exception is raised only when a file
exists but is unreadable or contains invalid TOML.

### SettingsValidationError

Raised when merged configuration values fail Pydantic validation.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `namespace` | `str` | Namespace that failed (e.g., `"core"`) |
| `validation_error` | `Any` | Pydantic `ValidationError` details |
| `source_layer` | `str \| None` | Which layer caused the failure |

**Message format:** `Validation failed for '<namespace>' namespace [from <source_layer> layer]: <validation_error>`

**When raised:**
- Field type mismatch (e.g., string where float is expected)
- Value outside range (e.g., saturation > 2.0)
- Invalid enum value (e.g., backend = "invalid")

### SettingsOverrideError

Raised when a dotted-key path passed to `get_config()` or `apply_overrides()` does not
exist in the configuration schema.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `key` | `str` | The invalid key path |

**Message format:** `Override key path does not exist: <key>`

```python
from color_scheme_settings import get_config, SettingsOverrideError

try:
    config = get_config({"core.nonexistent.field": "value"})
except SettingsOverrideError as e:
    print(e.key)  # "core.nonexistent.field"
```

### SettingsRegistryError

Raised by `SchemaRegistry` on duplicate registration or access to an unknown namespace.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `namespace` | `str` | The namespace involved |
| `reason` | `str` | Detail (e.g., "Namespace already registered") |

**Message format:** `Registry error for namespace '<namespace>': <reason>`

**When raised:**
- `SchemaRegistry.register()` called twice with the same namespace
- `SchemaRegistry.get()` called for a namespace that was never registered

```python
from color_scheme_settings import SchemaRegistry, SettingsRegistryError

try:
    SchemaRegistry.register("core", AppConfig, defaults_file)
    SchemaRegistry.register("core", AppConfig, defaults_file)  # raises
except SettingsRegistryError as e:
    print(e.namespace)  # "core"
    print(e.reason)     # "Namespace already registered"
```

---

## Template exceptions

**Module:** `color_scheme_templates.errors`

```python
from color_scheme_templates.errors import (
    TemplateError,
    TemplateNotFoundError,
    TemplateRegistryError,
)
```

### TemplateError

Base exception for all template errors.

### TemplateNotFoundError

Raised when a requested template cannot be found in any registered directory.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `template_name` | `str` | Name of the template that could not be found |
| `searched_paths` | `list[Path]` | Directories that were searched |

**Message format:** `Template '<template_name>' not found. Searched: <paths>`

**When raised:**
- Template name does not exist in any registered template directory

### TemplateRegistryError

Raised when `TemplateRegistry.register()` is called with a namespace that is already
registered, or when `TemplateRegistry.get()` is called for an unregistered namespace.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `namespace` | `str` | The namespace involved |
| `reason` | `str` | Detail (e.g., `"namespace already registered"`) |

**Message format:** `Template registry error for '<namespace>': <reason>`

```python
from color_scheme_templates.errors import TemplateRegistryError

try:
    TemplateRegistry.register("core", templates_dir)
    TemplateRegistry.register("core", templates_dir)  # raises
except TemplateRegistryError as e:
    print(e.namespace)  # "core"
    print(e.reason)     # "namespace already registered"
```

---

## Verification reference

| BHV | Behavior |
|-----|---------|
| BHV-0010 | `BackendNotAvailableError` raised when backend binary is absent |
| BHV-0017 | `SettingsRegistryError` on duplicate namespace registration |
| BHV-0018 | `SettingsRegistryError` on `get()` for unknown namespace |
| BHV-0033 | `TemplateRegistryError` on duplicate template namespace registration |


---

## See also

- [Core Types](../reference/types.md) — types involved in error scenarios
- [Settings API](../reference/settings-api.md) — settings functions that raise these exceptions
