# Contributing Guide

Thank you for your interest in contributing to color-scheme! This guide will help you understand our development process and standards.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Commit Message Conventions](#commit-message-conventions)
- [Pull Request Process](#pull-request-process)
- [Code Review Expectations](#code-review-expectations)
- [Design Compliance](#design-compliance)

## Getting Started

Before contributing, make sure you have:

1. **Set up your development environment**: See [Getting Started Guide](getting-started.md)
2. **Read the architecture**: [Architecture Overview](../architecture/overview.md)
3. **Understood the testing approach**: [Testing Guide](testing.md)

## Development Workflow

### 1. Find or Create an Issue

Before starting work:

- Check existing issues on GitHub
- Comment on the issue to claim it
- For new features, create an issue first to discuss
- Use issue templates when available

### 2. Create a Feature Branch

Branch naming convention:

```bash
# Feature branches
git checkout -b feature/core/<short-description>
git checkout -b feature/orchestrator/<short-description>

# Bug fix branches
git checkout -b bugfix/<issue-number>-<short-description>

# Documentation branches
git checkout -b docs/<short-description>

# Refactoring branches
git checkout -b refactor/<short-description>
```

Examples:
- `feature/core/pywal-backend`
- `bugfix/123-fix-config-validation`
- `docs/update-installation-guide`
- `refactor/simplify-settings-loader`

### 3. Make Changes

Follow these principles:

**YAGNI (You Aren't Gonna Need It)**:
- Only implement what's needed now
- Don't add features for hypothetical future use
- Keep it simple

**DRY (Don't Repeat Yourself)**:
- Extract common code into functions
- Use configuration over duplication
- Share utilities across modules

**TDD (Test-Driven Development)**:
- Write tests first (when practical)
- Ensure tests fail before implementing
- Implement just enough to pass tests
- Refactor while keeping tests green

### 4. Write Tests

All code must have tests with ≥95% coverage:

```bash
cd packages/core

# Write unit tests
# tests/unit/test_your_feature.py

# Run tests
uv run pytest tests/unit/test_your_feature.py -v

# Check coverage
uv run pytest --cov=src/color_scheme --cov-report=term-missing

# Ensure 95%+ coverage
uv run pytest --cov=src/color_scheme --cov-fail-under=95
```

See [Testing Guide](testing.md) for detailed testing patterns.

### 5. Update Documentation

Update relevant documentation:

- **CHANGELOG.md**: Add entry under "Unreleased"
- **Docstrings**: Add/update for all public APIs
- **User docs**: Update `docs/user-guide/` if user-facing
- **Dev docs**: Update `docs/development/` if process changes
- **README.md**: Update if installation/usage changes

### 6. Run Code Quality Checks

Before committing, run all quality checks:

```bash
cd packages/core

# Format code
uv run black .
uv run isort .

# Lint code
uv run ruff check .
uv run ruff check --fix .  # Auto-fix issues

# Type check
uv run mypy src/

# Security scan
uv run bandit -r src/

# Run all tests
uv run pytest --cov=src --cov-fail-under=95
```

Or use pre-commit hooks (if installed):

```bash
pre-commit run --all-files
```

### 7. Verify Design Compliance

Run verification scripts:

```bash
# Check design compliance
./scripts/verify-design-compliance.sh

# Check documentation
./scripts/verify-documentation.sh

# For phase completion
./scripts/phase-gate-check.sh <phase-number>
```

### 8. Commit Changes

Use conventional commit format (see [Commit Conventions](#commit-message-conventions)):

```bash
git add <files>
git commit -m "feat(core): add pywal backend implementation

Implements pywal backend for color extraction.

- Added PywalBackend class
- Added tests with 98% coverage
- Updated configuration to support pywal options

Closes #123"
```

### 9. Push and Create Pull Request

```bash
# Push branch
git push origin feature/core/your-feature

# Create PR on GitHub
# - Use PR template
# - Fill all sections
# - Link related issues
# - Add screenshots if UI changes
```

### 10. Address Review Feedback

When reviewers comment:

1. Read feedback carefully
2. Ask questions if unclear
3. Make requested changes
4. Push updates to same branch
5. Respond to comments
6. Request re-review when ready

### 11. Merge

Once approved and CI passes:

- Squash commits if many small commits
- Ensure commit message follows conventions
- Delete branch after merge

## Code Standards

### Python Style

We follow PEP 8 with these tools:

**Black** (code formatting):
- Line length: 88 characters
- Configuration in `pyproject.toml`

```bash
uv run black .
uv run black --check .  # Check without modifying
```

**isort** (import sorting):
- Profile: black
- Configuration in `pyproject.toml`

```bash
uv run isort .
uv run isort --check .  # Check without modifying
```

**Ruff** (linting):
- Fast Python linter
- Checks: pycodestyle, pyflakes, isort, bugbear, comprehensions, pyupgrade, etc.
- Configuration in `pyproject.toml`

```bash
uv run ruff check .
uv run ruff check --fix .  # Auto-fix issues
```

**mypy** (type checking):
- Static type checker
- Configuration in `pyproject.toml`

```bash
uv run mypy src/
```

### Type Hints

Use type hints for all function signatures:

```python
from pathlib import Path
from typing import Optional


def extract_colors(
    image_path: Path,
    backend: str = "pywal",
    n_colors: int = 16
) -> ColorScheme:
    """Extract colors from image.

    Args:
        image_path: Path to image file
        backend: Backend to use (pywal, wallust, custom)
        n_colors: Number of colors to extract

    Returns:
        ColorScheme with extracted colors

    Raises:
        ValueError: If backend is invalid
        FileNotFoundError: If image doesn't exist
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def generate_output(
    color_scheme: ColorScheme,
    formats: list[str],
    output_dir: Path
) -> list[Path]:
    """Generate output files in specified formats.

    Renders templates for each format and writes to output directory.

    Args:
        color_scheme: Color scheme to render
        formats: List of output formats (json, css, scss, etc.)
        output_dir: Directory to write output files

    Returns:
        List of paths to generated files

    Raises:
        ValueError: If format is unsupported
        OSError: If output directory is not writable

    Example:
        >>> scheme = ColorScheme(...)
        >>> files = generate_output(scheme, ["json", "css"], Path("/tmp"))
        >>> print(files)
        [Path("/tmp/colors.json"), Path("/tmp/colors.css")]
    """
    ...
```

### Error Handling

Be explicit about error conditions:

```python
# Good: Explicit validation
if not image_path.exists():
    raise FileNotFoundError(f"Image not found: {image_path}")

if backend not in ["pywal", "wallust", "custom"]:
    raise ValueError(f"Invalid backend: {backend}")

# Bad: Silent failures
if not image_path.exists():
    return None  # Caller doesn't know what went wrong
```

### Configuration over Hard-coding

Use configuration files, not hard-coded values:

```python
# Good: Use configuration
from color_scheme.config.settings import Settings

settings = Settings.get()
backend = settings.generation.default_backend

# Bad: Hard-coded values
backend = "pywal"  # What if user wants wallust?
```

### Logging

Use the configured logger:

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Loading configuration from %s", config_file)
logger.info("Extracting colors using %s backend", backend)
logger.warning("Template not found, using default")
logger.error("Failed to extract colors: %s", error)
```

## Commit Message Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding/updating tests
- `refactor`: Code refactoring (no functionality change)
- `perf`: Performance improvement
- `chore`: Build/tooling changes
- `ci`: CI/CD changes
- `style`: Code style changes (formatting, whitespace)

### Scope

Package or component affected:

- `core`: Core package
- `orchestrator`: Orchestrator package
- `config`: Configuration system
- `cli`: CLI commands
- `backends`: Backend implementations
- `templates`: Template system
- `docs`: Documentation
- `ci`: CI/CD

### Subject

- Short summary (≤50 characters)
- Imperative mood ("add feature", not "added feature")
- No period at end
- Lowercase

### Body (optional)

- Detailed explanation
- Why the change was made
- What changed
- Wrap at 72 characters

### Footer (optional)

- Reference issues: `Closes #123`, `Fixes #456`
- Breaking changes: `BREAKING CHANGE: describe change`
- Co-authors: `Co-Authored-By: Name <email>`

### Examples

Simple feature:
```
feat(core): add pywal backend implementation
```

With body and footer:
```
feat(core): add pywal backend implementation

Implements PywalBackend class that delegates color extraction to
the pywal command-line tool.

- Added PywalBackend class with extract_colors method
- Added configuration options for pywal algorithm
- Added tests with 98% coverage

Closes #123
```

Bug fix:
```
fix(config): resolve environment variables in paths

Settings loader now properly expands $HOME and other environment
variables in path settings.

Fixes #456
```

Documentation:
```
docs: update installation guide with uv setup

Added detailed uv installation instructions and troubleshooting
section.
```

Breaking change:
```
feat(config): change settings file format to TOML

BREAKING CHANGE: Configuration files must now use TOML format
instead of YAML. Run `color-scheme migrate-config` to convert.

Closes #789
```

## Pull Request Process

### 1. PR Title

Use conventional commit format for PR title:

```
feat(core): add custom backend implementation
```

### 2. PR Description

Use the PR template and fill all sections:

- **Summary**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Changes**: List of changes made
- **Testing**: How was this tested?
- **Screenshots**: If UI changes (N/A for this project)
- **Checklist**: Complete all items

### 3. PR Checklist

Before creating PR, ensure:

- [ ] Code follows style guidelines (black, ruff, isort)
- [ ] Type hints added (mypy passes)
- [ ] Tests written with ≥95% coverage
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow conventions
- [ ] Design compliance verified
- [ ] CI checks pass

### 4. Review Process

1. **Self-review**: Review your own PR first
2. **Automated checks**: Ensure CI passes
3. **Code review**: Wait for maintainer review
4. **Address feedback**: Make requested changes
5. **Re-review**: Request re-review after changes
6. **Approval**: Get approval from maintainer
7. **Merge**: Squash and merge

### 5. After Merge

- Delete feature branch
- Close related issues
- Update project board (if applicable)

## Code Review Expectations

### As a Contributor

When your PR is reviewed:

- **Be responsive**: Reply to comments within 24-48 hours
- **Be open**: Accept feedback gracefully
- **Ask questions**: If feedback is unclear, ask
- **Make changes**: Address all comments
- **Test thoroughly**: Re-test after changes
- **Be patient**: Reviews take time

### As a Reviewer

When reviewing PRs:

- **Be respectful**: Critique code, not people
- **Be specific**: Explain why changes are needed
- **Be helpful**: Suggest improvements
- **Be timely**: Review within 48 hours
- **Be thorough**: Check code, tests, docs

### Review Focus Areas

1. **Correctness**: Does it work as intended?
2. **Tests**: Are there tests? Do they cover edge cases?
3. **Design**: Is it well-designed? Follows patterns?
4. **Complexity**: Is it unnecessarily complex?
5. **Naming**: Are names clear and consistent?
6. **Documentation**: Is it documented?
7. **Error handling**: Are errors handled properly?
8. **Performance**: Are there performance issues?
9. **Security**: Any security concerns?
10. **Style**: Does it follow code standards?

## Design Compliance

All contributions must comply with the design document:

- [Monorepo Architecture Design](../plans/2026-01-18-monorepo-architecture-design.md)

### Verification

Run compliance checks before submitting PR:

```bash
# Check design compliance
./scripts/verify-design-compliance.sh

# Check documentation compliance
./scripts/verify-documentation.sh
```

### Design Principles

From the design document:

1. **Monorepo structure**: Keep packages independent
2. **Configuration system**: Use dynaconf + Pydantic
3. **Backend abstraction**: Follow backend interface
4. **Template-based output**: Use Jinja2 templates
5. **CLI consistency**: Same interface for both packages
6. **Type safety**: Pydantic models for all data
7. **Testing**: 95%+ coverage requirement

### When to Deviate

If you need to deviate from the design:

1. Open an issue for discussion
2. Create an ADR (Architecture Decision Record)
3. Get consensus from maintainers
4. Update design document
5. Proceed with implementation

## Getting Help

If you need help:

1. **Check documentation**: Read relevant guides first
2. **Search issues**: Someone may have had the same question
3. **Ask in issue**: Comment on the issue you're working on
4. **Open discussion**: Use GitHub Discussions for general questions
5. **Create issue**: For bugs or feature requests

## Resources

- [Getting Started Guide](getting-started.md)
- [Testing Guide](testing.md)
- [Architecture Overview](../architecture/overview.md)
- [Error Database](../troubleshooting/error-database.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Google Style Python Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

## Thank You

Thank you for contributing to color-scheme! Your contributions help make this project better for everyone.
