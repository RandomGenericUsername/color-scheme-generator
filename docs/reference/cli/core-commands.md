# Core CLI Commands Reference

**Package:** `color-scheme-core`
**Version:** 0.1.0
**Entry Point:** `color-scheme-core`

Complete reference for the core command-line interface. This package provides direct access to color scheme generation without containerization.

---

## `version`

Display version information for the core package.

### Synopsis

```bash
color-scheme-core version
```

### Description

Shows the installed version of the `color-scheme-core` package.

### Options

None

### Exit Codes

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

## `generate`

Generate color scheme files from an image with multiple output formats.

### Synopsis

```bash
color-scheme-core generate [OPTIONS] IMAGE_PATH
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `IMAGE_PATH` | Yes | Path to source image file. Can be absolute or relative. Image must be readable and in a format supported by Pillow (PNG, JPG, GIF, etc.). |

### Options

| Option | Type | Range/Values | Default | Description |
|--------|------|--------------|---------|-------------|
| `--output-dir`, `-o` | Path | any valid directory | `~/.config/color-scheme/output` | Output directory where color scheme files will be written. Created if it does not exist. |
| `--backend`, `-b` | Enum | `pywal`, `wallust`, `custom` | auto-detected | Backend to use for color extraction. If not specified, auto-detection attempts to find an available backend in order: pywal, wallust, custom. |
| `--format`, `-f` | Enum (repeatable) | `json`, `sh`, `css`, `gtk.css`, `yaml`, `sequences`, `rasi`, `scss` | all 8 formats | Output format(s) to generate. Can be specified multiple times for multiple formats. If not specified, all 8 formats are generated. |
| `--saturation`, `-s` | Float | 0.0 to 2.0 | from settings (default 1.0) | Saturation adjustment factor. Values < 1.0 desaturate colors, > 1.0 saturate. Applied after color extraction. |

### Description

Extracts colors from an image using the specified backend and generates color scheme files in requested formats. The command:

1. Validates the input image exists and is readable
2. Selects a backend (specified or auto-detected)
3. Extracts colors from the image
4. Applies saturation adjustment if specified
5. Renders templates and writes output files
6. Displays a summary table of generated files

### Examples

```bash
# Generate with auto-detected backend, all default formats
color-scheme-core generate wallpaper.jpg

# Specify backend and output directory
color-scheme-core generate wallpaper.jpg -b pywal -o ~/my-colors

# Generate specific formats only
color-scheme-core generate wallpaper.jpg -f json -f css -f scss

# Adjust saturation (boost by 50%)
color-scheme-core generate wallpaper.jpg -s 1.5

# Desaturate colors (reduce by 30%)
color-scheme-core generate wallpaper.jpg -s 0.7

# Combine multiple options
color-scheme-core generate /path/to/image.png -b custom -o ./output -f json -f yaml -s 1.2
```

### Backend Selection

If `--backend` is not specified, the command auto-detects available backends:

1. **pywal**: Checks if `wal` binary is in PATH and can be executed
2. **wallust**: Checks if `wallust` binary is in PATH and can be executed
3. **custom**: Always available (built-in Python implementation)

Auto-detection stops at the first available backend. To use a specific backend, use `-b`.

### Output Files

Generated files are placed in the output directory with standardized names:

| Format | Filename | Content Type |
|--------|----------|--------------|
| json | `colors.json` | JSON with all color data and metadata |
| sh | `colors.sh` | Bash/shell script with variable exports |
| css | `colors.css` | CSS custom properties |
| gtk.css | `colors.gtk.css` | GTK theme definitions |
| yaml | `colors.yaml` | YAML configuration format |
| sequences | `colors.sequences` | ANSI escape sequences |
| rasi | `colors.rasi` | Rofi theme configuration |
| scss | `colors.scss` | Sass variable definitions |

### Error Handling

The command provides detailed error messages for common issues:

| Error | Cause | Solution |
|-------|-------|----------|
| "Image file not found" | IMAGE_PATH does not exist | Verify image path and try again |
| "Path is not a file" | IMAGE_PATH points to directory | Specify a file, not a directory |
| "Backend '<name>' not available" | Backend binary not installed or in PATH | Install backend or use auto-detection |
| "Invalid image" | Image format not supported or corrupted | Use PNG/JPG/GIF format, verify file integrity |
| "Color extraction failed" | Backend failed to process image | Check image quality, try different backend |
| "Template rendering failed" | Template syntax error | Report as bug with template name shown |
| "Failed to write output file" | Permission denied or disk full | Check directory permissions and disk space |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all files generated |
| 1 | Error occurred (see stderr for details) |

### Configuration Interaction

This command reads from configuration at multiple levels (in priority order):

1. **CLI arguments** (highest priority)
2. **Settings file** at `./settings.toml` or `~/.config/color-scheme/settings.toml`
3. **Package defaults** from `packages/core/src/color_scheme/config/settings.toml`

Use `--output-dir` and `--saturation` to override settings file values.

### Performance Considerations

- **Image preprocessing**: Custom backend resizes images to max 200x200 for clustering
- **Backend timeout**: External backends (pywal, wallust) timeout after 30 seconds
- **Format generation**: Slower formats in order: json, sequences, then others
- **Large output directories**: Writing 8 formats generates ~8 files

### See Also

- [show command](#show) - Display colors without writing files
- [Configuration Reference](../configuration/settings-schema.md)
- [Template Variables](../templates/variables.md)

---

## `show`

Display extracted colors in the terminal without writing files.

### Synopsis

```bash
color-scheme-core show [OPTIONS] IMAGE_PATH
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `IMAGE_PATH` | Yes | Path to source image file. Can be absolute or relative. Image must be readable and in a format supported by Pillow (PNG, JPG, GIF, etc.). |

### Options

| Option | Type | Range/Values | Default | Description |
|--------|------|--------------|---------|-------------|
| `--backend`, `-b` | Enum | `pywal`, `wallust`, `custom` | auto-detected | Backend to use for color extraction. If not specified, auto-detects an available backend. |
| `--saturation`, `-s` | Float | 0.0 to 2.0 | from settings (default 1.0) | Saturation adjustment factor. Applied to all colors before display. |

### Description

Extracts colors from an image and displays them in formatted terminal tables without writing any output files. The command:

1. Validates the input image exists and is readable
2. Selects a backend (specified or auto-detected)
3. Extracts colors from the image
4. Applies saturation adjustment if specified
5. Displays color information in three tables:
   - Information panel (source, backend, saturation)
   - Special colors table (background, foreground, cursor)
   - Terminal colors table (ANSI colors 0-15)

### Examples

```bash
# Show colors with auto-detected backend
color-scheme-core show wallpaper.jpg

# Specify backend
color-scheme-core show wallpaper.jpg -b custom

# Adjust saturation while displaying
color-scheme-core show wallpaper.jpg -s 1.5

# Use pywal backend specifically
color-scheme-core show ~/images/background.png -b pywal
```

### Display Format

The output contains three sections:

#### Information Panel

Shows metadata about the color extraction:
- Source image path
- Backend used
- Saturation adjustment factor (if applied)

#### Special Colors Table

Displays the three main colors:
- **Background**: Dark color for terminal background
- **Foreground**: Light color for terminal text
- **Cursor**: Highlight color for cursor

Each row shows:
- Color name
- Color preview (colored square)
- Hex value (`#RRGGBB`)
- RGB value (`rgb(R, G, B)`)

#### Terminal Colors Table (ANSI)

Displays all 16 standard terminal colors (indices 0-15):

| Index | Name | Usage |
|-------|------|-------|
| 0 | Black | Dark color |
| 1 | Red | Error/warning color |
| 2 | Green | Success color |
| 3 | Yellow | Warning color |
| 4 | Blue | Info color |
| 5 | Magenta | Accent color |
| 6 | Cyan | Accent color |
| 7 | White | Light color |
| 8 | Bright Black | Gray |
| 9 | Bright Red | Bright error |
| 10 | Bright Green | Bright success |
| 11 | Bright Yellow | Bright warning |
| 12 | Bright Blue | Bright info |
| 13 | Bright Magenta | Bright accent |
| 14 | Bright Cyan | Bright accent |
| 15 | Bright White | Bright text |

Each color row shows: index, ANSI name, color preview, hex, and RGB values.

### Color Preview Quality

Color previews are displayed as colored squares in the terminal. Preview quality depends on terminal color support:
- **True color terminals** (24-bit): Exact hex colors displayed
- **256-color terminals**: Colors approximated to 256-color palette
- **16-color terminals**: Colors approximated to 16 ANSI colors

### Backend Selection

Same as [generate command](#backend-selection) - auto-detects if not specified.

### Error Handling

Errors are reported immediately with context:

| Error | Cause | Solution |
|-------|-------|----------|
| "Image file not found" | IMAGE_PATH does not exist | Verify image path |
| "Backend '<name>' not available" | Backend not installed | Install or use auto-detection |
| "Invalid image" | Unsupported format or corrupted | Use PNG/JPG/GIF, verify file |
| "Color extraction failed" | Backend processing error | Try different backend |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - colors displayed |
| 1 | Error occurred (see stderr for details) |

### Configuration Interaction

Reads configuration from (in priority order):

1. **CLI arguments** (highest priority)
2. **Settings file** (`./settings.toml` or `~/.config/color-scheme/settings.toml`)
3. **Package defaults**

### Performance

This command is faster than `generate` because:
- No file I/O (no template rendering)
- No disk writes
- Display only happens at terminal

### See Also

- [generate command](#generate) - Save colors to files
- [Configuration Reference](../configuration/settings-schema.md)

---

## Global Options and Behavior

### Help

All commands support the `-h` or `--help` option:

```bash
color-scheme-core --help
color-scheme-core generate --help
color-scheme-core show --help
```

### Logging

Logging is configured via `~/.config/color-scheme/settings.toml` or `./settings.toml`:

```toml
[logging]
level = "INFO"      # DEBUG, INFO, WARNING, ERROR, CRITICAL
show_time = true    # Include timestamps
show_path = false   # Include file paths
```

Logs are written to stderr and do not interfere with command output.

### Environment Variables

| Variable | Effect | Example |
|----------|--------|---------|
| `$HOME` | Expanded in all paths | `~/colors` → `/home/user/colors` |
| `$USER` | Expanded in all paths | User-specific paths |
| `COLOR_SCHEME_TEMPLATES` | Override template directory | Custom template location |

### File Path Handling

- **Relative paths**: Resolved from current working directory
- **Tilde expansion**: `~` expands to user home directory
- **Environment variables**: `$VAR` and `${VAR}` are expanded
- **Directory creation**: Output directories are created if they don't exist

### Configuration Files

Configuration is loaded from (in priority order):

1. **CLI arguments** (highest priority)
2. **User config**: `~/.config/color-scheme/settings.toml`
3. **Project config**: `./settings.toml` (in current directory)
4. **Package defaults**: Built-in defaults

---

## Command Summary Table

| Command | Purpose | Main Arguments | Output |
|---------|---------|----------------|--------|
| `version` | Show version | none | Version string |
| `generate` | Create color files | IMAGE_PATH | 1-8 color files |
| `show` | Display colors | IMAGE_PATH | Terminal tables |

---

## Entry Point Details

### Console Script

The `color-scheme-core` command is installed as a console script that calls `color_scheme.cli.main:main()`.

**Location:** `packages/core/src/color_scheme/cli/main.py`

**Installation:**
```bash
pip install packages/core
```

The script is registered in `pyproject.toml` under `[project.scripts]`.

### Programmatic Usage

To use the CLI programmatically:

```python
from color_scheme.cli.main import app
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ["generate", "image.jpg", "-o", "output"])
```

---

## Troubleshooting

### Backend Not Found

**Problem:** "Backend 'pywal' not available"

**Solutions:**
1. Install the backend: `pip install pywal` or `sudo pacman -S pywal`
2. Verify binary is in PATH: `which wal`
3. Use auto-detection: Omit `-b` flag
4. Use custom backend: `color-scheme-core generate image.jpg -b custom`

### Image Not Found

**Problem:** "Image file not found: /path/to/image.jpg"

**Solutions:**
1. Verify file exists: `ls /path/to/image.jpg`
2. Check current directory: `pwd`
3. Use absolute path: `color-scheme-core generate /home/user/images/image.jpg`

### Permission Denied

**Problem:** "Failed to write output file"

**Solutions:**
1. Check directory permissions: `ls -ld ~/.config/color-scheme/output`
2. Create directory manually: `mkdir -p ~/.config/color-scheme/output`
3. Change permissions: `chmod 755 ~/.config/color-scheme/output`
4. Use different output directory: `color-scheme-core generate image.jpg -o /tmp/colors`

### Unsupported Image Format

**Problem:** "Invalid image"

**Solutions:**
1. Use supported formats: PNG, JPG, GIF, BMP, TIFF
2. Convert image: `ffmpeg -i image.webp image.png`
3. Check file is not corrupted: Open in image viewer first

---

## Related Documentation

- [Orchestrator Commands](orchestrator-commands.md) - Containerized CLI
- [Configuration Schema](../configuration/settings-schema.md) - Settings reference
- [API Reference](../api/types.md) - Python API
- [Troubleshooting Guide](../../how-to/troubleshoot-errors.md) - Common solutions
