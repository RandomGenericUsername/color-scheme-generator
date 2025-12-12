# Quick Start

Generate your first color scheme with `color-scheme`.

---

## Prerequisites

Ensure you have completed [Installation](installation.md).

---

## Generate a Color Scheme

```bash
cd orchestrator
uv run color-scheme generate /path/to/your/image.png
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
uv run color-scheme generate image.png --output-dir ~/my-colors

# Use specific backend
uv run color-scheme generate image.png --backend pywal
uv run color-scheme generate image.png --backend wallust

# Use Podman instead of Docker
uv run color-scheme generate image.png --runtime podman

# Verbose output
uv run color-scheme generate image.png --verbose
```

---

## Pass Options to Core Tool

Arguments after the image are passed to the core tool inside the container:

```bash
# Adjust saturation
uv run color-scheme generate image.png --saturation 1.5

# Specific formats
uv run color-scheme generate image.png --formats json css

# Use specific pywal algorithm
uv run color-scheme generate image.png --pywal-algorithm colorz
```

---

## Check System Status

```bash
uv run color-scheme status
```

Shows:
- Available container runtime
- Built images
- Configuration

---

## Next Steps

- [Usage Guide](../guides/usage.md) - Detailed usage
- [Configuration](../configuration/) - Customize settings
- [Examples](../examples/) - More examples

