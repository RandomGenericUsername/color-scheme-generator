# Backend Configuration

Configure different color extraction backends.

---

## Available Backends

| Backend | Description | Requirements |
|---------|-------------|--------------|
| `pywal` | pywal library | `uv sync --extra pywal` |
| `wallust` | wallust tool | wallust installed |
| `custom` | Built-in k-means | None |

---

## pywal Backend

### Configuration

```toml
[backends.pywal]
backend_algorithm = "wal"
```

### Algorithms

| Algorithm | Description |
|-----------|-------------|
| `wal` | Default pywal algorithm |
| `colorz` | colorz-based extraction |
| `colorthief` | Color Thief algorithm |
| `haishoku` | Haishoku algorithm |
| `schemer2` | Schemer2 algorithm |

### CLI Usage

```bash
uv run colorscheme-gen generate image.png --backend pywal --pywal-algorithm colorz
```

---

## wallust Backend

### Configuration

```toml
[backends.wallust]
backend_type = "resized"
```

### Backend Types

| Type | Description |
|------|-------------|
| `resized` | Resize image before processing (default) |
| `full` | Use full resolution |
| `thumb` | Use thumbnail |
| `fastresize` | Fast resize algorithm |
| `wal` | pywal-compatible mode |

### CLI Usage

```bash
uv run colorscheme-gen generate image.png --backend wallust --wallust-backend full
```

---

## custom Backend

### Configuration

```toml
[backends.custom]
algorithm = "kmeans"
n_clusters = 16
```

### Options

| Option | Values | Default |
|--------|--------|---------|
| `algorithm` | `kmeans`, `minibatch` | `kmeans` |
| `n_clusters` | 8-256 | 16 |

### CLI Usage

```bash
uv run colorscheme-gen generate image.png --backend custom
```

---

## Backend Selection Priority

1. CLI `--backend` flag
2. Environment variable `COLORSCHEME_GENERATION__DEFAULT_BACKEND`
3. Config file `[generation] default_backend`
4. Default: `pywal`

---

## Auto Backend

When `default_backend = "auto"`:

1. Try wallust (if installed)
2. Try pywal (if installed)
3. Fall back to custom

