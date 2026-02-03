# How to Run Tests

Complete guide to running tests, checking coverage, and debugging test failures.

## Quick Start

```bash
cd packages/core

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_config.py

# Run with coverage
uv run pytest --cov=src/color_scheme --cov-report=term
```

---

## Running Tests

### All Tests

```bash
cd packages/core
uv run pytest
```

### Specific Test File

```bash
uv run pytest tests/unit/test_config.py
```

### Specific Test Function

```bash
uv run pytest tests/unit/test_config.py::test_default_values
```

### Specific Test Class

```bash
uv run pytest tests/unit/test_config.py::TestLoggingSettings
```

### Tests Matching Pattern

```bash
# Run tests with "backend" in their name
uv run pytest -k "backend"

# Run tests matching multiple patterns
uv run pytest -k "backend or config"

# Exclude tests matching pattern
uv run pytest -k "not slow"
```

---

## Parallel Execution

Speed up tests using multiple CPU cores:

```bash
# Auto-detect cores
uv run pytest -n auto

# Specific number of workers
uv run pytest -n 4
```

---

## Coverage Reports

### Terminal Report

```bash
uv run pytest --cov=src/color_scheme --cov-report=term
```

Shows coverage summary in terminal.

### Missing Lines Report

```bash
uv run pytest --cov=src/color_scheme --cov-report=term-missing
```

Shows which specific lines are not covered.

### HTML Report

```bash
uv run pytest --cov=src/color_scheme --cov-report=html
```

Generates `htmlcov/index.html`. Open in browser:

```bash
# Linux
xdg-open htmlcov/index.html

# macOS
open htmlcov/index.html
```

### Enforce Coverage Threshold

```bash
# Fail if coverage < 95%
uv run pytest --cov=src/color_scheme --cov-fail-under=95
```

### Combined Reports

```bash
uv run pytest --cov=src/color_scheme \
    --cov-report=term \
    --cov-report=html \
    --cov-report=xml
```

---

## Useful Options

### Stop on First Failure

```bash
uv run pytest -x
```

### Show Print Statements

```bash
uv run pytest -s
```

### Verbose + Capture Output

```bash
uv run pytest -v -s
```

### Show Slowest Tests

```bash
uv run pytest --durations=10
```

### Re-run Only Failed Tests

```bash
uv run pytest --lf
```

### Run Tests with Specific Marker

```bash
# Run only slow tests
uv run pytest -m slow

# Skip slow tests
uv run pytest -m "not slow"
```

---

## Testing Different Packages

### Core Package

```bash
cd packages/core
uv run pytest
```

### Settings Package

```bash
cd packages/settings
uv run pytest
```

### Orchestrator Package

```bash
cd packages/orchestrator
uv run pytest
```

### All Packages (via Makefile)

```bash
# From repository root
make test-all
```

---

## Writing Tests

### Test File Location

Place tests in the appropriate directory:

```
packages/core/tests/
├── unit/           # Fast, isolated tests
│   ├── test_config.py
│   └── test_backends.py
├── integration/    # End-to-end tests
│   └── test_generate.py
└── fixtures/       # Test data
    └── sample.png
```

### Test Structure

Use the Arrange-Act-Assert pattern:

```python
def test_extraction_returns_colors(self, sample_image):
    """Test that extraction returns expected colors."""
    # Arrange - Set up test data
    backend = PywalBackend()

    # Act - Execute the code
    result = backend.extract(sample_image)

    # Assert - Verify results
    assert len(result.colors) == 16
    assert result.background is not None
```

### Using Fixtures

Define reusable setup in `conftest.py`:

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_image():
    """Provide path to test image."""
    return Path(__file__).parent / "fixtures" / "sample.png"

@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide temporary output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output
```

Use in tests:

```python
def test_with_fixtures(sample_image, temp_output_dir):
    """Test using fixtures."""
    # sample_image and temp_output_dir are injected
    assert sample_image.exists()
```

### Parametrized Tests

Test multiple inputs efficiently:

```python
@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR"])
def test_valid_log_levels(level):
    """Test all valid log levels."""
    settings = LoggingSettings(level=level)
    assert settings.level == level
```

### Testing Exceptions

```python
def test_invalid_input_raises_error():
    """Test that invalid input raises ValueError."""
    with pytest.raises(ValueError, match="Invalid"):
        process_input(invalid_data)
```

### Mocking

```python
from unittest.mock import Mock, patch

def test_with_mock(mocker):
    """Test with mocked dependency."""
    # Mock subprocess call
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = Mock(returncode=0, stdout='{"color": "#000"}')

    # Test code that calls subprocess
    result = backend.extract(image)

    # Verify mock was called
    mock_run.assert_called_once()
```

### Testing CLI Commands

```python
from typer.testing import CliRunner
from color_scheme.cli.main import app

def test_version_command():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "color-scheme" in result.stdout
```

---

## Troubleshooting

### Tests Not Found

```bash
# Check test file naming (must start with test_)
ls tests/unit/test_*.py

# Run from package directory
cd packages/core
uv run pytest
```

### Import Errors

```bash
# Ensure dependencies installed
uv sync --dev

# Check package is importable
uv run python -c "import color_scheme"
```

### Fixture Not Found

1. Check `conftest.py` exists in tests directory
2. Verify fixture is decorated with `@pytest.fixture`
3. Check fixture name matches parameter name

### Coverage Too Low

```bash
# See uncovered lines
uv run pytest --cov=src/color_scheme --cov-report=term-missing

# Generate HTML for visual inspection
uv run pytest --cov=src/color_scheme --cov-report=html
```

Add tests for uncovered code paths.

### Flaky Tests

If tests pass/fail inconsistently:

1. Check for shared state between tests
2. Look for timing dependencies
3. Mock external dependencies
4. Run repeatedly: `uv run pytest --count=10 test_file.py`

### Slow Tests

```bash
# Find slowest tests
uv run pytest --durations=10

# Run in parallel
uv run pytest -n auto
```

Consider:
- Moving slow tests to `integration/`
- Marking slow tests: `@pytest.mark.slow`
- Optimizing test setup with fixtures

---

## CI Integration

Tests run automatically via GitHub Actions on every push/PR.

### Run CI Checks Locally

```bash
cd packages/core

# Same checks as CI
uv run ruff check .
uv run black --check .
uv run mypy src/
uv run pytest --cov=src/color_scheme --cov-fail-under=95
```

### Full Pipeline

```bash
# From repository root
make pipeline
```

---

## Test Markers

### Built-in Markers

```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_specific():
    pass

@pytest.mark.xfail(reason="Known bug")
def test_known_failure():
    pass
```

### Custom Markers

Define in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
]
```

Use:

```python
@pytest.mark.slow
def test_slow_operation():
    pass
```

Run:

```bash
# Only slow tests
uv run pytest -m slow

# Skip slow tests
uv run pytest -m "not slow"
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `uv run pytest` | Run all tests |
| `uv run pytest -v` | Verbose output |
| `uv run pytest -x` | Stop on first failure |
| `uv run pytest -n auto` | Parallel execution |
| `uv run pytest --cov=src` | Coverage report |
| `uv run pytest --lf` | Re-run failed tests |
| `uv run pytest -k "name"` | Match test names |
| `make test-core` | Test core package |
| `make test-all` | Test all packages |

---

## Related Documentation

- [How to Contribute](contribute.md) - Contribution workflow
- [Developer Setup Tutorial](../tutorials/developer-setup.md) - Environment setup
- [Makefile Reference](../reference/makefile.md) - Make commands
