# How-to: Install and Manage Backend Container Images

The orchestrator CLI (`color-scheme`) runs color extraction inside Docker or Podman
containers. Use the `install` command to build those images before generating color
schemes.

## Prerequisites

- `color-scheme` (orchestrator package) installed.
- Docker installed (default) or Podman (pass `--engine podman`).
- Docker daemon running, or Podman service available.

---

## Install all backend images

```bash
color-scheme install
```

When no backend argument is given, all three backends are built: `pywal`, `wallust`,
and `custom`. The command runs three separate container builds in sequence.

---

## Install a specific backend

```bash
color-scheme install pywal
color-scheme install wallust
color-scheme install custom
```

---

## Use Podman instead of Docker

The default engine is `docker`. To use Podman:

```bash
color-scheme install --engine podman
# or short form:
color-scheme install -e podman
```

The `--engine` option accepts `docker` or `podman` (case-insensitive). Any other value
causes exit code 1 with a message containing "Invalid engine" and
"Must be 'docker' or 'podman'".

---

## Container images built

Each successful build produces an image tagged as `color-scheme-<backend>:latest`:

| Backend | Image name |
|---------|-----------|
| `pywal` | `color-scheme-pywal:latest` |
| `wallust` | `color-scheme-wallust:latest` |
| `custom` | `color-scheme-custom:latest` |

If an `image_registry` is configured (e.g., `ghcr.io/myorg`), the image name becomes
`ghcr.io/myorg/color-scheme-<backend>:latest`. Trailing slashes in the registry name
are stripped automatically.

---

## Verify images after installation

```bash
# Docker
docker images | grep color-scheme

# Podman
podman images | grep color-scheme
```

---

## Check build output

A successful build for a backend prints:

```
Built successfully
Build Summary
Success:
All backend images built successfully!
```

A failed build (non-zero container engine exit code) prints "Build failed" and the
command exits with code 1.

---

## Preview the build plan without building (dry-run)

```bash
color-scheme install custom --dry-run
```

Shows "DRY-RUN" and "Build Plan" without running any container engine commands.

---

## Uninstall backend images

Remove images to reclaim disk space:

```bash
# Remove all images (prompts for confirmation)
color-scheme uninstall

# Remove a specific backend
color-scheme uninstall pywal

# Skip confirmation
color-scheme uninstall --yes

# Remove using Podman
color-scheme uninstall --engine podman
```

The `--yes` / `-y` flag skips the "Are you sure?" prompt. The `--dry-run` / `-n`
flag shows the removal plan without deleting anything and also skips the confirmation
prompt.

Use the same engine for uninstall as was used for install.

---

## Verification

| Behavior | Expected |
|----------|----------|
| `install` with no backend builds pywal, wallust, and custom | BHV-0027 |
| Default engine is docker when `--engine` is not specified | BHV-0025 |
| `--engine invalid` exits 1 with "Invalid engine" message | BHV-0026 |
| Build command structure: `<engine> build -f <dockerfile> -t <image> <context>` | BHV-0028 |
| Successful build shows "Built successfully" and summary | BHV-0034 |
| Failed build shows "Build failed" and exits 1 | BHV-0035 |
| `install --dry-run` shows "Build Plan", exits 0, no build runs | BHV-0029 |
| `uninstall --dry-run` skips confirmation, exits 0, no removal | BHV-0030 |
