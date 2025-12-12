# Color Scheme Generator Documentation

**A powerful tool for extracting color schemes from images**

---

## Component Documentation

This project consists of two components, each with its own documentation:

| Component | Command | Documentation |
|-----------|---------|---------------|
| **Core Tool** | `colorscheme-gen` | [core/docs/](../core/docs/) |
| **Orchestrator** | `color-scheme` | [orchestrator/docs/](../orchestrator/docs/) |

---

## Which Tool Should I Use?

| Tool | Use Case |
|------|----------|
| **Core Tool** (`colorscheme-gen`) | Local execution, no containers, development |
| **Orchestrator** (`color-scheme`) | Containerized backends, isolation, production |

### Core Tool

Runs backends directly on your system. Requires backend dependencies (pywal, wallust) installed locally.

```bash
cd core
uv run colorscheme-gen generate /path/to/image.png
```

📖 **Documentation:** [core/docs/](../core/docs/)

### Orchestrator

Runs backends inside Docker/Podman containers. No local dependencies needed.

```bash
cd orchestrator
uv run color-scheme generate /path/to/image.png
```

📖 **Documentation:** [orchestrator/docs/](../orchestrator/docs/)

---

## Quick Start

```bash
# Clone and install
git clone <repository-url>
cd color-scheme-generator
make install

# Build containers (for orchestrator)
make docker-build

# Generate colors
cd orchestrator
uv run color-scheme generate /path/to/wallpaper.png

# Output: ~/.config/color-scheme/output/
```

---

## Project Structure

```
color-scheme-generator/
├── core/                    # Standalone tool
│   ├── docs/                # Core documentation
│   └── src/
├── orchestrator/            # Container orchestrator
│   ├── docs/                # Orchestrator documentation
│   ├── docker/              # Backend Dockerfiles
│   └── src/
└── docs/                    # This index
    ├── README.md            # You are here
    └── DOCUMENTATION_GUIDELINES.md
```

---

## Documentation Guidelines

See [DOCUMENTATION_GUIDELINES.md](DOCUMENTATION_GUIDELINES.md) for information on how documentation is structured and how to contribute.

