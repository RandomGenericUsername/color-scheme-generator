# Installation

Install `color-scheme` orchestrator.

---

## Prerequisites

Before installing, ensure you have:

- Python 3.12 or higher
- uv package manager (recommended)
- Docker or Podman container runtime

See [Prerequisites](prerequisites.md) for detailed setup instructions.

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

This installs:
- The core colorscheme-generator tool
- container-manager library for Docker/Podman orchestration
- rich library for beautiful terminal output

Or with development dependencies:

```bash
uv sync --all-extras --dev
```

### 2. Build Container Images

```bash
make docker-build
```

This builds:
- `color-scheme-pywal:latest` - Container with pywal backend
- `color-scheme-wallust:latest` - Container with wallust backend

### 3. Verify Installation

```bash
uv run color-scheme --help
```

Expected output:

```
usage: color-scheme [-h] {install,generate,show,status} ...

Container orchestrator for color-scheme-generator

positional arguments:
  {install,generate,show,status}
                        Command to execute
    install             Install and initialize backends
    generate            Generate a color scheme
    show                Show information
    status              Show system status
```

### 4. Verify Container Images

```bash
docker images | grep color-scheme
```

Expected output:

```
color-scheme-pywal     latest    abc123...   10 minutes ago   500MB
color-scheme-wallust   latest    def456...   10 minutes ago   450MB
```

### 5. Test Generation

```bash
uv run color-scheme generate /path/to/image.png --verbose
```

---

## Troubleshooting

### Container Runtime Not Found

If you see "No container runtime found", ensure Docker or Podman is installed:

```bash
docker --version   # or
podman --version
```

### Permission Denied (Docker)

If you get permission errors with Docker:

```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Image Build Fails

If container image build fails, check:

1. Internet connection (for downloading base images)
2. Docker daemon is running: `sudo systemctl status docker`

---

## Next Steps

- [Quick Start](quick-start.md) - Generate your first color scheme
- [Configuration](../configuration/settings.md) - Customize settings
