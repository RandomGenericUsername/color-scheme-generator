# How-to: Configure Settings

This guide covers how to adjust color-scheme settings through configuration files,
environment variables, and programmatic CLI overrides.

## Prerequisites

- `color-scheme-core` (and optionally `color-scheme`) installed.

---

## Configuration file locations

Settings are resolved from four layers in priority order (lowest to highest):

| Priority | Layer | Source |
|----------|-------|--------|
| 1 (lowest) | Package defaults | Built-in defaults bundled with each package |
| 2 | Project config | `./settings.toml` in the current directory |
| 3 | User config | `~/.config/color-scheme/settings.toml` |
| 4 (highest) | CLI overrides | Passed via `get_config(overrides)` at runtime |

A higher-priority layer overrides individual keys from lower layers. Missing files are
silently ignored.

### User config example

Create or edit `~/.config/color-scheme/settings.toml`:

```toml
[core.generation]
saturation_adjustment = 1.2
default_backend = "wallust"

[core.output]
directory = "/home/user/colors"
formats = ["json", "sh", "css"]

[core.logging]
level = "WARNING"
```

The key format for project and user config files is `[<namespace>.<section>]`.

---

## Environment variables

### COLORSCHEME_* — map to nested config keys

Environment variables with the `COLORSCHEME_` prefix are collected and applied on top
of the user config layer (ENV has higher priority than user config).

Format: `COLORSCHEME_<SECTION>__<KEY>` (double underscore as nesting separator,
uppercase).

```bash
# Set default backend via env var
export COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom

# Set output directory via env var
export COLORSCHEME_OUTPUT__DIRECTORY=/tmp/colors

# Set saturation via env var
export COLORSCHEME_GENERATION__SATURATION_ADJUSTMENT=1.5
```

The double underscore (`__`) separates the section name from the field name.

### COLOR_SCHEME_TEMPLATES — override template directory

The `COLOR_SCHEME_TEMPLATES` environment variable is a special case (different prefix)
that sets the template directory used for Jinja2 rendering:

```bash
export COLOR_SCHEME_TEMPLATES=/path/to/custom/templates
```

This is distinct from the `COLORSCHEME_` prefix pattern. It maps directly to
`templates.directory` in the configuration.

---

## Applying CLI overrides programmatically

The `get_config` function loads the full configuration with optional runtime overrides
applied on top of all other layers:

```python
from color_scheme_settings import get_config

config = get_config({
    "core.generation.saturation_adjustment": 0.5,
    "core.output.directory": "/custom/output",
    "core.output.formats": ["json", "sh"],
})

print(config.core.generation.saturation_adjustment)  # 0.5
```

Correct signature:

```python
get_config(overrides: dict[str, Any] | None = None) -> BaseModel
```

Pass a dict of dotted-key paths to values. The overrides take precedence over all
layers including user config and environment variables.

---

## List values: replacement semantics

When a list key is overridden (in any layer), the entire list is replaced — elements
are not merged:

```toml
# Package default
formats = ["json", "css", "yaml", "sh", "scss", "rasi", "sequences", "gtk.css"]

# User config (replaces the list entirely)
[core.output]
formats = ["json", "sh"]
```

Result: `formats == ["json", "sh"]`. The other 6 formats are removed.

This applies to all list-valued configuration keys, not only `formats`.

---

## Caching behavior

`load_config()` caches its result after the first call. Subsequent calls return the
same object:

```python
from color_scheme_settings import load_config

config1 = load_config()
config2 = load_config()
assert config1 is config2  # True — same cached instance
```

To force a fresh load (e.g., after changing config files in tests):

```python
from color_scheme_settings import reload_config
fresh = reload_config()
```

---

## Verification

| Behavior | Expected |
|----------|----------|
| Layers applied in order package < project < user < CLI | BHV-0019 |
| List values in override layer replace the entire list | BHV-0020 |
| `get_config(overrides)` takes precedence over all layers | BHV-0021 |
| `load_config()` returns the same object on second call | BHV-0022 |
| `COLORSCHEME_SECTION__KEY` maps to `section.key` in config | BHV-0031 |
| `COLOR_SCHEME_TEMPLATES` maps to `templates.directory` | BHV-0032 |
