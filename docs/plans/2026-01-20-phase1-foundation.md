# Phase 1: Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish monorepo structure, CI/CD pipelines, and core package skeleton with fully functional settings system.

**Architecture:** Create packages/core and packages/orchestrator directories with proper Python package structure. Implement dynaconf + Pydantic settings system in core. Setup CI workflows that run on every PR. Create development environment automation.

**Tech Stack:** Python 3.12+, uv, pytest, dynaconf, Pydantic, GitHub Actions, Typer

---

## Task 1: Create Monorepo Directory Structure

**Files:**
- Create: `packages/core/src/color_scheme/__init__.py`
- Create: `packages/core/tests/__init__.py`
- Create: `packages/orchestrator/src/color_scheme_orchestrator/__init__.py`
- Create: `packages/orchestrator/tests/__init__.py`

**Step 1: Create core package structure**

Run:
```bash
mkdir -p packages/core/src/color_scheme
mkdir -p packages/core/tests/unit
mkdir -p packages/core/tests/integration
mkdir -p packages/core/tests/fixtures
touch packages/core/src/color_scheme/__init__.py
touch packages/core/tests/__init__.py
touch packages/core/tests/unit/__init__.py
touch packages/core/tests/integration/__init__.py
```

**Step 2: Create orchestrator package structure**

Run:
```bash
mkdir -p packages/orchestrator/src/color_scheme_orchestrator
mkdir -p packages/orchestrator/tests/unit
mkdir -p packages/orchestrator/tests/integration
touch packages/orchestrator/src/color_scheme_orchestrator/__init__.py
touch packages/orchestrator/tests/__init__.py
touch packages/orchestrator/tests/unit/__init__.py
touch packages/orchestrator/tests/integration/__init__.py
```

**Step 3: Create documentation structure**

Run:
```bash
mkdir -p docs/user-guide
mkdir -p docs/development/recipes
mkdir -p docs/knowledge-base/adrs
mkdir -p docs/knowledge-base/performance
mkdir -p docs/troubleshooting
```

**Step 4: Verify directory structure**

Run:
```bash
tree -L 4 -I '__pycache__|*.pyc' packages/
tree -L 3 docs/
```

Expected: Directory structure matches design document Section 9

**Step 5: Commit**

Run:
```bash
git add packages/ docs/
git commit -m "feat(monorepo): create initial directory structure

Created package directories:
- packages/core with src and tests
- packages/orchestrator with src and tests

Created documentation structure:
- docs/user-guide
- docs/development
- docs/knowledge-base
- docs/troubleshooting

Implements design Section 1 (monorepo structure).

Part of Phase 1: Foundation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Initialize Core Package with pyproject.toml

**Files:**
- Create: `packages/core/pyproject.toml`
- Modify: `packages/core/src/color_scheme/__init__.py`

**Step 1: Create core package version**

Edit `packages/core/src/color_scheme/__init__.py`:
```python
"""Color scheme generator core package.

Standalone color scheme generation with multiple backends.
"""

__version__ = "0.1.0"
```

**Step 2: Create core pyproject.toml**

Create `packages/core/pyproject.toml`:
```toml
[project]
name = "color-scheme-core"
version = "0.1.0"
description = "Core color scheme generator with multiple backends (pywal, wallust, custom)"
requires-python = ">=3.12"
readme = "README.md"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]

dependencies = [
    "pydantic>=2.11.9",
    "pillow>=10.0.0",
    "jinja2>=3.1.6",
    "dynaconf>=3.2.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "typer>=0.12.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
pywal = ["pywal>=3.3.0"]

[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.5.0",
    "mypy>=1.11.0",
    "black>=24.0.0",
    "ruff>=0.6.0",
    "isort>=5.13.0",
    "bandit>=1.7.5",
]

[project.scripts]
color-scheme = "color_scheme.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/color_scheme"]

[tool.black]
line-length = 88
target-version = ["py312"]
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "ARG",  # flake8-unused-arguments
    "SIM",  # flake8-simplify
    "PTH",  # flake8-use-pathlib
    "N",    # pep8-naming
]
ignore = []

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["ARG", "PTH"]

[tool.mypy]
python_version = "3.12"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_defs = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
warn_unused_configs = true
strict_equality = true
show_error_codes = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --tb=short"
```

**Step 3: Create core package README**

Create `packages/core/README.md`:
```markdown
# color-scheme-core

Core color scheme generator with multiple backends.

## Features

- Multiple color extraction backends (pywal, wallust, custom)
- Multiple output formats (JSON, CSS, SCSS, YAML, shell scripts, etc.)
- Configurable via settings.toml
- CLI and Python API

## Installation

```bash
pip install color-scheme-core
```

## Usage

```bash
# Generate color scheme
color-scheme generate image.png

# Show color scheme
color-scheme show
```

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Check coverage
uv run pytest --cov
```

## Documentation

See main project documentation in repository root.
```

**Step 4: Initialize uv environment**

Run:
```bash
cd packages/core
uv sync --dev
cd ../..
```

Expected: Creates .venv and installs dependencies

**Step 5: Verify installation**

Run:
```bash
cd packages/core
uv run python -c "import color_scheme; print(color_scheme.__version__)"
cd ../..
```

Expected: Prints "0.1.0"

**Step 6: Commit**

Run:
```bash
git add packages/core/
git commit -m "feat(core): initialize core package with pyproject.toml

Created core package configuration:
- pyproject.toml with all dependencies and tooling config
- Package version in __init__.py
- README with basic usage
- Initialized uv environment

Core package is now installable and has CLI entry point registered.

Part of Phase 1: Foundation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Initialize Orchestrator Package with pyproject.toml

**Files:**
- Create: `packages/orchestrator/pyproject.toml`
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/__init__.py`
- Create: `packages/orchestrator/README.md`

**Step 1: Create orchestrator package version**

Edit `packages/orchestrator/src/color_scheme_orchestrator/__init__.py`:
```python
"""Color scheme orchestrator - containerized execution.

Runs color-scheme-core in containers for isolated backend execution.
"""

__version__ = "0.1.0"
```

**Step 2: Create orchestrator pyproject.toml**

Create `packages/orchestrator/pyproject.toml`:
```toml
[project]
name = "color-scheme-orchestrator"
version = "0.1.0"
description = "Container orchestrator for color-scheme-core"
requires-python = ">=3.12"
readme = "README.md"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]

dependencies = [
    "color-scheme-core>=0.1.0",
    "typer>=0.12.0",
    "rich>=13.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.5.0",
    "mypy>=1.11.0",
    "black>=24.0.0",
    "ruff>=0.6.0",
    "isort>=5.13.0",
    "bandit>=1.7.5",
]

[project.scripts]
color-scheme = "color_scheme_orchestrator.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/color_scheme_orchestrator"]

# Inherit tooling config from core (same settings)
[tool.black]
line-length = 88
target-version = ["py312"]

[tool.isort]
profile = "black"
line_length = 88

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PTH", "N"]
ignore = []

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["ARG", "PTH"]

[tool.mypy]
python_version = "3.12"
check_untyped_defs = true
disallow_incomplete_defs = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --tb=short"
```

**Step 3: Create orchestrator README**

Create `packages/orchestrator/README.md`:
```markdown
# color-scheme-orchestrator

Container orchestrator for color-scheme-core.

## Features

- Runs color extraction in isolated containers
- Same CLI as core package
- Automatic container image management
- Supports Docker and Podman

## Installation

```bash
pip install color-scheme-orchestrator
```

Requires Docker or Podman.

## Usage

```bash
# Install backend container images
color-scheme install pywal

# Generate color scheme (containerized)
color-scheme generate image.png

# Show color scheme (delegates to core, no container)
color-scheme show
```

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest
```

## Documentation

See main project documentation in repository root.
```

**Step 4: Initialize uv environment**

Run:
```bash
cd packages/orchestrator
# Note: This will fail because color-scheme-core isn't published yet
# We'll install core in editable mode
echo 'color-scheme-core = { path = "../core", editable = true }' >> pyproject.toml
uv sync --dev
cd ../..
```

Expected: Creates .venv with core package as editable dependency

**Step 5: Verify installation**

Run:
```bash
cd packages/orchestrator
uv run python -c "import color_scheme_orchestrator; print(color_scheme_orchestrator.__version__)"
cd ../..
```

Expected: Prints "0.1.0"

**Step 6: Commit**

Run:
```bash
git add packages/orchestrator/
git commit -m "feat(orchestrator): initialize orchestrator package

Created orchestrator package configuration:
- pyproject.toml with dependencies (including core as editable)
- Package version in __init__.py
- README with basic usage
- Initialized uv environment

Orchestrator depends on core and has same CLI entry point name.

Part of Phase 1: Foundation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Create Core Package Config System

**Files:**
- Create: `packages/core/src/color_scheme/config/__init__.py`
- Create: `packages/core/src/color_scheme/config/enums.py`
- Create: `packages/core/src/color_scheme/config/defaults.py`
- Create: `packages/core/src/color_scheme/config/config.py`
- Create: `packages/core/src/color_scheme/config/settings.py`
- Create: `packages/core/src/color_scheme/config/settings.toml`

**Step 1: Create config package init**

Create `packages/core/src/color_scheme/config/__init__.py`:
```python
"""Configuration system using dynaconf + Pydantic."""

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend, ColorAlgorithm
from color_scheme.config.settings import Settings

__all__ = ["AppConfig", "Backend", "ColorAlgorithm", "Settings"]
```

**Step 2: Create enums**

Create `packages/core/src/color_scheme/config/enums.py`:
```python
"""Enumerations for configuration."""

from enum import Enum


class Backend(str, Enum):
    """Available color extraction backends."""

    PYWAL = "pywal"
    WALLUST = "wallust"
    CUSTOM = "custom"


class ColorAlgorithm(str, Enum):
    """Custom backend color extraction algorithms."""

    KMEANS = "kmeans"
    DOMINANT = "dominant"
```

**Step 3: Create defaults**

Create `packages/core/src/color_scheme/config/defaults.py`:
```python
"""Default configuration values."""

from pathlib import Path

# Logging defaults
default_log_level = "INFO"
default_show_time = True
default_show_path = False

# Output defaults
output_directory = Path.home() / ".config" / "color-scheme" / "output"
default_formats = [
    "json",
    "sh",
    "css",
    "gtk.css",
    "yaml",
    "sequences",
    "rasi",
    "scss",
]

# Generation defaults
default_backend = "pywal"
saturation_adjustment = 1.0

# Backend-specific defaults
pywal_backend_algorithm = "haishoku"
wallust_backend_type = "resized"
custom_algorithm = "kmeans"
custom_n_clusters = 16

# Template defaults
template_directory = Path("templates")
```

**Step 4: Create Pydantic config models (part 1 - base models)**

Create `packages/core/src/color_scheme/config/config.py`:
```python
"""Pydantic configuration models for colorscheme generator."""

import logging
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from color_scheme.config.defaults import (
    custom_algorithm,
    custom_n_clusters,
    default_backend,
    default_formats,
    output_directory,
    pywal_backend_algorithm,
    saturation_adjustment,
    template_directory,
    wallust_backend_type,
)
from color_scheme.config.enums import Backend, ColorAlgorithm


class LoggingSettings(BaseModel):
    """Logging configuration."""

    level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    show_time: bool = Field(
        default=True,
        description="Show timestamps in log messages",
    )
    show_path: bool = Field(
        default=False,
        description="Show file path in log messages",
    )

    @field_validator("level", mode="before")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate logging level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid logging level: {v}. "
                f"Must be one of: {', '.join(sorted(valid_levels))}"
            )
        return v_upper

    def get_level_int(self) -> int:
        """Get logging level as integer."""
        return getattr(logging, self.level)


class OutputSettings(BaseModel):
    """Output configuration."""

    directory: Path = Field(
        default=output_directory,
        description="Directory where generated files are written",
    )
    formats: list[str] = Field(
        default_factory=lambda: default_formats.copy(),
        description="Output formats to generate",
    )


class GenerationSettings(BaseModel):
    """Color scheme generation defaults."""

    default_backend: str = Field(
        default=default_backend,
        description="Default backend for color extraction",
    )

    saturation_adjustment: float = Field(
        default=saturation_adjustment,
        ge=0.0,
        le=2.0,
        description="Default saturation adjustment factor",
    )

    @field_validator("default_backend", mode="before")
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate backend string."""
        try:
            Backend(v)
            return v
        except ValueError:
            valid = ", ".join([b.value for b in Backend])
            raise ValueError(
                f"Invalid backend '{v}'. Valid options: {valid}"
            ) from None


class PywalBackendSettings(BaseModel):
    """Pywal backend configuration."""

    backend_algorithm: str = Field(
        default=pywal_backend_algorithm,
        description="Pywal color extraction algorithm",
    )

    @field_validator("backend_algorithm")
    @classmethod
    def validate_backend_algorithm(cls, v: str) -> str:
        """Validate backend algorithm."""
        allowed = {"wal", "colorz", "colorthief", "haishoku", "schemer2"}
        if v not in allowed:
            raise ValueError(
                f"Invalid backend_algorithm: {v}. "
                f"Must be one of: {', '.join(sorted(allowed))}"
            )
        return v


class WallustBackendSettings(BaseModel):
    """Wallust backend configuration."""

    backend_type: str = Field(
        default=wallust_backend_type,
        description="Wallust backend type",
    )


class CustomBackendSettings(BaseModel):
    """Custom Python backend configuration."""

    algorithm: str = Field(
        default=custom_algorithm, description="Color extraction algorithm"
    )
    n_clusters: int = Field(
        default=custom_n_clusters,
        ge=8,
        le=256,
        description="Number of color clusters for extraction",
    )

    @field_validator("algorithm", mode="before")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate algorithm string."""
        try:
            ColorAlgorithm(v)
            return v
        except ValueError:
            valid = ", ".join([a.value for a in ColorAlgorithm])
            raise ValueError(
                f"Invalid algorithm '{v}'. Valid options: {valid}"
            ) from None


class BackendSettings(BaseModel):
    """Backend-specific configurations."""

    pywal: PywalBackendSettings = Field(
        default_factory=PywalBackendSettings,
        description="Pywal backend settings",
    )
    wallust: WallustBackendSettings = Field(
        default_factory=WallustBackendSettings,
        description="Wallust backend settings",
    )
    custom: CustomBackendSettings = Field(
        default_factory=CustomBackendSettings,
        description="Custom backend settings",
    )


class TemplateSettings(BaseModel):
    """Template rendering configuration."""

    directory: Path = Field(
        default=template_directory,
        description="Directory containing Jinja2 templates",
    )


class AppConfig(BaseModel):
    """Application configuration root model."""

    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Logging configuration",
    )
    output: OutputSettings = Field(
        default_factory=OutputSettings,
        description="Output configuration",
    )
    generation: GenerationSettings = Field(
        default_factory=GenerationSettings,
        description="Generation defaults",
    )
    backends: BackendSettings = Field(
        default_factory=BackendSettings,
        description="Backend-specific settings",
    )
    templates: TemplateSettings = Field(
        default_factory=TemplateSettings,
        description="Template configuration",
    )
```

**Step 5: Create settings loader**

Create `packages/core/src/color_scheme/config/settings.py`:
```python
"""Settings loader using dynaconf + Pydantic."""

import os
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf
from pydantic import ValidationError

from color_scheme.config.config import AppConfig as PydanticAppConfig

# Get the config directory
CONFIG_DIR = Path(__file__).parent
SETTINGS_FILE = CONFIG_DIR / "settings.toml"


class SettingsModel:
    """Settings loader using dynaconf + Pydantic.

    Loads settings from TOML files using dynaconf, converts to lowercase,
    resolves environment variables, and validates with Pydantic.
    """

    def __init__(self, settings_files: list[str] | None = None):
        """Initialize settings loader.

        Args:
            settings_files: List of settings file paths. If None, uses default.
        """
        if settings_files is None:
            settings_files = [str(SETTINGS_FILE)]

        self.dynaconf_settings: Dynaconf = Dynaconf(
            settings_files=settings_files,
        )
        self.settings: PydanticAppConfig = self.get_pydantic_config(
            self._convert_dict_to_lower_case(
                self._resolve_environment_variables(
                    self.dynaconf_settings.to_dict()
                )
            )
        )

    @staticmethod
    def _convert_dict_to_lower_case(
        settings_dict: dict[str, Any],
    ) -> dict[str, Any]:
        """Convert all keys to lowercase recursively."""
        lower_case_dict = {}
        for key, value in settings_dict.items():
            if isinstance(value, dict):
                lower_case_dict[key.lower()] = (
                    SettingsModel._convert_dict_to_lower_case(value)
                )
            else:
                lower_case_dict[key.lower()] = value
        return lower_case_dict

    @staticmethod
    def _resolve_environment_variables(
        settings_dict: dict[str, Any],
    ) -> dict[str, Any]:
        """Resolve environment variables in string values."""

        def _resolve_string_values(data: Any) -> Any:
            """Recursively resolve env variables."""
            if isinstance(data, str):
                return os.path.expandvars(data)
            elif isinstance(data, dict):
                return {
                    key: _resolve_string_values(value)
                    for key, value in data.items()
                }
            elif isinstance(data, list):
                return [_resolve_string_values(item) for item in data]
            else:
                return data

        return _resolve_string_values(settings_dict)

    @staticmethod
    def get_pydantic_config(settings: dict) -> PydanticAppConfig:
        """Validate settings with Pydantic."""
        try:
            return PydanticAppConfig(**settings)
        except ValidationError as e:
            raise e

    def get(self) -> PydanticAppConfig:
        """Get validated settings."""
        return self.settings


# Global settings instance
Settings: SettingsModel = SettingsModel()
```

**Step 6: Create settings.toml**

Create `packages/core/src/color_scheme/config/settings.toml`:
```toml
# Logging configuration
[logging]
level = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
show_time = true
show_path = false

# Output configuration
[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]

# Generation defaults
[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

# Backend-specific settings
[backends.pywal]
backend_algorithm = "haishoku"

[backends.wallust]
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16

# Template configuration
[templates]
directory = "templates"
```

**Step 7: Commit**

Run:
```bash
git add packages/core/src/color_scheme/config/
git commit -m "feat(core): implement configuration system with dynaconf + Pydantic

Created complete config system:
- Enums for backends and algorithms
- Default values module
- Pydantic models for validation
- Settings loader using dynaconf
- settings.toml with all configuration

Settings system follows design Section 4.
Uses same pattern as reference implementation.

Part of Phase 1: Foundation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Test Configuration System

**Files:**
- Create: `packages/core/tests/unit/test_config.py`
- Create: `packages/core/tests/conftest.py`

**Step 1: Create pytest configuration**

Create `packages/core/tests/conftest.py`:
```python
"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_settings_dict():
    """Sample settings dictionary for testing."""
    return {
        "logging": {
            "level": "DEBUG",
            "show_time": True,
            "show_path": False,
        },
        "output": {
            "directory": "/tmp/test-output",
            "formats": ["json", "css"],
        },
        "generation": {
            "default_backend": "custom",
            "saturation_adjustment": 1.5,
        },
        "backends": {
            "pywal": {"backend_algorithm": "haishoku"},
            "wallust": {"backend_type": "resized"},
            "custom": {"algorithm": "kmeans", "n_clusters": 16},
        },
        "templates": {"directory": "templates"},
    }
```

**Step 2: Write config tests**

Create `packages/core/tests/unit/test_config.py`:
```python
"""Tests for configuration system."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from color_scheme.config.config import (
    AppConfig,
    BackendSettings,
    CustomBackendSettings,
    GenerationSettings,
    LoggingSettings,
    OutputSettings,
    PywalBackendSettings,
)
from color_scheme.config.enums import Backend, ColorAlgorithm
from color_scheme.config.settings import Settings, SettingsModel


class TestEnums:
    """Test configuration enums."""

    def test_backend_enum_values(self):
        """Test Backend enum has correct values."""
        assert Backend.PYWAL.value == "pywal"
        assert Backend.WALLUST.value == "wallust"
        assert Backend.CUSTOM.value == "custom"

    def test_color_algorithm_enum_values(self):
        """Test ColorAlgorithm enum has correct values."""
        assert ColorAlgorithm.KMEANS.value == "kmeans"
        assert ColorAlgorithm.DOMINANT.value == "dominant"


class TestLoggingSettings:
    """Test LoggingSettings model."""

    def test_default_values(self):
        """Test default logging settings."""
        settings = LoggingSettings()
        assert settings.level == "INFO"
        assert settings.show_time is True
        assert settings.show_path is False

    def test_valid_log_level(self):
        """Test valid log levels are accepted."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = LoggingSettings(level=level)
            assert settings.level == level

    def test_invalid_log_level(self):
        """Test invalid log level raises error."""
        with pytest.raises(ValidationError):
            LoggingSettings(level="INVALID")

    def test_case_insensitive_log_level(self):
        """Test log level is case-insensitive."""
        settings = LoggingSettings(level="debug")
        assert settings.level == "DEBUG"

    def test_get_level_int(self):
        """Test getting log level as integer."""
        import logging

        settings = LoggingSettings(level="DEBUG")
        assert settings.get_level_int() == logging.DEBUG


class TestOutputSettings:
    """Test OutputSettings model."""

    def test_default_values(self):
        """Test default output settings."""
        settings = OutputSettings()
        assert isinstance(settings.directory, Path)
        assert "json" in settings.formats
        assert "css" in settings.formats


class TestGenerationSettings:
    """Test GenerationSettings model."""

    def test_default_values(self):
        """Test default generation settings."""
        settings = GenerationSettings()
        assert settings.default_backend == "pywal"
        assert settings.saturation_adjustment == 1.0

    def test_valid_backend(self):
        """Test valid backend values."""
        for backend in ["pywal", "wallust", "custom"]:
            settings = GenerationSettings(default_backend=backend)
            assert settings.default_backend == backend

    def test_invalid_backend(self):
        """Test invalid backend raises error."""
        with pytest.raises(ValidationError):
            GenerationSettings(default_backend="invalid")

    def test_saturation_range(self):
        """Test saturation adjustment range validation."""
        # Valid values
        GenerationSettings(saturation_adjustment=0.0)
        GenerationSettings(saturation_adjustment=1.0)
        GenerationSettings(saturation_adjustment=2.0)

        # Invalid values
        with pytest.raises(ValidationError):
            GenerationSettings(saturation_adjustment=-0.1)
        with pytest.raises(ValidationError):
            GenerationSettings(saturation_adjustment=2.1)


class TestPywalBackendSettings:
    """Test PywalBackendSettings model."""

    def test_default_values(self):
        """Test default pywal settings."""
        settings = PywalBackendSettings()
        assert settings.backend_algorithm == "haishoku"

    def test_valid_algorithms(self):
        """Test valid pywal algorithms."""
        for algo in ["wal", "colorz", "colorthief", "haishoku", "schemer2"]:
            settings = PywalBackendSettings(backend_algorithm=algo)
            assert settings.backend_algorithm == algo

    def test_invalid_algorithm(self):
        """Test invalid algorithm raises error."""
        with pytest.raises(ValidationError):
            PywalBackendSettings(backend_algorithm="invalid")


class TestCustomBackendSettings:
    """Test CustomBackendSettings model."""

    def test_default_values(self):
        """Test default custom backend settings."""
        settings = CustomBackendSettings()
        assert settings.algorithm == "kmeans"
        assert settings.n_clusters == 16

    def test_valid_algorithms(self):
        """Test valid custom algorithms."""
        for algo in ["kmeans", "dominant"]:
            settings = CustomBackendSettings(algorithm=algo)
            assert settings.algorithm == algo

    def test_invalid_algorithm(self):
        """Test invalid algorithm raises error."""
        with pytest.raises(ValidationError):
            CustomBackendSettings(algorithm="invalid")

    def test_n_clusters_range(self):
        """Test n_clusters range validation."""
        # Valid values
        CustomBackendSettings(n_clusters=8)
        CustomBackendSettings(n_clusters=16)
        CustomBackendSettings(n_clusters=256)

        # Invalid values
        with pytest.raises(ValidationError):
            CustomBackendSettings(n_clusters=7)
        with pytest.raises(ValidationError):
            CustomBackendSettings(n_clusters=257)


class TestAppConfig:
    """Test AppConfig model."""

    def test_default_values(self):
        """Test AppConfig with all defaults."""
        config = AppConfig()
        assert config.logging.level == "INFO"
        assert config.generation.default_backend == "pywal"
        assert isinstance(config.backends, BackendSettings)

    def test_from_dict(self, sample_settings_dict):
        """Test creating AppConfig from dictionary."""
        config = AppConfig(**sample_settings_dict)
        assert config.logging.level == "DEBUG"
        assert config.generation.default_backend == "custom"
        assert config.generation.saturation_adjustment == 1.5


class TestSettingsModel:
    """Test SettingsModel loader."""

    def test_global_settings_loads(self):
        """Test that global Settings instance loads successfully."""
        config = Settings.get()
        assert isinstance(config, AppConfig)
        assert config.logging.level in [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]

    def test_convert_to_lowercase(self):
        """Test key conversion to lowercase."""
        input_dict = {"LOGGING": {"LEVEL": "INFO"}, "OUTPUT": {"DIRECTORY": "/tmp"}}
        result = SettingsModel._convert_dict_to_lower_case(input_dict)
        assert "logging" in result
        assert "LOGGING" not in result
        assert result["logging"]["level"] == "INFO"

    def test_resolve_environment_variables(self):
        """Test environment variable resolution."""
        import os

        os.environ["TEST_VAR"] = "test_value"
        input_dict = {"path": "$TEST_VAR/subdir"}
        result = SettingsModel._resolve_environment_variables(input_dict)
        assert result["path"] == "test_value/subdir"
```

**Step 3: Run tests**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_config.py -v
```

Expected: All tests pass

**Step 4: Check coverage**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_config.py --cov=src/color_scheme/config --cov-report=term
```

Expected: Coverage ≥ 95%

**Step 5: Commit**

Run:
```bash
cd ../..
git add packages/core/tests/
git commit -m "test(core): add comprehensive config system tests

Tests cover:
- Enums (Backend, ColorAlgorithm)
- All Pydantic models with validation
- Settings loader (dynaconf integration)
- Default values and overrides
- Environment variable resolution
- Case conversion

Coverage: 95%+ on config module.

Part of Phase 1: Foundation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Create Core CI Pipeline

**Files:**
- Create: `.github/workflows/ci-core.yml`

**Step 1: Create core CI workflow**

Create `.github/workflows/ci-core.yml`:
```yaml
name: Core Package CI

on:
  push:
    branches: ["**"]
    paths:
      - "packages/core/**"
      - "templates/**"
      - ".github/workflows/ci-core.yml"
  pull_request:
    branches: [develop, main]
    paths:
      - "packages/core/**"
      - "templates/**"

jobs:
  lint:
    name: Lint (Core)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: |
          cd packages/core
          uv sync --dev

      - name: Ruff check
        run: |
          cd packages/core
          uv run ruff check .

      - name: Black check
        run: |
          cd packages/core
          uv run black --check .

      - name: isort check
        run: |
          cd packages/core
          uv run isort --check .

      - name: mypy type check
        run: |
          cd packages/core
          uv run mypy src/

  security:
    name: Security Scan (Core)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: |
          cd packages/core
          uv sync --dev

      - name: Bandit security scan
        run: |
          cd packages/core
          uv run bandit -r src/ -f json -o bandit-report.json

      - name: Upload security report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: bandit-report-core
          path: packages/core/bandit-report.json

  test:
    name: Test (Core)
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.12", "3.13"]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: |
          cd packages/core
          uv sync --dev

      - name: Run tests with coverage
        run: |
          cd packages/core
          uv run pytest -n auto --cov=src --cov-report=xml --cov-report=term

      - name: Check coverage threshold
        run: |
          cd packages/core
          uv run coverage report --fail-under=95

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: packages/core/coverage.xml
          flags: core
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: false
```

**Step 2: Test workflow syntax**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci-core.yml'))"
```

Expected: No syntax errors

**Step 3: Commit**

Run:
```bash
git add .github/workflows/ci-core.yml
git commit -m "feat(ci): add core package CI pipeline

CI workflow for core package:
- Lint job: ruff, black, isort, mypy
- Security job: bandit scan
- Test job: matrix (Ubuntu/macOS, Python 3.12/3.13)
- Coverage check: ≥95% threshold

Runs on push to any branch and PRs to main/develop.

Implements design Section 7 (CI/CD).

Part of Phase 1: Foundation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Create Development Setup Script

**Files:**
- Create: `scripts/dev-setup.sh`

**Step 1: Create dev setup script**

Create `scripts/dev-setup.sh`:
```bash
#!/bin/bash
set -e

# Load utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

validate_repo_root
REPO_ROOT=$(get_repo_root)

print_section "Development Environment Setup"
echo "Setting up color-scheme development environment..."
echo ""

# Check prerequisites
print_info "Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3.12+ required"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if (( $(echo "$PYTHON_VERSION < 3.12" | bc -l) )); then
    print_error "Python 3.12+ required (found $PYTHON_VERSION)"
    exit 1
fi
print_success "Python $PYTHON_VERSION found"

if ! command_exists git; then
    print_error "Git required"
    exit 1
fi
print_success "Git found"

if command_exists docker; then
    print_success "Docker found (optional for orchestrator)"
elif command_exists podman; then
    print_success "Podman found (optional for orchestrator)"
else
    print_warning "Docker/Podman not found (optional for orchestrator)"
fi

echo ""

# Install uv if not present
if ! command_exists uv; then
    print_info "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    print_success "uv installed"
else
    print_success "uv already installed"
fi

echo ""

# Setup core package
print_info "Setting up core package..."
cd "$REPO_ROOT/packages/core"
uv sync --dev
print_success "Core package dependencies installed"

echo ""

# Setup orchestrator package
print_info "Setting up orchestrator package..."
cd "$REPO_ROOT/packages/orchestrator"
uv sync --dev
print_success "Orchestrator package dependencies installed"

cd "$REPO_ROOT"
echo ""

# Install pre-commit hooks
print_info "Installing pre-commit hooks..."
if ! command_exists pre-commit; then
    pip install pre-commit
fi
pre-commit install
print_success "Pre-commit hooks installed"

echo ""

# Create necessary directories
print_info "Creating directories..."
mkdir -p ~/.config/color-scheme/output
print_success "Created ~/.config/color-scheme/output"

echo ""

# Run initial tests
print_info "Running initial tests..."
cd "$REPO_ROOT/packages/core"
if uv run pytest --quiet 2>/dev/null; then
    print_success "Core tests passing"
else
    print_warning "Core tests failing (may be expected in early development)"
fi

cd "$REPO_ROOT"
echo ""

# Summary
print_section "Setup Complete"
print_success "Development environment ready!"
echo ""
echo "Next steps:"
echo "  1. Review settings.toml and customize (if needed)"
echo "  2. Create a feature branch:"
echo "     git checkout -b feature/core/your-feature develop"
echo "  3. Make changes and run tests:"
echo "     cd packages/core && uv run pytest"
echo "  4. See docs/development/verification-guide.md for workflow details"
echo ""
print_info "Run verification checks:"
echo "  ./scripts/verify-design-compliance.sh"
echo "  ./scripts/verify-documentation.sh"
```

**Step 2: Make script executable**

Run:
```bash
chmod +x scripts/dev-setup.sh
```

**Step 3: Test the script**

Run:
```bash
./scripts/dev-setup.sh
```

Expected: Script runs successfully, all checks pass

**Step 4: Commit**

Run:
```bash
git add scripts/dev-setup.sh
git commit -m "feat(scripts): add development environment setup script

Automated setup script that:
- Checks prerequisites (Python 3.12+, git, docker/podman)
- Installs uv package manager
- Sets up both packages with dev dependencies
- Installs pre-commit hooks
- Creates necessary directories
- Runs initial tests

Makes onboarding frictionless.

Implements design Section 9 (development setup).

Part of Phase 1: Foundation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Create Initial Documentation

**Files:**
- Create: `docs/user-guide/installation.md`
- Create: `docs/development/contributing.md`
- Modify: `README.md`

**Step 1: Create installation guide**

Create `docs/user-guide/installation.md`:
```markdown
# Installation Guide

## Core Package (Host Installation)

Install the core package directly on your system:

```bash
pip install color-scheme-core
```

**Requirements**:
- Python 3.12+
- Backend dependencies (install separately):
  - pywal: `pip install pywal`
  - wallust: Install from [wallust releases](https://github.com/dharmx/wallust)
  - custom: Included (no extra dependencies)

## Orchestrator Package (Containerized)

Install the orchestrator for containerized execution:

```bash
pip install color-scheme-orchestrator
```

**Requirements**:
- Python 3.12+
- Docker or Podman
- No backend dependencies needed (run in containers)

After installation, pull backend images:

```bash
color-scheme install pywal
color-scheme install wallust
color-scheme install custom
```

## Development Installation

Clone the repository:

```bash
git clone https://github.com/your-org/color-scheme.git
cd color-scheme
```

Run automated setup:

```bash
./scripts/dev-setup.sh
```

Or manual setup:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup core package
cd packages/core
uv sync --dev

# Setup orchestrator package
cd ../orchestrator
uv sync --dev

# Install pre-commit hooks
pre-commit install
```

## Verification

Verify installation:

```bash
# Check version
color-scheme --version

# Run tests (dev installation)
cd packages/core
uv run pytest
```

## Next Steps

- [Configuration Guide](configuration.md)
- [CLI Reference](cli-reference.md)
- [Backend Documentation](backends.md)
```

**Step 2: Create contributing guide**

Create `docs/development/contributing.md`:
```markdown
# Contributing Guide

Thank you for contributing to color-scheme!

## Development Workflow

### 1. Setup Development Environment

```bash
./scripts/dev-setup.sh
```

See [Installation Guide](../user-guide/installation.md) for details.

### 2. Create Feature Branch

```bash
git checkout develop
git pull
git checkout -b feature/core/your-feature
```

Branch naming convention:
- `feature/<package>/<description>` - New features
- `bugfix/<issue>-<description>` - Bug fixes
- `docs/<description>` - Documentation
- `refactor/<description>` - Code improvements

### 3. Make Changes

Follow these principles:
- **YAGNI**: Only implement what's needed
- **DRY**: Don't repeat yourself
- **TDD**: Write tests first

### 4. Write Tests

All code must have tests with ≥95% coverage:

```bash
cd packages/core
uv run pytest tests/unit/test_your_feature.py -v
uv run pytest --cov=src/color_scheme --cov-report=term
```

### 5. Update Documentation

- Update CHANGELOG.md
- Update relevant docs in `docs/`
- Add docstrings to public APIs

### 6. Run Verification

```bash
./scripts/verify-design-compliance.sh
./scripts/verify-documentation.sh
```

### 7. Commit Changes

Use Conventional Commits format:

```bash
git commit -m "feat(core): add new feature

Detailed description of changes.

Closes #123"
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `ci`

### 8. Create Pull Request

1. Push branch: `git push origin feature/core/your-feature`
2. Create PR on GitHub
3. Fill out PR template completely
4. Wait for CI to pass
5. Self-review using PR checklist

### 9. Merge

Once CI passes and self-review is complete, merge your PR.

## Code Standards

### Python Style

- Black formatting (88 char line length)
- isort for imports
- Ruff for linting
- Type hints where practical

Run formatters:

```bash
cd packages/core
uv run black .
uv run isort .
uv run ruff check --fix .
```

### Testing

- Unit tests for individual components
- Integration tests for end-to-end flows
- Use pytest fixtures for common setup
- Mock external dependencies

See [Testing Patterns](testing-patterns.md) for examples.

### Documentation

- Docstrings for all public APIs
- User-facing docs in `docs/user-guide/`
- Development docs in `docs/development/`
- Architecture decisions in `docs/knowledge-base/adrs/`

## Getting Help

- Check [Troubleshooting](../troubleshooting/common-issues.md)
- Review [Error Database](../troubleshooting/error-database.md)
- Open an issue on GitHub

## Design Compliance

All contributions must follow the design document:
- `docs/plans/2026-01-18-monorepo-architecture-design.md`

The verification scripts enforce this automatically.
```

**Step 3: Update main README**

Edit `README.md`:
```markdown
# color-scheme

CLI tool for extracting and generating color schemes from images.

## Features

- **Multiple Backends**: pywal, wallust, custom Python algorithm
- **Multiple Formats**: JSON, CSS, SCSS, YAML, shell scripts, GTK, rofi, terminal sequences
- **Flexible Deployment**: Run on host or in containers
- **Configurable**: Settings file with CLI overrides
- **Type-Safe**: Pydantic validation throughout

## Quick Start

### Installation

```bash
# Core package (host installation)
pip install color-scheme-core

# Orchestrator (containerized)
pip install color-scheme-orchestrator
```

### Usage

```bash
# Generate color scheme
color-scheme generate wallpaper.png

# Show color scheme
color-scheme show

# Use specific backend
color-scheme generate wallpaper.png --backend wallust
```

## Documentation

- [Installation Guide](docs/user-guide/installation.md)
- [Configuration Guide](docs/user-guide/configuration.md)
- [CLI Reference](docs/user-guide/cli-reference.md)
- [Backend Documentation](docs/user-guide/backends.md)
- [Contributing Guide](docs/development/contributing.md)

## Development

```bash
# Clone repository
git clone https://github.com/your-org/color-scheme.git
cd color-scheme

# Run setup script
./scripts/dev-setup.sh

# Run tests
cd packages/core
uv run pytest
```

See [Contributing Guide](docs/development/contributing.md) for full workflow.

## Architecture

This is a monorepo with two packages:

- **color-scheme-core**: Standalone color extraction and generation
- **color-scheme-orchestrator**: Container orchestration layer

Both expose the same `color-scheme` CLI. Choose based on your needs:
- Core: Direct installation, you manage dependencies
- Orchestrator: Containerized, isolated execution

See [Architecture Design](docs/plans/2026-01-18-monorepo-architecture-design.md) for details.

## Project Status

Current version: **Phase 1 (Foundation)** - v0.1.0

See [Implementation Progress](docs/implementation-progress.md) for roadmap.

## License

MIT
```

**Step 4: Commit**

Run:
```bash
git add docs/user-guide/installation.md docs/development/contributing.md README.md
git commit -m "docs: add installation and contributing guides, update README

Created initial documentation:
- Installation guide for both packages
- Contributing guide with full workflow
- Updated README with project overview

Provides essential documentation for users and contributors.

Part of Phase 1: Foundation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Verify Phase 1 Completion

**Files:**
- Modify: `docs/implementation-progress.md`

**Step 1: Run design compliance check**

Run:
```bash
./scripts/verify-design-compliance.sh
```

Expected: Should pass most checks now that structure is in place

**Step 2: Run documentation verification**

Run:
```bash
./scripts/verify-documentation.sh
```

Expected: Should pass with documentation in place

**Step 3: Run Phase 1 gate check**

Run:
```bash
./scripts/phase-gate-check.sh 1
```

Expected: All Phase 1 checks pass

**Step 4: Update implementation progress**

Edit `docs/implementation-progress.md`:

Mark Phase 1 as complete:
```markdown
## Phase 0: Verification Infrastructure ✅ COMPLETE

**Completion Date**: 2026-01-20

[... existing Phase 0 content ...]

---

## Phase 1: Foundation ✅ COMPLETE

**Goal**: Establish monorepo structure, CI/CD, and core package skeleton

**Completion Date**: 2026-01-20

**Tasks**:
- [x] Create monorepo directory structure
- [x] Initialize core package with pyproject.toml
- [x] Initialize orchestrator package with pyproject.toml
- [x] Implement settings system (dynaconf + Pydantic)
- [x] Create configuration tests (95%+ coverage)
- [x] Setup core CI pipeline
- [x] Create development setup script
- [x] Write initial documentation

**Design Compliance**:
- ✅ Monorepo structure (Section 1)
- ✅ Package structure (Section 9)
- ✅ Configuration system (Section 4)
- ✅ CI/CD pipeline (Section 7)
- ✅ Documentation (Section 5)

**Deliverables**:
- Both packages created with proper structure
- Settings system fully functional and tested
- CI pipeline running on GitHub Actions
- Development environment automated
- Core documentation in place

**Phase Gate**: PASSED

---

## Phase 2: Core Package - Backends

**Status**: 📝 PLANNED

**Goal**: Implement all three color extraction backends with full test coverage

**Planned Start**: 2026-01-21
```

**Step 5: Final commit**

Run:
```bash
git add docs/implementation-progress.md
git commit -m "docs(progress): mark Phase 1 foundation as complete

Phase 1 deliverables completed:
- Monorepo structure with both packages
- Configuration system with 95%+ test coverage
- CI pipeline for core package
- Development environment automation
- Initial documentation

Phase 1 gate check passing.
Ready to proceed to Phase 2: Core Backends.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Step 6: Create summary**

Run:
```bash
echo "Phase 1 Complete!"
echo ""
echo "Created:"
echo "  - Monorepo with core and orchestrator packages"
echo "  - Configuration system (dynaconf + Pydantic)"
echo "  - CI pipeline for core package"
echo "  - Development automation scripts"
echo "  - Documentation structure"
echo ""
echo "Verification:"
./scripts/phase-gate-check.sh 1
echo ""
echo "Next: Phase 2 - Implement color extraction backends"
```

---

## Completion

Phase 1 complete! You now have:

✅ **Monorepo structure** - Both packages properly organized
✅ **Configuration system** - Settings with validation and tests
✅ **CI/CD pipeline** - Automated testing on GitHub Actions
✅ **Development environment** - One-command setup
✅ **Documentation** - Installation, contributing, and architecture docs

All verification checks should pass.

---

**Plan saved to:** `docs/plans/2026-01-20-phase1-foundation.md`
