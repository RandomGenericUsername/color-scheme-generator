# Architecture Overview

High-level design of the orchestrator.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     color-scheme CLI                             │
├─────────────────────────────────────────────────────────────────┤
│  CLI Layer (Click)                                              │
│  - Argument parsing                                             │
│  - Runtime detection                                            │
│  - Command dispatch                                             │
├─────────────────────────────────────────────────────────────────┤
│  Orchestrator Layer                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Container  │  │    Volume    │  │   Backend    │          │
│  │   Runner     │  │   Manager    │  │   Selector   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
├─────────────────────────────────────────────────────────────────┤
│  Container Runtime Abstraction                                  │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │      Docker      │  │      Podman      │                    │
│  └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Container (Backend)                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    colorscheme-gen                       │    │
│  │                    (Core Tool)                           │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Components

### CLI Layer

- Built with Click
- Parses orchestrator-specific options
- Detects container runtime
- Passes through core tool options

### Orchestrator Layer

**Container Runner:**
- Manages container lifecycle
- Executes container commands
- Handles container output

**Volume Manager:**
- Mounts image file into container
- Mounts output directory
- Handles path translation

**Backend Selector:**
- Selects appropriate container image
- Validates backend availability

### Runtime Abstraction

- Docker support
- Podman support
- Auto-detection

---

## Container Images

| Image | Contains |
|-------|----------|
| `color-scheme-pywal` | colorscheme-gen + pywal |
| `color-scheme-wallust` | colorscheme-gen + wallust |

---

## Directory Structure

```
orchestrator/
├── src/
│   └── color_scheme/
│       ├── __init__.py
│       ├── cli/              # CLI commands
│       ├── container/        # Container management
│       └── config/           # Configuration
├── docker/
│   ├── Dockerfile.pywal      # pywal image
│   └── Dockerfile.wallust    # wallust image
├── tests/                    # Test suite
├── docs/                     # Documentation
└── pyproject.toml           # Project config
```

