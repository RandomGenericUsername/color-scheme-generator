# Development Setup

Set up your development environment.

---

## Prerequisites

- Python 3.11+
- uv package manager
- Docker or Podman
- Git

---

## Clone Repository

```bash
git clone <repository-url>
cd color-scheme-generator/orchestrator
```

---

## Install Dependencies

```bash
make install-dev
```

Or with uv:

```bash
uv sync --all-extras --dev
```

---

## Build Container Images

```bash
make docker-build
```

---

## Verify Setup

```bash
# Run tests
make test

# Run linter
make lint

# Run type checker
make type-check
```

---

## Project Structure

```
orchestrator/
├── src/
│   └── color_scheme/
│       ├── __init__.py
│       ├── cli/              # CLI commands
│       ├── container/        # Container management
│       └── config/           # Configuration
├── docker/
│   ├── Dockerfile.pywal
│   └── Dockerfile.wallust
├── tests/                    # Test suite
├── docs/                     # Documentation
├── pyproject.toml           # Project config
└── Makefile                 # Build tasks
```

---

## Development Workflow

1. Create a branch: `git checkout -b feature/my-feature`
2. Make changes
3. Rebuild containers if needed: `make docker-build`
4. Run tests: `make test`
5. Run checks: `make check`
6. Commit changes
7. Push and create PR

