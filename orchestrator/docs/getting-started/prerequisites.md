# Prerequisites

System requirements for `color-scheme` orchestrator.

---

## Required

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.12+ | Runtime |
| uv | Latest | Package manager (recommended) |
| Docker or Podman | Latest | Container runtime |

### Python Dependencies

The orchestrator has the following Python dependencies (installed automatically):

| Package | Version | Purpose |
|---------|---------|---------|
| colorscheme-generator | (local) | The core color scheme generator |
| container-manager | Latest | Container orchestration library |
| rich | >=13.0.0 | Beautiful terminal output and logging |

The core tool dependencies are also installed (see core prerequisites).

### Install Python

```bash
# Ubuntu/Debian
sudo apt-get install python3.12

# Fedora
sudo dnf install python3.12

# Arch
sudo pacman -S python
```

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### Install Docker

```bash
# Ubuntu/Debian
sudo apt-get install docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Log out and back in
```

### Or Install Podman

```bash
# Fedora
sudo dnf install podman

# Ubuntu
sudo apt-get install podman
```

---

## Verify Requirements

```bash
python3 --version    # Should be 3.12+
uv --version         # Should show uv version
docker --version     # Or podman --version
```

---

## Container Runtime Detection

The orchestrator auto-detects the available runtime:

1. Checks for Docker first
2. Falls back to Podman if Docker is not available

Override with `--runtime docker` or `--runtime podman`.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COLOR_SCHEME_RUNTIME` | Container runtime (docker/podman) | Auto-detect |
| `COLOR_SCHEME_OUTPUT_DIR` | Output directory for generated files | `~/.local/share/color-scheme/output` |
| `COLOR_SCHEME_CONFIG_DIR` | Configuration directory | `~/.config/color-scheme` |
| `COLOR_SCHEME_VERBOSE` | Enable verbose output | `false` |
| `COLOR_SCHEME_DEBUG` | Enable debug output | `false` |
