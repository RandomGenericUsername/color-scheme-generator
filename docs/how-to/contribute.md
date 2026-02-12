# How to Contribute

Step-by-step guide for contributing code, documentation, and fixes to color-scheme.

## Overview

This guide covers the complete contribution workflow:

1. [Set up your environment](#prerequisites)
2. [Create a feature branch](#create-a-feature-branch)
3. [Make changes](#make-changes)
4. [Write tests](#write-tests)
5. [Run verification](#run-verification)
6. [Commit and push](#commit-changes)
7. [Create a pull request](#create-pull-request)

---

## Prerequisites

Before contributing, ensure you have:

- Development environment set up → [Developer Setup Tutorial](../tutorials/developer-setup.md)
- Git configured with your GitHub account
- Understanding of the [project architecture](../explanations/architecture.md)

---

## Create a Feature Branch

Always work on a dedicated branch, never directly on `develop` or `main`.

### Branch Naming Convention

```bash
git checkout develop
git pull origin develop
git checkout -b <type>/<package>/<description>
```

| Type | Use Case | Example |
|------|----------|---------|
| `feature` | New functionality | `feature/core/add-wallust-backend` |
| `bugfix` | Bug fixes | `bugfix/core/fix-color-parsing` |
| `docs` | Documentation only | `docs/update-api-reference` |
| `refactor` | Code improvements | `refactor/core/simplify-config` |
| `test` | Test additions | `test/core/add-backend-tests` |

### Example

```bash
git checkout develop
git pull
git checkout -b feature/core/improve-color-extraction
```

---

## Make Changes

### Development Principles

Follow these principles when writing code:

| Principle | Description |
|-----------|-------------|
| **YAGNI** | Only implement what's needed now |
| **DRY** | Don't repeat yourself |
| **TDD** | Write tests first when possible |
| **Type Hints** | Add types for public APIs |

### Code Style

The project uses automated formatting:

```bash
cd packages/core

# Format code
uv run black .
uv run isort .

# Fix linting issues
uv run ruff check --fix .
```

Pre-commit hooks enforce style automatically on commit.

### Adding New Features

1. **Create the implementation** in the appropriate module
2. **Add tests** for all new code
3. **Update documentation** if adding public APIs
4. **Add docstrings** to public functions/classes

Example structure for a new backend:

```python
# packages/core/src/color_scheme/backends/new_backend.py

"""New color extraction backend.

This module provides color extraction using NewAlgorithm.
"""

from pathlib import Path
from color_scheme.types import ColorScheme, BackendProtocol


class NewBackend(BackendProtocol):
    """Extract colors using NewAlgorithm.

    Example:
        >>> backend = NewBackend()
        >>> colors = backend.extract(Path("image.png"))
    """

    def extract(self, image: Path) -> ColorScheme:
        """Extract color scheme from image.

        Args:
            image: Path to the source image.

        Returns:
            Extracted color scheme with 16 colors.

        Raises:
            BackendError: If extraction fails.
        """
        # Implementation
        ...
```

---

## Write Tests

All code must have tests. Target 95%+ coverage.

### Test Location

```
packages/core/tests/
├── unit/           # Fast, isolated tests
│   └── test_new_backend.py
└── integration/    # End-to-end tests
    └── test_generate.py
```

### Test Structure

Use the Arrange-Act-Assert pattern:

```python
# packages/core/tests/unit/test_new_backend.py

import pytest
from pathlib import Path
from color_scheme.backends.new_backend import NewBackend


class TestNewBackend:
    """Tests for NewBackend."""

    def test_extract_returns_16_colors(self, sample_image):
        """Test that extraction returns exactly 16 colors."""
        # Arrange
        backend = NewBackend()

        # Act
        result = backend.extract(sample_image)

        # Assert
        assert len(result.colors) == 16

    def test_extract_invalid_image_raises_error(self):
        """Test that invalid image raises BackendError."""
        # Arrange
        backend = NewBackend()
        invalid_path = Path("nonexistent.png")

        # Act & Assert
        with pytest.raises(BackendError, match="not found"):
            backend.extract(invalid_path)
```

### Run Tests

```bash
cd packages/core

# Run all tests
uv run pytest

# Run specific file
uv run pytest tests/unit/test_new_backend.py -v

# Check coverage
uv run pytest --cov=src/color_scheme --cov-report=term
```

See [How to Run Tests](run-tests.md) for detailed testing guide.

---

## Run Verification

Before committing, verify your changes pass all checks.

### Quick Check

```bash
cd packages/core

# Format
uv run black .
uv run isort .

# Lint
uv run ruff check .

# Type check
uv run mypy src/

# Test
uv run pytest --cov=src/color_scheme --cov-fail-under=95
```

### Full Pipeline

From repository root:

```bash
make pipeline
```

This runs the same checks as CI:
- ✅ Linting (ruff, black, isort, mypy)
- ✅ Security scan (bandit)
- ✅ Tests with coverage (95% minimum)

---

## Commit Changes

### Conventional Commits

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Use |
|------|-----|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding tests |
| `refactor` | Code change that doesn't fix bug or add feature |
| `perf` | Performance improvement |
| `chore` | Maintenance tasks |
| `ci` | CI/CD changes |

### Examples

```bash
# Feature
git commit -m "feat(core): add wallust backend support

Implement color extraction using wallust binary.
Supports all wallust color schemes.

Closes #42"

# Bug fix
git commit -m "fix(core): handle missing image gracefully

Return proper error message instead of stack trace
when image file doesn't exist."

# Documentation
git commit -m "docs: update API reference for backends"
```

### Stage and Commit

```bash
git add -A
git commit -m "feat(core): your feature description"
```

Pre-commit hooks run automatically. If they fail:

1. Review the error messages
2. Fix the issues (many are auto-fixed)
3. Stage changes again: `git add -A`
4. Retry commit

---

## Create Pull Request

### Push Your Branch

```bash
git push origin feature/core/your-feature
```

### Open PR on GitHub

1. Navigate to the repository on GitHub
2. Click "Compare & pull request" for your branch
3. Fill out the PR template completely

### PR Checklist

Before submitting, verify:

- [ ] Branch name follows convention
- [ ] All commits use Conventional Commits format
- [ ] All tests pass locally
- [ ] Coverage is ≥95%
- [ ] Documentation updated (if needed)
- [ ] `make pipeline` passes

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Added X
- Fixed Y
- Updated Z

## Testing
How to test these changes:
1. Run `uv run pytest tests/unit/test_x.py`
2. ...

## Related Issues
Closes #123
```

### After Submitting

1. Wait for CI checks to pass
2. Address any review comments
3. Once approved, merge your PR

---

## Updating Documentation

When changes affect user-facing behavior:

### Update Relevant Docs

| Change Type | Documentation to Update |
|-------------|------------------------|
| New CLI command | `docs/reference/cli/core-commands.md` |
| New backend | `docs/reference/backends/` |
| Configuration change | `docs/reference/configuration/` |
| New feature | Relevant how-to guide |

### Docstrings

All public APIs need docstrings:

```python
def extract_colors(image: Path, num_colors: int = 16) -> ColorScheme:
    """Extract a color scheme from an image.

    Args:
        image: Path to the source image file.
        num_colors: Number of colors to extract. Defaults to 16.

    Returns:
        ColorScheme containing the extracted colors.

    Raises:
        FileNotFoundError: If the image doesn't exist.
        BackendError: If color extraction fails.

    Example:
        >>> from color_scheme import extract_colors
        >>> scheme = extract_colors(Path("wallpaper.png"))
        >>> print(scheme.background)
        #1a1b26
    """
```

---

## Quick Reference

### Common Commands

```bash
# Create branch
git checkout -b feature/core/name

# Format code
make format-core

# Run tests
make test-core

# Full verification
make pipeline

# Commit
git commit -m "feat(core): description"

# Push
git push origin feature/core/name
```

### Branch → PR Workflow

```
1. git checkout -b feature/core/x  # Create branch
2. # Make changes
3. make format                      # Format
4. make test-core                   # Test
5. git commit -m "feat(core): x"    # Commit
6. git push origin feature/core/x   # Push
7. # Open PR on GitHub
```

---

## Related Documentation

- [Developer Setup Tutorial](../tutorials/developer-setup.md) - Environment setup
- [How to Run Tests](run-tests.md) - Testing guide
- [How to Set Up Pre-commit](setup-pre-commit.md) - Pre-commit hooks
- [Makefile Reference](../reference/makefile.md) - Available make commands
