# Makefile Guide

This document explains the Makefile for the color-scheme project and its available commands.

## Overview

The Makefile provides a unified interface for common development, testing, linting, and deployment tasks across all packages in the monorepo.

## Directory Structure

- `packages/core/` - Core color scheme generation package
- `packages/orchestrator/` - Container orchestration layer
- `packages/settings/` - Shared configuration system
- `tools/` - Utility scripts (contains `test-all-commands.sh`)

## Available Commands

### Setup & Installation

```bash
make dev                    # Set up complete development environment
make install-deps          # Install dependencies for all packages
make install-core          # Install core package only
make install-orchestrator  # Install orchestrator package only
```

### Code Quality

```bash
make lint                   # Run linting on all packages
make lint-core              # Lint core package (ruff, black, isort, mypy)
make lint-settings          # Lint settings package
make lint-orchestrator      # Lint orchestrator package

make format                 # Auto-format all code
make format-core            # Format core package
make format-settings        # Format settings package
make format-orchestrator    # Format orchestrator package
```

### Security

```bash
make security               # Run security scans on all packages
make security-core          # Security scan for core (bandit)
make security-settings      # Security scan for settings
make security-orchestrator  # Security scan for orchestrator
```

### Testing

```bash
make test-all               # Run comprehensive test suite
                            # Executes tools/test-all-commands.sh
make test-core              # Unit tests for core with coverage (95%+ required)
make test-settings          # Unit tests for settings
make test-orchestrator      # Unit tests for orchestrator
```

### Building

```bash
make build                  # Build all packages
make build-core             # Build core package
make build-settings         # Build settings package
make build-orchestrator     # Build orchestrator package
```

### CI/CD Pipeline

```bash
make pipeline               # Validate entire pipeline locally
                            # Simulates GitHub Actions workflow:
                            # - Linting check
                            # - Security scan
                            # - Test suite with 95%+ coverage requirement
```

### Cleanup

```bash
make clean                  # Remove all build artifacts and caches
                            # Cleans __pycache__, .pytest_cache, dist/, etc.
```

## Recommended Workflow

### Before pushing to remote:

```bash
make clean          # Clean artifacts
make dev            # Install dependencies
make format         # Auto-format code
make pipeline       # Full validation (ensures CI won't fail)
```

### For continuous development:

```bash
make dev            # Set up once
make format         # Format changes
make test-core      # Test core changes
make lint           # Check quality
```

### Before creating a PR:

```bash
make pipeline       # Full pipeline validation
                    # If successful, your PR is safe to push
```

## Package-Specific Development

Each package can be developed independently:

```bash
# Working on core only
cd packages/core
uv sync --dev
uv run pytest
uv run black .
uv run ruff check --fix .

# Or use make commands
make format-core
make test-core
make lint-core
```

## GitHub Actions Integration

The `make pipeline` command simulates the exact CI/CD pipeline that runs in GitHub Actions:
- **Linting**: Ruff, Black, isort, mypy
- **Security**: Bandit security scan
- **Testing**: Pytest with coverage requirements (95%+ for core)

If `make pipeline` passes locally, your code will pass the GitHub Actions workflow.

## Environment

- **Python Version**: 3.12+
- **Package Manager**: `uv` (fast Python package manager)
- **Test Framework**: pytest with xdist (parallel execution)
- **Linters**: ruff, black, isort, mypy, bandit

## Troubleshooting

**Issue**: Command not found
```bash
# Install uv if not present
pip install uv
```

**Issue**: Tests fail due to missing dependencies
```bash
make clean
make dev
```

**Issue**: Pipeline validation fails
```bash
# Format and fix automatically
make format

# Run linter with fixes
make lint-core

# Then check pipeline again
make pipeline
```

## Notes

- All commands use the `uv` package manager for consistency
- Each package can be developed independently
- The `tools/test-all-commands.sh` script tests both core CLI and orchestrator CLI
- Coverage requirement: Core package must maintain 95%+ coverage
