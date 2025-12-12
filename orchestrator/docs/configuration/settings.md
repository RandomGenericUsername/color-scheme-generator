# Settings Reference

Configuration via environment variables and CLI.

---

## Configuration Precedence

```
CLI Arguments  →  Environment Variables  →  Defaults
   (highest)                               (lowest)
```

---

## Directory Configuration

### `output_dir`

| Property | Value |
|----------|-------|
| Default | `~/.config/color-scheme/output` |
| CLI | `--output-dir PATH` |
| Env | `COLOR_SCHEME_OUTPUT_DIR` |

Where generated color schemes are saved.

```bash
# CLI
uv run color-scheme generate image.png --output-dir ~/my-colors

# Environment
export COLOR_SCHEME_OUTPUT_DIR=~/my-colors
```

### `config_dir`

| Property | Value |
|----------|-------|
| Default | `~/.config/color-scheme` |
| CLI | `--config-dir PATH` |
| Env | `COLOR_SCHEME_CONFIG_DIR` |

---

## Runtime Configuration

### `runtime`

| Property | Value |
|----------|-------|
| Default | Auto-detect (Docker → Podman) |
| CLI | `--runtime RUNTIME` |
| Env | `COLOR_SCHEME_RUNTIME` |
| Options | `docker`, `podman` |

```bash
# CLI
uv run color-scheme generate image.png --runtime podman

# Environment
export COLOR_SCHEME_RUNTIME=docker
```

### `runtime_path`

| Property | Value |
|----------|-------|
| Default | Uses PATH |
| Env | `COLOR_SCHEME_RUNTIME_PATH` |

Custom path to runtime binary.

---

## Container Configuration

### `container_timeout`

| Property | Value |
|----------|-------|
| Default | `300` (5 minutes) |
| Env | `COLOR_SCHEME_CONTAINER_TIMEOUT` |

Maximum container execution time in seconds.

### `container_memory_limit`

| Property | Value |
|----------|-------|
| Default | `512m` |
| Env | `COLOR_SCHEME_CONTAINER_MEMORY_LIMIT` |

Memory limit for containers.

---

## Logging Configuration

### `verbose`

| Property | Value |
|----------|-------|
| Default | `false` |
| CLI | `--verbose`, `-v` |
| Env | `COLOR_SCHEME_VERBOSE=true` |

### `debug`

| Property | Value |
|----------|-------|
| Default | `false` |
| CLI | `--debug`, `-d` |
| Env | `COLOR_SCHEME_DEBUG=true` |

---

## Environment Variables Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `COLOR_SCHEME_RUNTIME` | string | auto | Container runtime |
| `COLOR_SCHEME_RUNTIME_PATH` | path | - | Custom runtime path |
| `COLOR_SCHEME_OUTPUT_DIR` | path | `~/.config/color-scheme/output` | Output directory |
| `COLOR_SCHEME_CONFIG_DIR` | path | `~/.config/color-scheme` | Config directory |
| `COLOR_SCHEME_CONTAINER_TIMEOUT` | int | 300 | Timeout (seconds) |
| `COLOR_SCHEME_CONTAINER_MEMORY_LIMIT` | string | 512m | Memory limit |
| `COLOR_SCHEME_VERBOSE` | bool | false | Verbose output |
| `COLOR_SCHEME_DEBUG` | bool | false | Debug output |

---

## Example Configuration

```bash
# ~/.bashrc or ~/.zshrc

export COLOR_SCHEME_RUNTIME=docker
export COLOR_SCHEME_OUTPUT_DIR=~/.config/color-scheme/output
export COLOR_SCHEME_CONTAINER_TIMEOUT=600
export COLOR_SCHEME_CONTAINER_MEMORY_LIMIT=1g
export COLOR_SCHEME_VERBOSE=true
```

