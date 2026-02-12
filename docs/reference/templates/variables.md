# Template Variables Reference

**Scope:** All variables available in Jinja2 templates
**Extracted:** February 2, 2026
**Location:** Template context passed to all templates via `template.render()`

Complete reference for all variables, objects, and properties available when rendering output templates.

---

## Quick Reference

| Variable | Type | Description |
|----------|------|-------------|
| `source_image` | `str` | Path to source image file |
| `backend` | `str` | Name of backend used |
| `generated_at` | `str` | ISO format timestamp of generation |
| `background` | `Color` | Background color object |
| `foreground` | `Color` | Foreground color object |
| `cursor` | `Color` | Cursor color object |
| `colors` | `list[Color]` | Array of 16 terminal colors |

---

## Template Context

### Context Setup in Code

In `packages/core/src/color_scheme/output/manager.py`, the template context is built as:

```python
content = template.render(
    source_image=str(color_scheme.source_image),
    backend=color_scheme.backend,
    generated_at=color_scheme.generated_at.isoformat(),
    background=color_scheme.background,
    foreground=color_scheme.foreground,
    cursor=color_scheme.cursor,
    colors=color_scheme.colors,
)
```

All 7 variables are passed to **every template**.

---

## Variables

### `source_image`

**Type:** `str` (string)
**Description:** Path to the source image file
**Format:** Absolute or relative file path
**Example:** `"/home/user/wallpaper.jpg"`

**Usage in Templates:**

```jinja2
{# JSON #}
"source_image": "{{ source_image }}"

{# Shell #}
# Generated from: {{ source_image }}

{# Comment #}
<!-- Image: {{ source_image }} -->
```

**Availability:** Always present, never empty

---

### `backend`

**Type:** `str` (string)
**Description:** Name of the backend used for color extraction
**Values:** `"pywal"`, `"wallust"`, or `"custom"`
**Example:** `"pywal"`

**Usage in Templates:**

```jinja2
{# JSON #}
"backend": "{{ backend }}"

{# YAML #}
backend: {{ backend }}

{# Comment #}
// Extracted with: {{ backend }}
```

**Availability:** Always present, never empty

---

### `generated_at`

**Type:** `str` (ISO 8601 format)
**Description:** Timestamp when color scheme was generated
**Format:** `YYYY-MM-DDTHH:MM:SS.ssssss` (ISO 8601)
**Example:** `"2024-02-02T14:30:45.123456"`

**Usage in Templates:**

```jinja2
{# JSON #}
"generated_at": "{{ generated_at }}"

{# Shell comment #}
# Generated: {{ generated_at }}

{# CSS comment #}
/* Generated: {{ generated_at }} */
```

**Availability:** Always present

**Parsing Example:**
```python
from datetime import datetime
timestamp = "2024-02-02T14:30:45.123456"
dt = datetime.fromisoformat(timestamp)
```

---

## Color Objects

### `background` Color Object

**Type:** `Color` (Pydantic BaseModel)
**Description:** Background color for terminal/application
**Typically:** Dark color (e.g., black, dark gray)

**Properties:**

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `hex` | `str` | Hexadecimal color code | `"#1A1A1A"` |
| `rgb[0]` | `int` | Red channel (0-255) | `26` |
| `rgb[1]` | `int` | Green channel (0-255) | `26` |
| `rgb[2]` | `int` | Blue channel (0-255) | `26` |
| `hsl` | `tuple[float, float, float] \| None` | HSL values or None | `(0.0, 0.0, 0.102)` |

**Usage in Templates:**

```jinja2
{# Hex color #}
background="{{ background.hex }}"

{# RGB components #}
rgb({{ background.rgb[0] }}, {{ background.rgb[1] }}, {{ background.rgb[2] }})

{# All RGB as tuple #}
[{{ background.rgb[0] }}, {{ background.rgb[1] }}, {{ background.rgb[2] }}]

{# Direct access (if HSL available) #}
{% if background.hsl %}
  hsl({{ background.hsl[0] }}, {{ background.hsl[1] }}, {{ background.hsl[2] }})
{% endif %}
```

**Example Output:**
```
background="#1A1A1A"
rgb(26, 26, 26)
[26, 26, 26]
```

---

### `foreground` Color Object

**Type:** `Color` (Pydantic BaseModel)
**Description:** Foreground color for terminal text
**Typically:** Light color (e.g., white, light gray)

**Properties:** Same as `background` (all Color objects have identical structure)

| Property | Type | Example |
|----------|------|---------|
| `hex` | `str` | `"#E8E8E8"` |
| `rgb[0]` | `int` | `232` |
| `rgb[1]` | `int` | `232` |
| `rgb[2]` | `int` | `232` |
| `hsl` | `tuple[float, float, float] \| None` | `(0.0, 0.0, 0.910)` |

**Usage in Templates:**

```jinja2
{# Hex color #}
foreground="{{ foreground.hex }}"

{# CSS variable #}
--foreground-color: {{ foreground.hex }};

{# Shell export #}
export FOREGROUND="{{ foreground.hex }}"
```

**Example Output:**
```
foreground="#E8E8E8"
--foreground-color: #E8E8E8;
export FOREGROUND="#E8E8E8"
```

---

### `cursor` Color Object

**Type:** `Color` (Pydantic BaseModel)
**Description:** Cursor/highlight color
**Typically:** Accent color (often blue, cyan, or other contrasting color)

**Properties:** Same as `background` and `foreground`

| Property | Type | Example |
|----------|------|---------|
| `hex` | `str` | `"#33FF57"` |
| `rgb[0]` | `int` | `51` |
| `rgb[1]` | `int` | `255` |
| `rgb[2]` | `int` | `87` |
| `hsl` | `tuple[float, float, float] \| None` | `(120.0, 1.0, 0.600)` |

**Usage in Templates:**

```jinja2
{# Hex color #}
cursor="{{ cursor.hex }}"

{# CSS custom property #}
--cursor-color: {{ cursor.hex }};

{# Rofi theme #}
accent: {{ cursor.hex }};
```

**Example Output:**
```
cursor="#33FF57"
--cursor-color: #33FF57;
accent: #33FF57;
```

---

## Terminal Colors Array

### `colors`

**Type:** `list[Color]` (array of Color objects)
**Length:** Exactly 16 elements (ANSI colors 0-15)
**Description:** Standard terminal color palette

| Index | Color Name | Typical Use |
|-------|-----------|------------|
| 0 | Black | Dark background |
| 1 | Red | Errors, warnings |
| 2 | Green | Success, positive |
| 3 | Yellow | Warnings, notices |
| 4 | Blue | Info, hyperlinks |
| 5 | Magenta | Accent, special |
| 6 | Cyan | Accent, special |
| 7 | White | Light text |
| 8 | Bright Black | Gray text |
| 9 | Bright Red | Bright errors |
| 10 | Bright Green | Bright success |
| 11 | Bright Yellow | Bright warnings |
| 12 | Bright Blue | Bright info |
| 13 | Bright Magenta | Bright accent |
| 14 | Bright Cyan | Bright accent |
| 15 | Bright White | Light/bright text |

### Accessing Colors in Templates

#### By Index

```jinja2
{# Access specific color by index #}
color0="{{ colors[0].hex }}"
color1="{{ colors[1].hex }}"
color15="{{ colors[15].hex }}"
```

#### By Loop

```jinja2
{# Iterate over all 16 colors #}
{% for color in colors %}
  color{{ loop.index0 }}="{{ color.hex }}"
{% endfor %}

{# Produces: color0="...", color1="...", ... color15="..." #}
```

#### Color Properties

Each color in the array has the same properties as `background`, `foreground`, and `cursor`:

```jinja2
{# Hex #}
{{ colors[0].hex }}

{# RGB #}
{{ colors[0].rgb[0] }}, {{ colors[0].rgb[1] }}, {{ colors[0].rgb[2] }}

{# All RGB #}
[{{ colors[0].rgb[0] }}, {{ colors[0].rgb[1] }}, {{ colors[0].rgb[2] }}]

{# HSL (if available) #}
{% if colors[0].hsl %}
  {{ colors[0].hsl[0] }}, {{ colors[0].hsl[1] }}, {{ colors[0].hsl[2] }}
{% endif %}
```

### Loop Variables

When iterating with `for color in colors`:

```jinja2
{% for color in colors %}
  {# Loop built-in variables #}
  loop.index      {# 1-based index: 1, 2, 3, ... 16 #}
  loop.index0     {# 0-based index: 0, 1, 2, ... 15 #}
  loop.first      {# true for first item #}
  loop.last       {# true for last item #}
  loop.length     {# always 16 #}
  loop.revindex   {# 16, 15, 14, ... 1 #}
  loop.revindex0  {# 15, 14, 13, ... 0 #}

  {# Color value #}
  color: {{ color.hex }}
{% endfor %}
```

### Example: Color Array Access

```jinja2
{# First color (black) #}
{{ colors[0].hex }}     {# e.g., "#000000" #}

{# Last color (bright white) #}
{{ colors[15].hex }}    {# e.g., "#FFFFFF" #}

{# Red color (index 1) #}
{{ colors[1].hex }}     {# e.g., "#FF0000" #}

{# Green color (index 2) #}
{{ colors[2].hex }}     {# e.g., "#00FF00" #}
```

---

## Color Object Structure

### Complete Color Definition

Each color object (for `background`, `foreground`, `cursor`, and each item in `colors`) is a Pydantic `BaseModel`:

```python
class Color(BaseModel):
    hex: str                              # Pattern: ^#[0-9a-fA-F]{6}$
    rgb: tuple[int, int, int]             # RGB values 0-255
    hsl: tuple[float, float, float] | None  # Optional HSL
```

### Color Value Ranges

| Component | Type | Min | Max | Format |
|-----------|------|-----|-----|--------|
| hex | `str` | n/a | n/a | `#RRGGBB` (6 hex digits) |
| rgb[0] (R) | `int` | 0 | 255 | Decimal |
| rgb[1] (G) | `int` | 0 | 255 | Decimal |
| rgb[2] (B) | `int` | 0 | 255 | Decimal |
| hsl[0] (H) | `float` | 0.0 | 360.0 | Degrees |
| hsl[1] (S) | `float` | 0.0 | 1.0 | 0-1 range |
| hsl[2] (L) | `float` | 0.0 | 1.0 | 0-1 range |

### Color Conversion Examples

```jinja2
{# Hex to RGB string #}
rgb({{ colors[0].rgb[0] }}, {{ colors[0].rgb[1] }}, {{ colors[0].rgb[2] }})

{# Hex to HSL (if available) #}
{% if colors[0].hsl %}
  hsl({{ colors[0].hsl[0]|int }}, {{ (colors[0].hsl[1]*100)|int }}%, {{ (colors[0].hsl[2]*100)|int }}%)
{% endif %}

{# Color name from index #}
{% set color_names = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white',
                      'bright-black', 'bright-red', 'bright-green', 'bright-yellow',
                      'bright-blue', 'bright-magenta', 'bright-cyan', 'bright-white'] %}
{{ color_names[loop.index0] }}: {{ color.hex }}
```

---

## Template Examples

### JSON Template

```jinja2
{
  "metadata": {
    "source_image": "{{ source_image }}",
    "backend": "{{ backend }}",
    "generated_at": "{{ generated_at }}"
  },
  "colors": {
    "background": "{{ background.hex }}",
    "foreground": "{{ foreground.hex }}",
    "cursor": "{{ cursor.hex }}",
    "palette": [
{% for color in colors %}
      "{{ color.hex }}"{{ "," if not loop.last }}
{% endfor %}
    ]
  }
}
```

### Shell Script Template

```jinja2
#!/bin/sh
# Colors extracted from: {{ source_image }}
# Backend: {{ backend }}
# Generated: {{ generated_at }}

background="{{ background.hex }}"
foreground="{{ foreground.hex }}"
cursor="{{ cursor.hex }}"

{% for color in colors -%}
color{{ loop.index0 }}="{{ color.hex }}"
{% endfor %}

export background foreground cursor
{% for i in range(16) -%}
export color{{ i }}
{% endfor %}
```

### CSS Template

```jinja2
/* Generated from: {{ source_image }} */
/* Backend: {{ backend }} */
/* Generated: {{ generated_at }} */

:root {
  --background: {{ background.hex }};
  --foreground: {{ foreground.hex }};
  --cursor: {{ cursor.hex }};

{% for color in colors %}
  --color-{{ loop.index0 }}: {{ color.hex }};
{% endfor %}
}

body {
  background-color: var(--background);
  color: var(--foreground);
}

.cursor {
  background-color: var(--cursor);
}
```

### YAML Template

```jinja2
# Generated from: {{ source_image }}
# Backend: {{ backend }}
# Generated: {{ generated_at }}

colors:
  background: {{ background.hex }}
  foreground: {{ foreground.hex }}
  cursor: {{ cursor.hex }}
  palette:
{% for color in colors %}
    - "{{ color.hex }}"
{% endfor %}
```

---

## Jinja2 Filters and Built-ins

Standard Jinja2 filters and functions are available in templates:

### String Filters

```jinja2
{{ source_image|upper }}        {# Uppercase #}
{{ source_image|lower }}        {# Lowercase #}
{{ source_image|length }}       {# String length #}
{{ backend|replace('a', 'A') }} {# Replace #}
```

### Math/Type Filters

```jinja2
{{ 3.14159|int }}               {# Convert to int: 3 #}
{{ 3|float }}                   {# Convert to float: 3.0 #}
{{ colors|length }}             {# Array length: 16 #}
```

### Loop Variables (in for loops)

```jinja2
{% for color in colors %}
  loop.index      {# 1, 2, ..., 16 #}
  loop.index0     {# 0, 1, ..., 15 #}
  loop.first      {# true for first #}
  loop.last       {# true for last #}
{% endfor %}
```

### Conditionals

```jinja2
{% if background.hsl %}
  Has HSL data
{% else %}
  No HSL data
{% endif %}

{% if loop.first %}
  First color
{% endif %}
```

### Set Variables

```jinja2
{% set my_var = background.hex %}
Color: {{ my_var }}

{% set color_names = ['black', 'red', 'green', ...] %}
Name: {{ color_names[0] }}
```

---

## Variable Availability by Template Format

All 7 variables are available in **every template**:

| Variable | JSON | Shell | CSS | GTK | YAML | Sequences | Rasi | SCSS |
|----------|------|-------|-----|-----|------|-----------|------|------|
| `source_image` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `backend` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `generated_at` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `background` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `foreground` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `cursor` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `colors[16]` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Special Cases

### HSL Availability

The `hsl` property on Color objects is **optional** (`None` possible). Always check before use:

```jinja2
{% if color.hsl %}
  HSL: {{ color.hsl[0] }}, {{ color.hsl[1] }}, {{ color.hsl[2] }}
{% else %}
  No HSL data
{% endif %}
```

### Empty Colors

The `colors` array **always contains exactly 16 elements**. No color is ever None or empty.

```jinja2
{# Safe - always has 16 colors #}
{% for color in colors %}
  {{ color.hex }}
{% endfor %}
```

### Timestamp Format

The `generated_at` is always ISO 8601 format. Parse if needed:

```jinja2
{# Already formatted #}
Generated: {{ generated_at }}

{# Parse with Python/JavaScript if needed in output #}
```

---

## Template Development Tips

### Debug Variables

```jinja2
{# Print all available variables #}
{{ context.keys() }}

{# Pretty-print a value #}
{{ value|pprint }}

{# Check variable type #}
{{ colors[0].__class__.__name__ }}
```

### Iterate with Index

```jinja2
{# Using loop.index0 for 0-based colors #}
{% for color in colors %}
  color{{ loop.index0 }}: {{ color.hex }}
{% endfor %}

{# Using range for explicit numbering #}
{% for i in range(16) %}
  color{{ i }}: {{ colors[i].hex }}
{% endfor %}
```

### Conditional Formatting

```jinja2
{# Add comma except on last item #}
{% for color in colors %}
  "{{ color.hex }}"{{ "," if not loop.last }}
{% endfor %}

{# Different format for first #}
{% for color in colors %}
  {% if loop.first %}first: {% endif %}{{ color.hex }}
{% endfor %}
```

---

## Related Documentation

- [Format Reference](format-reference.md) - Details of each output format
- [CLI Commands](../cli/core-commands.md) - How to generate with templates
- [Output Manager](../api/output-manager.md) - Template rendering code
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Template engine details
