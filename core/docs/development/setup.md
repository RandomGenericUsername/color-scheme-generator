# Development Setup

Set up your development environment.

---

## Prerequisites

- Python 3.11+
- uv package manager
- Git

---

## Clone Repository

```bash
git clone <repository-url>
cd color-scheme-generator/core
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
core/
├── src/
│   └── colorscheme_generator/
│       ├── __init__.py
│       ├── cli/              # CLI commands
│       ├── core/             # Core logic
│       ├── backends/         # Backend implementations
│       ├── templates/        # Template engine
│       └── output/           # Output handling
├── tests/                    # Test suite
├── docs/                     # Documentation
├── pyproject.toml           # Project config
└── Makefile                 # Build tasks
```

---

## Development Workflow

1. Create a branch: `git checkout -b feature/my-feature`
2. Make changes
3. Run tests: `make test`
4. Run checks: `make check`
5. Commit changes
6. Push and create PR

