# Basic Examples

Simple usage examples for `color-scheme`.

---

## Generate Color Scheme

```bash
cd orchestrator
uv run color-scheme generate ~/Pictures/wallpaper.png
```

---

## Custom Output Directory

```bash
uv run color-scheme generate image.png --output-dir ~/my-colors
```

---

## Different Backends

```bash
# pywal (default)
uv run color-scheme generate image.png --backend pywal

# wallust
uv run color-scheme generate image.png --backend wallust
```

---

## Use Podman Instead of Docker

```bash
uv run color-scheme generate image.png --runtime podman
```

---

## Adjust Saturation

```bash
uv run color-scheme generate image.png --saturation 1.5
```

---

## Specific Formats Only

```bash
uv run color-scheme generate image.png --formats json css
```

---

## Verbose Output

```bash
uv run color-scheme generate image.png --verbose
```

---

## Check System Status

```bash
uv run color-scheme status
```

---

## Use Generated Colors in Shell

```bash
# Source the colors
source ~/.config/color-scheme/output/colors.sh

# Use in scripts
echo "Background: $BACKGROUND"
echo "Foreground: $FOREGROUND"
```

