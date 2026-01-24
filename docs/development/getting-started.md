# Developer Getting Started Guide

This guide walks you through setting up your development environment and making your first contribution to color-scheme.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Manual Setup](#manual-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Making Your First Contribution](#making-your-first-contribution)
- [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have the following installed:

### Required

- **Python 3.12 or higher**
  ```bash
  python3 --version  # Should be 3.12+
  ```
  If you need to install Python 3.12+:
  - **Ubuntu/Debian**: `sudo apt install python3.12`
  - **macOS**: `brew install python@3.12`
  - **Windows**: Download from [python.org](https://www.python.org/downloads/)

- **Git**
  ```bash
  git --version
  ```
  Install from [git-scm.com](https://git-scm.com/) if needed

- **curl** (for uv installation)
  ```bash
  curl --version
  ```

### Optional (for Orchestrator Development)

- **Docker** or **Podman** (container runtime)
  ```bash
  docker --version  # or podman --version
  ```

## Quick Start

The fastest way to get started is using our automated setup script:

```bash
# Clone the repository
git clone https://github.com/your-org/color-scheme.git
cd color-scheme

# Run the setup script
./scripts/setup-dev.sh
```

The script will:
1. Check prerequisites (Python 3.12+, git)
2. Install uv package manager
3. Install all dependencies (core + orchestrator + dev tools)
4. Set up pre-commit hooks
5. Verify installation with tests

**Note**: If the script fails, see [Manual Setup](#manual-setup) below.

## Manual Setup

If you prefer manual setup or the script fails:

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/color-scheme.git
cd color-scheme
```

### 2. Install uv Package Manager

uv is a fast Python package manager that we use for dependency management:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload your shell or source the environment
source $HOME/.cargo/env  # or restart your terminal
```

Verify installation:
```bash
uv --version
```

### 3. Install Core Package Dependencies

```bash
cd packages/core
uv sync --dev
cd ../..
```

This creates a virtual environment and installs:
- Core dependencies (Pydantic, Jinja2, dynaconf, etc.)
- Development tools (pytest, black, ruff, mypy, etc.)

### 4. Install Orchestrator Package Dependencies

```bash
cd packages/orchestrator
uv sync --dev
cd ../..
```

This installs orchestrator dependencies including core as an editable dependency.

### 5. Set Up Pre-commit Hooks (Optional)

Pre-commit hooks run code quality checks before each commit:

```bash
# Install pre-commit if not already installed
pip install pre-commit

# Install the hooks
pre-commit install
```

To run manually:
```bash
pre-commit run --all-files
```

### 6. Verify Installation

Run tests to ensure everything is set up correctly:

```bash
cd packages/core
uv run pytest -v
```

All tests should pass.

## Project Structure

Understanding the project structure will help you navigate the codebase:

```
color-scheme/                   # Repository root
│
├── packages/                   # Monorepo packages
│   ├── core/                   # Core package (standalone)
│   │   ├── src/
│   │   │   └── color_scheme/
│   │   │       ├── __init__.py
│   │   │       ├── cli/        # CLI commands and main entry point
│   │   │       │   ├── main.py # Typer app
│   │   │       │   └── ...
│   │   │       ├── config/     # Configuration system (Phase 1 ✅)
│   │   │       │   ├── config.py      # Pydantic models
│   │   │       │   ├── settings.py    # Settings loader
│   │   │       │   ├── enums.py       # Enumerations
│   │   │       │   ├── defaults.py    # Default values
│   │   │       │   └── settings.toml  # Default settings
│   │   │       ├── backends/   # Color extraction (Phase 2 - Coming)
│   │   │       ├── generators/ # Output generation (Phase 3 - Coming)
│   │   │       └── templates/  # Jinja2 templates
│   │   ├── tests/
│   │   │   ├── unit/          # Unit tests
│   │   │   ├── integration/   # Integration tests
│   │   │   ├── fixtures/      # Test fixtures
│   │   │   └── conftest.py    # Pytest configuration
│   │   └── pyproject.toml     # Package configuration
│   │
│   └── orchestrator/          # Orchestrator package (containerized)
│       ├── src/
│       │   └── color_scheme_orchestrator/
│       │       ├── __init__.py
│       │       └── cli/       # CLI delegation
│       ├── tests/
│       └── pyproject.toml
│
├── templates/                 # Shared Jinja2 templates
│   ├── colors.json.j2
│   ├── colors.css.j2
│   ├── colors.scss.j2
│   └── ...
│
├── scripts/                   # Development scripts
│   ├── setup-dev.sh          # Automated environment setup
│   ├── phase-gate-check.sh   # Phase completion verification
│   ├── verify-design-compliance.sh
│   ├── verify-documentation.sh
│   └── utils.sh              # Shared utilities
│
├── docs/                      # Documentation
│   ├── README.md             # Documentation index
│   ├── architecture/         # Architecture docs
│   ├── development/          # Developer docs (you are here!)
│   ├── user-guide/          # User documentation
│   ├── knowledge-base/      # ADRs, performance notes
│   ├── troubleshooting/     # Error database
│   ├── plans/               # Implementation plans
│   └── templates/           # Doc templates
│
├── .github/                  # GitHub configuration
│   ├── workflows/           # CI/CD pipelines
│   │   ├── ci-core.yml     # Core package CI
│   │   └── ...
│   └── pull_request_template.md
│
├── pyproject.toml           # Root project configuration
├── settings.toml            # Runtime settings
├── README.md                # Project overview
├── CHANGELOG.md             # Change log
└── CLAUDE.md                # Claude AI guidance
```

### Key Directories

- **packages/core/src/color_scheme/**: Main source code for core functionality
- **packages/core/tests/**: All tests for core package
- **packages/orchestrator/**: Container orchestration layer
- **templates/**: Jinja2 templates for output formats
- **scripts/**: Development automation scripts
- **docs/**: All project documentation

### Configuration Files

- **pyproject.toml**: Package dependencies and tool configuration (black, ruff, mypy, pytest)
- **settings.toml**: Runtime configuration (logging, output, backends)
- **.pre-commit-config.yaml**: Pre-commit hook configuration (if present)

## Development Workflow

### 1. Choose a Package

Decide which package you're working on:

- **Core**: Color extraction, generation, CLI
- **Orchestrator**: Container management, delegation

Most development happens in **core**.

### 2. Activate Virtual Environment

Each package has its own virtual environment:

```bash
# For core
cd packages/core
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# For orchestrator
cd packages/orchestrator
source .venv/bin/activate
```

Or use `uv run` to run commands without activating:

```bash
uv run python -c "import color_scheme; print(color_scheme.__version__)"
```

### 3. Run Tests

Always run tests before and after making changes:

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_config.py

# Run with coverage
uv run pytest --cov=src/color_scheme --cov-report=term

# Run in parallel (faster)
uv run pytest -n auto

# Verbose output
uv run pytest -v
```

### 4. Code Quality Tools

Run these before committing:

```bash
# Format code
uv run black .
uv run isort .

# Lint
uv run ruff check .
uv run ruff check --fix .  # Auto-fix issues

# Type check
uv run mypy src/

# Security scan
uv run bandit -r src/
```

Or run all via pre-commit:

```bash
pre-commit run --all-files
```

### 5. Making Changes

1. Create a feature branch (see [Contributing Guide](contributing.md))
2. Make your changes
3. Write tests (see [Testing Guide](testing.md))
4. Run tests and code quality tools
5. Commit with conventional commit message
6. Push and create PR

## Making Your First Contribution

Let's make a simple contribution to get familiar with the workflow.

### Example: Add a New Test

1. **Create a branch**:
   ```bash
   git checkout -b feature/core/improve-config-tests
   ```

2. **Navigate to tests**:
   ```bash
   cd packages/core/tests/unit
   ```

3. **Edit test file** (or create new one):
   ```python
   # tests/unit/test_config.py

   def test_logging_settings_custom():
       """Test custom logging settings."""
       from color_scheme.config.config import LoggingSettings

       settings = LoggingSettings(
           level="WARNING",
           show_time=False,
           show_path=True
       )

       assert settings.level == "WARNING"
       assert settings.show_time is False
       assert settings.show_path is True
   ```

4. **Run the test**:
   ```bash
   uv run pytest tests/unit/test_config.py::test_logging_settings_custom -v
   ```

5. **Check coverage**:
   ```bash
   uv run pytest --cov=src/color_scheme/config --cov-report=term
   ```

6. **Run code quality checks**:
   ```bash
   uv run black tests/unit/test_config.py
   uv run ruff check tests/unit/test_config.py
   ```

7. **Commit**:
   ```bash
   git add tests/unit/test_config.py
   git commit -m "test(core): add test for custom logging settings"
   ```

8. **Push and create PR**:
   ```bash
   git push origin feature/core/improve-config-tests
   # Then create PR on GitHub
   ```

## Common Development Tasks

### Running the CLI

```bash
# Core package
cd packages/core
uv run color-scheme --help
uv run color-scheme version

# Orchestrator package
cd packages/orchestrator
uv run color-scheme --help
```

### Installing New Dependencies

```bash
# Add to package
uv add <package-name>

# Add to dev dependencies
uv add --dev <package-name>

# Sync after adding
uv sync
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add <package-name>@latest
```

### Checking Code Coverage

```bash
# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html

# Open in browser (Linux/macOS)
open htmlcov/index.html

# Check coverage threshold
uv run pytest --cov=src --cov-fail-under=95
```

### Running CI Checks Locally

Before pushing, run the same checks that CI will run:

```bash
cd packages/core

# Lint
uv run ruff check .
uv run black --check .
uv run isort --check .

# Type check
uv run mypy src/

# Tests with coverage
uv run pytest --cov=src --cov-fail-under=95

# Security scan
uv run bandit -r src/
```

## Troubleshooting

### uv not found

After installing uv, you may need to reload your shell:

```bash
source $HOME/.cargo/env
# or
exec $SHELL  # Restart shell
```

### Python version too old

Check your Python version:

```bash
python3 --version
```

If it's < 3.12, install Python 3.12+ before proceeding.

### Tests failing

If tests fail after setup:

1. Ensure you're in the right directory: `packages/core/`
2. Dependencies installed: `uv sync --dev`
3. Check for error messages in test output
4. See [Error Database](../troubleshooting/error-database.md)

### Import errors

If you get import errors:

1. Ensure virtual environment is activated or using `uv run`
2. Check dependencies are installed: `uv sync`
3. Verify Python path: `uv run python -c "import sys; print(sys.path)"`

### Pre-commit hooks failing

If pre-commit hooks fail:

1. Run the specific tool manually to see the error
2. Fix the issues
3. Re-run: `pre-commit run --all-files`

## Next Steps

Now that your environment is set up:

1. **Read the architecture**: [Architecture Overview](../architecture/overview.md)
2. **Understand testing**: [Testing Guide](testing.md)
3. **Learn the workflow**: [Contributing Guide](contributing.md)
4. **Pick an issue**: Check GitHub issues labeled `good-first-issue`
5. **Join discussions**: GitHub Discussions or open an issue

## Getting Help

If you're stuck:

1. Check the [Error Database](../troubleshooting/error-database.md)
2. Review [Architecture Overview](../architecture/overview.md)
3. Read existing code and tests
4. Open a GitHub issue with `question` label
5. Check GitHub Discussions

## Resources

- [Architecture Overview](../architecture/overview.md)
- [Testing Guide](testing.md)
- [Contributing Guide](contributing.md)
- [Python 3.12 Documentation](https://docs.python.org/3.12/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
