# Settings Layered Architecture Design

**Date:** 2026-01-29
**Status:** In Progress - Brainstorming

## Requirement

Expose the settings file at the root of the project for easy manipulation, with a layered configuration system where:
- Settings from files are used unless overridden by CLI arguments
- Example: If `output.directory = "/tmp/dir"` in settings.toml and no `--output-dir` arg is passed, use `/tmp/dir`. If the arg is passed, use the arg value.

## Agreed Architecture

**Layered Configuration Priority** (lowest to highest):

1. **Package defaults** (`packages/core/src/color_scheme/config/settings.toml`)
   - Lowest priority
   - Shipped with code
   - Built-in fallback values

2. **Project root** (`settings.toml` at repository root)
   - Development/deployment defaults
   - Version-controlled project configuration

3. **User config** (`~/.config/color-scheme/settings.toml`)
   - User-specific overrides
   - Survives package updates

4. **CLI arguments** (`--output-dir`, `--backend`, etc.)
   - Highest priority
   - Runtime overrides
   - Explicit user intent

**Pattern:** Built-in → Project → User → Runtime

## Current Implementation

### Settings Loading (packages/core/src/color_scheme/config/settings.py)
- Uses dynaconf + Pydantic validation
- Currently only loads from package directory: `packages/core/src/color_scheme/config/settings.toml`
- `Settings.get()` returns validated `AppConfig` instance
- Supports environment variable expansion (`$HOME`, etc.)

### CLI Argument Handling (packages/core/src/color_scheme/cli/main.py)
- CLI arguments are optional (all default to `None`)
- Settings loaded via `Settings.get()`
- Overrides applied via `GeneratorConfig.from_settings(settings, **overrides)` (lines 119-127)
- Current override pattern works well

### Current Settings Structure
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

## Questions to Resolve

### Question 1: Configuration Merging Strategy ⏸️ CURRENT

When loading settings from multiple layers, how should we merge nested settings like `[backends.pywal]` or `[output]`?

**Option A: Deep merge** - Each layer can override individual fields
```toml
# Package default: backends.pywal.backend_algorithm = "haishoku"
# User config: backends.pywal.some_other_field = "value"
# Result: Both fields present, merged together
```

**Option B: Section replacement** - If a section exists in a higher layer, it completely replaces the lower layer
```toml
# Package default: backends.pywal.backend_algorithm = "haishoku"
# User config has [backends.pywal] section with one field
# Result: Only user's pywal config used, package defaults ignored for that section
```

**Option C: Smart merge** - List fields append, scalar fields replace
```toml
# Package: formats = ["json", "css"]
# User: formats = ["yaml"]
# Result: ["json", "css", "yaml"] or just ["yaml"]?
```

**Recommendation:** Option A (Deep merge) for maximum flexibility

---

## Implementation Notes

### Files to Modify
- `packages/core/src/color_scheme/config/settings.py` - Add multi-file loading
- Root `settings.toml` - Create with project defaults
- `~/.config/color-scheme/settings.toml` - Document for users (create on first run?)

### Current Working Pattern
The CLI already does the right thing with overrides:
```python
# Build GeneratorConfig with overrides (line 119-127)
overrides: dict[str, object] = {}
if output_dir is not None:
    overrides["output_dir"] = output_dir
if saturation is not None:
    overrides["saturation_adjustment"] = saturation
if formats is not None:
    overrides["formats"] = formats

config = GeneratorConfig.from_settings(settings, **overrides)
```

This pattern should be preserved - CLI args always win.

## Next Steps

1. Answer Question 1 (merging strategy)
2. Design the settings file discovery mechanism
3. Design the dynaconf multi-file loading approach
4. Handle orchestrator-specific settings (`ContainerSettings`)
5. Define migration path for existing users
6. Write implementation plan
