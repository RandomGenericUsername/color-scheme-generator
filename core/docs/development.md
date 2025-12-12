# Development Guide

Guide for contributing to and developing colorscheme-generator.

---

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Adding Features](#adding-features)
- [Submitting Changes](#submitting-changes)

---

## Development Setup

### Prerequisites

- Python ≥3.12
- [uv](https://docs.astral.sh/uv/) package manager
- git
- (Optional) pyenv for Python version management
- (Optional) Rust/Cargo for wallust backend testing

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Clone Repository

```bash
git clone https://github.com/yourusername/colorscheme-generator.git
cd colorscheme-generator
```

### Install Development Dependencies

```bash
cd core

# Install with dev dependencies using Makefile
make install-dev

# Or manually with uv
uv sync --all-extras --dev
```

The virtual environment will be automatically created by uv in `.venv/`.

This installs:
- The package in editable mode (`-e`)
- Development dependencies (pytest, mypy, black, ruff, etc.)
- Optional pywal backend support

### Verify Installation

```bash
# Run tests
pytest

# Check types
mypy src/

# Format code
black src/

# Lint code
ruff check src/
```

---

## Project Structure

```
colorscheme-generator/
├── core/                              # Main package
│   ├── src/colorscheme_generator/
│   │   ├── backends/                 # Color extraction backends
│   │   │   ├── __init__.py
│   │   │   ├── pywal.py             # Pywal backend
│   │   │   ├── wallust.py           # Wallust backend
│   │   │   └── custom.py            # Custom PIL backend
│   │   ├── config/                  # Configuration system
│   │   │   ├── __init__.py
│   │   │   ├── settings.toml        # Default settings
│   │   │   ├── settings.py          # Dynaconf loader
│   │   │   ├── config.py            # Pydantic models
│   │   │   ├── defaults.py          # Default values
│   │   │   └── enums.py             # Enumerations
│   │   ├── core/                    # Core types and managers
│   │   │   ├── __init__.py
│   │   │   ├── types.py             # ColorScheme, Color, etc.
│   │   │   ├── base.py              # Abstract base classes
│   │   │   ├── exceptions.py        # Custom exceptions
│   │   │   └── managers/
│   │   │       ├── __init__.py
│   │   │       └── output_manager.py
│   │   ├── templates/               # Jinja2 templates
│   │   │   ├── colors.json.j2
│   │   │   ├── colors.sh.j2
│   │   │   ├── colors.css.j2
│   │   │   └── ...
│   │   ├── __init__.py
│   │   ├── cli.py                   # CLI entry point
│   │   └── factory.py               # Backend factory
│   ├── tests/                       # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py              # Pytest fixtures
│   │   ├── test_backends/
│   │   ├── test_config/
│   │   ├── test_core/
│   │   └── test_cli.py
│   ├── pyproject.toml               # Package metadata
│   └── README.md
├── docs/                            # Documentation
│   ├── README.md                    # Entry point
│   ├── architecture.md
│   ├── user-guide.md
│   ├── configuration.md
│   ├── templates.md
│   └── development.md (this file)
├── CLI_SETTINGS_OVERRIDE_ARCHITECTURE.md
├── .gitignore
└── LICENSE
```

---

## Running Tests

### Run All Tests

```bash
cd core
pytest
```

### Run Specific Test File

```bash
pytest tests/test_backends/test_custom.py
```

### Run Specific Test

```bash
pytest tests/test_backends/test_custom.py::test_custom_backend_generate
```

### Run with Coverage

```bash
pytest --cov=colorscheme_generator --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Fast Tests

```bash
pytest -m "not slow"
```

### Run Integration Tests

```bash
pytest -m integration
```

---

## Code Style

### Formatting with Black

```bash
# Format all code
black src/ tests/

# Check without modifying
black --check src/ tests/
```

### Linting with Ruff

```bash
# Lint code
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### Type Checking with Mypy

```bash
# Check types
mypy src/

# Check specific file
mypy src/colorscheme_generator/backends/custom.py
```

### Import Sorting with isort

```bash
# Sort imports
isort src/ tests/

# Check without modifying
isort --check src/ tests/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Adding Features

### Adding a New Backend

See **[Architecture Documentation](architecture.md#adding-a-new-backend)** for detailed steps.

**Quick overview**:

1. Create backend class in `backends/`:
```python
# backends/my_backend.py
from pathlib import Path
from colorscheme_generator.core.base import ColorSchemeGenerator
from colorscheme_generator.core.types import ColorScheme, GeneratorConfig
from colorscheme_generator.config.config import AppConfig

class MyBackendGenerator(ColorSchemeGenerator):
    def __init__(self, settings: AppConfig):
        self.settings = settings
    
    def is_available(self) -> bool:
        # Check if backend is available
        return True
    
    def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
        # Extract colors and return ColorScheme
        pass
```

2. Add to factory in `factory.py`
3. Add enum in `config/enums.py`
4. Add settings in `config/config.py`
5. Write tests in `tests/test_backends/`

### Adding a New Output Format

See **[Templates Guide](templates.md#creating-custom-templates)** for detailed steps.

**Quick overview**:

1. Create template in `templates/`:
```jinja2
{# templates/colors.myformat.j2 #}
# My Format
background: {{ background.hex }}
foreground: {{ foreground.hex }}
{% for color in colors %}
color{{ loop.index0 }}: {{ color.hex }}
{% endfor %}
```

2. Add to default formats in `config/defaults.py`:
```python
default_formats = ["json", "sh", "css", "myformat"]
```

3. Write tests in `tests/test_core/test_output_manager.py`

### Adding a New Configuration Option

1. Add to `config/defaults.py`:
```python
my_new_setting = "default_value"
```

2. Add to `config/config.py`:
```python
class MySettings(BaseModel):
    my_new_setting: str = Field(
        default=my_new_setting,
        description="Description of setting",
    )
```

3. Add to `config/settings.toml`:
```toml
[my_section]
my_new_setting = "default_value"
```

4. Update documentation in `docs/configuration.md`

5. Write tests in `tests/test_config/`

---

## Submitting Changes

### 1. Create a Branch

```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code
- Add tests
- Update documentation

### 3. Run Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Run tests
pytest

# Check coverage
pytest --cov=colorscheme_generator --cov-report=term-missing
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new backend for X"
```

**Commit Message Format**:
```
<type>: <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat: add wallust backend support
fix: handle missing image files gracefully
docs: update configuration guide
test: add tests for saturation adjustment
```

### 5. Push Changes

```bash
git push origin feature/my-new-feature
```

### 6. Create Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR template:
   - Description of changes
   - Related issues
   - Testing done
   - Screenshots (if applicable)

### 7. Address Review Comments

- Make requested changes
- Push updates to the same branch
- Respond to comments

---

## Testing Guidelines

### Unit Tests

Test individual components in isolation:

```python
# tests/test_core/test_types.py
import pytest
from colorscheme_generator.core.types import Color

def test_color_creation():
    """Test Color object creation."""
    color = Color(hex="#ff5733", rgb=(255, 87, 51))
    assert color.hex == "#ff5733"
    assert color.rgb == (255, 87, 51)

def test_color_saturation_adjustment():
    """Test saturation adjustment."""
    color = Color(hex="#ff5733", rgb=(255, 87, 51))
    adjusted = color.adjust_saturation(1.5)

    # Adjusted color should be more saturated
    assert adjusted.hex != color.hex
    assert adjusted.rgb != color.rgb
```

### Integration Tests

Test component interactions:

```python
# tests/test_backends/test_integration.py
import pytest
from pathlib import Path
from colorscheme_generator.backends.custom import CustomGenerator
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.core.types import GeneratorConfig

@pytest.mark.integration
def test_custom_backend_full_workflow(tmp_path):
    """Test full workflow with custom backend."""
    # Setup
    settings = Settings.get()
    generator = CustomGenerator(settings)
    config = GeneratorConfig.from_settings(settings)

    # Create test image
    test_image = tmp_path / "test.png"
    # ... create test image ...

    # Generate color scheme
    colorscheme = generator.generate(test_image, config)

    # Verify
    assert colorscheme.background is not None
    assert colorscheme.foreground is not None
    assert len(colorscheme.colors) == 16
```

### Fixtures

Use pytest fixtures for common setup:

```python
# tests/conftest.py
import pytest
from pathlib import Path
from PIL import Image

@pytest.fixture
def test_image(tmp_path):
    """Create a test image."""
    img_path = tmp_path / "test.png"
    img = Image.new('RGB', (100, 100), color='red')
    img.save(img_path)
    return img_path

@pytest.fixture
def mock_settings():
    """Create mock settings."""
    from colorscheme_generator.config.settings import Settings
    return Settings.get()
```

### Mocking

Use mocking for external dependencies:

```python
# tests/test_backends/test_pywal.py
import pytest
from unittest.mock import patch, MagicMock
from colorscheme_generator.backends.pywal import PywalGenerator

@patch('shutil.which')
def test_pywal_is_available(mock_which, mock_settings):
    """Test pywal availability check."""
    mock_which.return_value = "/usr/bin/wal"

    generator = PywalGenerator(mock_settings)
    assert generator.is_available() is True

    mock_which.return_value = None
    assert generator.is_available() is False
```

---

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use pdb Debugger

```python
import pdb; pdb.set_trace()  # Set breakpoint
```

### Use pytest with pdb

```bash
pytest --pdb  # Drop into debugger on failure
pytest -x --pdb  # Stop on first failure and debug
```

### Print Debugging

```python
print(f"Debug: {variable}")
print(f"Type: {type(variable)}")
print(f"Dir: {dir(variable)}")
```

---

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
    """Generate color scheme from image.

    Args:
        image_path: Path to source image
        config: Generator configuration

    Returns:
        ColorScheme object with extracted colors

    Raises:
        InvalidImageError: If image cannot be opened
        ColorExtractionError: If color extraction fails

    Example:
        >>> generator = CustomGenerator(settings)
        >>> scheme = generator.generate(Path("image.png"), config)
        >>> print(scheme.background.hex)
        #1a1b26
    """
    pass
```

### Update Documentation

When adding features, update:
- `docs/README.md` - If it's a major feature
- `docs/user-guide.md` - User-facing features
- `docs/configuration.md` - New settings
- `docs/templates.md` - Template-related changes
- `docs/architecture.md` - Architectural changes
- `docs/development.md` - Development process changes

---

## Release Process

### 1. Update Version

Edit `core/pyproject.toml`:
```toml
[project]
version = "0.2.0"
```

### 2. Update Changelog

Add to `docs/README.md`:
```markdown
### v0.2.0 (2025-12-15)
- feat: Add CLI settings override
- feat: Add saturation adjustment
- fix: Handle missing backends gracefully
```

### 3. Create Git Tag

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

### 4. Build Package

```bash
cd core
python -m build
```

### 5. Upload to PyPI

```bash
python -m twine upload dist/*
```

---

## Troubleshooting Development Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'colorscheme_generator'`

**Solution**:
```bash
# Reinstall in editable mode
pip install -e .
```

### Test Failures

**Problem**: Tests fail after changes

**Solution**:
1. Run specific failing test with verbose output:
   ```bash
   pytest -vv tests/test_file.py::test_name
   ```
2. Check test fixtures and mocks
3. Verify test data and expectations

### Type Errors

**Problem**: Mypy reports type errors

**Solution**:
1. Add type hints:
   ```python
   def func(arg: str) -> int:
       return int(arg)
   ```
2. Use `# type: ignore` for unavoidable issues:
   ```python
   result = external_lib.func()  # type: ignore
   ```

### Formatting Conflicts

**Problem**: Black and isort conflict

**Solution**:
Configure isort to be compatible with Black in `pyproject.toml`:
```toml
[tool.isort]
profile = "black"
```

---

## Resources

### Python Resources
- [Python Documentation](https://docs.python.org/3/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Pytest Documentation](https://docs.pytest.org/)

### Project-Specific
- [Dynaconf Documentation](https://www.dynaconf.com/)
- [Pywal Documentation](https://github.com/dylanaraps/pywal)
- [Wallust Documentation](https://codeberg.org/explosion-mental/wallust)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [Mypy Type Checker](https://mypy.readthedocs.io/)

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/colorscheme-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/colorscheme-generator/discussions)
- **Email**: maintainer@example.com

---

## Code of Conduct

Be respectful, inclusive, and constructive. See CODE_OF_CONDUCT.md for details.

---

## License

MIT License - see LICENSE file for details.


