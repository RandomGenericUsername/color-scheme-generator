# Backend Configuration

Configure container-based backends.

---

## Available Backends

| Backend | Image | Description |
|---------|-------|-------------|
| `pywal` | `color-scheme-pywal:latest` | pywal in container |
| `wallust` | `color-scheme-wallust:latest` | wallust in container |

---

## pywal Backend

### Container Image

Built from `docker/Dockerfile.pywal`.

### Select pywal

```bash
uv run color-scheme generate image.png --backend pywal
```

### pywal Algorithms

Pass algorithm to core tool:

```bash
uv run color-scheme generate image.png --pywal-algorithm colorz
```

Available: `wal`, `colorz`, `colorthief`, `haishoku`, `schemer2`

---

## wallust Backend

### Container Image

Built from `docker/Dockerfile.wallust`.

### Select wallust

```bash
uv run color-scheme generate image.png --backend wallust
```

### wallust Backend Types

Pass backend type to core tool:

```bash
uv run color-scheme generate image.png --wallust-backend full
```

Available: `resized`, `full`, `thumb`, `fastresize`, `wal`

---

## Building Images

```bash
# Build all images
make docker-build

# Build specific image
make docker-build-pywal
make docker-build-wallust
```

---

## Rebuilding Images

If you modify the core tool, rebuild images:

```bash
make docker-build
```

---

## Custom Backend

To create a custom backend:

1. Create `backend.py` in orchestrator directory
2. Run `make docker-build-custom`

The custom backend image uses `docker/Dockerfile.custom`.

