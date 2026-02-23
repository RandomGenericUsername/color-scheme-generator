# Settings Schema Reference

**Scope:** Complete TOML configuration schema for color-scheme
**Location:** Configuration files at multiple levels (see [File Locations](#file-locations))
**Version:** 0.1.0 (matches core package version)

Comprehensive reference for all configuration options, their types, allowed values, and defaults.

---

## Quick Reference

All configuration is stored in TOML format with sections for different concerns:

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

---

## File Locations (Priority Order)

Configuration is loaded from multiple locations in priority order (highest to lowest):

1. **CLI Arguments** (highest priority)
   - Command-line options override all settings
   - Example: `color-scheme-core generate image.jpg -b custom -o /tmp/output`

2. **User Settings**
   - Location: `~/.config/color-scheme/settings.toml`
   - Scope: User-wide defaults
   - Applied to: All color-scheme commands

3. **Project Settings**
   - Location: `./settings.toml` (in current working directory)
   - Scope: Project-specific overrides
   - Applied to: Commands run from that directory

4. **Package Defaults** (lowest priority)
   - Embedded in package
   - Location: `packages/core/src/color_scheme/config/settings.toml`
   - Used when no user or project settings exist

### File Resolution Example

When you run `color-scheme-core generate image.jpg`:

1. Check for `./settings.toml` (current directory) → use if exists
2. Otherwise check `~/.config/color-scheme/settings.toml` → use if exists
3. Otherwise use package defaults
4. Apply any CLI arguments on top

---

## Configuration Keys

### Case-Insensitivity

**All configuration keys are case-insensitive.** Keys are automatically normalized to lowercase during loading.

| Input | Normalized |
|-------|-----------|
| `[LOGGING]` | `[logging]` |
| `[Logging]` | `[logging]` |
| `[logging]` | `[logging]` |
| `DEFAULT_BACKEND` | `default_backend` |
| `Default_Backend` | `default_backend` |
| `default_backend` | `default_backend` |

You can use any case style:

```toml
# All equivalent
[LOGGING]
LEVEL = "INFO"

[Logging]
Level = "INFO"

[logging]
level = "INFO"
```

---

## Section: `[logging]`

### Purpose
Controls logging output for color-scheme commands.

### Configuration

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `level` | String | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` | Logging level (case-insensitive, normalized to uppercase) |
| `show_time` | Boolean | `true`, `false` | `true` | Include timestamps in log messages |
| `show_path` | Boolean | `true`, `false` | `false` | Include file path information in log messages |

### Logging Levels Explained

| Level | Priority | When to Use | Example Output |
|-------|----------|------------|-----------------|
| `DEBUG` | 10 | Detailed troubleshooting | "Loading config from /path/to/settings.toml" |
| `INFO` | 20 | Normal operation | "Auto-detected backend: pywal" |
| `WARNING` | 30 | Potential issues | "Output directory doesn't exist, creating..." |
| `ERROR` | 40 | Errors that don't stop execution | "Failed to load format: unknown format" |
| `CRITICAL` | 50 | Fatal errors | "Image file corrupted, cannot process" |

### Examples

**Development debugging:**
```toml
[logging]
level = "DEBUG"
show_time = true
show_path = true
```

**Production use:**
```toml
[logging]
level = "WARNING"
show_time = false
show_path = false
```

**Quiet operation:**
```toml
[logging]
level = "ERROR"
show_time = false
show_path = false
```

---

## Section: `[output]`

### Purpose
Controls output file generation and location. These settings are used by the `OutputManager` to determine where and how to write generated color scheme files.

### Configuration

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `directory` | Path | any valid directory path | `$HOME/.config/color-scheme/output` | Directory where output files are written. Supports environment variable expansion. Created if doesn't exist. |
| `formats` | Array | `json`, `sh`, `css`, `gtk.css`, `yaml`, `sequences`, `rasi`, `scss` | all 8 formats | Which output formats to generate. Can be partial list. |

### Path Expansion

The `directory` value supports **environment variable expansion**:

| Syntax | Expands To | Example |
|--------|-----------|---------|
| `$HOME` | User home directory | `/home/username` |
| `$USER` | Current username | `john` |
| `${VAR}` | Environment variable | `/opt/myapp` |
| `~` | Home directory shortcut | `/home/username` |

### Examples

**Default location:**
```toml
[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]
```

**Custom directory:**
```toml
[output]
directory = "/var/lib/color-schemes"
formats = ["json", "css", "scss"]
```

**Relative path:**
```toml
[output]
directory = "./local-colors"
formats = ["json", "sh"]
```

**User-specific:**
```toml
[output]
directory = "~/.config/my-colors"
formats = ["json", "yaml"]
```

### Supported Output Formats

| Format | File | Use Case | Content |
|--------|------|----------|---------|
| `json` | `colors.json` | API/programmatic access | JSON object with colors and metadata |
| `sh` | `colors.sh` | Bash/shell scripts | Shell variables with `export` statements |
| `css` | `colors.css` | Web CSS | CSS custom properties `:root { --color-0: #... }` |
| `gtk.css` | `colors.gtk.css` | GTK theming | GTK `@define-color` statements |
| `yaml` | `colors.yaml` | Configuration files | YAML format with color hierarchies |
| `sequences` | `colors.sequences` | Terminal escape codes | OSC escape sequences for terminal colors |
| `rasi` | `colors.rasi` | Rofi theming | Rofi theme variable definitions |
| `scss` | `colors.scss` | Sass/SCSS | Sass `$variable` definitions |

---

## Section: `[generation]`

### Purpose
Provides default values for color scheme generation that can be overridden at runtime.

### Configuration

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `default_backend` | String | `pywal`, `wallust`, `custom` | `pywal` | Default backend to use if not specified on command line. If auto-detection is used, this is the fallback. |
| `saturation_adjustment` | Float | 0.0 to 2.0 (inclusive) | 1.0 | Default saturation adjustment multiplier. Used if `-s` option not specified. |

### Saturation Adjustment

The saturation value is a multiplier applied to all extracted colors:

| Value | Effect | Use Case |
|-------|--------|----------|
| 0.0 | Completely desaturated (grayscale) | Reduce color intensity |
| < 1.0 | Less saturated | Muted/pastel colors |
| 1.0 | No adjustment (natural colors) | Default, natural appearance |
| > 1.0 | More saturated | Vibrant/vivid colors |
| 2.0 | Maximum saturation | Maximum color intensity |

### Backend Auto-Detection

If no backend is specified via CLI, the system checks in this order:
1. Check if `pywal` backend is available (binary in PATH)
2. Check if `wallust` backend is available (binary in PATH)
3. Fall back to `custom` backend (always available)

The `default_backend` only affects which backend is **tried first** in the sequence.

### Examples

**Conservative defaults:**
```toml
[generation]
default_backend = "custom"
saturation_adjustment = 0.8
```

**Vibrant colors:**
```toml
[generation]
default_backend = "pywal"
saturation_adjustment = 1.3
```

**Neutral defaults:**
```toml
[generation]
default_backend = "pywal"
saturation_adjustment = 1.0
```

---

## Section: `[backends.pywal]`

### Purpose
Pywal-specific configuration. **Note:** These settings only control color extraction from pywal. The `OutputManager` handles file generation independently, ignoring pywal's output directory.

### Configuration

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `backend_algorithm` | String | `wal`, `colorz`, `colorthief`, `haishoku`, `schemer2` | `haishoku` | Algorithm pywal uses for color extraction. Different algorithms produce different color palettes from the same image. |

### Pywal Algorithms

| Algorithm | Description | Performance | Color Quality |
|-----------|-------------|-------------|---------------|
| `wal` | Original pywal algorithm | Fast | Good for variety |
| `colorz` | Colorz-based extraction | Medium | Balanced |
| `colorthief` | Color Thief algorithm | Medium | Detail-focused |
| `haishoku` | Haishoku-based extraction | Medium | Rich palettes (default) |
| `schemer2` | Schemer2 algorithm | Slow | Complex processing |

### Examples

**Fast extraction:**
```toml
[backends.pywal]
backend_algorithm = "wal"
```

**Rich color palettes:**
```toml
[backends.pywal]
backend_algorithm = "haishoku"
```

**Detail-focused:**
```toml
[backends.pywal]
backend_algorithm = "colorthief"
```

---

## Section: `[backends.wallust]`

### Purpose
Wallust-specific configuration. Controls how the wallust backend extracts colors.

### Configuration

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `backend_type` | String | string (wallust backend type) | `resized` | Type/mode for wallust color extraction |

### Wallust Backend Types

The `backend_type` is passed directly to wallust. Common values:

| Type | Description |
|------|-------------|
| `resized` | Resize image before processing (default, faster) |
| `full` | Process full resolution image (slower, more details) |

**Note:** Exact available types depend on your wallust version.

### Examples

```toml
[backends.wallust]
backend_type = "resized"
```

---

## Section: `[backends.custom]`

### Purpose
Configuration for the built-in Python backend. These settings control the K-means clustering algorithm used for color extraction.

### Configuration

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `algorithm` | String | `kmeans`, `dominant` | `kmeans` | Color extraction algorithm to use |
| `n_clusters` | Integer | 8 to 256 (inclusive) | 16 | Number of color clusters to extract |

### Algorithms

| Algorithm | Status | Description |
|-----------|--------|-------------|
| `kmeans` | ✅ **Implemented** | K-means clustering - extracts dominant color groups |
| `dominant` | ⚠️ **NOT IMPLEMENTED** | Dominant color extraction - not yet available |

**Important:** The `dominant` algorithm is **not currently implemented**. Using it will raise an error. Use `kmeans` instead.

### Cluster Count Guidance

| Value | Use Case | Characteristics |
|-------|----------|-----------------|
| 8 | Simple, minimal palette | Fastest, most aggressive grouping |
| 16 | **Balanced (default)** | Good for terminal colors, good performance |
| 32 | Rich palette | More detail, slower |
| 64 | Very detailed | Much slower, high detail |
| 256 | Maximum detail | Slowest, maximum precision |

**Recommendation:** Use `16` for most use cases. This matches standard terminal color count (ANSI 16 colors).

### Examples

**Fast clustering:**
```toml
[backends.custom]
algorithm = "kmeans"
n_clusters = 8
```

**Detailed extraction:**
```toml
[backends.custom]
algorithm = "kmeans"
n_clusters = 32
```

**Default balanced:**
```toml
[backends.custom]
algorithm = "kmeans"
n_clusters = 16
```

---

## Section: `[templates]`

### Purpose
Configuration for Jinja2 template rendering. The `OutputManager` uses these templates to generate output files.

### Configuration

| Key | Type | Values | Default | Description |
|-----|------|--------|---------|-------------|
| `directory` | Path | any valid directory path | auto-detected | Directory containing Jinja2 templates for output generation |

### Template Auto-Detection

If not specified or set to `<auto>`, the template directory is detected in this order:

1. **Environment variable** `COLOR_SCHEME_TEMPLATES`
   - Highest priority
   - Example: `export COLOR_SCHEME_TEMPLATES=/custom/templates`

2. **Container path** `/templates`
   - Used when running inside a Docker/Podman container
   - Mounted from orchestrator

3. **Project templates** `./templates` (relative to project root)
   - Used on host system
   - Default location for development

### Available Templates

Template files for output generation:

| Filename | Output Format | Purpose |
|----------|----------------|---------|
| `colors.json.j2` | JSON | JSON color data with metadata |
| `colors.sh.j2` | Shell | Shell script variables |
| `colors.css.j2` | CSS | CSS custom properties |
| `colors.gtk.css.j2` | GTK CSS | GTK theme colors |
| `colors.yaml.j2` | YAML | YAML configuration |
| `colors.sequences.j2` | Sequences | Terminal escape sequences |
| `colors.rasi.j2` | Rasi | Rofi theme variables |
| `colors.scss.j2` | SCSS | Sass variables |

### Examples

**Auto-detect (recommended):**
```toml
[templates]
directory = "<auto>"
```

**Custom directory:**
```toml
[templates]
directory = "/etc/color-scheme/templates"
```

**User templates:**
```toml
[templates]
directory = "~/.local/share/color-scheme/templates"
```

**Via environment variable:**
```bash
export COLOR_SCHEME_TEMPLATES=/custom/templates
color-scheme-core generate image.jpg
```

---

## Complete Configuration Example

### Minimal Configuration
```toml
# Just the required sections with defaults
[logging]
level = "INFO"

[output]
directory = "$HOME/.config/color-scheme/output"

[generation]
default_backend = "pywal"
```

### Development Configuration
```toml
[logging]
level = "DEBUG"
show_time = true
show_path = true

[output]
directory = "./local-colors"
formats = ["json", "sh", "css"]

[generation]
default_backend = "custom"
saturation_adjustment = 1.0

[backends.custom]
algorithm = "kmeans"
n_clusters = 16

[backends.pywal]
backend_algorithm = "haishoku"

[templates]
directory = "<auto>"
```

### Production Configuration
```toml
[logging]
level = "WARNING"
show_time = false
show_path = false

[output]
directory = "/var/lib/color-schemes/$USER"
formats = ["json", "css", "scss"]

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

---

## Environment Variable Expansion

All **Path values** in configuration support shell-style variable expansion:

### Supported Syntax

| Syntax | Expanded Value |
|--------|----------------|
| `$HOME` | User home directory |
| `$USER` | Current username |
| `$SHELL` | Current shell path |
| `${VARIABLE}` | Any environment variable |
| `~` | Home directory (only at start of path) |

### Examples

```toml
[output]
directory = "$HOME/.config/color-scheme/output"

[output]
directory = "/home/$USER/.colors"

[templates]
directory = "${TEMPLATES_DIR}"
```

### Expanded Values

When configuration is loaded, variables are expanded:

```toml
# Before expansion (in file)
directory = "$HOME/.config/color-scheme"

# After expansion (in memory)
directory = "/home/john/.config/color-scheme"
```

---

## Validation Rules

### Type Validation

All values are validated according to their type:

| Type | Validation |
|------|-----------|
| String | Must be valid string (quoted in TOML) |
| Boolean | Must be `true` or `false` |
| Integer | Must be whole number, may have range constraints |
| Float | Must be number, may have range constraints (e.g., 0.0-2.0) |
| Array | Must be valid array syntax, values validated individually |
| Path | Must be valid path string (expandable, not validated to exist) |

### Range Validation

| Field | Min | Max | Error if Out of Range |
|-------|-----|-----|----------------------|
| `logging.level` | - | - | Must be valid level name |
| `generation.saturation_adjustment` | 0.0 | 2.0 | "Value must be 0.0-2.0" |
| `backends.custom.n_clusters` | 8 | 256 | "Value must be 8-256" |

### Enum Validation

| Field | Valid Values | Error if Invalid |
|-------|-------------|-----------------|
| `generation.default_backend` | `pywal`, `wallust`, `custom` | "Invalid backend '...'" |
| `backends.custom.algorithm` | `kmeans`, `dominant` | "Invalid algorithm '...'" |
| `output.formats` | `json`, `sh`, `css`, `gtk.css`, `yaml`, `sequences`, `rasi`, `scss` | "Unknown format '...'" |

### Example Errors

**Invalid logging level:**
```
ValidationError: 1 validation error for LoggingSettings
level
  Value error, Invalid logging level: TRACE.
  Must be one of: CRITICAL, DEBUG, ERROR, INFO, WARNING [type=value_error]
```

**Saturation out of range:**
```
ValidationError: 1 validation error for GenerationSettings
saturation_adjustment
  Input should be less than or equal to 2 [type=less_than_equal]
```

---

## Configuration Precedence Example

Given this file structure:

```
/home/john/
├── .config/color-scheme/settings.toml    # User settings
└── projects/myproject/
    ├── settings.toml                      # Project settings
    └── image.jpg
```

When running from `/home/john/projects/myproject`:

```bash
color-scheme-core generate image.jpg -s 1.5
```

Configuration precedence:

1. **CLI argument** `-s 1.5` → `saturation_adjustment = 1.5` ✓ **Used**
2. **Project settings** `./settings.toml` (if exists) → checked
3. **User settings** `~/.config/color-scheme/settings.toml` (if exists) → checked
4. **Package defaults** → fallback

### Merging Example

If project settings don't specify `format`, but user settings do:

```toml
# ~/.config/color-scheme/settings.toml
[output]
formats = ["json", "sh"]

# ./settings.toml (project)
[generation]
default_backend = "custom"

# Result (merged)
formats = ["json", "sh"]              # from user settings
default_backend = "custom"            # from project settings
saturation_adjustment = 1.0           # from package defaults
```

---

## Troubleshooting Configuration

### Configuration not loading

**Problem:** Settings seem to be ignored

**Solutions:**
1. Verify file path:
   ```bash
   cat ~/.config/color-scheme/settings.toml
   cat ./settings.toml
   ```

2. Check file format (must be valid TOML):
   ```bash
   python -c "import tomllib; tomllib.loads(open('settings.toml').read())"
   ```

3. Try with debug logging:
   ```bash
   DEBUG=1 color-scheme-core generate image.jpg
   ```

### Validation errors

**Problem:** "ValidationError: ... is not valid"

**Solutions:**
1. Check field type (string, number, boolean, array)
2. Check allowed values (for enums)
3. Check range constraints (for numbers)
4. Verify TOML syntax

### Path expansion not working

**Problem:** `$HOME` or `$USER` not expanded

**Solutions:**
1. Use correct syntax: `$VAR` or `${VAR}`
2. Don't use `$` inside quoted paths
3. Verify environment variable exists: `echo $HOME`

---

## See Also

- [Default Values](defaults.md) - All default values listed
- [Environment Variables](environment-variables.md) - Runtime environment variables
- [Core CLI Commands](../cli/core-commands.md) - How to use CLI with settings
- [API Reference](../api/types.md) - Configuration classes
