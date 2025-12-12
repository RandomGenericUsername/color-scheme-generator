# Code Style

Coding standards for `colorscheme-gen`.

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

### Imports

```python
# Standard library
import os
from pathlib import Path

# Third-party
import click
from jinja2 import Template

# Local
from colorscheme_generator.core import generate
```

### Type Hints

```python
def generate_colorscheme(
    image_path: str,
    backend: str = "pywal",
    saturation: float = 1.0,
) -> dict[str, Any]:
    """Generate a color scheme from an image."""
    ...
```

### Docstrings

```python
def process_image(path: str) -> dict:
    """
    Process an image and extract colors.

    Args:
        path: Path to the source image.

    Returns:
        Dictionary containing color data.

    Raises:
        ImageError: If the image cannot be processed.
    """
    ...
```

### Naming

- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

---

## Pre-commit

Install pre-commit hooks:

```bash
uv run pre-commit install
```

Hooks run automatically on commit.

