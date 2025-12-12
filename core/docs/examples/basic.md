# Basic Examples

Simple usage examples for `colorscheme-gen`.

---

## Generate Color Scheme

```bash
cd core
uv run colorscheme-gen generate ~/Pictures/wallpaper.png
```

---

## Custom Output Directory

```bash
uv run colorscheme-gen generate image.png --output-dir ~/my-colors
```

---

## Specific Formats Only

```bash
# Only JSON and CSS
uv run colorscheme-gen generate image.png --formats json css

# Only shell variables
uv run colorscheme-gen generate image.png --formats sh
```

---

## Different Backends

```bash
# pywal (default)
uv run colorscheme-gen generate image.png --backend pywal

# wallust
uv run colorscheme-gen generate image.png --backend wallust

# Custom k-means
uv run colorscheme-gen generate image.png --backend custom
```

---

## Adjust Saturation

```bash
# Boost saturation
uv run colorscheme-gen generate image.png --saturation 1.5

# Reduce saturation
uv run colorscheme-gen generate image.png --saturation 0.7

# Grayscale
uv run colorscheme-gen generate image.png --saturation 0.0
```

---

## View Generated Colors

```bash
uv run colorscheme-gen show ~/.config/color-scheme/output/colors.json
```

---

## Use Generated Colors in Shell

```bash
# Source the colors
source ~/.config/color-scheme/output/colors.sh

# Use in scripts
echo "Background: $BACKGROUND"
echo "Foreground: $FOREGROUND"
echo "Accent: $COLOR1"
```

---

## Quick One-Liner

```bash
cd core && uv run colorscheme-gen generate ~/Pictures/wallpaper.png && cat ~/.config/color-scheme/output/colors.json
```

