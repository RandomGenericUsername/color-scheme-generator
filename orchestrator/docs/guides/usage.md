# Usage Guide

Complete guide to using `color-scheme`.

---

## Basic Usage

```bash
cd orchestrator
uv run color-scheme generate /path/to/image.png
```

---

## Commands

### generate

Generate a color scheme from an image using a containerized backend.

```bash
uv run color-scheme generate IMAGE [OPTIONS]
```

**Arguments:**

- `IMAGE` - Path to the source image (required)

**Orchestrator Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir`, `-o` | Output directory | `~/.config/color-scheme/output` |
| `--backend`, `-b` | Backend: pywal, wallust | `pywal` |
| `--runtime` | Container runtime: docker, podman | Auto-detect |
| `--verbose`, `-v` | Verbose output | Off |
| `--debug`, `-d` | Debug output | Off |

**Passthrough Options (to core tool):**

| Option | Description |
|--------|-------------|
| `--saturation` | Saturation adjustment (0.0-2.0) |
| `--formats` | Output formats |
| `--pywal-algorithm` | pywal algorithm |
| `--wallust-backend` | wallust backend type |

### status

Show system status.

```bash
uv run color-scheme status
```

---

## Backend Selection

```bash
# pywal (default)
uv run color-scheme generate image.png --backend pywal

# wallust
uv run color-scheme generate image.png --backend wallust
```

Each backend runs in its own container image.

---

## Container Runtime

```bash
# Auto-detect (default)
uv run color-scheme generate image.png

# Force Docker
uv run color-scheme generate image.png --runtime docker

# Force Podman
uv run color-scheme generate image.png --runtime podman
```

---

## Passing Options to Core Tool

Options after the image path are passed to the core tool inside the container:

```bash
# Adjust saturation
uv run color-scheme generate image.png --saturation 1.5

# Specific formats
uv run color-scheme generate image.png --formats json css

# pywal algorithm
uv run color-scheme generate image.png --pywal-algorithm colorz

# wallust backend type
uv run color-scheme generate image.png --wallust-backend full
```

See [Core Tool Configuration](../../../core/docs/configuration/settings.md) for all options.

---

## Debugging

```bash
# Verbose output
uv run color-scheme generate image.png --verbose

# Debug output (includes container commands)
uv run color-scheme generate image.png --debug
```

