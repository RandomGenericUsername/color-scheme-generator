# Templates Guide

Using custom templates with `color-scheme`.

---

## Overview

Templates are processed by the core tool inside the container. The orchestrator passes template options through to the core tool.

---

## Using Custom Templates

1. Create your template directory locally
2. It will be mounted into the container
3. The core tool processes templates

```bash
uv run color-scheme generate image.png --template-dir ~/my-templates
```

---

## Template Format

Templates use Jinja2 syntax. See the [Core Tool Templates Guide](../../../core/docs/guides/templates.md) for full details.

### Example Template

```bash
# Create template directory
mkdir -p ~/my-templates

# Create a template
cat > ~/my-templates/dunst.conf << 'EOF'
[global]
    frame_color = "{{ colors.color4 }}"
    
[urgency_normal]
    background = "{{ special.background }}"
    foreground = "{{ special.foreground }}"
EOF
```

### Use Template

```bash
uv run color-scheme generate wallpaper.png --template-dir ~/my-templates
```

Output appears in `~/.config/color-scheme/output/dunst.conf`.

---

## Available Variables

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
        ...
        "color15": "#c0caf5"
    }
}
```

---

## For More Information

See the full [Core Tool Templates Guide](../../../core/docs/guides/templates.md).

