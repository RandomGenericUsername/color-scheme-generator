# Testing

Running and writing tests for `colorscheme-gen`.

---

## Running Tests

```bash
# All tests
make test

# Verbose output
make test-verbose

# With coverage
make coverage
```

---

## Test Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-verbose` | Run with verbose output |
| `make coverage` | Run with coverage report |
| `make coverage-report` | Open HTML coverage report |

---

## Running Specific Tests

```bash
# Run specific test file
uv run pytest tests/test_cli.py

# Run specific test
uv run pytest tests/test_cli.py::test_generate_command

# Run tests matching pattern
uv run pytest -k "backend"
```

---

## Test Structure

```
tests/
├── conftest.py          # Fixtures
├── test_cli.py          # CLI tests
├── test_backends.py     # Backend tests
├── test_templates.py    # Template tests
├── test_output.py       # Output tests
└── fixtures/            # Test data
    ├── images/
    └── expected/
```

---

## Writing Tests

```python
# tests/test_example.py
import pytest
from colorscheme_generator.core import generate_colorscheme

def test_generate_produces_colors(tmp_path, sample_image):
    """Test that generate produces valid color data."""
    colors = generate_colorscheme(sample_image)
    
    assert "special" in colors
    assert "colors" in colors
    assert colors["special"]["background"].startswith("#")

def test_generate_with_invalid_image():
    """Test that invalid image raises error."""
    with pytest.raises(ImageError):
        generate_colorscheme("/nonexistent/image.png")
```

---

## Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_image():
    """Return path to sample test image."""
    return Path(__file__).parent / "fixtures/images/sample.png"

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
```

---

## Coverage

```bash
# Generate coverage report
make coverage

# View HTML report
make coverage-report
```

Coverage report opens in browser at `htmlcov/index.html`.

