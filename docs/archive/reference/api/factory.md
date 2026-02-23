# Factory Pattern API

**Scope:** Backend factory for creating and detecting backends
**Extracted:** February 3, 2026
**Source:** `packages/core/src/color_scheme/factory.py`

Complete reference for the `BackendFactory` class: instantiation, detection, and auto-selection of color scheme backends.

---

## Overview

The `BackendFactory` class provides a centralized way to:
- Create generators for specific backends
- Detect which backends are available
- Auto-detect the best available backend (with preference order)

---

## BackendFactory

**Class:** `color_scheme.factory.BackendFactory`
**Module:** `packages/core/src/color_scheme/factory.py`
**Purpose:** Factory for creating and detecting backend generators

### Initialization

```python
from color_scheme.factory import BackendFactory
from color_scheme.config.config import AppConfig

settings = AppConfig()
factory = BackendFactory(settings)
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `settings` | `AppConfig` | Application configuration used for all generators |

---

## Methods

### `create(backend: Backend) -> ColorSchemeGenerator`

Creates a generator for the specified backend and verifies it's available.

**Parameters:**
- `backend` (`Backend`): Backend enum value (CUSTOM, PYWAL, or WALLUST)

**Returns:** `ColorSchemeGenerator` instance ready to use

**Raises:**
- `BackendNotAvailableError` - Backend is not available on the system

**Behavior:**
1. Instantiates the backend generator
2. Calls `ensure_available()` to verify it's installed
3. Raises error if not available
4. Returns the generator

**Example:**
```python
from color_scheme.factory import BackendFactory
from color_scheme.config.enums import Backend
from color_scheme.config.config import AppConfig

factory = BackendFactory(AppConfig())

try:
    # Create custom backend (always succeeds)
    custom = factory.create(Backend.CUSTOM)

    # Create pywal backend (may fail if not installed)
    pywal = factory.create(Backend.PYWAL)

except BackendNotAvailableError as e:
    print(f"{e.backend} not available: {e.reason}")
```

**Logging:**
- DEBUG: "Creating generator for backend: {backend}"
- INFO: "Created {backend} generator"

---

### `detect_available() -> list[Backend]`

Detects all available backends on the system.

**Parameters:** None

**Returns:** List of available `Backend` enum values

**Behavior:**
1. Iterates through all Backend enum values
2. Tries to instantiate each backend generator
3. Checks `is_available()` on each generator
4. Returns list of available backends

**Guaranteed:** Always includes at least `Backend.CUSTOM` (built-in)

**Example:**
```python
factory = BackendFactory(settings)

# Check what backends are available
available = factory.detect_available()
print(f"Available backends: {[b.value for b in available]}")

# Iterate through available backends
for backend in available:
    generator = factory.create(backend)
    scheme = generator.generate(image_path, config)
    # Use scheme...
```

**Output Examples:**
```python
# All backends available
[<Backend.CUSTOM: 'custom'>, <Backend.PYWAL: 'pywal'>, <Backend.WALLUST: 'wallust'>]

# Only custom and pywal
[<Backend.CUSTOM: 'custom'>, <Backend.PYWAL: 'pywal'>]

# Only custom (minimum)
[<Backend.CUSTOM: 'custom'>]
```

**Logging:**
- DEBUG: "Backend {backend} is available"
- DEBUG: "Backend {backend} is not available"
- DEBUG: "Failed to check backend {backend}: {error}"
- INFO: "Available backends: {list of values}"

---

### `auto_detect() -> Backend`

Auto-detects the best available backend based on preference order.

**Parameters:** None

**Returns:** `Backend` enum value (preference order: wallust > pywal > custom)

**Preference Order:**
1. **WALLUST** - Rust-based, fastest
2. **PYWAL** - Python-based, well-maintained
3. **CUSTOM** - Built-in fallback (always succeeds)

**Behavior:**
1. Checks backends in preference order
2. Returns the first available backend
3. Always returns at least CUSTOM (guaranteed not to fail)

**Example:**
```python
factory = BackendFactory(settings)

# Auto-detect best backend
best_backend = factory.auto_detect()
generator = factory.create(best_backend)

print(f"Using backend: {best_backend.value}")

# Generate colors
scheme = generator.generate(image_path, config)
```

**Scenarios:**
```python
# Wallust installed
auto_detect() → Backend.WALLUST

# Wallust not installed, Pywal installed
auto_detect() → Backend.PYWAL

# Both external tools not installed
auto_detect() → Backend.CUSTOM

# All available
auto_detect() → Backend.WALLUST  # Highest preference
```

**Logging:**
- DEBUG: "Auto-detecting best available backend"
- DEBUG: "Failed to check backend {backend}: {error}"
- INFO: "Auto-detected backend: {backend}"
- INFO: "Falling back to custom backend"

---

### `_instantiate_generator(backend: Backend) -> ColorSchemeGenerator` (Private)

Internal method to instantiate a generator without availability checks.

**Parameters:**
- `backend` (`Backend`): Backend to instantiate

**Returns:** Unverified `ColorSchemeGenerator` instance

**Raises:**
- `ValueError` - Unknown backend enum value

**Note:** This is a private method (prefix `_`). Use public methods instead.

---

## Usage Patterns

### Basic Usage

```python
from color_scheme.factory import BackendFactory
from color_scheme.config.enums import Backend
from color_scheme.config.config import AppConfig
from color_scheme.core.types import GeneratorConfig
from pathlib import Path

# Setup
settings = AppConfig()
factory = BackendFactory(settings)
image_path = Path("/path/to/image.jpg")
config = GeneratorConfig()

# Create specific backend
try:
    backend = factory.create(Backend.PYWAL)
    scheme = backend.generate(image_path, config)
except BackendNotAvailableError:
    print("Pywal not installed, trying custom...")
    backend = factory.create(Backend.CUSTOM)
    scheme = backend.generate(image_path, config)
```

### Auto-Detection

```python
factory = BackendFactory(settings)

# Get best available backend
best_backend = factory.auto_detect()
generator = factory.create(best_backend)

scheme = generator.generate(image_path, config)
print(f"Generated colors using: {best_backend.value}")
```

### Trying Multiple Backends

```python
factory = BackendFactory(settings)
available = factory.detect_available()

for backend_enum in available:
    try:
        generator = factory.create(backend_enum)
        scheme = generator.generate(image_path, config)
        print(f"Success with {backend_enum.value}")
        break
    except Exception as e:
        print(f"Failed with {backend_enum.value}: {e}")
        continue
```

### With CLI Arguments

```python
from color_scheme.factory import BackendFactory
from color_scheme.config.enums import Backend

def generate_colors(image_path: str, backend_name: str = None):
    factory = BackendFactory(settings)

    if backend_name:
        # User specified backend
        backend = Backend(backend_name)
        generator = factory.create(backend)
    else:
        # Auto-detect
        backend = factory.auto_detect()
        generator = factory.create(backend)

    return generator.generate(Path(image_path), GeneratorConfig())
```

---

## Backend Enum

**Class:** `color_scheme.config.enums.Backend`

### Values

| Value | Enum Member | Description |
|-------|-------------|-------------|
| `"custom"` | `Backend.CUSTOM` | Built-in K-means backend |
| `"pywal"` | `Backend.PYWAL` | Python-based external tool |
| `"wallust"` | `Backend.WALLUST` | Rust-based external tool |

### Usage

```python
from color_scheme.config.enums import Backend

# By value (string)
backend = Backend("custom")

# By enum member
backend = Backend.CUSTOM

# Get all backends
for b in Backend:
    print(b.value)  # "custom", "pywal", "wallust"
```

---

## Error Handling

### BackendNotAvailableError

Raised when a requested backend is not available.

```python
from color_scheme.core.exceptions import BackendNotAvailableError
from color_scheme.factory import BackendFactory
from color_scheme.config.enums import Backend

factory = BackendFactory(settings)

try:
    generator = factory.create(Backend.PYWAL)
except BackendNotAvailableError as e:
    print(f"Backend: {e.backend}")
    print(f"Reason: {e.reason}")
    # Fall back to custom
    generator = factory.create(Backend.CUSTOM)
```

### ValueError

Raised if an invalid backend is passed (shouldn't happen with enum).

```python
try:
    generator = factory._instantiate_generator(Backend.CUSTOM)
except ValueError as e:
    print(f"Invalid backend: {e}")
```

---

## Testing

See `packages/core/tests/unit/test_factory.py` for usage examples:

```python
from color_scheme.factory import BackendFactory
from color_scheme.config.enums import Backend

factory = BackendFactory(app_config)

# Test auto-detect
backend = factory.auto_detect()
assert backend in [Backend.CUSTOM, Backend.PYWAL, Backend.WALLUST]

# Test detect_available
available = factory.detect_available()
assert Backend.CUSTOM in available

# Test create
generator = factory.create(Backend.CUSTOM)
assert generator.backend_name == "custom"
```

---

## Complete Example

```python
from color_scheme.factory import BackendFactory
from color_scheme.config.config import AppConfig
from color_scheme.core.types import GeneratorConfig
from color_scheme.core.exceptions import BackendNotAvailableError
from pathlib import Path

# Initialize
settings = AppConfig()
factory = BackendFactory(settings)

# Show available backends
print("Available backends:")
for backend in factory.detect_available():
    print(f"  - {backend.value}")

# Auto-detect and generate
best_backend = factory.auto_detect()
generator = factory.create(best_backend)

print(f"\nUsing backend: {best_backend.value}")

# Generate colors
image_path = Path("/path/to/image.jpg")
config = GeneratorConfig()

try:
    scheme = generator.generate(image_path, config)
    print(f"Generated {len(scheme.colors)} colors")
    print(f"Background: {scheme.background.hex}")
    print(f"Foreground: {scheme.foreground.hex}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Related Documentation

- [Backend API](backends.md) - Backend implementations
- [Core Types](types.md) - ColorScheme and related types
- [Configuration](../configuration/settings-schema.md) - Backend settings
- [CLI Commands](../cli/core-commands.md) - Using factory in CLI
