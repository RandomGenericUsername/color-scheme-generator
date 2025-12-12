# Installation

Install `color-scheme` orchestrator.

---

## Quick Install

```bash
cd orchestrator

# Install Python package
make install

# Build container images
make docker-build
```

---

## Step-by-Step

### 1. Install Python Package

```bash
cd orchestrator
uv sync
```

Or with development dependencies:

```bash
uv sync --all-extras --dev
```

### 2. Build Container Images

```bash
make docker-build
```

This builds:
- `color-scheme-pywal:latest`
- `color-scheme-wallust:latest`

### 3. Verify Installation

```bash
uv run color-scheme --help
```

Expected output:

```
Usage: color-scheme [OPTIONS] COMMAND [ARGS]...

  Color Scheme Orchestrator - Run color extraction in containers.

Commands:
  generate  Generate a color scheme from an image.
  status    Show system status.
```

### 4. Verify Images

```bash
docker images | grep color-scheme
```

Expected output:

```
color-scheme-pywal     latest    ...
color-scheme-wallust   latest    ...
```

---

## Next Steps

- [Quick Start](quick-start.md) - Generate your first color scheme

