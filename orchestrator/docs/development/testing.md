# Testing

Running and writing tests for `color-scheme`.

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
| `make test-parallel` | Run tests in parallel |
| `make coverage` | Run with coverage report |

---

## Running Specific Tests

```bash
# Run specific test file
uv run pytest tests/test_cli.py

# Run specific test
uv run pytest tests/test_cli.py::test_generate_command

# Run tests matching pattern
uv run pytest -k "container"
```

---

## Test Structure

```
tests/
├── conftest.py              # Fixtures
├── test_cli.py              # CLI tests
├── test_container.py        # Container tests
├── test_config.py           # Config tests
└── fixtures/                # Test data
    └── images/
```

---

## Integration Tests

Integration tests require Docker/Podman and built images:

```bash
# Build images first
make docker-build

# Run integration tests
uv run pytest tests/test_integration.py
```

---

## Mocking Container Runtime

For unit tests, mock the container runtime:

```python
from unittest.mock import patch

def test_generate_without_docker():
    with patch('color_scheme.container.runner.run_container') as mock:
        mock.return_value = (0, '{"colors": {...}}')
        # Test code here
```

---

## Coverage

```bash
# Generate coverage report
make coverage

# View HTML report
make coverage-report
```

