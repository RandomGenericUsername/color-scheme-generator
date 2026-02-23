# Reference: color-scheme-core CLI

**Package:** `color-scheme-core`
**Entry point:** `color-scheme-core`
**Source:** `packages/core/src/color_scheme/cli/main.py`

---

## Command summary

| Command | Purpose |
|---------|---------|
| `version` | Show package version |
| `generate` | Extract colors from an image and write output files |
| `show` | Display extracted colors in the terminal (no files written) |

---

## `color-scheme-core version`

### Synopsis

```bash
color-scheme-core version
```

### Description

Prints the installed version of the `color-scheme-core` package.

### Options

None.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Unexpected error |

### Example

```bash
$ color-scheme-core version
color-scheme-core version 0.1.0
```

---

## `color-scheme-core generate`

### Synopsis

```bash
color-scheme-core generate [OPTIONS] IMAGE_PATH
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `IMAGE_PATH` | Yes | Path to source image file (PNG, JPG, GIF, or any format supported by Pillow). Absolute or relative. |

### Options

| Option | Short | Type | Range / Values | Default | Description |
|--------|-------|------|----------------|---------|-------------|
| `--output-dir` | `-o` | Path | Any valid directory | `~/.config/color-scheme/output` | Directory where output files are written. |
| `--backend` | `-b` | Enum | `pywal`, `wallust`, `custom` | Auto-detected | Backend for color extraction. When omitted, auto-detection runs (see backend selection). |
| `--format` | `-f` | Enum (repeatable) | `json`, `sh`, `css`, `gtk.css`, `yaml`, `sequences`, `rasi`, `scss` | All 8 formats | Output format(s) to generate. Specify multiple times for multiple formats. |
| `--saturation` | `-s` | Float | 0.0 – 2.0 | From settings (default 1.0) | Saturation multiplier. Values < 1.0 desaturate; > 1.0 saturate. |
| `--dry-run` | `-n` | Flag | — | false | Show execution plan without writing any files. |

### Description

Extracts 16 colors from the image using the selected backend, applies saturation
adjustment, renders all requested output templates, and writes the resulting files to
the output directory.

Steps:
1. Validate the image file exists and is readable.
2. Select a backend (specified or auto-detected).
3. Extract colors (exit 1 if backend unavailable).
4. Apply saturation factor to all colors.
5. Render output templates and write files.
6. Print a summary table of generated files.

### Backend selection

When `--backend` is not specified, auto-detection checks in this order:

1. **wallust** — checks if the `wallust` binary is in PATH
2. **pywal** — checks if the `wal` binary is in PATH
3. **custom** — always available (built-in Python implementation)

The first available backend is used.

### Output files

All generated files are placed in the output directory:

| Format | Filename | Content |
|--------|----------|---------|
| `json` | `colors.json` | JSON object with all color data and metadata |
| `sh` | `colors.sh` | Bash script with exported variable definitions |
| `css` | `colors.css` | CSS custom properties |
| `gtk.css` | `colors.gtk.css` | GTK theme definitions |
| `yaml` | `colors.yaml` | YAML configuration |
| `sequences` | `colors.sequences` | ANSI terminal escape sequences |
| `rasi` | `colors.rasi` | Rofi theme configuration |
| `scss` | `colors.scss` | Sass variable definitions |

When `--format` is specified, only the listed format(s) are produced.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | All requested files generated successfully |
| 1 | Error — invalid image, backend unavailable, or write failure |

### Error messages

| Message | Cause |
|---------|-------|
| `Image file not found` | IMAGE_PATH does not exist |
| `Path is not a file` | IMAGE_PATH is a directory |
| `Backend '<name>' not available` | Backend binary not in PATH |
| `Color extraction failed` | Backend failed to process image |
| `Template rendering failed` | Template syntax error |
| `Failed to write output file` | Permission denied or disk full |

### Examples

```bash
# Default: auto-detect backend, all 8 formats, default output dir
color-scheme-core generate wallpaper.jpg

# Specify backend and output directory
color-scheme-core generate wallpaper.jpg -b custom -o ~/my-colors

# Only generate JSON and CSS
color-scheme-core generate wallpaper.jpg -f json -f css

# Boost saturation
color-scheme-core generate wallpaper.jpg -s 1.4

# Dry-run: see the plan, write nothing
color-scheme-core generate wallpaper.jpg --dry-run
color-scheme-core generate wallpaper.jpg -n
```

---

## `color-scheme-core show`

### Synopsis

```bash
color-scheme-core show [OPTIONS] IMAGE_PATH
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `IMAGE_PATH` | Yes | Path to source image file. |

### Options

| Option | Short | Type | Range / Values | Default | Description |
|--------|-------|------|----------------|---------|-------------|
| `--backend` | `-b` | Enum | `pywal`, `wallust`, `custom` | Auto-detected | Backend for color extraction. |
| `--saturation` | `-s` | Float | 0.0 – 2.0 | From settings (default 1.0) | Saturation multiplier applied before display. |
| `--dry-run` | `-n` | Flag | — | false | Show execution plan without displaying colors. |

### Description

Extracts colors from the image and displays them in formatted terminal tables. No output
files are written.

Output contains three sections:

1. **Information panel** — source image path, backend used, and saturation factor
   (saturation line is omitted when the value is 1.0).
2. **Special colors table** — background, foreground, and cursor; shows name, colored
   preview, hex value, and RGB value.
3. **Terminal colors table (ANSI)** — all 16 colors (indices 0–15); shows index, name,
   colored preview, hex, and RGB.

When `--dry-run` is given, the execution plan is printed but the color tables are
suppressed.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Colors displayed successfully |
| 1 | Error — image not found, backend unavailable, or extraction failure |

### Examples

```bash
# Auto-detect backend, show all colors
color-scheme-core show wallpaper.jpg

# Force custom backend
color-scheme-core show wallpaper.jpg -b custom

# Adjust saturation for display
color-scheme-core show wallpaper.jpg -s 1.3

# Dry-run
color-scheme-core show wallpaper.jpg --dry-run
```

---

## Global behavior

### Help

```bash
color-scheme-core --help
color-scheme-core generate --help
color-scheme-core show --help
```

### Configuration interaction

CLI arguments override settings from configuration files. Layer order (highest priority
first): CLI flags > user config > project config > package defaults.

### Environment variables

| Variable | Effect |
|----------|--------|
| `COLOR_SCHEME_TEMPLATES` | Override the Jinja2 template directory |
| `COLORSCHEME_<SECTION>__<KEY>` | Set any config key via env var (double-underscore nesting) |

---

## Verification reference

| BHV | Behavior |
|-----|---------|
| BHV-0001 | `generate` with valid image exits 0 and creates output files |
| BHV-0002 | `--format` restricts output to specified formats only |
| BHV-0003 | `generate` with invalid image path exits 1 with error message |
| BHV-0004 | `generate --dry-run` exits 0, shows plan |
| BHV-0005 | `-n` is alias for `--dry-run` |
| BHV-0006 | Dry-run creates no files |
| BHV-0007 | `show` displays background, foreground, cursor, and 16 ANSI colors |
| BHV-0008 | `show --dry-run` suppresses color tables |
| BHV-0009 | Auto-detect order: wallust > pywal > custom |
| BHV-0010 | `BackendNotAvailableError` raised when backend binary absent |


---

## See also

- [Use Dry-Run Mode](../how-to/use-dry-run.md) — preview generate without writing files
- [Configure Settings](../how-to/configure-settings.md) — change output directory, formats, and saturation defaults
- [Core Types](../reference/types.md) — Color, ColorScheme, and GeneratorConfig models
