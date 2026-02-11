# Tool Configuration & Consistency

This document explains how tools are configured across the project to ensure consistency between local development and CI/CD.

## Configuration Sources

### 1. Root `pyproject.toml`
The root `pyproject.toml` contains centralized tool configurations that apply workspace-wide:

- **Black**: `line-length = 88`, `target-version = ["py312"]`
- **isort**: `profile = "black"`, `line_length = 88`
- **Ruff**: `line-length = 88`, `target-version = "py312"`
- **mypy**: `python_version = "3.12"`, `ignore_missing_imports = true`, `disable_error_code = ["import-untyped"]`
- **pytest**: `addopts = "-n auto --color=yes --cov-report=term-missing"`
- **coverage**: `fail_under = 95`

### 2. `.pre-commit-config.yaml`
Local pre-commit hooks that run before each commit:

```yaml
# Black formatting
args: [--line-length=88]

# isort import sorting
args: [--profile=black, --line-length=88]

# Ruff linting
args: [--fix, --line-length=88]

# mypy type checking
args: [--ignore-missing-imports, --disable-error-code=import-untyped]

# Bandit security scanning
args: [-ll]  # Only report MEDIUM and HIGH severity
```

### 3. GitHub Actions Workflows
CI/CD workflows in `.github/workflows/` that run on push/PR:

Each workflow (ci-core.yml, ci-settings.yml, ci-templates.yml, ci-orchestrator.yml) includes:

```yaml
# Linting commands with explicit arguments
ruff check --line-length 88 .
black --check --line-length 88 .
isort --check --profile black --line-length 88 .

# Type checking
mypy --ignore-missing-imports --disable-error-code=import-untyped src/

# Security scanning
bandit -r src/ -ll -f json -o bandit-report.json
```

## Consistency Guarantee

The following rules are enforced **identically** across pre-commit hooks and GitHub Actions:

| Tool | Setting | Value |
|------|---------|-------|
| Black | Line Length | 88 characters |
| isort | Profile | black |
| isort | Line Length | 88 characters |
| Ruff | Line Length | 88 characters |
| mypy | Python Version | 3.12 |
| mypy | Ignore Missing Imports | enabled |
| mypy | Import Untyped Errors | disabled |
| Bandit | Severity Filter | MEDIUM and HIGH only (-ll) |

## Workflow

1. **Local Development**: Pre-commit hooks run before each commit with the exact same configuration as CI
2. **Code Review**: GitHub Actions verify the same rules pass in CI/CD
3. **Consistency**: Code that passes locally will always pass in CI

## Running Tools Manually

To manually run tools with the correct configuration:

```bash
# From project root
make format        # Runs all formatters
make lint          # Runs all linters
make security      # Runs security scans
make test-all      # Runs full test suite

# Individual packages
make format-core
make lint-settings
make test-orchestrator
make security-templates

# Full pipeline
make pipeline      # Runs lint → security → test (matches CI)
```

## Adding New Tools

When adding new tools or changing configurations:

1. Update `pyproject.toml` (centralized config)
2. Update `.pre-commit-config.yaml` (local hooks)
3. Update all `.github/workflows/*.yml` files (CI/CD)

Ensure the same arguments and settings are used in all three places.

## Troubleshooting

**"Code passes locally but fails in CI"**
- Check that all tools have the same arguments in both `.pre-commit-config.yaml` and GitHub Actions workflows
- Verify version compatibility between local and CI environments
- Run `make pipeline` locally to simulate CI environment

**"Pre-commit hook failures"**
- Run the specific formatter: `make format-{package}`
- Check that `pyproject.toml` tool configurations are correct
- Verify pre-commit hooks are installed: `pre-commit install`

**"Different formatting on different machines"**
- Ensure all team members use the same tool versions from `uv.lock`
- Run `uv sync --dev --all-packages` to install exact versions
- Check that `pyproject.toml` is committed and shared
