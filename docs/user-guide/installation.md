# Installation Guide

## Core Package (Host Installation)

Install the core package directly on your system:

```bash
pip install color-scheme-core
```

**Requirements**:
- Python 3.12+
- Backend dependencies (install separately):
  - pywal: `pip install pywal`
  - wallust: Install from [wallust releases](https://github.com/dharmx/wallust)
  - custom: Included (no extra dependencies)

## Orchestrator Package (Containerized)

Install the orchestrator for containerized execution:

```bash
pip install color-scheme-orchestrator
```

**Requirements**:
- Python 3.12+
- Docker or Podman
- No backend dependencies needed (run in containers)

After installation, pull backend images:

```bash
color-scheme install pywal
color-scheme install wallust
color-scheme install custom
```

## Development Installation

Clone the repository:

```bash
git clone https://github.com/your-org/color-scheme.git
cd color-scheme
```

Run automated setup:

```bash
./scripts/dev-setup.sh
```

Or manual setup:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup core package
cd packages/core
uv sync --dev

# Setup orchestrator package
cd ../orchestrator
uv sync --dev

# Install pre-commit hooks
pre-commit install
```

## Verification

Verify installation:

```bash
# Check version
color-scheme --version

# Run tests (dev installation)
cd packages/core
uv run pytest
```

## Next Steps

- [Configuration Guide](configuration.md)
- [CLI Reference](cli-reference.md)
- [Backend Documentation](backends.md)
