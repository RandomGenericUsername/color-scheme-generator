# Prerequisites

System requirements for `color-scheme`.

---

## Required

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Runtime |
| uv | Latest | Package manager |
| Docker or Podman | Latest | Container runtime |

### Install Python

```bash
# Ubuntu/Debian
sudo apt-get install python3.11

# Fedora
sudo dnf install python3.11

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
python3 --version    # Should be 3.11+
uv --version         # Should show uv version
docker --version     # Or podman --version
```

---

## Container Runtime Detection

The orchestrator auto-detects the available runtime:

1. Checks for Docker
2. Falls back to Podman

Override with `--runtime docker` or `--runtime podman`.

