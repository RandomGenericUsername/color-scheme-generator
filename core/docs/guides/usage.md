# Usage Guide

Complete guide to using `colorscheme-gen`.

---

## Basic Usage

```bash
cd core
uv run colorscheme-gen generate /path/to/image.png
```

---

## Commands

### generate

Generate a color scheme from an image.

```bash
uv run colorscheme-gen generate IMAGE [OPTIONS]
```

**Arguments:**

- `IMAGE` - Path to the source image (required)

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir PATH` | Output directory | `~/.config/color-scheme/output` |
| `--backend NAME` | Backend to use | `pywal` |
| `--formats LIST` | Output formats | `json sh css yaml` |
| `--saturation FLOAT` | Saturation adjustment (0.0-2.0) | `1.0` |
| `--template-dir PATH` | Custom templates directory | Built-in |
| `--pywal-algorithm NAME` | pywal algorithm | `wal` |
| `--wallust-backend NAME` | wallust backend type | `resized` |

### show

Display a color scheme from a JSON file.

```bash
uv run colorscheme-gen show /path/to/colors.json
```

---

## Backend Options

### pywal

```bash
uv run colorscheme-gen generate image.png --backend pywal
```

Algorithms: `wal`, `colorz`, `colorthief`, `haishoku`, `schemer2`

```bash
uv run colorscheme-gen generate image.png --pywal-algorithm colorz
```

### wallust

```bash
uv run colorscheme-gen generate image.png --backend wallust
```

Backend types: `resized`, `full`, `thumb`, `fastresize`, `wal`

```bash
uv run colorscheme-gen generate image.png --wallust-backend full
```

### custom

```bash
uv run colorscheme-gen generate image.png --backend custom
```

Uses built-in k-means clustering algorithm.

---

## Output Formats

Specify which formats to generate:

```bash
uv run colorscheme-gen generate image.png --formats json css sh
```

Available formats: `json`, `sh`, `css`, `gtk.css`, `yaml`, `toml`, `sequences`, `rasi`

---

## Saturation Adjustment

Control color saturation:

```bash
# Grayscale
uv run colorscheme-gen generate image.png --saturation 0.0

# Original
uv run colorscheme-gen generate image.png --saturation 1.0

# Boosted
uv run colorscheme-gen generate image.png --saturation 1.5
```

---

## Custom Templates

Use custom template directory:

```bash
uv run colorscheme-gen generate image.png --template-dir ~/my-templates
```

See [Templates Guide](templates.md) for creating templates.

