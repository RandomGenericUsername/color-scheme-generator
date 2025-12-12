# Templates Guide

Create custom templates for `colorscheme-gen`.

---

## Overview

Templates use Jinja2 syntax to generate custom configuration files from color schemes.

---

## Template Location

**Default:** Built-in templates in the package.

**Custom:** Specify with `--template-dir` or in `settings.toml`:

```toml
[templates]
directory = "~/.config/colorscheme-generator/templates"
```

---

## Available Variables

Templates receive these variables:

```python
{
    "wallpaper": "/path/to/image.png",
    "special": {
        "background": "#1a1b26",
        "foreground": "#c0caf5",
        "cursor": "#c0caf5"
    },
    "colors": {
        "color0": "#1a1b26",
        "color1": "#f7768e",
        "color2": "#9ece6a",
        # ... through color15
    }
}
```

---

## Example Templates

### Shell Variables (`colors.sh`)

```bash
# colors.sh
export WALLPAPER="{{ wallpaper }}"
export BACKGROUND="{{ special.background }}"
export FOREGROUND="{{ special.foreground }}"
{% for name, value in colors.items() %}
export {{ name | upper }}="{{ value }}"
{% endfor %}
```

### CSS Variables (`colors.css`)

```css
:root {
    --background: {{ special.background }};
    --foreground: {{ special.foreground }};
{% for name, value in colors.items() %}
    --{{ name }}: {{ value }};
{% endfor %}
}
```

### Rofi Theme (`colors.rasi`)

```css
* {
    background: {{ special.background }};
    foreground: {{ special.foreground }};
    color0: {{ colors.color0 }};
    color1: {{ colors.color1 }};
}
```

---

## Creating a Template

1. Create template file:

```bash
mkdir -p ~/.config/colorscheme-generator/templates
nano ~/.config/colorscheme-generator/templates/myapp.conf
```

2. Add template content:

```
# MyApp Configuration
background_color = "{{ special.background }}"
text_color = "{{ special.foreground }}"
accent_color = "{{ colors.color1 }}"
```

3. Use the template:

```bash
uv run colorscheme-gen generate image.png \
    --template-dir ~/.config/colorscheme-generator/templates
```

4. Output appears in `~/.config/color-scheme/output/myapp.conf`

---

## Template Tips

- Template filename becomes output filename
- Use `.j2` extension for clarity (optional)
- Jinja2 filters available: `upper`, `lower`, etc.

