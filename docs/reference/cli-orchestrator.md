# Reference: color-scheme CLI (Orchestrator)

**Package:** `color-scheme-orchestrator`
**Entry point:** `color-scheme`
**Source:** `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`

The orchestrator CLI wraps `color-scheme-core` by running backends inside Docker or
Podman containers. Backend dependencies are isolated in container images rather than
installed on the host.

---

## Command summary

| Command | Container? | Purpose |
|---------|-----------|---------|
| `version` | No | Show package version |
| `generate` | Yes | Generate color files via container |
| `show` | No | Display colors (delegates to core CLI on host) |
| `install` | Yes | Build backend container images |
| `uninstall` | Yes | Remove backend container images |

---

## `color-scheme version`

### Synopsis

```bash
color-scheme version
```

Prints the installed version of the `color-scheme-orchestrator` package. No options.

---

## `color-scheme generate`

### Synopsis

```bash
color-scheme generate [OPTIONS] IMAGE_PATH
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `IMAGE_PATH` | Yes | Path to source image file. |

### Options

| Option | Short | Type | Range / Values | Default | Description |
|--------|-------|------|----------------|---------|-------------|
| `--output-dir` | `-o` | Path | Any valid directory | `~/.config/color-scheme/output` | Output directory. |
| `--backend` | `-b` | Enum | `pywal`, `wallust`, `custom` | Auto-detected | Backend to use. |
| `--format` | `-f` | Enum (repeatable) | `json`, `sh`, `css`, `gtk.css`, `yaml`, `sequences`, `rasi`, `scss` | All 8 formats | Output format(s). |
| `--saturation` | `-s` | Float | 0.0 – 2.0 | From settings (default 1.0) | Saturation multiplier. |
| `--dry-run` | `-n` | Flag | — | false | Show plan without running. |

### Description

Runs `color-scheme-core generate` inside a container. The container image for the
selected backend must exist (built via `color-scheme install`).

### Container image names

| Backend | Image name |
|---------|-----------|
| `pywal` | `color-scheme-pywal:latest` |
| `wallust` | `color-scheme-wallust:latest` |
| `custom` | `color-scheme-custom:latest` |

With a configured registry (e.g., `ghcr.io/myorg`), the image name becomes
`ghcr.io/myorg/color-scheme-<backend>:latest`.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | All files generated |
| 1 | Error |

---

## `color-scheme show`

### Synopsis

```bash
color-scheme show [OPTIONS] IMAGE_PATH
```

### Options

Same as `color-scheme-core show`: `--backend` / `-b`, `--saturation` / `-s`,
`--dry-run` / `-n`.

### Description

Delegates directly to `color-scheme-core show` on the host. No container is launched.
Output format is identical to the core `show` command.

---

## `color-scheme install`

### Synopsis

```bash
color-scheme install [OPTIONS] [BACKEND]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `BACKEND` | No | `pywal`, `wallust`, or `custom`. If omitted, all three are installed. |

### Options

| Option | Short | Type | Values | Default | Description |
|--------|-------|------|--------|---------|-------------|
| `--engine` | `-e` | String | `docker`, `podman` | `docker` | Container engine to use for building images. |
| `--dry-run` | `-n` | Flag | — | false | Show build plan without building. |

### Description

Builds a container image for each specified backend using the selected container engine.

When no backend is specified, all three backends (pywal, wallust, custom) are built.

The build command structure per backend:

```
<engine> build -f <dockerfile> -t color-scheme-<backend>:latest <project_root>
```

### Engine validation

The `--engine` value is validated at runtime:

- Accepted: `docker`, `podman` (case-insensitive; stored as lowercase).
- Any other value: exits 1 with a message containing "Invalid engine" and
  "Must be 'docker' or 'podman'".

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | All images built successfully |
| 1 | One or more images failed to build, or invalid engine |

### Examples

```bash
# Install all backends with default engine (docker)
color-scheme install

# Install one backend
color-scheme install wallust

# Install with Podman
color-scheme install --engine podman

# Dry-run: see build plan, no builds run
color-scheme install custom --dry-run
color-scheme install -n
```

---

## `color-scheme uninstall`

### Synopsis

```bash
color-scheme uninstall [OPTIONS] [BACKEND]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `BACKEND` | No | Backend to remove. If omitted, all three are removed. |

### Options

| Option | Short | Type | Values | Default | Description |
|--------|-------|------|--------|---------|-------------|
| `--engine` | `-e` | String | `docker`, `podman` | `docker` | Container engine. |
| `--yes` | `-y` | Flag | — | false | Skip confirmation prompt. |
| `--dry-run` | `-n` | Flag | — | false | Show removal plan without removing anything. Also skips confirmation. |

### Description

Removes container images for the specified backend(s) by running the container engine's
image removal command. Disk space is reclaimed after removal.

Without `--yes` or `--dry-run`, the command prints a confirmation prompt listing the
images to be removed and asks "Are you sure?". `--dry-run` bypasses this prompt and
runs no removal.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | All images removed |
| 1 | One or more images failed to remove |

### Examples

```bash
# Remove all images (with confirmation)
color-scheme uninstall

# Remove one backend, skip confirmation
color-scheme uninstall pywal --yes

# Dry-run: see removal plan, no images removed, no confirmation prompt
color-scheme uninstall custom --dry-run
color-scheme uninstall -n

# Remove using Podman
color-scheme uninstall --engine podman
```

---

## Global behavior

### Help

```bash
color-scheme --help
color-scheme generate --help
color-scheme install --help
color-scheme uninstall --help
```

### Configuration interaction

Layer order same as core CLI: CLI flags > user config > project config > package
defaults.

---

## Verification reference

| BHV | Behavior |
|-----|---------|
| BHV-0023 | `ContainerSettings` accepts only `docker` or `podman` |
| BHV-0024 | Image name format: `color-scheme-<backend>:latest` |
| BHV-0025 | Default engine is docker |
| BHV-0026 | Invalid engine exits 1 with "Invalid engine" message |
| BHV-0027 | No backend arg installs pywal, wallust, and custom |
| BHV-0028 | Build uses `<engine> build -f ... -t ... <context>` |
| BHV-0029 | `install --dry-run` shows "Build Plan", exits 0 |
| BHV-0030 | `uninstall --dry-run` skips confirmation, exits 0 |
| BHV-0034 | Successful build shows "Built successfully" and summary |
| BHV-0035 | Failed build shows "Build failed", exits 1 |
| BHV-0036 | Registry trailing slash is stripped |
