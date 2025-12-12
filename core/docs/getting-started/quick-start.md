# Quick Start

Generate your first color scheme with `colorscheme-gen`.

---

## Prerequisites

Ensure you have completed [Installation](installation.md).

---

## Generate a Color Scheme

```bash
cd core
uv run colorscheme-gen generate /path/to/your/image.png
```

---

## View Output

Generated files are in `~/.config/color-scheme/output/`:

```bash
ls -la ~/.config/color-scheme/output/
```

Output files:

- `colors.json` - Structured color data
- `colors.sh` - Shell variables
- `colors.css` - CSS custom properties
- `colors.yaml` - YAML format

---

## Common Options

```bash
# Custom output directory
uv run colorscheme-gen generate image.png --output-dir ~/my-colors

# Specific formats
uv run colorscheme-gen generate image.png --formats json css

# Adjust saturation (0.0 to 2.0)
uv run colorscheme-gen generate image.png --saturation 1.5

# Use specific backend algorithm
uv run colorscheme-gen generate image.png --backend pywal --pywal-algorithm colorz
```

---

## View Generated Colors

```bash
uv run colorscheme-gen show ~/.config/color-scheme/output/colors.json
```

---

## Example Output

`colors.json`:

```json
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

## Next Steps

- [Usage Guide](../guides/usage.md) - Detailed usage
- [Configuration](../configuration/) - Customize settings
- [Examples](../examples/) - More examples

