# Development Pipeline Guide

This guide explains how to use the development pipeline for the color-scheme project.

## Quick Start

### First Time Setup
```bash
make dev
```
This installs all development dependencies and pre-commit hooks.

### Before Committing
```bash
make pipeline
```
This runs the complete validation pipeline (linting, security, tests) just like GitHub Actions will.

---

## Common Workflows

### 🎨 Format Your Code
```bash
make format
```
Auto-formats all code in all packages using Black, isort, and Ruff.

**For a specific package:**
```bash
make format-settings      # or format-core, format-templates, format-orchestrator
```

### 🔍 Check Code Quality
```bash
make lint
```
Checks for formatting issues, linting problems, and type errors in all packages.

**For a specific package:**
```bash
make lint-settings
```

### ✅ Run Tests
```bash
make test-all
```
Runs all tests with coverage reporting.

**For a specific package:**
```bash
make test-settings        # or test-core, test-templates, test-orchestrator
```

### 🔒 Security Check
```bash
make security
```
Runs Bandit security scanner on all packages.

### 🚀 Full Pipeline (Local CI)
```bash
make pipeline
```
Runs the complete pipeline that simulates GitHub Actions:
1. Linting on all packages
2. Security scans
3. Tests with coverage validation

---

## Understanding Error Messages

### When `make format` or `make lint` fails

The Makefile now provides **clear guidance** on what to do:

```
Linting settings package...
Black formatting needed. Run: make format-settings
make: *** [Makefile:66: lint-settings] Error 1
```

**This means:** Run `make format-settings` to fix the formatting issues.

### Common Issues & Solutions

| Error | Solution |
|-------|----------|
| `Black formatting needed` | `make format-<package>` |
| `Ruff found issues` | `make format-<package>` |
| `Import sorting needed` | `make format-<package>` |
| `Type errors found` | Fix manually or ask for help |
| `Security issues detected` | Review with `make security-<package>` |

---

## Pre-commit Hooks

Pre-commit hooks run **automatically** before every commit to catch issues early.

### Install Hooks
```bash
pre-commit install
```

### Run Manually
```bash
pre-commit run --all-files
```

### Hooks Included
- **File checks:** Trailing whitespace, EOF, YAML/JSON/TOML syntax
- **Python formatting:** Black, isort
- **Linting:** Ruff
- **Type checking:** mypy
- **Security:** Bandit
- **Large files:** Detects files >1MB

---

## Development Environment

### Install Dependencies
```bash
make install-deps          # Install all dev dependencies
make install-settings      # Install specific package
make install-core
make install-templates
make install-orchestrator
```

### Clean Build Artifacts
```bash
make clean
```
Removes `__pycache__`, `.pytest_cache`, `.mypy_cache`, build artifacts, etc.

---

## GitHub Actions

Workflows are automatically triggered on push/PR:

### Workflows
- `ci-core.yml` - Runs when core package changes
- `ci-settings.yml` - Runs when settings package changes
- `ci-templates.yml` - Runs when templates package changes
- `ci-orchestrator.yml` - Runs when orchestrator package changes

### What They Do
Each workflow:
1. **Lints** - Runs ruff, black, isort, mypy
2. **Security** - Runs Bandit and uploads report
3. **Tests** - Runs on ubuntu + macos with Python 3.12 & 3.13
   - Reports coverage to Codecov
   - Enforces 95% coverage threshold

### Setup Codecov
Add `CODECOV_TOKEN` secret to GitHub repo settings for coverage reports.

---

## Tools Overview

| Tool | Purpose | Run Via |
|------|---------|---------|
| **Ruff** | Fast linting | `make lint` |
| **Black** | Code formatting | `make format` |
| **isort** | Import sorting | `make format` |
| **mypy** | Type checking | `make lint` |
| **Bandit** | Security scanning | `make security` |
| **pytest** | Unit testing | `make test-all` |
| **pre-commit** | Git hooks | `pre-commit run` |

---

## Typical Development Workflow

```bash
# 1. Make your changes
vim packages/core/src/color_scheme/something.py

# 2. Format code
make format-core

# 3. Check quality
make lint-core

# 4. Run tests
make test-core

# 5. Commit (pre-commit hooks run automatically)
git add packages/core/
git commit -m "feat: describe your changes"

# 6. Before final push, validate full pipeline
make pipeline
```

---

## CLI Tool Usage

The color-scheme orchestrator provides a CLI for generating color schemes:

```bash
# Generate a color scheme from a wallpaper
color-scheme generate --input wallpaper.jpg --output scheme.json

# Use a template
color-scheme generate --input wallpaper.jpg --template drun-colors

# See all options
color-scheme --help
```

For development testing:
```bash
# Run with editable install
pip install -e packages/orchestrator

# Test the CLI
color-scheme --help
```

---

## Troubleshooting

### Issue: "ImportError" when running tests
**Solution:** Make sure dependencies are installed:
```bash
make install-deps
```

### Issue: Pre-commit hook fails with "command not found"
**Solution:** Reinstall pre-commit hooks:
```bash
pre-commit clean
pre-commit install
```

### Issue: Tests fail with "module not found"
**Solution:** Ensure all workspace packages are installed:
```bash
uv sync --dev --all-packages
```

### Issue: Coverage is below 95%
**Solution:** Check which functions aren't covered:
```bash
make test-core  # See uncovered lines in output
# Or view the HTML report
open htmlcov/index.html
```

---

## Architecture Overview

The project is organized as a monorepo with 4 packages:

- **settings** - Shared layered configuration system for all packages
- **templates** - Template discovery and management system
- **core** - Color scheme generation engine with multiple backends
- **orchestrator** - CLI orchestration layer (entry point for users)

Each package has its own tests, configuration, and CI/CD workflow.

---

## Coverage Requirements

All packages must maintain **95% code coverage**:
- `packages/settings` - 95% required
- `packages/templates` - 95% required
- `packages/core` - 95% required
- `packages/orchestrator` - 95% required

Run `make test-all` to check coverage across all packages.

---

## Contributing

1. Create a branch for your feature
2. Make changes and format code: `make format`
3. Run tests: `make test-all`
4. Check the full pipeline: `make pipeline`
5. Commit with clear messages
6. Push and create a pull request

The GitHub Actions workflows will automatically validate all changes.
