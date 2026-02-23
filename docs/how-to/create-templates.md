# How-to: Create Custom Templates

This guide shows how to write your own Jinja2 templates that override the built-in
output formats produced by `color-scheme-core generate`.

## Prerequisites

- `color-scheme-core` installed.
- Basic familiarity with Jinja2 syntax.

---

## How custom templates work

Each output format (`json`, `sh`, `css`, etc.) is rendered from a Jinja2 template
file. By pointing the `COLOR_SCHEME_TEMPLATES` environment variable at a directory
containing your own `.j2` files, you can replace any built-in template with your own
implementation.

**Important:** Custom templates replace existing format implementations — they do not
add new format names. The `--format` / `-f` option still only accepts the 8 built-in
format identifiers (`json`, `sh`, `css`, `gtk.css`, `yaml`, `sequences`, `rasi`,
`scss`). If you want a custom format, create a template file named after one of those
identifiers (e.g. `colors.sh.j2`) and override its rendering.

---

## Template variables

Every template receives the following context:

| Variable | Type | Example value |
|----------|------|---------------|
| `source_image` | `str` | `"/home/user/wallpaper.jpg"` |
| `backend` | `str` | `"custom"`, `"pywal"`, or `"wallust"` |
| `generated_at` | `str` | `"2026-02-23T14:05:00.000000"` |
| `background` | `Color` | Background color object |
| `foreground` | `Color` | Foreground/text color object |
| `cursor` | `Color` | Cursor color object |
| `colors` | `list[Color]` | 16 ANSI palette colors (index 0–15) |

### Color object properties

Each `Color` object has:

| Property | Type | Example |
|----------|------|---------|
| `hex` | `str` | `"#FF5733"` |
| `rgb` | `tuple[int, int, int]` | `(255, 87, 51)` |
| `hsl` | `tuple[float, float, float] \| None` | `(10.0, 1.0, 0.6)` or `None` |

---

## Step-by-step: override the shell output format

### 1. Create a template directory

```bash
mkdir -p ~/.config/color-scheme/templates
```

### 2. Write a template file

Template filename must match the built-in naming scheme: `colors.<format>.j2`.
To override the `sh` format, create `colors.sh.j2`:

```jinja
#!/bin/sh
# Generated from: {{ source_image }}
# Backend: {{ backend }}
# Generated: {{ generated_at }}

# Special colors
background="{{ background.hex }}"
foreground="{{ foreground.hex }}"
cursor="{{ cursor.hex }}"

# ANSI palette (0–15)
{% for color in colors -%}
color{{ loop.index0 }}="{{ color.hex }}"
{% endfor -%}

export background foreground cursor
{% for i in range(16) -%}
export color{{ i }}
{% endfor -%}
```

### 3. Point color-scheme at your template directory

```bash
export COLOR_SCHEME_TEMPLATES=~/.config/color-scheme/templates
color-scheme-core generate wallpaper.jpg -f sh
```

Your `colors.sh.j2` is used instead of the built-in one.

To set this permanently, add the export to your shell init file:

```bash
# ~/.bashrc or ~/.zshrc
export COLOR_SCHEME_TEMPLATES="$HOME/.config/color-scheme/templates"
```

---

## More template examples

### CSS with rgb() values instead of hex

Create `colors.css.j2`:

```jinja
/* Generated from: {{ source_image }} */
:root {
  --background: rgb({{ background.rgb | join(', ') }});
  --foreground: rgb({{ foreground.rgb | join(', ') }});
  --cursor: rgb({{ cursor.rgb | join(', ') }});
{% for color in colors %}
  --color{{ loop.index0 }}: rgb({{ color.rgb | join(', ') }});
{% endfor %}
}
```

### Lua table (e.g. for Neovim)

Create `colors.sh.j2` (repurpose the `sh` slot if you do not use shell variables):

```jinja
-- Generated from: {{ source_image }}
local M = {
  background = "{{ background.hex }}",
  foreground = "{{ foreground.hex }}",
  cursor = "{{ cursor.hex }}",
  colors = {
{% for color in colors -%}
    "{{ color.hex }}",
{% endfor -%}
  },
}
return M
```

### JSON with RGB values added

Create `colors.json.j2`:

```jinja
{
  "source_image": "{{ source_image }}",
  "backend": "{{ backend }}",
  "generated_at": "{{ generated_at }}",
  "background": { "hex": "{{ background.hex }}", "rgb": [{{ background.rgb | join(', ') }}] },
  "foreground": { "hex": "{{ foreground.hex }}", "rgb": [{{ foreground.rgb | join(', ') }}] },
  "cursor": { "hex": "{{ cursor.hex }}", "rgb": [{{ cursor.rgb | join(', ') }}] },
  "colors": [
    {% for color in colors -%}
    { "hex": "{{ color.hex }}", "rgb": [{{ color.rgb | join(', ') }}] }{{ ", " if not loop.last }}
    {% endfor -%}
  ]
}
```

---

## Jinja2 syntax reference

### Variables

```jinja
{{ background.hex }}       {# outputs #1A1A1A #}
{{ colors[0].hex }}        {# first ANSI color #}
{{ colors | length }}      {# outputs 16 #}
```

### Loops

```jinja
{% for color in colors %}
  {{ loop.index0 }}: {{ color.hex }}
{% endfor %}
```

`loop.index0` is 0-based; `loop.index` is 1-based. `loop.first` and `loop.last` are
`True` on the first and last iteration respectively.

### Whitespace control

The `-` modifier strips whitespace:

```jinja
{% for color in colors -%}
color{{ loop.index0 }}="{{ color.hex }}"
{% endfor -%}
```

### Filters

```jinja
{{ text | upper }}              {# UPPERCASE #}
{{ text | lower }}              {# lowercase #}
{{ list | join(', ') }}         {# join list elements #}
{{ value | default('none') }}   {# fallback if value is falsy #}
```

### Comments

```jinja
{# This is a comment — not included in output #}
```

---

## Validate a template before use

```python
from jinja2 import Template

with open("colors.sh.j2") as f:
    Template(f.read())   # raises TemplateSyntaxError if invalid
```

---

## See also

- [Exceptions reference](../reference/exceptions.md) — `TemplateRenderError` and `TemplateRegistryError`
- [Configure Settings](../how-to/configure-settings.md) — `COLOR_SCHEME_TEMPLATES` environment variable
- [Core Types reference](../reference/types.md) — `Color`, `ColorScheme`, and `ColorFormat` definitions
