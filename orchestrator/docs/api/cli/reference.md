# CLI Reference

Complete command-line reference for `color-scheme`.

---

## Synopsis

```bash
color-scheme [OPTIONS] COMMAND [ARGS]...
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show version |
| `--verbose`, `-v` | Verbose output |
| `--debug`, `-d` | Debug output |

---

## Commands

### generate

Generate a color scheme from an image using a containerized backend.

```bash
color-scheme generate [OPTIONS] IMAGE [PASSTHROUGH_ARGS]...
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `IMAGE` | Yes | Path to source image |
| `PASSTHROUGH_ARGS` | No | Arguments passed to core tool |

**Orchestrator Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output-dir`, `-o` | PATH | `~/.config/color-scheme/output` | Output directory |
| `--backend`, `-b` | STRING | `pywal` | Backend: pywal, wallust |
| `--runtime` | STRING | Auto | Runtime: docker, podman |

**Passthrough Options (to core tool):**

| Option | Type | Description |
|--------|------|-------------|
| `--saturation` | FLOAT | Saturation (0.0-2.0) |
| `--formats` | LIST | Output formats |
| `--pywal-algorithm` | STRING | pywal algorithm |
| `--wallust-backend` | STRING | wallust backend type |

**Examples:**

```bash
# Basic usage
color-scheme generate wallpaper.png

# Custom output directory
color-scheme generate wallpaper.png -o ~/my-colors

# Use wallust backend
color-scheme generate wallpaper.png -b wallust

# Force Podman
color-scheme generate wallpaper.png --runtime podman

# Pass options to core tool
color-scheme generate wallpaper.png --saturation 1.5 --formats json css
```

---

### status

Show system status.

```bash
color-scheme status
```

Shows:
- Detected container runtime
- Available container images
- Configuration values

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Container runtime not found |
| 4 | Container execution failed |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `COLOR_SCHEME_RUNTIME` | Container runtime |
| `COLOR_SCHEME_OUTPUT_DIR` | Output directory |
| `COLOR_SCHEME_VERBOSE` | Enable verbose output |

See [Settings Reference](../../configuration/settings.md) for all variables.

