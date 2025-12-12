# CLI Reference

Complete command-line reference for `colorscheme-gen`.

---

## Synopsis

```bash
colorscheme-gen [OPTIONS] COMMAND [ARGS]...
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show version |

---

## Commands

### generate

Generate a color scheme from an image.

```bash
colorscheme-gen generate [OPTIONS] IMAGE
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `IMAGE` | Yes | Path to source image |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output-dir`, `-o` | PATH | `~/.config/color-scheme/output` | Output directory |
| `--backend`, `-b` | STRING | `pywal` | Backend: pywal, wallust, custom |
| `--formats`, `-f` | LIST | `json sh css yaml` | Output formats |
| `--saturation`, `-s` | FLOAT | `1.0` | Saturation (0.0-2.0) |
| `--template-dir`, `-t` | PATH | Built-in | Custom templates directory |
| `--pywal-algorithm` | STRING | `wal` | pywal algorithm |
| `--wallust-backend` | STRING | `resized` | wallust backend type |

**Examples:**

```bash
# Basic usage
colorscheme-gen generate wallpaper.png

# Custom output directory
colorscheme-gen generate wallpaper.png -o ~/my-colors

# Use wallust with full resolution
colorscheme-gen generate wallpaper.png -b wallust --wallust-backend full

# Generate only JSON and CSS with boosted saturation
colorscheme-gen generate wallpaper.png -f json css -s 1.5
```

---

### show

Display a color scheme from a JSON file.

```bash
colorscheme-gen show [OPTIONS] FILE
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `FILE` | Yes | Path to colors.json file |

**Examples:**

```bash
colorscheme-gen show ~/.config/color-scheme/output/colors.json
```

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `COLORSCHEME_SETTINGS_FILE` | Path to settings.toml |
| `COLORSCHEME_GENERATION__DEFAULT_BACKEND` | Default backend |
| `COLORSCHEME_OUTPUT__DIRECTORY` | Output directory |

See [Settings Reference](../../configuration/settings.md) for all variables.

