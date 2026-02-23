# Makefile Reference

Complete reference for all Makefile commands in the color-scheme project.

## Overview

The Makefile provides a unified interface for development, testing, and CI/CD tasks across all packages in the monorepo.

```bash
# See all available commands
make help
```

---

## Setup Commands

### `make dev`

Set up complete development environment.

```bash
make dev
```

**Actions**:
- Installs uv if not present
- Installs dependencies for all packages
- Sets up pre-commit hooks

### `make install-deps`

Install dependencies for all packages.

```bash
make install-deps
```

### `make install-core`

Install core package only.

```bash
make install-core
```

### `make install-settings`

Install settings package only.

```bash
make install-settings
```

### `make install-orchestrator`

Install orchestrator package only.

```bash
make install-orchestrator
```

---

## Code Quality Commands

### `make lint`

Run linting on all packages.

```bash
make lint
```

**Runs**: ruff, black (check), isort (check), mypy

### `make lint-core`

Lint core package only.

```bash
make lint-core
```

### `make lint-settings`

Lint settings package only.

```bash
make lint-settings
```

### `make lint-orchestrator`

Lint orchestrator package only.

```bash
make lint-orchestrator
```

### `make format`

Auto-format all code.

```bash
make format
```

**Runs**: black, isort, ruff --fix

### `make format-core`

Format core package only.

```bash
make format-core
```

### `make format-settings`

Format settings package only.

```bash
make format-settings
```

### `make format-orchestrator`

Format orchestrator package only.

```bash
make format-orchestrator
```

---

## Security Commands

### `make security`

Run security scans on all packages.

```bash
make security
```

**Runs**: bandit -r src/

### `make security-core`

Security scan for core package.

```bash
make security-core
```

### `make security-settings`

Security scan for settings package.

```bash
make security-settings
```

### `make security-orchestrator`

Security scan for orchestrator package.

```bash
make security-orchestrator
```

---

## Testing Commands

### `make test-all`

Run comprehensive test suite across all packages.

```bash
make test-all
```

**Executes**: `tools/test-all-commands.sh`

### `make test-core`

Run unit tests for core package with coverage.

```bash
make test-core
```

**Coverage requirement**: 95%+

### `make test-settings`

Run unit tests for settings package.

```bash
make test-settings
```

### `make test-orchestrator`

Run unit tests for orchestrator package.

```bash
make test-orchestrator
```

---

## Build Commands

### `make build`

Build all packages.

```bash
make build
```

### `make build-core`

Build core package only.

```bash
make build-core
```

### `make build-settings`

Build settings package only.

```bash
make build-settings
```

### `make build-orchestrator`

Build orchestrator package only.

```bash
make build-orchestrator
```

---

## CI/CD Commands

### `make pipeline`

Validate entire CI pipeline locally.

```bash
make pipeline
```

**Simulates GitHub Actions workflow**:
1. Linting check
2. Security scan
3. Test suite with 95%+ coverage requirement

**Use before pushing** to ensure CI won't fail.

---

## Cleanup Commands

### `make clean`

Remove all build artifacts and caches.

```bash
make clean
```

**Removes**:
- `__pycache__/` directories
- `.pytest_cache/`
- `dist/`
- `*.egg-info/`
- `.coverage`
- `htmlcov/`
- `.mypy_cache/`
- `.ruff_cache/`

---

## Recommended Workflows

### Before Pushing to Remote

```bash
make clean          # Clean artifacts
make dev            # Install dependencies
make format         # Auto-format code
make pipeline       # Full validation
```

### Continuous Development

```bash
make dev            # Set up once
make format         # Format changes
make test-core      # Test changes
make lint           # Check quality
```

### Before Creating a PR

```bash
make pipeline       # Full pipeline validation
# If successful, safe to push
```

### Package-Specific Development

```bash
# Core only
make format-core
make test-core
make lint-core

# Settings only
make format-settings
make test-settings
make lint-settings
```

---

## Environment Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Package Manager | uv |
| Test Framework | pytest + xdist |
| Linters | ruff, black, isort, mypy |
| Security | bandit |

---

## GitHub Actions Integration

`make pipeline` runs the same checks as GitHub Actions CI:

| Check | Make Command | CI Step |
|-------|--------------|---------|
| Linting | `make lint` | Lint job |
| Security | `make security` | Security job |
| Tests | `make test-core` | Test job |
| Coverage | Included in tests | Coverage check |

If `make pipeline` passes locally, your code will pass CI.

---

## Troubleshooting

### Command Not Found

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### Tests Fail Due to Missing Dependencies

```bash
make clean
make dev
```

### Pipeline Validation Fails

```bash
# Format and fix automatically
make format

# Run linter with fixes
make lint-core

# Check pipeline again
make pipeline
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `make dev` | Full development setup |
| `make format` | Auto-format all code |
| `make lint` | Check code quality |
| `make test-core` | Test core package |
| `make test-all` | Test all packages |
| `make security` | Security scan |
| `make pipeline` | Full CI validation |
| `make clean` | Remove build artifacts |

---

## Related Documentation

- [How to Contribute](../how-to/contribute.md) - Contribution workflow
- [How to Run Tests](../how-to/run-tests.md) - Testing guide
- [How to Set Up Pre-commit](../how-to/setup-pre-commit.md) - Pre-commit hooks
