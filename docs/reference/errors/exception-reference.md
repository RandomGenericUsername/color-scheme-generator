# Exception Reference

**Scope:** Complete exception hierarchy for color-scheme
**Extracted:** February 2, 2026
**Total Exceptions:** 11 (6 core + 5 settings)

Complete reference for all exceptions that can be raised by color-scheme components, their meanings, properties, and how to handle them.

---

## Exception Hierarchy Overview

```
Exception (Python built-in)
│
├── ColorSchemeError (color-scheme core base)
│   ├── InvalidImageError
│   ├── ColorExtractionError
│   ├── BackendNotAvailableError
│   ├── TemplateRenderError
│   └── OutputWriteError
│
└── SettingsError (color-scheme-settings base)
    ├── SettingsFileError
    ├── SettingsValidationError
    ├── SettingsOverrideError
    └── SettingsRegistryError
```

---

## Core Package Exceptions

All core exceptions inherit from `ColorSchemeError`, which inherits from Python's built-in `Exception`.

### ColorSchemeError (Base)

**Type:** `color_scheme.core.exceptions.ColorSchemeError`
**Inherits:** `Exception`
**Purpose:** Base exception for all color-scheme core errors

**Properties:** None (base class only)

**Usage:**
```python
try:
    # color-scheme core operations
    pass
except ColorSchemeError as e:
    print(f"Color scheme error: {e}")
```

**When Raised:**
- Indirectly - raised by subclasses when any core operation fails

---

### InvalidImageError

**Type:** `color_scheme.core.exceptions.InvalidImageError`
**Inherits:** `ColorSchemeError`
**Purpose:** Image file cannot be read or processed

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `image_path` | `str` | Path to the invalid image file |
| `reason` | `str` | Specific reason why image is invalid |
| `message` | `str` | Full error message (via `str(exception)`) |

**Message Format:**
```
Invalid image '<image_path>': <reason>
```

**When Raised:**
- File does not exist
- File is not readable (permission denied)
- File format not supported by Pillow (not PNG, JPG, GIF, etc.)
- File is corrupted or truncated
- Image dimensions are invalid (0 width/height)

**Common Reasons:**
- `"File not found"`
- `"Permission denied"`
- `"Unsupported image format"`
- `"Cannot identify image file"`
- `"Image file is truncated"`

**Example Handling:**
```python
from color_scheme.core.exceptions import InvalidImageError

try:
    generator = ColorSchemeGenerator(image_path="missing.jpg")
except InvalidImageError as e:
    print(f"Image problem: {e.reason}")
    print(f"File was: {e.image_path}")
    # Suggest: check file exists, verify format
```

**Example Output:**
```
Invalid image '/home/user/image.jpg': Cannot identify image file
```

---

### ColorExtractionError

**Type:** `color_scheme.core.exceptions.ColorExtractionError`
**Inherits:** `ColorSchemeError`
**Purpose:** Backend fails to extract colors from image

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `backend` | `str` | Name of the backend that failed (e.g., "pywal") |
| `reason` | `str` | Specific reason why extraction failed |
| `message` | `str` | Full error message |

**Message Format:**
```
Color extraction failed (<backend>): <reason>
```

**When Raised:**
- Backend process crashes or exits with error
- Backend timeout (external binary takes too long)
- Backend returns invalid color data
- Out of memory during processing
- Dependency missing at runtime

**Common Reasons:**
- `"Backend process exited with code 1"`
- `"Backend timeout"`
- `"Invalid color data returned"`
- `"Insufficient memory"`
- `"Dependency not found"`

**Example Handling:**
```python
from color_scheme.core.exceptions import ColorExtractionError

try:
    colors = generator.generate(image_path="image.jpg")
except ColorExtractionError as e:
    print(f"Backend {e.backend} failed: {e.reason}")
    # Suggest: try different backend, check dependencies
```

**Example Output:**
```
Color extraction failed (pywal): Backend timeout
```

---

### BackendNotAvailableError

**Type:** `color_scheme.core.exceptions.BackendNotAvailableError`
**Inherits:** `ColorSchemeError`
**Purpose:** Requested backend is not available on this system

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `backend` | `str` | Name of backend that is unavailable (e.g., "wallust") |
| `reason` | `str` | Specific reason why backend is unavailable |
| `message` | `str` | Full error message |

**Message Format:**
```
Backend '<backend>' not available: <reason>
```

**When Raised:**
- Backend binary not in PATH (not installed)
- Backend binary exists but not executable
- Backend configuration missing
- Container image not found (orchestrator)
- Required backend dependencies not installed

**Common Reasons:**
- `"Binary 'wal' not found in PATH"`
- `"Binary 'wallust' is not executable"`
- `"Container image 'color-scheme-pywal:latest' not found"`

**Example Handling:**
```python
from color_scheme.core.exceptions import BackendNotAvailableError

try:
    generator = factory.create("pywal")
except BackendNotAvailableError as e:
    print(f"Cannot use backend {e.backend}: {e.reason}")
    print("Solutions:")
    print("  - Install the backend package")
    print("  - Use auto-detection to find available backend")
    print("  - Use 'custom' backend (always available)")
```

**Example Output:**
```
Backend 'pywal' not available: Binary 'wal' not found in PATH
```

---

### TemplateRenderError

**Type:** `color_scheme.core.exceptions.TemplateRenderError`
**Inherits:** `ColorSchemeError`
**Purpose:** Jinja2 template rendering fails

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `template_name` | `str` | Name of the template file (e.g., "colors.json.j2") |
| `reason` | `str` | Specific rendering error from Jinja2 |
| `message` | `str` | Full error message |

**Message Format:**
```
Template rendering failed ('<template_name>'): <reason>
```

**When Raised:**
- Template file not found
- Template syntax error (Jinja2 syntax)
- Template variable not provided
- Filter or macro error in template
- Template encoding error

**Common Reasons:**
- `"Template not found"`
- `"Unexpected end of template"`
- `"Undefined variable 'colors'"`
- `"Unknown filter 'invalid_filter'"`
- `"Syntax error in template"`

**Example Handling:**
```python
from color_scheme.core.exceptions import TemplateRenderError

try:
    output_manager.render_and_write(colors)
except TemplateRenderError as e:
    print(f"Template error in {e.template_name}: {e.reason}")
    # Suggest: check template syntax, verify color object
```

**Example Output:**
```
Template rendering failed ('colors.json.j2'): Undefined variable 'colors'
```

---

### OutputWriteError

**Type:** `color_scheme.core.exceptions.OutputWriteError`
**Inherits:** `ColorSchemeError`
**Purpose:** Cannot write output file to disk

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `file_path` | `str` | Full path to the file that couldn't be written |
| `reason` | `str` | Specific reason why write failed |
| `message` | `str` | Full error message |

**Message Format:**
```
Failed to write '<file_path>': <reason>
```

**When Raised:**
- Output directory doesn't exist and cannot be created
- Permission denied (insufficient write permissions)
- Disk full (no space for file)
- File path is invalid
- File is locked by another process
- Output directory is actually a file

**Common Reasons:**
- `"Permission denied"`
- `"No space left on device"`
- `"File already exists and is not writable"`
- `"Is a directory"`
- `"File or directory does not exist"`

**Example Handling:**
```python
from color_scheme.core.exceptions import OutputWriteError

try:
    output_manager.write_all(colors)
except OutputWriteError as e:
    print(f"Cannot write to {e.file_path}: {e.reason}")
    print("Solutions:")
    print("  - Check directory permissions: chmod 755 <dir>")
    print("  - Verify disk space: df -h")
    print("  - Use different output directory: -o /tmp/colors")
```

**Example Output:**
```
Failed to write '/home/user/.config/color-scheme/output/colors.json': Permission denied
```

---

## Settings Package Exceptions

All settings exceptions inherit from `SettingsError`, which inherits from Python's built-in `Exception`.

These are used by the `color_scheme_settings` package for configuration management.

### SettingsError (Base)

**Type:** `color_scheme_settings.SettingsError`
**Inherits:** `Exception`
**Purpose:** Base exception for all settings errors

**Properties:** None (base class only)

**Usage:**
```python
from color_scheme_settings import SettingsError

try:
    config = load_config()
except SettingsError as e:
    print(f"Configuration error: {e}")
```

**When Raised:**
- Indirectly - raised by subclasses when any settings operation fails

---

### SettingsFileError

**Type:** `color_scheme_settings.SettingsFileError`
**Inherits:** `SettingsError`
**Purpose:** TOML configuration file cannot be parsed

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `file_path` | `Path` | Path to the problematic TOML file |
| `reason` | `str` | Specific parsing or I/O error |
| `message` | `str` | Full error message |

**Message Format:**
```
Failed to load <file_path>: <reason>
```

**When Raised:**
- TOML syntax error (invalid TOML format)
- File permission denied (cannot read)
- File encoding error (not valid UTF-8)
- File I/O error (disk read failure)

**Common Reasons:**
- `"Invalid TOML syntax"`
- `"Permission denied"`
- `"Invalid UTF-8 encoding"`
- `"No such file or directory"` (in case of forced load)

**Important Note:**
Missing files are **silently ignored** (no exception). Exception only raised if file exists but cannot be read/parsed.

**Example Handling:**
```python
from color_scheme_settings import SettingsFileError

try:
    config = load_config()
except SettingsFileError as e:
    print(f"Cannot read configuration: {e.reason}")
    print(f"File: {e.file_path}")
    # Suggest: check file syntax, permissions
```

**Example Output:**
```
Failed to load /home/user/.config/color-scheme/settings.toml: Invalid TOML syntax
```

**Verification:**
```bash
# Check TOML syntax
python -c "import tomllib; tomllib.loads(open('settings.toml').read())"
```

---

### SettingsValidationError

**Type:** `color_scheme_settings.SettingsValidationError`
**Inherits:** `SettingsError`
**Purpose:** Configuration values fail Pydantic validation

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `namespace` | `str` | Namespace that failed validation (e.g., "core") |
| `validation_error` | `Any` | Pydantic ValidationError details |
| `source_layer` | `str \| None` | Which config layer caused the error ("defaults", "user", "project") |
| `message` | `str` | Full error message |

**Message Format:**
```
Validation failed for '<namespace>' namespace [from <source_layer> layer]: <validation_error>
```

**When Raised:**
- Field has invalid value (type mismatch)
- Value outside range (e.g., saturation > 2.0)
- Enum value not valid (e.g., backend = "invalid")
- Required field missing
- Invalid format (e.g., bad path)

**Common Reasons:**
- `"Field required"` - Missing required config key
- `"Value error, ... must be ... " `- Type or value constraint violation
- `"Value error, Invalid backend '...'"`  - Invalid enum value
- `"Input should be less than or equal to 2"` - Range violation

**Example Handling:**
```python
from color_scheme_settings import SettingsValidationError

try:
    config = load_config()
except SettingsValidationError as e:
    print(f"Configuration validation failed in {e.namespace}")
    if e.source_layer:
        print(f"Problem in {e.source_layer} configuration layer")
    print(f"Details: {e.validation_error}")
```

**Example Output:**
```
Validation failed for 'core' namespace (from user layer): Input should be less than or equal to 2
```

**Common Issues and Solutions:**

| Problem | Cause | Solution |
|---------|-------|----------|
| `Field required` | Missing key in settings | Add key to config file with valid value |
| `Invalid backend` | Invalid backend name | Use: pywal, wallust, or custom |
| `must be ... ` | Value outside range | Check range constraints (e.g., 0.0-2.0 for saturation) |
| `Value error` | Wrong type | Change value type (e.g., `1.5` instead of `"1.5"`) |

---

### SettingsOverrideError

**Type:** `color_scheme_settings.SettingsOverrideError`
**Inherits:** `SettingsError`
**Purpose:** CLI override targets a nonexistent configuration key

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `key` | `str` | The override key path that doesn't exist |
| `message` | `str` | Full error message |

**Message Format:**
```
Override key path does not exist: <key>
```

**When Raised:**
- CLI override with `--override` or `-O` flag uses invalid key path
- Key path doesn't exist in configuration schema
- Typo in override key name

**Example Override Syntax:**
```bash
# Valid override (key exists)
color-scheme-core generate image.jpg --override core.generation.saturation_adjustment=1.5

# Invalid override (key doesn't exist)
color-scheme-core generate image.jpg --override core.invalid_key=value
# → SettingsOverrideError: Override key path does not exist: core.invalid_key
```

**Example Handling:**
```python
from color_scheme_settings import SettingsOverrideError

try:
    config = get_config(overrides={"core.invalid.key": "value"})
except SettingsOverrideError as e:
    print(f"Invalid override key: {e.key}")
    print("Valid keys: core.generation.saturation_adjustment, core.output.directory, ...")
```

**Example Output:**
```
Override key path does not exist: core.invalid_key
```

**Valid Override Keys:**
```
core.logging.level
core.logging.show_time
core.logging.show_path
core.output.directory
core.output.formats
core.generation.default_backend
core.generation.saturation_adjustment
core.backends.pywal.backend_algorithm
core.backends.wallust.backend_type
core.backends.custom.algorithm
core.backends.custom.n_clusters
core.templates.directory
```

---

### SettingsRegistryError

**Type:** `color_scheme_settings.SettingsRegistryError`
**Inherits:** `SettingsError`
**Purpose:** Namespace conflict or missing schema registration

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `namespace` | `str` | Namespace that caused the registry error |
| `reason` | `str` | Specific reason for the registry error (optional) |
| `message` | `str` | Full error message |

**Message Format:**
```
Registry error for namespace '<namespace>'[: <reason>]
```

**When Raised:**
- Attempting to register namespace that already exists
- Attempting to access schema for unregistered namespace
- Duplicate namespace in registry
- Invalid namespace name format

**Common Reasons:**
- `"Namespace already registered"` - Cannot register duplicate
- `"Namespace not found"` - Trying to access unregistered namespace
- `"Invalid namespace format"` - Namespace name doesn't match pattern

**Example Handling:**
```python
from color_scheme_settings import SchemaRegistry, SettingsRegistryError

try:
    SchemaRegistry.register("core", CoreConfig, defaults_file)
except SettingsRegistryError as e:
    print(f"Registry error: {e.reason}")
```

**Example Output:**
```
Registry error for namespace 'core': Namespace already registered
```

---

## Exception Catching Patterns

### Catch All Color Scheme Errors

```python
from color_scheme.core.exceptions import ColorSchemeError

try:
    colors = generator.generate(image_path)
except ColorSchemeError as e:
    print(f"Color scheme operation failed: {e}")
    exit(1)
```

### Catch All Settings Errors

```python
from color_scheme_settings import SettingsError

try:
    config = load_config()
except SettingsError as e:
    print(f"Configuration error: {e}")
    exit(1)
```

### Catch All Color Scheme Errors

```python
from color_scheme.core.exceptions import ColorSchemeError

try:
    colors = generator.generate(image_path)
except ColorSchemeError as e:
    print(f"Color scheme operation failed: {e}")
    exit(1)
```

### Catch Specific Errors with Fallback

```python
from color_scheme.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
)

try:
    colors = generator.generate(image_path)
except InvalidImageError as e:
    print(f"Image problem: {e.reason}")
    print(f"File: {e.image_path}")
except BackendNotAvailableError as e:
    print(f"Backend {e.backend} not available")
    print("Try: color-scheme install")
except ColorExtractionError as e:
    print(f"Color extraction failed: {e.reason}")
    print("Try: different backend or image")
```

### Catch with Details

```python
from color_scheme.core.exceptions import ColorSchemeError

try:
    colors = generator.generate(image_path)
except ColorSchemeError as e:
    print(f"Error: {e}")

    # Handle specific error types
    if hasattr(e, 'backend'):
        print(f"Backend: {e.backend}")
    if hasattr(e, 'reason'):
        print(f"Reason: {e.reason}")
    if hasattr(e, 'file_path'):
        print(f"File: {e.file_path}")
```

---

## Exception Message Examples

### Core Exceptions

```python
# InvalidImageError
InvalidImageError("image.jpg", "Unsupported image format")
→ "Invalid image 'image.jpg': Unsupported image format"

# ColorExtractionError
ColorExtractionError("pywal", "Backend timeout")
→ "Color extraction failed (pywal): Backend timeout"

# BackendNotAvailableError
BackendNotAvailableError("wallust", "Binary 'wallust' not found in PATH")
→ "Backend 'wallust' not available: Binary 'wallust' not found in PATH"

# TemplateRenderError
TemplateRenderError("colors.json.j2", "Undefined variable 'colors'")
→ "Template rendering failed ('colors.json.j2'): Undefined variable 'colors'"

# OutputWriteError
OutputWriteError("/output/colors.json", "Permission denied")
→ "Failed to write '/output/colors.json': Permission denied"
```

### Settings Exceptions

```python
# SettingsFileError
SettingsFileError(Path("/home/user/.config/color-scheme/settings.toml"), "Invalid TOML syntax")
→ "Failed to load /home/user/.config/color-scheme/settings.toml: Invalid TOML syntax"

# SettingsValidationError (with source layer)
SettingsValidationError("core", "<Pydantic error>", "user")
→ "Validation failed for 'core' namespace (from user layer): <Pydantic error>"

# SettingsOverrideError
SettingsOverrideError("core.invalid.key")
→ "Override key path does not exist: core.invalid.key"

# SettingsRegistryError
SettingsRegistryError("core", "Namespace already registered")
→ "Registry error for namespace 'core': Namespace already registered"
```

---

## Count Summary

| Category | Count |
|----------|-------|
| Core exceptions | 6 |
| Settings exceptions | 5 |
| **Total** | **11** |

All 11 exceptions are documented above.

---

## Related Documentation

- [Error Troubleshooting Guide](../../how-to/troubleshoot-errors.md) - Common error solutions
- [CLI Commands](../cli/core-commands.md) - How commands handle errors
- [Settings Schema](../configuration/settings-schema.md) - Configuration validation
- [API Reference](../api/types.md) - Core classes that raise exceptions
