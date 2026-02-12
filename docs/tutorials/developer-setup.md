# Tutorial: Developer Environment Setup

This tutorial walks you through setting up a complete development environment for contributing to color-scheme.

## What You'll Learn

- Installing prerequisites (Python 3.12+, uv, Git)
- Cloning and configuring the repository
- Setting up all packages in development mode
- Verifying your environment works correctly
- Basic development workflow

## Prerequisites

Before starting, you'll need:

- A Unix-like terminal (Linux, macOS, or WSL on Windows)
- Basic Git knowledge
- ~500MB disk space for dependencies

## Time Required

**Quick Setup**: 5 minutes (automated script)
**Manual Setup**: 15-20 minutes

---

## Step 1: Check Prerequisites

### Python 3.12 or Higher

Check your Python version:

```bash
python3 --version
```

**Expected output**: `Python 3.12.x` or higher

If you need to install Python 3.12+:

| Platform | Command |
|----------|---------|
| Ubuntu/Debian | `sudo apt install python3.12` |
| Fedora | `sudo dnf install python3.12` |
| macOS | `brew install python@3.12` |
| Windows | Download from [python.org](https://www.python.org/downloads/) |

### Git

Verify Git is installed:

```bash
git --version
```

Install from [git-scm.com](https://git-scm.com/) if needed.

### curl

Required for uv installation:

```bash
curl --version
```

Most systems have curl pre-installed.

---

## Step 2: Clone the Repository

```bash
git clone https://github.com/your-org/color-scheme.git
cd color-scheme
```

You should see a directory structure like:

```
color-scheme/
├── packages/
│   ├── core/
│   ├── orchestrator/
│   └── settings/
├── templates/
├── docs/
├── Makefile
└── settings.toml
```

---

## Step 3: Quick Setup (Recommended)

The fastest way to get started is the automated setup:

```bash
./scripts/setup-dev.sh
```

The script will:

1. ✅ Check Python 3.12+ is installed
2. ✅ Install uv package manager
3. ✅ Install all package dependencies
4. ✅ Set up pre-commit hooks
5. ✅ Run verification tests

If successful, skip to [Step 6: Verify Installation](#step-6-verify-installation).

If the script fails, continue with manual setup below.

---

## Step 4: Manual Setup

### 4.1 Install uv Package Manager

uv is a fast Python package manager we use for dependency management:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reload your shell:

```bash
source $HOME/.cargo/env
# Or restart your terminal
```

Verify installation:

```bash
uv --version
```

**Expected output**: `uv 0.x.x`

### 4.2 Install Core Package

```bash
cd packages/core
uv sync --dev
cd ../..
```

This creates a virtual environment at `packages/core/.venv` and installs:

- Core dependencies: Pydantic, Jinja2, Typer, dynaconf
- Development tools: pytest, black, ruff, mypy, bandit

### 4.3 Install Settings Package

```bash
cd packages/settings
uv sync --dev
cd ../..
```

### 4.4 Install Orchestrator Package

```bash
cd packages/orchestrator
uv sync --dev
cd ../..
```

The orchestrator depends on core, which is installed as an editable dependency.

### 4.5 Set Up Pre-commit Hooks

Pre-commit hooks run code quality checks before each commit:

```bash
# Install pre-commit globally if not present
pip install pre-commit

# Install the project hooks
pre-commit install
```

Verify hooks are installed:

```bash
pre-commit run --all-files
```

---

## Step 5: Understand the Project Structure

### Package Layout

```
packages/
├── core/                    # Core package (standalone)
│   ├── src/
│   │   └── color_scheme/
│   │       ├── __init__.py
│   │       ├── cli/         # CLI commands
│   │       ├── config/      # Configuration system
│   │       ├── backends/    # Color extraction backends
│   │       └── generators/  # Output generators
│   ├── tests/
│   │   ├── unit/            # Unit tests
│   │   ├── integration/     # Integration tests
│   │   └── fixtures/        # Test data
│   └── pyproject.toml
│
├── orchestrator/            # Container orchestration
│   ├── src/
│   │   └── color_scheme_orchestrator/
│   ├── tests/
│   └── pyproject.toml
│
└── settings/                # Shared settings models
    ├── src/
    │   └── color_scheme_settings/
    ├── tests/
    └── pyproject.toml
```

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `packages/core/src/` | Main source code |
| `packages/core/tests/` | All tests |
| `templates/` | Jinja2 output templates |
| `docs/` | Documentation |
| `tools/` | Development scripts |

### Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package dependencies, tool config |
| `settings.toml` | Runtime configuration |
| `.pre-commit-config.yaml` | Pre-commit hook config |

---

## Step 6: Verify Installation

### Run Tests

```bash
cd packages/core
uv run pytest -v
```

**Expected**: All tests pass with 95%+ coverage.

### Check CLI

```bash
uv run color-scheme --help
uv run color-scheme version
```

**Expected**: Help text and version number displayed.

### Run Code Quality Checks

```bash
uv run ruff check .
uv run black --check .
uv run mypy src/
```

**Expected**: No errors or warnings.

### Verify Full Pipeline

From the repository root:

```bash
make pipeline
```

**Expected**: All checks pass (linting, security, tests).

---

## Step 7: Your First Development Workflow

### Create a Feature Branch

```bash
git checkout -b feature/core/my-first-change
```

### Make a Change

Edit any file—for example, add a test:

```python
# packages/core/tests/unit/test_example.py
def test_example():
    """Example test to verify setup."""
    assert 1 + 1 == 2
```

### Run Tests

```bash
cd packages/core
uv run pytest tests/unit/test_example.py -v
```

### Format Code

```bash
uv run black .
uv run isort .
```

### Commit

```bash
git add -A
git commit -m "test(core): add example test"
```

Pre-commit hooks run automatically. If they fail, fix issues and commit again.

### Clean Up

```bash
git checkout develop
git branch -d feature/core/my-first-change
```

---

## Troubleshooting

### "uv: command not found"

Reload your shell configuration:

```bash
source $HOME/.cargo/env
# Or restart your terminal
```

### Python Version Too Old

Install Python 3.12+ using the commands in Step 1.

If multiple Python versions exist, specify explicitly:

```bash
UV_PYTHON=python3.12 uv sync --dev
```

### Tests Failing After Setup

1. Ensure you're in the correct directory: `packages/core/`
2. Reinstall dependencies: `uv sync --dev`
3. Check for error messages in test output

### Import Errors

1. Use `uv run` to ensure correct environment
2. Or activate the venv: `source .venv/bin/activate`
3. Verify package installed: `uv run python -c "import color_scheme"`

### Pre-commit Hooks Failing

Run hooks manually to see detailed errors:

```bash
pre-commit run --all-files
```

Fix any issues, then commit again.

---

## Next Steps

Now that your environment is ready:

1. **Learn the workflow** → [How to Contribute](../how-to/contribute.md)
2. **Understand testing** → [How to Run Tests](../how-to/run-tests.md)
3. **Explore the CLI** → [CLI Reference](../reference/cli/core-commands.md)
4. **Pick an issue** → Check GitHub issues labeled `good-first-issue`

---

## Summary

You've successfully:

- [x] Installed Python 3.12+, uv, and Git
- [x] Cloned and set up the repository
- [x] Installed all package dependencies
- [x] Configured pre-commit hooks
- [x] Verified your development environment
- [x] Learned the basic development workflow

**You're ready to contribute!** 🎉
