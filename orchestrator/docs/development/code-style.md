# Code Style

Coding standards for `color-scheme`.

---

## Formatting

We use:

- **Black** for code formatting
- **isort** for import sorting
- **Ruff** for linting

---

## Commands

```bash
# Format code
make format

# Check formatting
make format-check

# Lint code
make lint

# Fix lint issues
make lint-fix

# Type check
make type-check

# Run all checks
make check
```

---

## Configuration

Configured in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"
line_length = 88

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.11"
strict = true
```

---

## Guidelines

### Type Hints

```python
def run_container(
    image: str,
    command: list[str],
    mounts: dict[str, str],
) -> tuple[int, str]:
    """Run a container and return exit code and output."""
    ...
```

### Docstrings

```python
def generate(image_path: str, backend: str) -> None:
    """
    Generate a color scheme from an image.

    Args:
        image_path: Path to the source image.
        backend: Backend to use (pywal, wallust).

    Raises:
        ContainerError: If container execution fails.
    """
    ...
```

---

## Pre-commit

Install pre-commit hooks:

```bash
uv run pre-commit install
```

