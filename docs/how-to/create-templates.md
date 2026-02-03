# How to Create Custom Templates

**Purpose:** Create custom output format templates
**Created:** February 3, 2026
**Tested:** Yes - template system verified

Learn how to create custom Jinja2 templates to generate output in your own format.

---

## Template System Overview

Color-scheme uses Jinja2 templates to generate output files. Each format (JSON, CSS, YAML, etc.) is a Jinja2 template. You can create custom templates to generate any format you need.

### How Templates Work

1. You create a `.j2` template file
2. Template receives color data via variables
3. Jinja2 renders the template
4. Output is written to a file

### Built-in Templates

Standard templates are in `templates/` directory:

```
templates/
├── colors.json.j2       # JSON format
├── colors.sh.j2         # Shell script
├── colors.css.j2        # CSS custom properties
├── colors.gtk.css.j2    # GTK color definitions
├── colors.yaml.j2       # YAML structure
├── colors.sequences.j2  # Terminal escape sequences
├── colors.rasi.j2       # Rofi theme syntax
└── colors.scss.j2       # Sass variables
```

---

## Template Variables

Every template receives these variables:

| Variable | Type | Description |
|----------|------|-------------|
| `source_image` | `str` | Path to source image |
| `backend` | `str` | Backend used (custom, pywal, wallust) |
| `generated_at` | `str` | ISO 8601 timestamp |
| `background` | `Color` | Background color object |
| `foreground` | `Color` | Foreground color object |
| `cursor` | `Color` | Cursor color object |
| `colors` | `list[Color]` | All 16 ANSI colors |

### Color Object Properties

Each color has:
- `hex` - Hex color (e.g., "#FF5733")
- `rgb` - Tuple (e.g., (255, 87, 51))
- `hsl` - Tuple (e.g., (10.0, 1.0, 0.5))

**Example:**
```jinja
{{ background.hex }}           # "#02120C"
{{ foreground.rgb }}           # (227, 190, 139)
{{ colors[0].hex }}            # "#02120C"
```

---

## Example: Simple Template

### Shell Script Template

The built-in `colors.sh.j2`:

```jinja
#!/bin/sh
# Color scheme generated from: {{ source_image }}
# Backend: {{ backend }}
# Generated: {{ generated_at }}

# Special colors
background="{{ background.hex }}"
foreground="{{ foreground.hex }}"
cursor="{{ cursor.hex }}"

# Terminal colors (0-15)
{% for color in colors -%}
color{{ loop.index0 }}="{{ color.hex }}"
{% endfor -%}

# Export for use in other scripts
export background foreground cursor
{% for i in range(16) -%}
export color{{ i }}
{% endfor -%}
```

**Generated Output:**

```bash
#!/bin/sh
# Color scheme generated from: /path/to/image.jpg
# Backend: custom
# Generated: 2026-02-03T12:00:38.704598

# Special colors
background="#02120C"
foreground="#E3BE8B"
cursor="#082219"

# Terminal colors (0-15)
color0="#02120C"
color1="#082219"
...
color15="#E3BE8B"

# Export for use in other scripts
export background foreground cursor
export color0 color1 color2 ...
```

---

## Creating Custom Templates

### Step 1: Create Template File

Create a `.j2` file with your custom format. Save in `templates/` directory:

```
templates/custom-format.j2
```

### Step 2: Use Template Variables

Access variables from the template context:

```jinja
{# Access special colors #}
{{ background.hex }}
{{ foreground.hex }}

{# Loop through all 16 colors #}
{% for color in colors %}
  {{ color.hex }}
{% endfor %}

{# Access metadata #}
{{ source_image }}
{{ backend }}
{{ generated_at }}
```

### Step 3: Test Template

Generate using your template:

```bash
export COLOR_SCHEME_TEMPLATES=./templates
color-scheme generate image.jpg
```

---

## Custom Template Examples

### Example 1: Python Dictionary

Create `templates/colors.py.j2`:

```python
# Color scheme: {{ source_image }}
# Backend: {{ backend }}
# Generated: {{ generated_at }}

COLORS = {
    # Special colors
    'background': '{{ background.hex }}',
    'foreground': '{{ foreground.hex }}',
    'cursor': '{{ cursor.hex }}',

    # ANSI colors
    {% for color in colors -%}
    'color{{ loop.index0 }}': '{{ color.hex }}',
    {% endfor -%}
}

# RGB values
RGB = {
    'background': {{ background.rgb }},
    'foreground': {{ foreground.rgb }},
    'cursor': {{ cursor.rgb }},
    'colors': [
        {% for color in colors -%}
        {{ color.rgb }},
        {% endfor -%}
    ]
}
```

**Generated Output:**

```python
# Color scheme: /path/to/image.jpg
# Backend: custom
# Generated: 2026-02-03T12:00:38.704598

COLORS = {
    # Special colors
    'background': '#02120C',
    'foreground': '#E3BE8B',
    'cursor': '#082219',

    # ANSI colors
    'color0': '#02120C',
    'color1': '#082219',
    ...
}
```

### Example 2: Lua Configuration

Create `templates/colors.lua.j2`:

```lua
-- Generated from: {{ source_image }}
-- Backend: {{ backend }}

local colors = {
  background = "{{ background.hex }}",
  foreground = "{{ foreground.hex }}",
  cursor = "{{ cursor.hex }}",

  palette = {
    {% for color in colors -%}
    "{{ color.hex }}",
    {% endfor -%}
  }
}

return colors
```

### Example 3: HTML Color Palette

Create `templates/colors.html.j2`:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Color Palette</title>
  <style>
    body {
      font-family: monospace;
      background: #f0f0f0;
      padding: 20px;
    }
    .palette {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
    }
    .color {
      width: 100%;
      padding: 20px;
      text-align: center;
      color: white;
      font-weight: bold;
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <h1>Color Palette</h1>
  <p>Generated from: {{ source_image }}</p>
  <p>Backend: {{ backend }}</p>
  <div class="palette">
    {% for color in colors -%}
    <div class="color" style="background: {{ color.hex }}">
      {{ color.hex }}
    </div>
    {% endfor -%}
  </div>
</body>
</html>
```

### Example 4: CSV Format

Create `templates/colors.csv.j2`:

```csv
Name,Hex,R,G,B
Background,{{ background.hex }},{{ background.rgb[0] }},{{ background.rgb[1] }},{{ background.rgb[2] }}
Foreground,{{ foreground.hex }},{{ foreground.rgb[0] }},{{ foreground.rgb[1] }},{{ foreground.rgb[2] }}
Cursor,{{ cursor.hex }},{{ cursor.rgb[0] }},{{ cursor.rgb[1] }},{{ cursor.rgb[2] }}
{% for color in colors -%}
Color{{ loop.index0 }},{{ color.hex }},{{ color.rgb[0] }},{{ color.rgb[1] }},{{ color.rgb[2] }}
{% endfor -%}
```

### Example 5: C Header File

Create `templates/colors.h.j2`:

```c
#ifndef COLORS_H
#define COLORS_H

/* Generated from: {{ source_image }} */
/* Backend: {{ backend }} */
/* Generated: {{ generated_at }} */

#define COLOR_BACKGROUND "{{ background.hex }}"
#define COLOR_FOREGROUND "{{ foreground.hex }}"
#define COLOR_CURSOR "{{ cursor.hex }}"

{% for color in colors -%}
#define COLOR{{ loop.index0 }} "{{ color.hex }}"
{% endfor %}

#endif /* COLORS_H */
```

---

## Jinja2 Template Syntax

### Variables

Access variables with double braces:

```jinja
{{ variable_name }}
{{ object.property }}
{{ list[index] }}
```

### Filters

Apply filters to modify values:

```jinja
{{ text | upper }}        # Uppercase
{{ text | lower }}        # Lowercase
{{ list | length }}       # Length
{{ value | default('N/A') }}  # Default value
```

### Loops

Iterate through lists:

```jinja
{% for color in colors %}
  {{ color.hex }}
{% endfor %}

{# Access loop info #}
{% for color in colors %}
  {{ loop.index }}     {# 1-indexed #}
  {{ loop.index0 }}    {# 0-indexed #}
  {{ loop.first }}     {# True on first iteration #}
  {{ loop.last }}      {# True on last iteration #}
{% endfor %}
```

### Conditionals

```jinja
{% if condition %}
  ...
{% elif other_condition %}
  ...
{% else %}
  ...
{% endif %}
```

### Comments

```jinja
{# This is a comment #}
```

---

## Using Custom Templates

### Method 1: Override Template Directory

Set environment variable before generating:

```bash
export COLOR_SCHEME_TEMPLATES=./templates
color-scheme generate image.jpg
```

The application will look for templates in the specified directory.

### Method 2: Place in Project

Copy custom templates to your project's `templates/` directory:

```
project/
├── templates/
│   ├── colors.json.j2
│   ├── colors.sh.j2
│   └── colors.py.j2  # Custom template
└── ...
```

Then:

```bash
cd project
color-scheme generate image.jpg
```

### Method 3: System-Wide

Copy to system templates directory (container use):

```bash
sudo cp templates/colors.py.j2 /templates/colors.py.j2
```

---

## Template Development Tips

### Start Simple

```jinja
{{ source_image }}
{{ backend }}
{{ background.hex }}
```

Test to ensure variables work.

### Use Loops for Repetitive Content

```jinja
{% for color in colors %}
  {{ color.hex }}
{% endfor %}
```

### Check Built-in Templates

Refer to existing templates in `templates/` for patterns:

```bash
cat templates/colors.json.j2
cat templates/colors.css.j2
```

### Test Incrementally

```bash
# Generate and check output
color-scheme generate test.jpg

# View generated file
cat ~/.config/color-scheme/output/colors.py
```

---

## Common Template Patterns

### Iterating with Index

```jinja
{% for color in colors %}
  color{{ loop.index0 }}: {{ color.hex }}
{% endfor %}
```

### Accessing Specific Colors

```jinja
{{ colors[0].hex }}    {# First color (black) #}
{{ colors[1].hex }}    {# Second color (red) #}
{{ colors[15].hex }}   {# Last color (white) #}
```

### Conditional Output

```jinja
{% if backend == "pywal" %}
  Using Pywal algorithm
{% endif %}
```

### Formatted Strings

```jinja
{{ 'Color %d: %s' % (loop.index0, color.hex) }}
```

---

## Troubleshooting Templates

### Template not found

```
Error: Template not found: colors.py.j2
```

**Solution:** Ensure template file exists and path is correct:

```bash
ls -la templates/colors.py.j2
export COLOR_SCHEME_TEMPLATES=/full/path/to/templates
```

### Variable not found

```
Error: 'colors' is undefined
```

**Solution:** Check variable name (case-sensitive):

```jinja
{{ colors }}     {# Correct #}
{{ color }}      {# Wrong #}
{{ Colors }}     {# Wrong - case sensitive #}
```

### Syntax error in template

```
Error: Unexpected character in Jinja2 template
```

**Solution:** Check Jinja2 syntax. Common issues:

- Missing closing `%}`
- Mismatched braces `{{ }}`
- Typo in filter names

---

## Complete Workflow Example

### Create Custom Template

```jinja
{# templates/colors.env.j2 #}
# Environment variables for color scheme
export BG='{{ background.hex }}'
export FG='{{ foreground.hex }}'
export COLORS_0='{{ colors[0].hex }}'
export COLORS_1='{{ colors[1].hex }}'
# ... more colors ...
```

### Generate

```bash
export COLOR_SCHEME_TEMPLATES=./templates
color-scheme generate wallpaper.jpg -f env
```

### Use

```bash
source ~/.config/color-scheme/output/colors.env
echo $BG    # #02120C
echo $FG    # #E3BE8B
```

---

## Related Documentation

- [Format Reference](../reference/templates/format-reference.md) - Built-in formats
- [Template Variables](../reference/templates/variables.md) - Complete variable reference
- [Customize Output](customize-output.md) - Choose which formats to generate
