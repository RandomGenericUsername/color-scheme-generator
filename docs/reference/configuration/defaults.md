# Default Values Reference

**Scope:** All default values used by color-scheme
**Extracted:** February 2, 2026
**Source:** `packages/core/src/color_scheme/config/defaults.py` and package configuration

Complete listing of all default values used when no configuration files or CLI options override them.

---

## Core Package Defaults

### Logging Defaults

| Setting | Value | Type | Note |
|---------|-------|------|------|
| `logging.level` | `INFO` | String | Log messages at INFO level and above |
| `logging.show_time` | `true` | Boolean | Show timestamps in logs |
| `logging.show_path` | `false` | Boolean | Don't show file paths in logs |

```python
default_log_level = "INFO"
default_show_time = True
default_show_path = False
```

### Output Defaults

| Setting | Value | Type | Note |
|---------|-------|------|------|
| `output.directory` | `$HOME/.config/color-scheme/output` | Path | Expands to user home directory |
| `output.formats` | All 8 formats (see below) | Array | JSON, shell, CSS, GTK, YAML, sequences, Rasi, SCSS |

**Default output directory expands to:**
- On Linux: `/home/username/.config/color-scheme/output`
- On macOS: `/Users/username/.config/color-scheme/output`
- On Windows: `C:\Users\username\.config\color-scheme\output`

**Default output formats (all 8):**
```python
default_formats = [
    "json",
    "sh",
    "css",
    "gtk.css",
    "yaml",
    "sequences",
    "rasi",
    "scss",
]
```

### Generation Defaults

| Setting | Value | Type | Range | Note |
|---------|-------|------|-------|------|
| `generation.default_backend` | `pywal` | String | `pywal`, `wallust`, `custom` | Primary color extraction backend |
| `generation.saturation_adjustment` | `1.0` | Float | 0.0 to 2.0 | No adjustment (neutral saturation) |

```python
default_backend = "pywal"
saturation_adjustment = 1.0
```

### Backend-Specific Defaults

#### Pywal Backend

| Setting | Value | Type | Note |
|---------|-------|------|------|
| `backends.pywal.backend_algorithm` | `haishoku` | String | Algorithm for color extraction |

```python
pywal_backend_algorithm = "haishoku"
```

**Why Haishoku?** It produces rich, balanced color palettes suitable for terminal themes.

#### Wallust Backend

| Setting | Value | Type | Note |
|---------|-------|------|------|
| `backends.wallust.backend_type` | `resized` | String | Process resized image (faster) |

```python
wallust_backend_type = "resized"
```

#### Custom Backend

| Setting | Value | Type | Range | Note |
|---------|-------|------|-------|------|
| `backends.custom.algorithm` | `kmeans` | String | `kmeans`, `dominant` | K-means clustering |
| `backends.custom.n_clusters` | `16` | Integer | 8 to 256 | Standard terminal color count |

```python
custom_algorithm = "kmeans"
custom_n_clusters = 16
```

**Why 16 clusters?** ANSI terminals use 16 colors. This default extracts exactly that number.

### Template Defaults

| Setting | Value | Type | Priority | Note |
|---------|-------|------|----------|------|
| `templates.directory` | Auto-detected | Path | 1. `$COLOR_SCHEME_TEMPLATES` → 2. `/templates` (container) → 3. `./templates` (project) | Template directory detection order |

```python
# Auto-detection logic (in priority order):
if (env_templates := os.getenv("COLOR_SCHEME_TEMPLATES")) is not None:
    template_directory = Path(env_templates)
elif _container_templates.exists():
    # Running in container
    template_directory = _container_templates  # /templates
else:
    # Running on host
    template_directory = _project_templates    # ./templates
```

---

## Complete Default Configuration

When no settings files exist, this is the effective configuration:

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

[templates]
directory = "<auto>"  # Auto-detected per priority order above
```

---

## Environment Variable Defaults

### Supported Environment Variables

| Variable | Purpose | Default Value | When Used |
|----------|---------|---|-----------|
| `COLOR_SCHEME_TEMPLATES` | Override template directory | (none - optional) | If set, used as template directory (highest priority) |
| `HOME` | User home directory | System value | Expands in paths like `$HOME/.config/...` |
| `USER` | Current username | System value | Can be used in paths like `/home/$USER/...` |

### Path Expansion Defaults

All path values support environment variable expansion with these defaults:

```python
# Default behavior from os.path.expandvars()
path = "$HOME/.config/color-scheme/output"
# Expands to: /home/username/.config/color-scheme/output

path = "~/colors"
# Expands to: /home/username/colors
```

---

## Configuration File Location Defaults

### Default Search Paths (in priority order)

1. **Current Directory** (Project-level)
   - Location: `./settings.toml`
   - When: If exists in current working directory

2. **User Configuration** (User-level)
   - Location: `~/.config/color-scheme/settings.toml`
   - When: If project config doesn't exist

3. **Package Defaults** (Built-in)
   - Location: Embedded in `packages/core/src/color_scheme/config/defaults.py`
   - When: If user config doesn't exist

### Example File Resolution

```bash
# Running from /home/john/projects/myproject/
color-scheme-core generate image.jpg

# Config resolution:
1. Check: /home/john/projects/myproject/settings.toml
2. If missing, check: /home/john/.config/color-scheme/settings.toml
3. If missing, use: package defaults
```

---

## CLI Argument Defaults

### generate Command

| Argument | CLI Flag | Default Behavior | Override Via |
|----------|----------|------------------|--------------|
| `image_path` | (required) | Must be provided | `color-scheme-core generate IMAGE_PATH` |
| `--output-dir` | `-o` | Use `output.directory` from settings | `-o /custom/path` |
| `--backend` | `-b` | Auto-detect or use `generation.default_backend` | `-b custom` |
| `--format` | `-f` | Use all formats from `output.formats` | `-f json -f css` |
| `--saturation` | `-s` | Use `generation.saturation_adjustment` | `-s 1.5` |

**Example:** Without CLI overrides
```bash
color-scheme-core generate image.jpg
# Uses: output.directory, default_backend, all formats, saturation 1.0
```

**Example:** With CLI overrides
```bash
color-scheme-core generate image.jpg -o /tmp/output -b wallust -s 1.3
# Overrides: output directory, backend, saturation (formats still use defaults)
```

### show Command

| Argument | CLI Flag | Default Behavior | Override Via |
|----------|----------|------------------|--------------|
| `image_path` | (required) | Must be provided | `color-scheme-core show IMAGE_PATH` |
| `--backend` | `-b` | Auto-detect or use `generation.default_backend` | `-b custom` |
| `--saturation` | `-s` | Use `generation.saturation_adjustment` | `-s 1.5` |

### install/uninstall Commands (Orchestrator)

| Argument | CLI Flag | Default Behavior | Override Via |
|----------|----------|------------------|--------------|
| `[backend]` | (optional) | Install/remove all backends | `color-scheme install pywal` |
| `--engine` | `-e` | Use `docker` | `-e podman` |
| `--yes` | `-y` | Prompt for confirmation | `-y` to skip confirmation |

---

## Hardcoded Defaults (Cannot be Configured)

Some values are hardcoded and **cannot** be changed via configuration:

| Setting | Value | Type | Reason |
|---------|-------|------|--------|
| Color count | 16 | Integer | ANSI terminal standard |
| Color names | ANSI 0-15 + background/foreground/cursor | Fixed | Terminal standards |
| Available backends | pywal, wallust, custom | Fixed | Implementation scope |
| Available formats | json, sh, css, gtk.css, yaml, sequences, rasi, scss | Fixed | Template set |
| Image input handling | Pillow-supported formats only | Fixed | Implementation dependency |
| Output file mode | 644 (user RW, others read) | Fixed | Security default |

---

## How Defaults Are Applied

### Configuration Merging Order

When color-scheme starts, configuration is loaded and merged in this order (highest to lowest priority):

1. **CLI Arguments** (highest priority)
   ```bash
   color-scheme-core generate image.jpg -s 1.5 -o /tmp/out
   ```
   → `saturation_adjustment = 1.5`, `output.directory = /tmp/out`

2. **Project Settings**
   ```toml
   # ./settings.toml
   [generation]
   saturation_adjustment = 1.2
   ```
   → Applied if `./settings.toml` exists

3. **User Settings**
   ```toml
   # ~/.config/color-scheme/settings.toml
   [output]
   formats = ["json", "sh"]
   ```
   → Applied if user config exists and not overridden above

4. **Package Defaults** (lowest priority)
   ```python
   # Embedded in package
   default_backend = "pywal"
   saturation_adjustment = 1.0
   ```
   → Applied if nothing above specifies a value

### Merging Example

Given these configs:

**Package defaults:**
```toml
[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]

[generation]
saturation_adjustment = 1.0
```

**User settings** (`~/.config/color-scheme/settings.toml`):
```toml
[output]
formats = ["json", "css"]
```

**Project settings** (`./settings.toml`):
```toml
[generation]
saturation_adjustment = 1.3
```

**CLI command:**
```bash
color-scheme-core generate image.jpg -s 1.5
```

**Resulting configuration:**
```toml
[output]
directory = "$HOME/.config/color-scheme/output"  # from package
formats = ["json", "css"]                          # from user (project didn't override)

[generation]
saturation_adjustment = 1.5                        # from CLI (highest priority!)
```

---

## Backend Auto-Detection Defaults

When no backend is specified (`--backend` not provided), the system tries in this order:

1. **pywal** (if binary is in PATH and executable)
   - Command: `which wal`
   - Used if available

2. **wallust** (if binary is in PATH and executable)
   - Command: `which wallust`
   - Used if pywal not available

3. **custom** (always available)
   - No external dependencies
   - Always works as fallback

**Note:** The `generation.default_backend` setting is used as a **hint** for the first choice, but availability still determines actual usage.

### Example Auto-Detection

```bash
# pywal binary is in PATH
color-scheme-core generate image.jpg
# → Uses pywal (auto-detected, even if default_backend = "custom")

# pywal not installed, wallust is
color-scheme-core generate image.jpg
# → Uses wallust (second choice)

# Neither installed
color-scheme-core generate image.jpg
# → Uses custom (always available)
```

---

## Container Defaults (Orchestrator Package)

### Template Directory Defaults (Container)

When running inside a container, templates are mounted at `/templates`:

```python
# Inside container
if Path("/templates").exists():
    template_directory = Path("/templates")
```

The orchestrator mounts:
- Host templates directory → Container `/templates` (read-only)

### Container Engine Defaults

| Setting | Value | Type | Note |
|---------|-------|------|------|
| orchestrator.engine | `docker` | String | Default container engine |

Can be overridden with `--engine podman`.

---

## Platform-Specific Defaults

### Path Defaults by OS

| Component | Linux | macOS | Windows |
|-----------|-------|-------|---------|
| Config | `~/.config/color-scheme` | `~/.config/color-scheme` | `%APPDATA%\color-scheme` |
| Output | `~/.config/color-scheme/output` | `~/.config/color-scheme/output` | `%APPDATA%\color-scheme\output` |
| Logging | stderr | stderr | stderr |
| Templates | `./templates` | `./templates` | `.\templates` |

### Tested Platforms

- **Linux**: Primary development platform
- **macOS**: Supported (path expansion via Python)
- **Windows**: Supported (path expansion via Python, use `\` or `/`)

---

## Special Cases and Edge Cases

### Empty Configuration File

If a settings file is empty or only has comments:

```toml
# This is my color-scheme settings
# (but it's empty)
```

Result: All defaults are used.

### Partial Configuration

If only some sections are specified:

```toml
# Only logging specified
[logging]
level = "DEBUG"
```

Result: Specified values used, others use defaults.

### Conflicting Defaults

If CLI argument conflicts with settings:

```bash
# settings.toml has: saturation_adjustment = 1.2
# CLI command:
color-scheme-core generate image.jpg -s 1.5

# Result: -s 1.5 wins (CLI takes precedence)
```

### Case Variations

All keys are normalized to lowercase:

```toml
[Logging]
LEVEL = "DEBUG"

# Treated as:
[logging]
level = "DEBUG"
```

---

## Resetting to Defaults

To use package defaults and ignore all configuration files:

```bash
# Move or remove config files (not recommended)
mv ~/.config/color-scheme/settings.toml ~/.config/color-scheme/settings.toml.bak
mv ./settings.toml ./settings.toml.bak

# Then run command - will use package defaults
color-scheme-core generate image.jpg
```

---

## Version Compatibility

These defaults apply to **color-scheme-core version 0.1.0** and later.

For version-specific defaults, check:
- Package: `packages/core/src/color_scheme/config/defaults.py`
- Embedded: `packages/core/src/color_scheme/config/settings.toml`

---

## Related Documentation

- [Settings Schema Reference](settings-schema.md) - Complete schema documentation
- [Environment Variables](environment-variables.md) - Available environment variables
- [Core CLI Commands](../cli/core-commands.md) - How CLI overrides work
- [Orchestrator Commands](../cli/orchestrator-commands.md) - Container default settings
