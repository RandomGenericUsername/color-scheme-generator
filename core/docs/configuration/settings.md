# Settings Reference

Configuration via `settings.toml`.

---

## Configuration File Location

**Default:**

```
~/.config/colorscheme-generator/settings.toml
```

**Custom location:**

```bash
export COLORSCHEME_SETTINGS_FILE=/path/to/settings.toml
```

---

## Configuration Structure

```toml
[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

[backends.pywal]
backend_algorithm = "wal"

[backends.wallust]
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16

[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "yaml"]

[templates]
directory = ""
```

---

## Generation Settings

### `default_backend`

| Property | Value |
|----------|-------|
| Type | String |
| Default | `"pywal"` |
| Options | `"pywal"`, `"wallust"`, `"custom"`, `"auto"` |

CLI override: `--backend`

### `saturation_adjustment`

| Property | Value |
|----------|-------|
| Type | Float |
| Default | `1.0` |
| Range | `0.0` - `2.0` |

CLI override: `--saturation`

---

## Output Settings

### `directory`

| Property | Value |
|----------|-------|
| Type | Path |
| Default | `$HOME/.config/color-scheme/output` |

Supports environment variable expansion.

CLI override: `--output-dir`

### `formats`

| Property | Value |
|----------|-------|
| Type | Array of strings |
| Default | `["json", "sh", "css", "yaml"]` |
| Options | `json`, `sh`, `css`, `gtk.css`, `yaml`, `toml`, `sequences`, `rasi` |

CLI override: `--formats`

---

## Template Settings

```toml
[templates]
directory = ""  # Empty = use built-in templates
```

CLI override: `--template-dir`

---

## Environment Variables

Override settings with environment variables:

```bash
# Pattern: COLORSCHEME_SECTION__SETTING
export COLORSCHEME_GENERATION__DEFAULT_BACKEND=wallust
export COLORSCHEME_GENERATION__SATURATION_ADJUSTMENT=1.5
export COLORSCHEME_OUTPUT__DIRECTORY=/tmp/colors
```

---

## Configuration Precedence

```
CLI Arguments  →  Environment Variables  →  Config File  →  Defaults
   (highest)                                                (lowest)
```

---

## Complete Example

```toml
# ~/.config/colorscheme-generator/settings.toml

[generation]
default_backend = "wallust"
saturation_adjustment = 1.3

[backends.pywal]
backend_algorithm = "colorthief"

[backends.wallust]
backend_type = "full"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16

[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "yaml", "sequences"]

[templates]
directory = ""
```

