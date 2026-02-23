# How to Set Up Pre-commit Hooks

Guide to installing and using pre-commit hooks for automated code quality checks.

## Overview

Pre-commit hooks run automatically before each `git commit`, catching issues before they reach CI/CD:

- ✅ Auto-format code (Black, isort)
- ✅ Lint for issues (Ruff)
- ✅ Type check (mypy)
- ✅ Security scan (Bandit)
- ✅ Validate YAML/JSON/TOML

---

## Installation

### Install Pre-commit Framework

```bash
pip install pre-commit
```

### Install Project Hooks

From the repository root:

```bash
pre-commit install
```

Verify installation:

```bash
ls .git/hooks/pre-commit
```

---

## How It Works

### Automatic Execution

Hooks run automatically on every commit:

```bash
git commit -m "feat(core): add feature"
# Hooks run automatically
# ✓ Trailing whitespace fixed
# ✓ Code formatted
# ✓ Imports sorted
# ✓ Linting passed
# ✓ Type checking passed
# Commit succeeds
```

### What Gets Checked

| Hook | Purpose | Auto-fixes |
|------|---------|------------|
| `trailing-whitespace` | Remove trailing spaces | ✅ |
| `end-of-file-fixer` | Ensure newline at EOF | ✅ |
| `check-yaml` | Validate YAML syntax | ❌ |
| `check-json` | Validate JSON syntax | ❌ |
| `check-toml` | Validate TOML syntax | ❌ |
| `black` | Format Python code | ✅ |
| `isort` | Sort imports | ✅ |
| `ruff` | Lint Python code | Partial |
| `mypy` | Type checking | ❌ |
| `bandit` | Security scan | ❌ |

---

## Running Hooks Manually

### All Files

```bash
pre-commit run --all-files
```

### Specific Hook

```bash
pre-commit run black --all-files
pre-commit run ruff --all-files
pre-commit run mypy --all-files
```

### Staged Files Only

```bash
pre-commit run
```

---

## Common Scenarios

### Hooks Fix Files Automatically

When hooks fix files:

```bash
git commit -m "feat: my feature"
# Black reformatted: src/file.py
# isort fixed: src/file.py

# Files were changed - stage them again
git add -A
git commit -m "feat: my feature"
# ✓ All hooks passed
# Commit succeeds
```

### Hooks Fail with Errors

When hooks fail:

```bash
git commit -m "feat: my feature"
# mypy failed: src/file.py:10: error: Missing return type

# Fix the issue
vim src/file.py

# Stage and commit again
git add src/file.py
git commit -m "feat: my feature"
```

### Format All Code Before Committing

Run all formatters at once:

```bash
pre-commit run --all-files
git add -A
git commit -m "style: format codebase"
```

---

## Bypassing Hooks

### Skip Hooks (Emergency Only)

```bash
git commit --no-verify -m "hotfix: emergency fix"
```

**Warning**: Use sparingly. CI will still run these checks.

### Skip Specific Hook

```bash
SKIP=mypy git commit -m "wip: work in progress"
```

---

## Troubleshooting

### Hooks Not Running

Reinstall hooks:

```bash
pre-commit install --force
```

### Hook Fails Unexpectedly

Run manually to see detailed output:

```bash
pre-commit run <hook-name> --all-files -v
```

### Python Version Mismatch

Ensure hooks use correct Python:

```bash
pre-commit clean
pre-commit install
```

### Update Hook Versions

```bash
pre-commit autoupdate
```

### See Installed Hooks

```bash
cat .pre-commit-config.yaml
```

---

## Configuration

Hooks are configured in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.7
    hooks:
      - id: bandit
        args: [-r, src/]
```

---

## Integration with Makefile

Pre-commit complements Makefile commands:

| Task | Pre-commit | Makefile |
|------|------------|----------|
| Format code | Auto on commit | `make format` |
| Lint code | Auto on commit | `make lint` |
| Run tests | Not included | `make test-all` |
| Full pipeline | Optional hook | `make pipeline` |

### Recommended Workflow

```bash
# During development
make format              # Format all code
make test-core           # Run tests

# Before committing
git add -A
git commit -m "..."      # Pre-commit runs automatically

# Before pushing
make pipeline            # Full CI simulation
```

---

## Benefits

| Benefit | Description |
|---------|-------------|
| **Catch issues early** | Before pushing to GitHub |
| **Consistent formatting** | Team-wide code style |
| **Automated fixes** | Less manual work |
| **Faster CI** | Fewer failed builds |
| **Security** | Catch vulnerabilities early |

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pre-commit install` | Install hooks |
| `pre-commit run --all-files` | Run all hooks |
| `pre-commit run black` | Run specific hook |
| `pre-commit autoupdate` | Update hook versions |
| `pre-commit clean` | Clear cache |
| `git commit --no-verify` | Skip hooks (emergency) |

---

## Related Documentation

- [How to Contribute](contribute.md) - Contribution workflow
- [How to Run Tests](run-tests.md) - Testing guide
- [Makefile Reference](../reference/makefile.md) - Make commands
