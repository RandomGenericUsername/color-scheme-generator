# Output Manager API

**Scope:** Output rendering and file writing API
**Extracted:** February 3, 2026
**Source:** `packages/core/src/color_scheme/output/manager.py`

Complete reference for the `OutputManager` class: template rendering, file writing, and format-specific handling.

---

## Overview

The `OutputManager` handles writing color schemes to files using Jinja2 templates. It manages:
- Loading and rendering templates
- Writing rendered content to files
- Special handling for binary formats (terminal sequences)
- Directory creation and error handling

---

## OutputManager

**Class:** `color_scheme.output.manager.OutputManager`
**Module:** `packages/core/src/color_scheme/output/manager.py`
**Purpose:** Renders and writes color schemes to files

### Initialization

```python
from color_scheme.output.manager import OutputManager
from color_scheme.config.config import AppConfig

settings = AppConfig()
manager = OutputManager(settings)
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `settings` | `AppConfig` | Application configuration |
| `template_env` | `jinja2.Environment` | Jinja2 environment for template loading and rendering |

### Template Directory

The template directory is resolved from `settings.templates.directory`:

```python
# If relative path:
template_dir = settings.templates.directory
if not template_dir.is_absolute():
    package_root = Path(__file__).parent.parent
    template_dir = package_root / template_dir
```

**Default:** `../templates/` relative to package root (usually `templates/` in project root)

---

## Methods

### `write_outputs(color_scheme: ColorScheme, output_dir: Path, formats: list[ColorFormat]) -> None`

Writes color scheme to files in specified formats.

**Parameters:**
- `color_scheme` (`ColorScheme`): Color scheme to write
- `output_dir` (`Path`): Directory to write files to
- `formats` (`list[ColorFormat]`): List of formats to generate

**Raises:**
- `TemplateRenderError` - Template rendering fails
- `OutputWriteError` - File writing fails

**Behavior:**
1. Creates output directory (with parents, no error if exists)
2. Iterates through each format
3. For each format, calls `_write_format()`
4. Updates `color_scheme.output_files` with generated paths

**Example:**
```python
from color_scheme.output.manager import OutputManager
from color_scheme.config.enums import ColorFormat
from pathlib import Path

manager = OutputManager(settings)

# Write multiple formats
manager.write_outputs(
    color_scheme=scheme,
    output_dir=Path("/output"),
    formats=[ColorFormat.JSON, ColorFormat.SH, ColorFormat.CSS]
)

# Check output files
print(scheme.output_files)
# {
#     'json': Path('/output/colors.json'),
#     'sh': Path('/output/colors.sh'),
#     'css': Path('/output/colors.css')
# }
```

---

### `_write_format(color_scheme: ColorScheme, output_dir: Path, fmt: ColorFormat) -> None` (Private)

Writes a single format to file.

**Parameters:**
- `color_scheme` (`ColorScheme`): Color scheme to write
- `output_dir` (`Path`): Output directory
- `fmt` (`ColorFormat`): Format to write

**Raises:**
- `TemplateRenderError` - Template rendering fails
- `OutputWriteError` - File writing fails

**Output File Name:**
- Pattern: `colors.{format_value}`
- Examples: `colors.json`, `colors.sh`, `colors.css`, `colors.gtk.css`

**Behavior:**
1. Renders template via `_render_template()`
2. Handles SEQUENCES format specially (binary conversion)
3. Writes file via `_write_file()` or `_write_binary_file()`

---

### `_render_template(color_scheme: ColorScheme, fmt: ColorFormat) -> str` (Private)

Renders Jinja2 template for a format.

**Parameters:**
- `color_scheme` (`ColorScheme`): Color scheme data
- `fmt` (`ColorFormat`): Format to render

**Returns:** Rendered template content as string

**Raises:**
- `TemplateRenderError` - Template not found or rendering fails

**Template Name:** `colors.{fmt.value}.j2`

**Template Context:** (7 variables)

| Variable | Type | Description |
|----------|------|-------------|
| `source_image` | `str` | Source image path (stringified) |
| `backend` | `str` | Backend name ("custom", "pywal", "wallust") |
| `generated_at` | `str` | ISO 8601 timestamp |
| `background` | `Color` | Background color object (has .hex, .rgb, .hsl) |
| `foreground` | `Color` | Foreground color object |
| `cursor` | `Color` | Cursor color object |
| `colors` | `list[Color]` | List of 16 terminal colors |

**Template Access:**
```jinja2
{# String variables #}
{{ source_image }}  -> "/path/to/image.jpg"
{{ backend }}       -> "custom"
{{ generated_at }}  -> "2024-02-03T14:30:45.123456"

{# Color object properties #}
{{ background.hex }}  -> "#1A1A1A"
{{ background.rgb }}  -> (26, 26, 26)
{{ background.hsl }}  -> (0.0, 0.0, 0.05) or null

{# Loop through colors #}
{% for color in colors %}
  {{ color.hex }}    -> "#000000", "#FF0000", etc.
  {{ color.rgb }}    -> (0, 0, 0), (255, 0, 0), etc.
{% endfor %}

{# Index specific colors #}
{{ colors[0].hex }}   -> Black (index 0)
{{ colors[1].hex }}   -> Red (index 1)
{{ colors[15].hex }}  -> White (index 15)
```

**Jinja2 Configuration:**
- `loader`: FileSystemLoader from template directory
- `undefined`: StrictUndefined (undefined variables cause errors)
- `trim_blocks`: True (removes block tags from output)
- `lstrip_blocks`: True (removes whitespace before blocks)
- `autoescape`: False (disabled to preserve color formats like `#FF0000`)

**Example:**
```python
from color_scheme.output.manager import OutputManager
from color_scheme.config.enums import ColorFormat

manager = OutputManager(settings)

# Render JSON template
json_content = manager._render_template(scheme, ColorFormat.JSON)
print(json_content)
# {
#   "metadata": { ... },
#   "special": { ... },
#   ...
# }
```

---

### `_convert_to_escape_sequences(content: str) -> bytes` (Private)

Converts template placeholders to actual terminal escape sequences.

**Parameters:**
- `content` (`str`): Template content with placeholders

**Returns:** Binary content with escape sequences

**Placeholder Conversion:**
- `]` → `\x1b]` (ESC + bracket)
- `\` → `\x1b\` (ESC + backslash)

**Purpose:** The SEQUENCES template uses simple placeholders for readability. This converts them to actual OSC escape sequences that terminals understand.

**Example:**
```python
# Template content
template_output = "]4;0;#000000\\]4;1;#FF0000\\..."

# After conversion
binary = manager._convert_to_escape_sequences(template_output)
# Binary: \x1b]4;0;#000000\x1b\...\x1b]4;1;#FF0000\x1b\...

# When written to file and cat/sourced in terminal:
# Terminal interprets \x1b sequences and sets colors
```

---

### `_write_binary_file(file_path: Path, content: bytes) -> None` (Private)

Writes binary content to file.

**Parameters:**
- `file_path` (`Path`): Path to write to
- `content` (`bytes`): Binary content

**Raises:**
- `OutputWriteError` - Permission denied or I/O error

**Usage:** SEQUENCES format (after escape sequence conversion)

---

### `_write_file(file_path: Path, content: str) -> None` (Private)

Writes text content to file.

**Parameters:**
- `file_path` (`Path`): Path to write to
- `content` (`str`): Text content

**Raises:**
- `OutputWriteError` - Permission denied or I/O error

**Encoding:** UTF-8

**Usage:** All formats except SEQUENCES

---

## Usage Patterns

### Basic Usage

```python
from color_scheme.output.manager import OutputManager
from color_scheme.config.enums import ColorFormat
from pathlib import Path

# Initialize
settings = AppConfig()
manager = OutputManager(settings)

# Write colors
manager.write_outputs(
    color_scheme=scheme,
    output_dir=Path("/output"),
    formats=[ColorFormat.JSON, ColorFormat.SH]
)

# Output files created
# /output/colors.json
# /output/colors.sh
```

### Single Format

```python
# Write just one format
manager.write_outputs(
    color_scheme=scheme,
    output_dir=Path("/output"),
    formats=[ColorFormat.JSON]
)
```

### All Formats

```python
from color_scheme.config.enums import ColorFormat

# Write all 8 formats
all_formats = [
    ColorFormat.JSON,
    ColorFormat.SH,
    ColorFormat.CSS,
    ColorFormat.GTK_CSS,
    ColorFormat.YAML,
    ColorFormat.SEQUENCES,
    ColorFormat.RASI,
    ColorFormat.SCSS
]

manager.write_outputs(
    color_scheme=scheme,
    output_dir=Path("/output"),
    formats=all_formats
)
```

### With Directory Creation

```python
from pathlib import Path

# Directory is created if it doesn't exist
output_dir = Path("/output/subdir/colors")
manager.write_outputs(
    color_scheme=scheme,
    output_dir=output_dir,
    formats=[ColorFormat.JSON]
)
# Creates: /output/subdir/colors/
```

### Accessing Output Files

```python
# After writing
manager.write_outputs(color_scheme=scheme, output_dir=Path("/out"), formats=[...])

# ColorScheme.output_files is populated
for fmt, path in scheme.output_files.items():
    print(f"{fmt}: {path}")
    assert path.exists()  # File has been written
```

---

## Template Directory Configuration

The template directory is read from `AppConfig`:

```python
# In AppConfig
settings.templates.directory

# Usually points to:
# - Relative: "../templates/" (resolved relative to package root)
# - Or absolute: "/path/to/templates"
```

**Template Files Expected:**
```
templates/
  colors.json.j2
  colors.sh.j2
  colors.css.j2
  colors.gtk.css.j2
  colors.yaml.j2
  colors.sequences.j2
  colors.rasi.j2
  colors.scss.j2
```

---

## Error Handling

### TemplateRenderError

Raised when template rendering fails.

```python
from color_scheme.core.exceptions import TemplateRenderError

try:
    manager.write_outputs(scheme, output_dir, [ColorFormat.JSON])
except TemplateRenderError as e:
    print(f"Template: {e.template_name}")
    print(f"Reason: {e.reason}")
```

**Causes:**
- Template file not found
- Undefined variable in template (StrictUndefined)
- Jinja2 rendering error

### OutputWriteError

Raised when file writing fails.

```python
from color_scheme.core.exceptions import OutputWriteError

try:
    manager.write_outputs(scheme, Path("/read-only"), [ColorFormat.JSON])
except OutputWriteError as e:
    print(f"File: {e.file_path}")
    print(f"Reason: {e.reason}")
```

**Causes:**
- Permission denied
- Directory doesn't exist (and can't be created)
- Disk full
- Invalid path

---

## Jinja2 Configuration Details

### Why `autoescape=False`

The OutputManager disables Jinja2's autoescape feature because:

1. We generate config files (CSS, JSON, YAML), not HTML
2. Hex colors like `#FF0000` would be escaped to `&#35;FF0000` (broken)
3. Security is not a concern (templates are in source code, not user input)

**Comment in code:**
```python
# NOTE: Autoescape disabled - we generate config files (CSS/JSON/YAML), not HTML.
# Enabling autoescape would corrupt hex colors: #FF0000 → &#35;FF0000
```

### Why `StrictUndefined`

- Prevents typos in templates from silently passing
- Any undefined variable raises an error
- Better for catching template bugs early

### Why `trim_blocks` and `lstrip_blocks`

- `trim_blocks=True` - Removes the line with block tags
- `lstrip_blocks=True` - Removes whitespace before blocks
- Results in cleaner output formatting

---

## Testing

See `packages/core/tests/integration/test_all_templates.py` for usage examples:

```python
from color_scheme.output.manager import OutputManager
from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    manager = OutputManager(settings)

    # Write outputs
    manager.write_outputs(
        color_scheme=scheme,
        output_dir=Path(tmpdir),
        formats=[ColorFormat.JSON, ColorFormat.SH]
    )

    # Verify files exist
    assert (Path(tmpdir) / "colors.json").exists()
    assert (Path(tmpdir) / "colors.sh").exists()
```

---

## Related Documentation

- [Core Types](types.md) - ColorScheme and Color classes
- [Template Variables](../templates/variables.md) - Available template variables
- [Format Reference](../templates/format-reference.md) - Each format's structure
- [CLI Commands](../cli/core-commands.md) - Using OutputManager from CLI
