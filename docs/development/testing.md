# Testing Guide

This guide covers testing practices, patterns, and workflows for the color-scheme project.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Running Tests](#running-tests)
- [Test Organization](#test-organization)
- [Writing Tests](#writing-tests)
- [Testing Patterns](#testing-patterns)
- [Coverage Requirements](#coverage-requirements)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Testing Philosophy

Our testing approach follows these principles:

### 1. Test-Driven Development (TDD)

Write tests before implementation when possible:

1. Write a failing test
2. Implement just enough code to pass
3. Refactor while keeping tests green

### 2. High Coverage (95%+)

All code must have comprehensive test coverage:
- Unit tests for individual functions/classes
- Integration tests for end-to-end flows
- Edge cases and error conditions

### 3. Fast Feedback

Tests should run quickly:
- Unit tests < 1s total
- Integration tests < 10s total
- Use pytest-xdist for parallel execution

### 4. Readable Tests

Tests are documentation:
- Clear test names describe what's being tested
- Arrange-Act-Assert pattern
- One assertion per test (generally)

### 5. Isolated Tests

Tests should not depend on each other:
- No shared state between tests
- Use fixtures for setup/teardown
- Mock external dependencies

## Running Tests

### Basic Test Execution

```bash
cd packages/core

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_config.py

# Run specific test
uv run pytest tests/unit/test_config.py::TestLoggingSettings::test_default_values

# Run tests matching pattern
uv run pytest -k "logging"
```

### Parallel Execution

Speed up tests with parallel execution:

```bash
# Run with auto-detected number of cores
uv run pytest -n auto

# Run with specific number of workers
uv run pytest -n 4
```

### Verbose Output

Get detailed test information:

```bash
# Verbose mode
uv run pytest -v

# Show print statements
uv run pytest -s

# Both
uv run pytest -v -s
```

### Coverage Reports

Generate coverage reports:

```bash
# Terminal report
uv run pytest --cov=src/color_scheme --cov-report=term

# HTML report (opens in browser)
uv run pytest --cov=src/color_scheme --cov-report=html
open htmlcov/index.html  # Linux/macOS
start htmlcov/index.html # Windows

# XML report (for CI)
uv run pytest --cov=src/color_scheme --cov-report=xml

# Multiple reports
uv run pytest --cov=src/color_scheme \
    --cov-report=term \
    --cov-report=html \
    --cov-report=xml
```

### Coverage Threshold

Enforce minimum coverage:

```bash
# Fail if coverage < 95%
uv run pytest --cov=src/color_scheme --cov-fail-under=95
```

### Other Useful Options

```bash
# Stop on first failure
uv run pytest -x

# Show slowest tests
uv run pytest --durations=10

# Re-run only failed tests
uv run pytest --lf

# Run tests marked with @pytest.mark.slow
uv run pytest -m slow

# Skip slow tests
uv run pytest -m "not slow"
```

## Test Organization

Tests are organized in a parallel structure to the source code:

```
packages/core/
├── src/
│   └── color_scheme/
│       ├── config/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── settings.py
│       │   └── enums.py
│       ├── cli/
│       └── backends/
│
└── tests/
    ├── __init__.py
    ├── conftest.py          # Shared fixtures and configuration
    │
    ├── unit/                # Unit tests (fast, isolated)
    │   ├── __init__.py
    │   ├── test_config.py   # Tests for config module
    │   ├── test_cli.py      # Tests for CLI
    │   └── test_backends.py # Tests for backends
    │
    ├── integration/         # Integration tests (slower, end-to-end)
    │   ├── __init__.py
    │   └── test_generate.py # End-to-end generation tests
    │
    └── fixtures/            # Test data and fixtures
        ├── __init__.py
        ├── sample_image.png
        └── sample_config.toml
```

### Unit Tests

Test individual components in isolation:

- **Location**: `tests/unit/`
- **Purpose**: Test single functions/classes
- **Speed**: Fast (<1s total)
- **Dependencies**: Mocked

Example: `tests/unit/test_config.py` tests configuration models

### Integration Tests

Test component interactions:

- **Location**: `tests/integration/`
- **Purpose**: Test end-to-end workflows
- **Speed**: Slower (up to 10s)
- **Dependencies**: Real or minimal mocking

Example: `tests/integration/test_generate.py` tests full color generation

### Fixtures

Shared test data and setup:

- **Location**: `tests/fixtures/`
- **Contents**: Sample images, configs, expected outputs
- **Usage**: Referenced by tests via pytest fixtures

## Writing Tests

### Test File Structure

```python
"""Tests for configuration system.

This module tests the configuration loading, validation, and defaults.
"""

import pytest
from pydantic import ValidationError

from color_scheme.config.config import LoggingSettings
from color_scheme.config.settings import Settings


class TestLoggingSettings:
    """Test LoggingSettings model."""

    def test_default_values(self):
        """Test default logging settings are correct."""
        # Arrange & Act
        settings = LoggingSettings()

        # Assert
        assert settings.level == "INFO"
        assert settings.show_time is True
        assert settings.show_path is False

    def test_valid_log_levels(self):
        """Test all valid log levels are accepted."""
        # Arrange
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        # Act & Assert
        for level in valid_levels:
            settings = LoggingSettings(level=level)
            assert settings.level == level

    def test_invalid_log_level(self):
        """Test invalid log level raises ValidationError."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            LoggingSettings(level="INVALID")
```

### Naming Conventions

**Test Files**:
- Prefix with `test_`: `test_config.py`, `test_backends.py`

**Test Classes**:
- Prefix with `Test`: `TestLoggingSettings`, `TestPywalBackend`
- Group related tests together

**Test Functions**:
- Prefix with `test_`: `test_default_values`, `test_invalid_input`
- Use descriptive names: `test_should_raise_error_when_backend_not_found`

### Arrange-Act-Assert Pattern

Structure tests in three phases:

```python
def test_color_extraction_from_image(self):
    """Test extracting colors from a valid image."""
    # Arrange - Set up test data and dependencies
    image_path = Path("tests/fixtures/sample.png")
    backend = PywalBackend()

    # Act - Execute the code under test
    result = backend.extract_colors(image_path)

    # Assert - Verify the results
    assert len(result.colors) == 16
    assert result.background is not None
    assert result.foreground is not None
```

### Using Fixtures

Define reusable test data in `conftest.py`:

```python
# tests/conftest.py

import pytest
from pathlib import Path


@pytest.fixture
def sample_image():
    """Provide path to sample test image."""
    return Path(__file__).parent / "fixtures" / "sample.png"


@pytest.fixture
def sample_settings_dict():
    """Provide sample settings dictionary."""
    return {
        "logging": {"level": "DEBUG"},
        "output": {"directory": "/tmp/test"},
    }
```

Use in tests:

```python
def test_with_sample_image(sample_image):
    """Test using the sample image fixture."""
    assert sample_image.exists()
    assert sample_image.suffix == ".png"
```

### Testing Exceptions

```python
def test_invalid_backend_raises_error(self):
    """Test that invalid backend raises ValueError."""
    with pytest.raises(ValueError, match="Invalid backend"):
        GenerationSettings(default_backend="invalid")
```

### Parametrized Tests

Test multiple inputs efficiently:

```python
@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_valid_log_levels(level):
    """Test all valid log levels are accepted."""
    settings = LoggingSettings(level=level)
    assert settings.level == level


@pytest.mark.parametrize("level,expected", [
    ("debug", "DEBUG"),
    ("info", "INFO"),
    ("warning", "WARNING"),
])
def test_case_insensitive_levels(level, expected):
    """Test log levels are case-insensitive."""
    settings = LoggingSettings(level=level)
    assert settings.level == expected
```

### Mocking External Dependencies

Use pytest-mock or unittest.mock:

```python
from unittest.mock import Mock, patch


def test_pywal_backend_calls_command(mocker):
    """Test that pywal backend calls the right command."""
    # Arrange
    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value = Mock(
        returncode=0,
        stdout='{"colors": {"color0": "#000000"}}'
    )

    # Act
    backend = PywalBackend()
    result = backend.extract_colors(Path("image.png"))

    # Assert
    mock_subprocess.assert_called_once()
    assert result is not None
```

## Testing Patterns

### Testing Pydantic Models

```python
def test_pydantic_model_validation():
    """Test Pydantic model validates correctly."""
    # Valid data
    valid_data = {"level": "INFO", "show_time": True}
    settings = LoggingSettings(**valid_data)
    assert settings.level == "INFO"

    # Invalid data
    invalid_data = {"level": "INVALID"}
    with pytest.raises(ValidationError) as exc_info:
        LoggingSettings(**invalid_data)

    # Check specific validation error
    assert "Invalid logging level" in str(exc_info.value)
```

### Testing File Operations

```python
def test_file_creation(tmp_path):
    """Test that output files are created correctly."""
    # Arrange - tmp_path is a pytest fixture providing temporary directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    output_file = output_dir / "colors.json"

    # Act
    generator = JSONGenerator()
    generator.write(color_scheme, output_file)

    # Assert
    assert output_file.exists()
    assert output_file.read_text().startswith("{")
```

### Testing CLI Commands

```python
from typer.testing import CliRunner
from color_scheme.cli.main import app


def test_cli_version_command():
    """Test the version command output."""
    runner = CliRunner()
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "color-scheme" in result.stdout
    assert "0.1.0" in result.stdout
```

### Testing Configuration Loading

```python
def test_settings_loads_from_file(tmp_path):
    """Test settings load from custom file."""
    # Arrange
    config_file = tmp_path / "test_settings.toml"
    config_file.write_text("""
    [logging]
    level = "DEBUG"
    """)

    # Act
    settings = SettingsModel(settings_files=[str(config_file)])
    config = settings.get()

    # Assert
    assert config.logging.level == "DEBUG"
```

### Testing Template Rendering

```python
def test_template_renders_colors():
    """Test Jinja2 template renders color scheme correctly."""
    # Arrange
    template_content = "{{ background }}"
    template = Template(template_content)
    color_scheme = ColorScheme(background="#000000")

    # Act
    output = template.render(background=color_scheme.background)

    # Assert
    assert output == "#000000"
```

## Coverage Requirements

### Minimum Coverage: 95%

All code must have at least 95% test coverage:

```bash
uv run pytest --cov=src/color_scheme --cov-fail-under=95
```

### What to Test

**Must have 100% coverage**:
- Public APIs
- Configuration loading
- Backend interfaces
- Output generation

**Can have <100% coverage**:
- Error handling for impossible cases
- Defensive programming checks
- Platform-specific code

### Checking Coverage by Module

```bash
# Coverage for specific module
uv run pytest --cov=src/color_scheme/config --cov-report=term

# See uncovered lines
uv run pytest --cov=src/color_scheme --cov-report=term-missing
```

### Excluding from Coverage

Use `# pragma: no cover` for code that can't be tested:

```python
if TYPE_CHECKING:  # pragma: no cover
    from typing import SomeType


def impossible_error():  # pragma: no cover
    """This should never be reached."""
    raise RuntimeError("Impossible state reached")
```

## CI/CD Integration

### CI Pipeline

Tests run automatically on every push and PR via GitHub Actions.

See `.github/workflows/ci-core.yml`:

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.12", "3.13"]

    steps:
      - name: Run tests with coverage
        run: |
          uv run pytest packages/core/tests/ \
            --cov=packages/core/src \
            --cov-report=xml \
            --cov-report=term \
            --cov-fail-under=95 \
            -v
```

### Running CI Checks Locally

Before pushing, run the same checks that CI will run:

```bash
cd packages/core

# All checks that CI runs
uv run ruff check .                    # Linting
uv run black --check .                 # Formatting
uv run isort --check .                 # Import sorting
uv run mypy src/                       # Type checking
uv run pytest --cov=src --cov-fail-under=95  # Tests + coverage
uv run bandit -r src/                  # Security scan
```

### Coverage Reports

Coverage reports are uploaded to Codecov automatically:

- View at: `https://codecov.io/gh/your-org/color-scheme`
- Badge in README shows coverage percentage
- Pull requests get coverage diff comments

## Troubleshooting

### Tests Not Found

If pytest can't find tests:

```bash
# Check that files start with test_
ls tests/unit/test_*.py

# Check PYTHONPATH
uv run python -c "import sys; print(sys.path)"

# Run from package directory
cd packages/core
uv run pytest
```

### Import Errors in Tests

```bash
# Ensure package is installed in dev mode
uv sync --dev

# Check imports
uv run python -c "import color_scheme; print(color_scheme.__file__)"
```

### Fixture Not Found

If pytest can't find a fixture:

1. Check `conftest.py` exists in tests directory
2. Ensure fixture is defined with `@pytest.fixture`
3. Check fixture name matches usage

### Coverage Too Low

If coverage is below 95%:

```bash
# See which lines are missing coverage
uv run pytest --cov=src/color_scheme --cov-report=term-missing

# Generate HTML report for visual inspection
uv run pytest --cov=src/color_scheme --cov-report=html
open htmlcov/index.html
```

Add tests for uncovered lines.

### Tests Slow

If tests are slow:

```bash
# Use parallel execution
uv run pytest -n auto

# See slowest tests
uv run pytest --durations=10

# Profile tests
uv run pytest --profile
```

Consider:
- Moving slow tests to integration/
- Marking slow tests: `@pytest.mark.slow`
- Optimizing test setup

### Flaky Tests

If tests pass/fail inconsistently:

1. Check for shared state between tests
2. Look for timing dependencies
3. Check for external dependencies (network, filesystem)
4. Add explicit cleanup in fixtures
5. Use `pytest-repeat` to reproduce: `uv run pytest --count=100`

## Best Practices Summary

1. **Write tests first** (TDD)
2. **Keep tests fast** (<1s for unit tests)
3. **One assertion per test** (generally)
4. **Use descriptive names** (test should document behavior)
5. **Mock external dependencies** (files, network, commands)
6. **Use fixtures** for setup/teardown
7. **Parametrize** similar tests
8. **Achieve 95%+ coverage**
9. **Run tests before committing**
10. **Keep tests maintainable** (refactor tests too)

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Plugin](https://pytest-cov.readthedocs.io/)
- [pytest-xdist for Parallel Tests](https://pytest-xdist.readthedocs.io/)
- [Pydantic Testing](https://docs.pydantic.dev/latest/concepts/testing/)
- [Typer Testing](https://typer.tiangolo.com/tutorial/testing/)

## Related Documentation

- [Getting Started](getting-started.md) - Development environment setup
- [Contributing Guide](contributing.md) - Full contribution workflow
- [Architecture Overview](../architecture/overview.md) - System design
