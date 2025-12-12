# Prerequisites

System requirements for `colorscheme-gen`.

---

## Required

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Runtime |
| uv | Latest | Package manager |

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
source ~/.bashrc  # or restart terminal
```

---

## Optional (for pywal backend)

If you want to use pywal locally, you need to install it:

```bash
pip install pywal
```

Or install the core tool with pywal support:

```bash
cd core
uv sync --extra pywal
```

---

## Verify Requirements

```bash
python3 --version    # Should be 3.11+
uv --version         # Should show uv version
```

