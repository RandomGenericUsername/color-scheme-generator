# Prerequisites

System requirements for `colorscheme-gen`.

---

## Required

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.12+ | Runtime |
| uv | Latest | Package manager (recommended) |

### Python Dependencies

The core tool has the following Python dependencies (installed automatically):

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | >=2.11.9 | Data validation and settings |
| pillow | >=10.0.0 | Image loading and processing |
| jinja2 | >=3.1.6 | Template rendering for output formats |
| dynaconf | >=3.2.0 | Configuration management |
| numpy | >=1.24.0 | Numerical operations for color processing |
| scikit-learn | >=1.3.0 | K-means clustering for custom backend |
| typer | >=0.12.0 | CLI framework |
| rich | >=13.0.0 | Beautiful terminal output and logging |

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
source ~/.bashrc  # or restart terminal
```

---

## Optional (for external backends)

### pywal Backend

If you want to use pywal locally (not in container), install it:

```bash
pip install pywal
```

Or install the core tool with pywal support:

```bash
cd core
uv sync --extra pywal
```

### wallust Backend

If you want to use wallust locally, install it from your package manager or build from source:

```bash
# Arch (AUR)
yay -S wallust

# From source (requires Rust)
cargo install wallust
```

---

## Verify Requirements

```bash
python3 --version    # Should be 3.12+
uv --version         # Should show uv version
```
