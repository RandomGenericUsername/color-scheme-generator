# Settings Layered Architecture Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the current single-file dynaconf+Pydantic config system with a multi-layer, namespace-aware settings architecture using a new shared `settings` package.

**Architecture:** A new `packages/settings/` package provides schema registration, TOML loading, deep merge, and CLI override infrastructure. Core and orchestrator register their schemas independently. Settings files are discovered from package defaults, project root, and user home, then deep-merged in priority order with CLI overrides on top.

**Tech Stack:** Python 3.12+, Pydantic v2, tomllib (stdlib), pytest

**Design doc:** `docs/plans/2026-01-30-settings-layered-architecture.md`

---

### Task 1: Create settings package scaffold

**Files:**
- Create: `packages/settings/pyproject.toml`
- Create: `packages/settings/src/color_scheme_settings/__init__.py`
- Create: `packages/settings/tests/__init__.py`
- Create: `packages/settings/tests/conftest.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "color-scheme-settings"
version = "0.1.0"
description = "Shared layered configuration system for color-scheme"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [
    { name = "Juan David", email = "jdavidth.01@gmail.com" }
]

dependencies = [
    "pydantic>=2.11.9",
]

[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.8.0",
    "mypy>=1.11.0",
    "black>=24.0.0",
    "ruff>=0.6.0",
    "isort>=5.13.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/color_scheme_settings"]

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

**Step 2: Create empty `__init__.py` for package and tests**

`packages/settings/src/color_scheme_settings/__init__.py`:
```python
"""Shared layered configuration system for color-scheme."""
```

`packages/settings/tests/__init__.py`: empty file

**Step 3: Create conftest.py with foundational fixtures**

`packages/settings/tests/conftest.py`:
```python
"""Shared fixtures for settings tests."""

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def tmp_settings_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure for settings files."""
    return tmp_path


@pytest.fixture
def core_defaults_toml(tmp_settings_dir: Path) -> Path:
    """Create a core package settings.toml (flat sections)."""
    content = """\
[logging]
level = "INFO"
show_time = true
show_path = false

[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]

[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

[backends.pywal]
backend_algorithm = "haishoku"

[backends.wallust]
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16
"""
    file_path = tmp_settings_dir / "core_settings.toml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def orchestrator_defaults_toml(tmp_settings_dir: Path) -> Path:
    """Create an orchestrator package settings.toml (flat sections)."""
    content = """\
[container]
engine = "docker"
"""
    file_path = tmp_settings_dir / "orchestrator_settings.toml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def project_root_toml(tmp_settings_dir: Path) -> Path:
    """Create a project root settings.toml (namespaced sections)."""
    content = """\
[core.generation]
default_backend = "wallust"

[core.output]
formats = ["json", "css", "yaml"]

[orchestrator.container]
engine = "podman"
"""
    file_path = tmp_settings_dir / "project_settings.toml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def user_config_toml(tmp_settings_dir: Path) -> Path:
    """Create a user config settings.toml (namespaced sections)."""
    content = """\
[core.generation]
saturation_adjustment = 1.3

[core.backends.custom]
n_clusters = 32
"""
    file_path = tmp_settings_dir / "user_settings.toml"
    file_path.write_text(content)
    return file_path
```

**Step 4: Verify package builds**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv sync`
Expected: dependencies installed, no errors

**Step 5: Commit**

```bash
git add packages/settings/
git commit -m "feat(settings): scaffold shared settings package"
```

---

### Task 2: Implement error hierarchy

**Files:**
- Create: `packages/settings/tests/test_errors.py`
- Create: `packages/settings/src/color_scheme_settings/errors.py`

**Step 1: Write the failing tests**

`packages/settings/tests/test_errors.py`:
```python
"""Tests for settings error hierarchy."""

from pathlib import Path

from color_scheme_settings.errors import (
    SettingsError,
    SettingsFileError,
    SettingsOverrideError,
    SettingsRegistryError,
    SettingsValidationError,
)


class TestSettingsErrorHierarchy:
    """All errors inherit from SettingsError."""

    def test_settings_file_error_is_settings_error(self):
        err = SettingsFileError(file_path=Path("/bad.toml"), reason="parse error")
        assert isinstance(err, SettingsError)

    def test_settings_validation_error_is_settings_error(self):
        err = SettingsValidationError(
            namespace="core", validation_error=None, source_layer="user"
        )
        assert isinstance(err, SettingsError)

    def test_settings_override_error_is_settings_error(self):
        err = SettingsOverrideError(key="core.bad.key")
        assert isinstance(err, SettingsError)

    def test_settings_registry_error_is_settings_error(self):
        err = SettingsRegistryError(namespace="core")
        assert isinstance(err, SettingsError)


class TestSettingsFileError:
    """SettingsFileError carries file path and reason."""

    def test_attributes(self):
        err = SettingsFileError(file_path=Path("/bad.toml"), reason="invalid syntax")
        assert err.file_path == Path("/bad.toml")
        assert err.reason == "invalid syntax"

    def test_str_contains_path_and_reason(self):
        err = SettingsFileError(file_path=Path("/bad.toml"), reason="invalid syntax")
        msg = str(err)
        assert "/bad.toml" in msg
        assert "invalid syntax" in msg


class TestSettingsValidationError:
    """SettingsValidationError carries namespace and layer context."""

    def test_attributes(self):
        err = SettingsValidationError(
            namespace="core", validation_error=None, source_layer="project"
        )
        assert err.namespace == "core"
        assert err.source_layer == "project"
        assert err.validation_error is None

    def test_str_contains_namespace(self):
        err = SettingsValidationError(
            namespace="core", validation_error=None, source_layer="user"
        )
        assert "core" in str(err)


class TestSettingsOverrideError:
    """SettingsOverrideError carries the bad key path."""

    def test_attributes(self):
        err = SettingsOverrideError(key="core.output.nonexistent")
        assert err.key == "core.output.nonexistent"

    def test_str_contains_key(self):
        err = SettingsOverrideError(key="core.output.nonexistent")
        assert "core.output.nonexistent" in str(err)


class TestSettingsRegistryError:
    """SettingsRegistryError carries the namespace."""

    def test_attributes(self):
        err = SettingsRegistryError(namespace="core")
        assert err.namespace == "core"

    def test_str_contains_namespace(self):
        err = SettingsRegistryError(namespace="core")
        assert "core" in str(err)
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_errors.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'color_scheme_settings.errors'`

**Step 3: Implement errors.py**

`packages/settings/src/color_scheme_settings/errors.py`:
```python
"""Error hierarchy for the settings system."""

from pathlib import Path
from typing import Any


class SettingsError(Exception):
    """Base exception for all settings errors."""


class SettingsFileError(SettingsError):
    """TOML file cannot be read or parsed.

    Raised for malformed TOML syntax or file permission issues.
    NOT raised for missing files (missing files are silently skipped).
    """

    def __init__(self, file_path: Path, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to load {file_path}: {reason}")


class SettingsValidationError(SettingsError):
    """Merged config fails Pydantic validation.

    Includes layer attribution to help the user identify which file
    introduced the invalid value.
    """

    def __init__(
        self,
        namespace: str,
        validation_error: Any,
        source_layer: str | None = None,
    ) -> None:
        self.namespace = namespace
        self.validation_error = validation_error
        self.source_layer = source_layer
        layer_info = f" (from {source_layer} layer)" if source_layer else ""
        super().__init__(
            f"Validation failed for '{namespace}' namespace{layer_info}: "
            f"{validation_error}"
        )


class SettingsOverrideError(SettingsError):
    """CLI override targets a nonexistent key path.

    Catches typos early rather than silently ignoring bad keys.
    """

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Override key path does not exist: {key}")


class SettingsRegistryError(SettingsError):
    """Namespace conflict or missing registration."""

    def __init__(self, namespace: str, reason: str = "") -> None:
        self.namespace = namespace
        detail = f": {reason}" if reason else ""
        super().__init__(f"Registry error for namespace '{namespace}'{detail}")
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_errors.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add packages/settings/src/color_scheme_settings/errors.py packages/settings/tests/test_errors.py
git commit -m "feat(settings): add error hierarchy"
```

---

### Task 3: Implement schema registry

**Files:**
- Create: `packages/settings/tests/test_registry.py`
- Create: `packages/settings/src/color_scheme_settings/registry.py`

**Step 1: Write the failing tests**

`packages/settings/tests/test_registry.py`:
```python
"""Tests for the schema registry."""

from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from color_scheme_settings.errors import SettingsRegistryError
from color_scheme_settings.registry import SchemaEntry, SchemaRegistry


class MockCoreConfig(BaseModel):
    """Mock core config for testing."""

    level: str = Field(default="INFO")


class MockOrchestratorConfig(BaseModel):
    """Mock orchestrator config for testing."""

    engine: str = Field(default="docker")


@pytest.fixture(autouse=True)
def clean_registry():
    """Reset registry before each test."""
    SchemaRegistry._entries.clear()
    yield
    SchemaRegistry._entries.clear()


class TestSchemaEntry:
    """Tests for SchemaEntry dataclass."""

    def test_create_entry(self, tmp_path: Path):
        entry = SchemaEntry(
            namespace="core",
            model=MockCoreConfig,
            defaults_file=tmp_path / "settings.toml",
        )
        assert entry.namespace == "core"
        assert entry.model is MockCoreConfig
        assert entry.defaults_file == tmp_path / "settings.toml"


class TestSchemaRegistryRegister:
    """Tests for registering schemas."""

    def test_register_single_namespace(self, tmp_path: Path):
        SchemaRegistry.register(
            namespace="core",
            model=MockCoreConfig,
            defaults_file=tmp_path / "settings.toml",
        )
        entry = SchemaRegistry.get("core")
        assert entry.namespace == "core"
        assert entry.model is MockCoreConfig

    def test_register_multiple_namespaces(self, tmp_path: Path):
        SchemaRegistry.register("core", MockCoreConfig, tmp_path / "core.toml")
        SchemaRegistry.register("orchestrator", MockOrchestratorConfig, tmp_path / "orch.toml")
        assert SchemaRegistry.get("core").model is MockCoreConfig
        assert SchemaRegistry.get("orchestrator").model is MockOrchestratorConfig

    def test_register_duplicate_raises_error(self, tmp_path: Path):
        SchemaRegistry.register("core", MockCoreConfig, tmp_path / "settings.toml")
        with pytest.raises(SettingsRegistryError):
            SchemaRegistry.register("core", MockCoreConfig, tmp_path / "settings.toml")


class TestSchemaRegistryGet:
    """Tests for retrieving schemas."""

    def test_get_registered_namespace(self, tmp_path: Path):
        SchemaRegistry.register("core", MockCoreConfig, tmp_path / "settings.toml")
        entry = SchemaRegistry.get("core")
        assert entry.namespace == "core"

    def test_get_unregistered_raises_error(self):
        with pytest.raises(SettingsRegistryError):
            SchemaRegistry.get("nonexistent")


class TestSchemaRegistryListings:
    """Tests for listing registered schemas."""

    def test_all_namespaces_empty(self):
        assert SchemaRegistry.all_namespaces() == []

    def test_all_namespaces(self, tmp_path: Path):
        SchemaRegistry.register("core", MockCoreConfig, tmp_path / "core.toml")
        SchemaRegistry.register("orchestrator", MockOrchestratorConfig, tmp_path / "orch.toml")
        namespaces = SchemaRegistry.all_namespaces()
        assert "core" in namespaces
        assert "orchestrator" in namespaces

    def test_all_entries_empty(self):
        assert SchemaRegistry.all_entries() == []

    def test_all_entries(self, tmp_path: Path):
        SchemaRegistry.register("core", MockCoreConfig, tmp_path / "core.toml")
        entries = SchemaRegistry.all_entries()
        assert len(entries) == 1
        assert entries[0].namespace == "core"


class TestSchemaRegistryClear:
    """Tests for clearing the registry."""

    def test_clear_removes_all(self, tmp_path: Path):
        SchemaRegistry.register("core", MockCoreConfig, tmp_path / "settings.toml")
        SchemaRegistry.clear()
        assert SchemaRegistry.all_namespaces() == []
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_registry.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'color_scheme_settings.registry'`

**Step 3: Implement registry.py**

`packages/settings/src/color_scheme_settings/registry.py`:
```python
"""Schema registration system for namespace-based configuration."""

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from color_scheme_settings.errors import SettingsRegistryError


@dataclass
class SchemaEntry:
    """A registered configuration schema."""

    namespace: str
    model: type[BaseModel]
    defaults_file: Path


class SchemaRegistry:
    """Registry for configuration schemas.

    Each package registers its namespace, Pydantic model, and defaults file.
    The registry has zero knowledge of specific schemas.
    """

    _entries: dict[str, SchemaEntry] = {}

    @classmethod
    def register(
        cls,
        namespace: str,
        model: type[BaseModel],
        defaults_file: Path,
    ) -> None:
        """Register a package's config schema.

        Args:
            namespace: Unique namespace identifier (e.g., "core", "orchestrator")
            model: Pydantic model class for validation
            defaults_file: Path to the package's settings.toml

        Raises:
            SettingsRegistryError: If namespace is already registered
        """
        if namespace in cls._entries:
            raise SettingsRegistryError(
                namespace=namespace,
                reason="namespace already registered",
            )
        cls._entries[namespace] = SchemaEntry(
            namespace=namespace,
            model=model,
            defaults_file=defaults_file,
        )

    @classmethod
    def get(cls, namespace: str) -> SchemaEntry:
        """Retrieve a registered schema by namespace.

        Raises:
            SettingsRegistryError: If namespace is not registered
        """
        if namespace not in cls._entries:
            raise SettingsRegistryError(
                namespace=namespace,
                reason="namespace not registered",
            )
        return cls._entries[namespace]

    @classmethod
    def all_entries(cls) -> list[SchemaEntry]:
        """Return all registered entries."""
        return list(cls._entries.values())

    @classmethod
    def all_namespaces(cls) -> list[str]:
        """Return all registered namespace names."""
        return list(cls._entries.keys())

    @classmethod
    def clear(cls) -> None:
        """Remove all registered schemas. Used for testing."""
        cls._entries.clear()
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_registry.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add packages/settings/src/color_scheme_settings/registry.py packages/settings/tests/test_registry.py
git commit -m "feat(settings): add schema registry"
```

---

### Task 4: Implement deep merge algorithm

**Files:**
- Create: `packages/settings/tests/test_merger.py`
- Create: `packages/settings/src/color_scheme_settings/merger.py`

**Step 1: Write the failing tests**

`packages/settings/tests/test_merger.py`:
```python
"""Tests for the deep merge algorithm."""

from color_scheme_settings.merger import deep_merge, merge_layers
from color_scheme_settings.loader import LayerSource


class TestDeepMerge:
    """Tests for deep_merge function."""

    def test_empty_base(self):
        result = deep_merge({}, {"a": 1})
        assert result == {"a": 1}

    def test_empty_override(self):
        result = deep_merge({"a": 1}, {})
        assert result == {"a": 1}

    def test_both_empty(self):
        result = deep_merge({}, {})
        assert result == {}

    def test_scalar_override(self):
        result = deep_merge({"a": 1}, {"a": 2})
        assert result == {"a": 2}

    def test_base_keys_preserved(self):
        result = deep_merge({"a": 1, "b": 2}, {"a": 10})
        assert result == {"a": 10, "b": 2}

    def test_new_keys_added(self):
        result = deep_merge({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_nested_dict_merge(self):
        base = {"section": {"key1": "v1", "key2": "v2"}}
        override = {"section": {"key2": "override"}}
        result = deep_merge(base, override)
        assert result == {"section": {"key1": "v1", "key2": "override"}}

    def test_deeply_nested_merge(self):
        base = {"a": {"b": {"c": 1, "d": 2}}}
        override = {"a": {"b": {"c": 10}}}
        result = deep_merge(base, override)
        assert result == {"a": {"b": {"c": 10, "d": 2}}}

    def test_list_replaced_entirely(self):
        base = {"formats": ["json", "css", "yaml"]}
        override = {"formats": ["json"]}
        result = deep_merge(base, override)
        assert result == {"formats": ["json"]}

    def test_list_in_nested_dict_replaced(self):
        base = {"output": {"formats": ["json", "css", "yaml"]}}
        override = {"output": {"formats": ["json"]}}
        result = deep_merge(base, override)
        assert result == {"output": {"formats": ["json"]}}

    def test_dict_overrides_scalar(self):
        base = {"a": "string"}
        override = {"a": {"nested": True}}
        result = deep_merge(base, override)
        assert result == {"a": {"nested": True}}

    def test_scalar_overrides_dict(self):
        base = {"a": {"nested": True}}
        override = {"a": "string"}
        result = deep_merge(base, override)
        assert result == {"a": "string"}

    def test_does_not_mutate_base(self):
        base = {"a": 1, "b": {"c": 2}}
        base_copy = {"a": 1, "b": {"c": 2}}
        deep_merge(base, {"a": 10, "b": {"c": 20}})
        assert base == base_copy

    def test_does_not_mutate_override(self):
        override = {"a": {"b": 1}}
        override_copy = {"a": {"b": 1}}
        deep_merge({"a": {"b": 0}}, override)
        assert override == override_copy


class TestMergeLayers:
    """Tests for merge_layers function."""

    def test_empty_layers(self):
        result = merge_layers([])
        assert result == {}

    def test_single_layer(self):
        layers = [
            LayerSource(
                layer="package",
                namespace="core",
                file_path=None,
                data={"logging": {"level": "INFO"}},
            )
        ]
        result = merge_layers(layers)
        assert result == {"core": {"logging": {"level": "INFO"}}}

    def test_two_layers_same_namespace(self):
        layers = [
            LayerSource(
                layer="package",
                namespace="core",
                file_path=None,
                data={"generation": {"default_backend": "pywal", "saturation_adjustment": 1.0}},
            ),
            LayerSource(
                layer="project",
                namespace="core",
                file_path=None,
                data={"generation": {"saturation_adjustment": 1.3}},
            ),
        ]
        result = merge_layers(layers)
        assert result["core"]["generation"]["default_backend"] == "pywal"
        assert result["core"]["generation"]["saturation_adjustment"] == 1.3

    def test_multiple_namespaces(self):
        layers = [
            LayerSource(layer="package", namespace="core", file_path=None, data={"logging": {"level": "INFO"}}),
            LayerSource(layer="package", namespace="orchestrator", file_path=None, data={"container": {"engine": "docker"}}),
        ]
        result = merge_layers(layers)
        assert "core" in result
        assert "orchestrator" in result
        assert result["core"]["logging"]["level"] == "INFO"
        assert result["orchestrator"]["container"]["engine"] == "docker"

    def test_three_layers_priority_order(self):
        """Package → Project → User, each overriding fields."""
        layers = [
            LayerSource(
                layer="package",
                namespace="core",
                file_path=None,
                data={
                    "generation": {"default_backend": "pywal", "saturation_adjustment": 1.0},
                    "output": {"formats": ["json", "css", "yaml"]},
                },
            ),
            LayerSource(
                layer="project",
                namespace="core",
                file_path=None,
                data={"generation": {"saturation_adjustment": 1.3}},
            ),
            LayerSource(
                layer="user",
                namespace="core",
                file_path=None,
                data={"output": {"formats": ["json"]}},
            ),
        ]
        result = merge_layers(layers)
        assert result["core"]["generation"]["default_backend"] == "pywal"
        assert result["core"]["generation"]["saturation_adjustment"] == 1.3
        assert result["core"]["output"]["formats"] == ["json"]
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_merger.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement merger.py and LayerSource in loader.py**

`packages/settings/src/color_scheme_settings/loader.py` (partial — just the dataclass for now):
```python
"""Settings layer discovery and TOML loading."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LayerSource:
    """A single settings layer loaded from a file."""

    layer: str
    namespace: str
    file_path: Path | None
    data: dict[str, Any]
```

`packages/settings/src/color_scheme_settings/merger.py`:
```python
"""Deep merge algorithm for layered settings."""

from typing import Any

from color_scheme_settings.loader import LayerSource


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base. Returns a new dict.

    Rules:
    - Dicts: recurse into matching keys, base keys preserved if not overridden
    - Lists: replaced entirely (atomic)
    - Scalars: replaced entirely
    - Keys in override not in base: added
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def merge_layers(layers: list[LayerSource]) -> dict[str, dict[str, Any]]:
    """Merge all layers into one dict per namespace.

    Layers must arrive in priority order (lowest priority first).

    Returns:
        Dict mapping namespace to merged settings dict.
        Example: {"core": {...merged...}, "orchestrator": {...merged...}}
    """
    merged: dict[str, dict[str, Any]] = {}
    for layer in layers:
        ns = layer.namespace
        if ns not in merged:
            merged[ns] = {}
        merged[ns] = deep_merge(merged[ns], layer.data)
    return merged
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_merger.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add packages/settings/src/color_scheme_settings/merger.py packages/settings/src/color_scheme_settings/loader.py packages/settings/tests/test_merger.py
git commit -m "feat(settings): add deep merge algorithm"
```

---

### Task 5: Implement settings loader

**Files:**
- Create: `packages/settings/tests/test_loader.py`
- Modify: `packages/settings/src/color_scheme_settings/loader.py`

**Step 1: Write the failing tests**

`packages/settings/tests/test_loader.py`:
```python
"""Tests for settings layer discovery and TOML loading."""

from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from color_scheme_settings.errors import SettingsFileError
from color_scheme_settings.loader import LayerSource, SettingsLoader, load_toml
from color_scheme_settings.registry import SchemaRegistry


class MockCoreConfig(BaseModel):
    level: str = Field(default="INFO")


class MockOrchestratorConfig(BaseModel):
    engine: str = Field(default="docker")


@pytest.fixture(autouse=True)
def clean_registry():
    SchemaRegistry.clear()
    yield
    SchemaRegistry.clear()


class TestLoadToml:
    """Tests for TOML file loading."""

    def test_load_valid_toml(self, tmp_path: Path):
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('[section]\nkey = "value"\n')
        result = load_toml(toml_file)
        assert result == {"section": {"key": "value"}}

    def test_load_malformed_toml_raises_error(self, tmp_path: Path):
        toml_file = tmp_path / "bad.toml"
        toml_file.write_text("this is not [[ valid toml")
        with pytest.raises(SettingsFileError) as exc_info:
            load_toml(toml_file)
        assert exc_info.value.file_path == toml_file

    def test_load_permission_error(self, tmp_path: Path):
        toml_file = tmp_path / "noperm.toml"
        toml_file.write_text('[section]\nkey = "value"\n')
        toml_file.chmod(0o000)
        with pytest.raises(SettingsFileError):
            load_toml(toml_file)
        toml_file.chmod(0o644)  # cleanup


class TestSettingsLoaderPackageLayer:
    """Tests for discovering package-level settings files."""

    def test_discovers_package_defaults(self, core_defaults_toml: Path):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        loader = SettingsLoader(project_root=None, user_config_path=None)
        layers = loader.discover_layers()
        core_layers = [l for l in layers if l.namespace == "core"]
        assert len(core_layers) == 1
        assert core_layers[0].layer == "package"
        assert "logging" in core_layers[0].data

    def test_missing_package_file_skipped(self, tmp_path: Path):
        SchemaRegistry.register("core", MockCoreConfig, tmp_path / "nonexistent.toml")
        loader = SettingsLoader(project_root=None, user_config_path=None)
        layers = loader.discover_layers()
        assert len(layers) == 0


class TestSettingsLoaderProjectLayer:
    """Tests for discovering project root settings file."""

    def test_discovers_project_root_namespaced(
        self, core_defaults_toml: Path, project_root_toml: Path
    ):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        SchemaRegistry.register("orchestrator", MockOrchestratorConfig, core_defaults_toml)
        loader = SettingsLoader(
            project_root=project_root_toml.parent,
            user_config_path=None,
        )
        layers = loader.discover_layers()
        project_layers = [l for l in layers if l.layer == "project"]
        assert len(project_layers) >= 1

    def test_no_project_root_no_project_layers(self, core_defaults_toml: Path):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        loader = SettingsLoader(project_root=None, user_config_path=None)
        layers = loader.discover_layers()
        project_layers = [l for l in layers if l.layer == "project"]
        assert len(project_layers) == 0


class TestSettingsLoaderUserLayer:
    """Tests for discovering user config settings file."""

    def test_discovers_user_config(
        self, core_defaults_toml: Path, user_config_toml: Path
    ):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        loader = SettingsLoader(
            project_root=None,
            user_config_path=user_config_toml,
        )
        layers = loader.discover_layers()
        user_layers = [l for l in layers if l.layer == "user"]
        assert len(user_layers) >= 1

    def test_missing_user_config_skipped(self, core_defaults_toml: Path, tmp_path: Path):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        loader = SettingsLoader(
            project_root=None,
            user_config_path=tmp_path / "nonexistent.toml",
        )
        layers = loader.discover_layers()
        user_layers = [l for l in layers if l.layer == "user"]
        assert len(user_layers) == 0


class TestSettingsLoaderLayerOrdering:
    """Tests that layers arrive in correct priority order."""

    def test_package_before_project_before_user(
        self,
        core_defaults_toml: Path,
        project_root_toml: Path,
        user_config_toml: Path,
    ):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        loader = SettingsLoader(
            project_root=project_root_toml.parent,
            user_config_path=user_config_toml,
        )
        layers = loader.discover_layers()
        core_layers = [l for l in layers if l.namespace == "core"]
        layer_names = [l.layer for l in core_layers]
        assert layer_names == ["package", "project", "user"]
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_loader.py -v`
Expected: FAIL — `ImportError: cannot import name 'SettingsLoader'`

**Step 3: Implement the full loader.py**

Replace `packages/settings/src/color_scheme_settings/loader.py`:
```python
"""Settings layer discovery and TOML loading."""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from color_scheme_settings.errors import SettingsFileError
from color_scheme_settings.registry import SchemaRegistry


@dataclass
class LayerSource:
    """A single settings layer loaded from a file."""

    layer: str
    namespace: str
    file_path: Path | None
    data: dict[str, Any]


def load_toml(file_path: Path) -> dict[str, Any]:
    """Load and parse a TOML file.

    Args:
        file_path: Path to the TOML file

    Returns:
        Parsed TOML as a dictionary

    Raises:
        SettingsFileError: If file cannot be read or parsed
    """
    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise SettingsFileError(file_path=file_path, reason=str(e)) from e
    except OSError as e:
        raise SettingsFileError(file_path=file_path, reason=str(e)) from e


class SettingsLoader:
    """Discovers and loads settings files from all layers.

    Layers (lowest to highest priority):
    1. Package defaults — flat sections, namespace inferred from registry
    2. Project root — namespaced sections ([core.*], [orchestrator.*])
    3. User config — namespaced sections ([core.*], [orchestrator.*])

    Args:
        project_root: Path to project root directory (contains settings.toml).
                      If None, project layer is skipped.
        user_config_path: Path to user settings file.
                          If None, defaults to ~/.config/color-scheme/settings.toml.
    """

    def __init__(
        self,
        project_root: Path | None = None,
        user_config_path: Path | None = None,
    ) -> None:
        self.project_root = project_root
        self.user_config_path = (
            user_config_path
            if user_config_path is not None
            else Path.home() / ".config" / "color-scheme" / "settings.toml"
        )

    def discover_layers(self) -> list[LayerSource]:
        """Discover all settings files across all layers.

        Returns:
            List of LayerSource objects in priority order (lowest first).
        """
        layers: list[LayerSource] = []

        # Layer 1: Package defaults (flat sections)
        for entry in SchemaRegistry.all_entries():
            if entry.defaults_file.exists():
                data = load_toml(entry.defaults_file)
                layers.append(
                    LayerSource(
                        layer="package",
                        namespace=entry.namespace,
                        file_path=entry.defaults_file,
                        data=data,
                    )
                )

        # Layer 2: Project root (namespaced sections)
        if self.project_root is not None:
            project_file = self.project_root / "settings.toml"
            if project_file.exists():
                data = load_toml(project_file)
                for ns in SchemaRegistry.all_namespaces():
                    if ns in data:
                        layers.append(
                            LayerSource(
                                layer="project",
                                namespace=ns,
                                file_path=project_file,
                                data=data[ns],
                            )
                        )

        # Layer 3: User config (namespaced sections)
        if self.user_config_path is not None and self.user_config_path.exists():
            data = load_toml(self.user_config_path)
            for ns in SchemaRegistry.all_namespaces():
                if ns in data:
                    layers.append(
                        LayerSource(
                            layer="user",
                            namespace=ns,
                            file_path=self.user_config_path,
                            data=data[ns],
                        )
                    )

        return layers
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_loader.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add packages/settings/src/color_scheme_settings/loader.py packages/settings/tests/test_loader.py
git commit -m "feat(settings): add layer discovery and TOML loader"
```

---

### Task 6: Implement CLI overrides

**Files:**
- Create: `packages/settings/tests/test_overrides.py`
- Create: `packages/settings/src/color_scheme_settings/overrides.py`

**Step 1: Write the failing tests**

`packages/settings/tests/test_overrides.py`:
```python
"""Tests for CLI override mechanism."""

from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict, Field

from color_scheme_settings.errors import SettingsOverrideError
from color_scheme_settings.overrides import apply_overrides


class MockLogging(BaseModel):
    level: str = Field(default="INFO")


class MockOutput(BaseModel):
    directory: Path = Field(default=Path("/default/output"))
    formats: list[str] = Field(default_factory=lambda: ["json", "css"])


class MockGeneration(BaseModel):
    default_backend: str = Field(default="pywal")
    saturation_adjustment: float = Field(default=1.0, ge=0.0, le=2.0)


class MockCoreConfig(BaseModel):
    logging: MockLogging = Field(default_factory=MockLogging)
    output: MockOutput = Field(default_factory=MockOutput)
    generation: MockGeneration = Field(default_factory=MockGeneration)


class MockContainer(BaseModel):
    engine: str = Field(default="docker")


class MockUnifiedConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    core: MockCoreConfig
    orchestrator: MockContainer


@pytest.fixture
def base_config() -> MockUnifiedConfig:
    return MockUnifiedConfig(
        core=MockCoreConfig(),
        orchestrator=MockContainer(),
    )


class TestApplyOverrides:
    """Tests for applying CLI overrides."""

    def test_override_scalar(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {"core.generation.saturation_adjustment": 1.5},
        )
        assert result.core.generation.saturation_adjustment == 1.5

    def test_override_path(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {"core.output.directory": Path("/custom/output")},
        )
        assert result.core.output.directory == Path("/custom/output")

    def test_override_list(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {"core.output.formats": ["json"]},
        )
        assert result.core.output.formats == ["json"]

    def test_override_orchestrator(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {"orchestrator.engine": "podman"},
        )
        assert result.orchestrator.engine == "podman"

    def test_multiple_overrides(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {
                "core.generation.saturation_adjustment": 0.5,
                "core.output.formats": ["yaml"],
                "orchestrator.engine": "podman",
            },
        )
        assert result.core.generation.saturation_adjustment == 0.5
        assert result.core.output.formats == ["yaml"]
        assert result.orchestrator.engine == "podman"

    def test_nonexistent_key_raises_error(self, base_config: MockUnifiedConfig):
        with pytest.raises(SettingsOverrideError) as exc_info:
            apply_overrides(base_config, {"core.nonexistent.key": "value"})
        assert "core.nonexistent.key" in str(exc_info.value)

    def test_nonexistent_leaf_raises_error(self, base_config: MockUnifiedConfig):
        with pytest.raises(SettingsOverrideError):
            apply_overrides(base_config, {"core.generation.nonexistent": 1.0})

    def test_original_not_mutated(self, base_config: MockUnifiedConfig):
        apply_overrides(
            base_config,
            {"core.generation.saturation_adjustment": 1.5},
        )
        assert base_config.core.generation.saturation_adjustment == 1.0

    def test_empty_overrides_returns_equivalent(self, base_config: MockUnifiedConfig):
        result = apply_overrides(base_config, {})
        assert result.core.generation.saturation_adjustment == base_config.core.generation.saturation_adjustment
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_overrides.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement overrides.py**

`packages/settings/src/color_scheme_settings/overrides.py`:
```python
"""CLI override application for validated config objects."""

from typing import Any

from pydantic import BaseModel

from color_scheme_settings.errors import SettingsOverrideError


def apply_overrides(
    config: BaseModel,
    overrides: dict[str, Any],
) -> BaseModel:
    """Apply CLI argument overrides to a validated config.

    Keys use dot notation with namespace prefix:
        "core.generation.saturation_adjustment" -> 1.5
        "core.output.directory" -> Path("/tmp/out")
        "orchestrator.engine" -> "podman"

    Args:
        config: Validated config object (must have model_dump and model_validate)
        overrides: Dict of dotted key paths to override values

    Returns:
        New config instance with overrides applied and re-validated.

    Raises:
        SettingsOverrideError: If a key path doesn't exist in the config.
    """
    if not overrides:
        return config

    config_dict = config.model_dump()

    for dotted_key, value in overrides.items():
        parts = dotted_key.split(".")
        target = config_dict

        # Walk to the parent of the leaf key
        for segment in parts[:-1]:
            if not isinstance(target, dict) or segment not in target:
                raise SettingsOverrideError(key=dotted_key)
            target = target[segment]

        # Set the leaf value
        leaf = parts[-1]
        if not isinstance(target, dict) or leaf not in target:
            raise SettingsOverrideError(key=dotted_key)
        target[leaf] = value

    # Re-validate through Pydantic
    return config.__class__.model_validate(config_dict)
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_overrides.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add packages/settings/src/color_scheme_settings/overrides.py packages/settings/tests/test_overrides.py
git commit -m "feat(settings): add CLI override mechanism"
```

---

### Task 7: Implement UnifiedConfig and public API

**Files:**
- Create: `packages/settings/tests/test_unified.py`
- Create: `packages/settings/src/color_scheme_settings/transforms.py`
- Create: `packages/settings/src/color_scheme_settings/unified.py`
- Modify: `packages/settings/src/color_scheme_settings/__init__.py`

**Step 1: Write the failing tests**

`packages/settings/tests/test_unified.py`:
```python
"""Tests for UnifiedConfig construction and transforms."""

import os
from typing import Any

import pytest

from color_scheme_settings.transforms import (
    convert_keys_to_lowercase,
    resolve_environment_variables,
)


class TestConvertKeysToLowercase:
    """Tests for recursive key lowercasing."""

    def test_simple_dict(self):
        result = convert_keys_to_lowercase({"LEVEL": "INFO"})
        assert result == {"level": "INFO"}

    def test_nested_dict(self):
        result = convert_keys_to_lowercase({"BACKENDS": {"PYWAL": {"ALGO": "haishoku"}}})
        assert result == {"backends": {"pywal": {"algo": "haishoku"}}}

    def test_values_unchanged(self):
        result = convert_keys_to_lowercase({"KEY": "VALUE_UNCHANGED"})
        assert result["key"] == "VALUE_UNCHANGED"

    def test_empty_dict(self):
        assert convert_keys_to_lowercase({}) == {}

    def test_list_values_unchanged(self):
        result = convert_keys_to_lowercase({"FORMATS": ["JSON", "CSS"]})
        assert result["formats"] == ["JSON", "CSS"]


class TestResolveEnvironmentVariables:
    """Tests for environment variable resolution."""

    def test_resolve_home(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("HOME", "/home/testuser")
        result = resolve_environment_variables(
            {"directory": "$HOME/.config/color-scheme"}
        )
        assert result["directory"] == "/home/testuser/.config/color-scheme"

    def test_resolve_nested(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("HOME", "/home/testuser")
        result = resolve_environment_variables(
            {"output": {"directory": "$HOME/output"}}
        )
        assert result["output"]["directory"] == "/home/testuser/output"

    def test_resolve_in_list(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("HOME", "/home/testuser")
        result = resolve_environment_variables(
            {"paths": ["$HOME/a", "$HOME/b"]}
        )
        assert result["paths"] == ["/home/testuser/a", "/home/testuser/b"]

    def test_non_string_values_unchanged(self):
        result = resolve_environment_variables(
            {"number": 42, "boolean": True, "none": None}
        )
        assert result["number"] == 42
        assert result["boolean"] is True
        assert result["none"] is None

    def test_empty_dict(self):
        assert resolve_environment_variables({}) == {}
```

**Step 2: Run tests to verify they fail**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_unified.py -v`
Expected: FAIL

**Step 3: Implement transforms.py**

`packages/settings/src/color_scheme_settings/transforms.py`:
```python
"""Data transformations for settings dictionaries."""

import os
from typing import Any


def convert_keys_to_lowercase(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively convert all dictionary keys to lowercase.

    Values are preserved as-is, including string values.
    """
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key.lower()] = convert_keys_to_lowercase(value)
        else:
            result[key.lower()] = value
    return result


def resolve_environment_variables(data: dict[str, Any]) -> dict[str, Any]:
    """Resolve environment variables ($HOME, $USER, etc.) in string values.

    Recursively processes nested dicts and lists.
    Non-string values pass through unchanged.
    """

    def _resolve(value: Any) -> Any:
        if isinstance(value, str):
            return os.path.expandvars(value)
        elif isinstance(value, dict):
            return {k: _resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_resolve(item) for item in value]
        return value

    return _resolve(data)
```

**Step 4: Run tests to verify they pass**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_unified.py -v`
Expected: All PASS

**Step 5: Implement unified.py and update __init__.py**

`packages/settings/src/color_scheme_settings/unified.py`:
```python
"""UnifiedConfig construction from merged layers."""

from typing import Any

from pydantic import BaseModel

from color_scheme_settings.errors import SettingsValidationError
from color_scheme_settings.registry import SchemaRegistry
from color_scheme_settings.transforms import (
    convert_keys_to_lowercase,
    resolve_environment_variables,
)


def build_validated_namespace(
    namespace: str,
    model: type[BaseModel],
    data: dict[str, Any],
) -> BaseModel:
    """Validate a single namespace's merged data through its Pydantic model.

    Args:
        namespace: The namespace identifier
        model: Pydantic model class
        data: Merged settings data

    Returns:
        Validated Pydantic model instance

    Raises:
        SettingsValidationError: If validation fails
    """
    try:
        transformed = resolve_environment_variables(data)
        transformed = convert_keys_to_lowercase(transformed)
        return model(**transformed)
    except Exception as e:
        raise SettingsValidationError(
            namespace=namespace,
            validation_error=e,
        ) from e


def build_unified_config(
    unified_model: type[BaseModel],
    merged: dict[str, dict[str, Any]],
) -> BaseModel:
    """Build a UnifiedConfig from merged layer data.

    Args:
        unified_model: The UnifiedConfig Pydantic model class
        merged: Dict mapping namespace to merged settings dict

    Returns:
        Validated UnifiedConfig instance
    """
    validated: dict[str, BaseModel] = {}
    for entry in SchemaRegistry.all_entries():
        ns_data = merged.get(entry.namespace, {})
        validated[entry.namespace] = build_validated_namespace(
            entry.namespace, entry.model, ns_data
        )
    return unified_model(**validated)
```

Update `packages/settings/src/color_scheme_settings/__init__.py`:
```python
"""Shared layered configuration system for color-scheme.

Public API:
    SchemaRegistry  — Register package config schemas
    load_config()   — Load and merge all layers (cached)
    reload_config() — Force reload (for testing)
    get_config()    — Load with optional CLI overrides
    apply_overrides — Apply dot-notation overrides to a config
"""

from typing import Any

from pydantic import BaseModel

from color_scheme_settings.errors import (
    SettingsError,
    SettingsFileError,
    SettingsOverrideError,
    SettingsRegistryError,
    SettingsValidationError,
)
from color_scheme_settings.loader import SettingsLoader
from color_scheme_settings.merger import merge_layers
from color_scheme_settings.overrides import apply_overrides
from color_scheme_settings.registry import SchemaRegistry
from color_scheme_settings.unified import build_unified_config

_config: BaseModel | None = None
_unified_model: type[BaseModel] | None = None
_loader_kwargs: dict[str, Any] = {}


def configure(
    unified_model: type[BaseModel],
    project_root: Any | None = None,
    user_config_path: Any | None = None,
) -> None:
    """Configure the settings system before first load.

    Args:
        unified_model: The Pydantic model class that composes all namespaces.
        project_root: Path to project root directory (optional).
        user_config_path: Path to user settings file (optional).
    """
    global _unified_model, _loader_kwargs, _config
    _unified_model = unified_model
    _loader_kwargs = {}
    if project_root is not None:
        _loader_kwargs["project_root"] = project_root
    if user_config_path is not None:
        _loader_kwargs["user_config_path"] = user_config_path
    _config = None


def load_config() -> BaseModel:
    """Load, merge, and validate all settings layers.

    Cached after first call. Use reload_config() to force refresh.

    Returns:
        Validated UnifiedConfig instance
    """
    global _config
    if _config is not None:
        return _config

    if _unified_model is None:
        raise SettingsError(
            "Settings system not configured. Call configure() first."
        )

    loader = SettingsLoader(**_loader_kwargs)
    layers = loader.discover_layers()
    merged = merge_layers(layers)
    _config = build_unified_config(_unified_model, merged)
    return _config


def reload_config() -> BaseModel:
    """Force reload from all layers. Useful for testing."""
    global _config
    _config = None
    return load_config()


def get_config(overrides: dict[str, Any] | None = None) -> BaseModel:
    """Load config with optional CLI overrides applied.

    Primary entry point for CLI commands.

    Args:
        overrides: Dict of dot-notation key paths to values.
                   Example: {"core.generation.saturation_adjustment": 1.5}

    Returns:
        Validated config with overrides applied.
    """
    config = load_config()
    if overrides:
        config = apply_overrides(config, overrides)
    return config


def reset() -> None:
    """Reset the entire settings system. For testing only."""
    global _config, _unified_model, _loader_kwargs
    _config = None
    _unified_model = None
    _loader_kwargs = {}
    SchemaRegistry.clear()


__all__ = [
    "SchemaRegistry",
    "configure",
    "load_config",
    "reload_config",
    "get_config",
    "apply_overrides",
    "reset",
    "SettingsError",
    "SettingsFileError",
    "SettingsOverrideError",
    "SettingsRegistryError",
    "SettingsValidationError",
]
```

**Step 6: Run all settings tests**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest -v`
Expected: All PASS

**Step 7: Commit**

```bash
git add packages/settings/src/color_scheme_settings/ packages/settings/tests/
git commit -m "feat(settings): add UnifiedConfig, transforms, and public API"
```

---

### Task 8: Implement end-to-end pipeline test

**Files:**
- Create: `packages/settings/tests/test_pipeline.py`

**Step 1: Write the integration test**

`packages/settings/tests/test_pipeline.py`:
```python
"""End-to-end pipeline tests: files → merge → validate → override."""

from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict, Field

import color_scheme_settings
from color_scheme_settings import (
    SchemaRegistry,
    configure,
    get_config,
    load_config,
    reload_config,
    reset,
)


class PipelineCoreGeneration(BaseModel):
    default_backend: str = Field(default="pywal")
    saturation_adjustment: float = Field(default=1.0, ge=0.0, le=2.0)


class PipelineCoreOutput(BaseModel):
    formats: list[str] = Field(default_factory=lambda: ["json", "css"])


class PipelineCoreConfig(BaseModel):
    generation: PipelineCoreGeneration = Field(default_factory=PipelineCoreGeneration)
    output: PipelineCoreOutput = Field(default_factory=PipelineCoreOutput)


class PipelineContainerConfig(BaseModel):
    engine: str = Field(default="docker")


class PipelineUnifiedConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    core: PipelineCoreConfig
    orchestrator: PipelineContainerConfig


@pytest.fixture(autouse=True)
def clean_state():
    reset()
    yield
    reset()


@pytest.fixture
def package_files(tmp_path: Path) -> tuple[Path, Path]:
    """Create package-level settings files."""
    core_file = tmp_path / "core_settings.toml"
    core_file.write_text("""\
[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

[output]
formats = ["json", "sh", "css"]
""")
    orch_file = tmp_path / "orch_settings.toml"
    orch_file.write_text("""\
[engine]
# This is wrong structure, orchestrator uses flat [container] but
# for this test, we use a simple top-level key
""")
    # Actually, orchestrator settings.toml has [container] section
    orch_file.write_text("""\
engine = "docker"
""")
    return core_file, orch_file


@pytest.fixture
def project_root_dir(tmp_path: Path) -> Path:
    """Create project root with namespaced settings."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    settings_file = project_dir / "settings.toml"
    settings_file.write_text("""\
[core.generation]
default_backend = "wallust"

[core.output]
formats = ["json", "yaml"]

[orchestrator]
engine = "podman"
""")
    return project_dir


@pytest.fixture
def user_config_file(tmp_path: Path) -> Path:
    """Create user config with namespaced settings."""
    user_file = tmp_path / "user_settings.toml"
    user_file.write_text("""\
[core.generation]
saturation_adjustment = 1.5
""")
    return user_file


class TestFullPipeline:
    """End-to-end tests for the complete settings pipeline."""

    def test_package_defaults_only(self, package_files: tuple[Path, Path]):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(PipelineUnifiedConfig)

        config = load_config()
        assert config.core.generation.default_backend == "pywal"
        assert config.core.generation.saturation_adjustment == 1.0
        assert config.core.output.formats == ["json", "sh", "css"]
        assert config.orchestrator.engine == "docker"

    def test_project_overrides_package(
        self,
        package_files: tuple[Path, Path],
        project_root_dir: Path,
    ):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(PipelineUnifiedConfig, project_root=project_root_dir)

        config = load_config()
        # Project overrides backend and formats
        assert config.core.generation.default_backend == "wallust"
        assert config.core.output.formats == ["json", "yaml"]
        # Package default preserved for saturation
        assert config.core.generation.saturation_adjustment == 1.0
        # Orchestrator overridden
        assert config.orchestrator.engine == "podman"

    def test_user_overrides_project(
        self,
        package_files: tuple[Path, Path],
        project_root_dir: Path,
        user_config_file: Path,
    ):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(
            PipelineUnifiedConfig,
            project_root=project_root_dir,
            user_config_path=user_config_file,
        )

        config = load_config()
        # User overrides saturation
        assert config.core.generation.saturation_adjustment == 1.5
        # Project override preserved for backend
        assert config.core.generation.default_backend == "wallust"
        # Project override preserved for formats
        assert config.core.output.formats == ["json", "yaml"]

    def test_cli_overrides_everything(
        self,
        package_files: tuple[Path, Path],
        project_root_dir: Path,
        user_config_file: Path,
    ):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(
            PipelineUnifiedConfig,
            project_root=project_root_dir,
            user_config_path=user_config_file,
        )

        config = get_config({
            "core.generation.saturation_adjustment": 0.5,
            "core.output.formats": ["scss"],
            "orchestrator.engine": "docker",
        })
        assert config.core.generation.saturation_adjustment == 0.5
        assert config.core.output.formats == ["scss"]
        assert config.orchestrator.engine == "docker"
        # backend still from project layer
        assert config.core.generation.default_backend == "wallust"

    def test_caching(self, package_files: tuple[Path, Path]):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(PipelineUnifiedConfig)

        config1 = load_config()
        config2 = load_config()
        assert config1 is config2

    def test_reload_reloads(self, package_files: tuple[Path, Path]):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(PipelineUnifiedConfig)

        config1 = load_config()
        config2 = reload_config()
        assert config1 is not config2

    def test_missing_package_file_uses_pydantic_defaults(self, tmp_path: Path):
        missing_file = tmp_path / "nonexistent.toml"
        SchemaRegistry.register("core", PipelineCoreConfig, missing_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, missing_file)
        configure(PipelineUnifiedConfig)

        config = load_config()
        assert config.core.generation.default_backend == "pywal"  # Pydantic default
        assert config.orchestrator.engine == "docker"  # Pydantic default
```

**Step 2: Run the pipeline tests**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest tests/test_pipeline.py -v`
Expected: All PASS

**Step 3: Run all settings package tests**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add packages/settings/tests/test_pipeline.py
git commit -m "test(settings): add end-to-end pipeline tests"
```

---

### Task 9: Wire settings package into core

**Files:**
- Modify: `packages/core/pyproject.toml` — add `color-scheme-settings` dependency, remove `dynaconf`
- Modify: `packages/core/src/color_scheme/config/__init__.py` — register schema
- Modify: `packages/core/src/color_scheme/config/settings.toml` — remove `[container]` section
- Delete: `packages/core/src/color_scheme/config/settings.py` — remove old SettingsModel

**Step 1: Update core pyproject.toml**

In `packages/core/pyproject.toml`, replace `"dynaconf>=3.2.0"` with `"color-scheme-settings>=0.1.0"` in the dependencies list. Add uv source:

```toml
[tool.uv.sources]
color-scheme-settings = { path = "../settings", editable = true }
```

**Step 2: Update core config/__init__.py**

Replace `packages/core/src/color_scheme/config/__init__.py`:
```python
"""Configuration system for color-scheme core."""

from pathlib import Path

from color_scheme_settings import SchemaRegistry

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend, ColorAlgorithm

SchemaRegistry.register(
    namespace="core",
    model=AppConfig,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = ["AppConfig", "Backend", "ColorAlgorithm"]
```

**Step 3: Remove `[container]` section from core settings.toml**

Edit `packages/core/src/color_scheme/config/settings.toml` to remove lines 7-8:
```toml
[container]
engine = "docker" # docker | podman
```

**Step 4: Delete the old settings.py**

Delete `packages/core/src/color_scheme/config/settings.py` entirely.

**Step 5: Sync dependencies**

Run: `cd /home/inumaki/Development/color-scheme/packages/core && uv sync`
Expected: resolves dependencies, no errors

**Step 6: Commit**

```bash
git add packages/core/
git rm packages/core/src/color_scheme/config/settings.py
git commit -m "refactor(core): wire settings package, remove dynaconf"
```

---

### Task 10: Wire settings package into orchestrator

**Files:**
- Modify: `packages/orchestrator/pyproject.toml` — add `color-scheme-settings` dependency
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/config/__init__.py` — register schema
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/config/settings.py` — remove `OrchestratorConfig` inheritance
- Create: `packages/orchestrator/src/color_scheme_orchestrator/config/settings.toml` — orchestrator defaults

**Step 1: Update orchestrator pyproject.toml**

Add `"color-scheme-settings>=0.1.0"` to dependencies. Add uv source:

```toml
[tool.uv.sources]
color-scheme-core = { path = "../core", editable = true }
color-scheme-settings = { path = "../settings", editable = true }
```

**Step 2: Create orchestrator settings.toml**

`packages/orchestrator/src/color_scheme_orchestrator/config/settings.toml`:
```toml
[container]
engine = "docker"
```

**Step 3: Update orchestrator config/__init__.py**

Replace `packages/orchestrator/src/color_scheme_orchestrator/config/__init__.py`:
```python
"""Configuration for orchestrator package."""

from pathlib import Path

from color_scheme_settings import SchemaRegistry

from color_scheme_orchestrator.config.settings import ContainerSettings

SchemaRegistry.register(
    namespace="orchestrator",
    model=ContainerSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = ["ContainerSettings"]
```

**Step 4: Clean up orchestrator config/settings.py**

Remove `OrchestratorConfig` and `OrchestratorSettings` from `packages/orchestrator/src/color_scheme_orchestrator/config/settings.py`. Keep only `ContainerSettings`. Remove the `AppConfig` imports:

```python
"""Orchestrator-specific configuration settings."""

from pydantic import BaseModel, Field, field_validator


class ContainerSettings(BaseModel):
    """Container engine configuration.

    Configures which container engine (Docker or Podman) to use for
    running containerized backends.
    """

    engine: str = Field(
        default="docker",
        description="Container engine to use (docker or podman)",
    )
    image_registry: str | None = Field(
        default=None,
        description="Registry prefix for container images",
    )

    @field_validator("engine", mode="before")
    @classmethod
    def validate_engine(cls, v: str) -> str:
        """Validate container engine is valid."""
        valid_engines = {"docker", "podman"}
        v_lower = v.lower()
        if v_lower not in valid_engines:
            raise ValueError(
                f"Invalid container engine: {v}. "
                f"Must be one of: {', '.join(sorted(valid_engines))}"
            )
        return v_lower

    @field_validator("image_registry", mode="before")
    @classmethod
    def normalize_registry(cls, v: str | None) -> str | None:
        """Normalize registry by removing trailing slashes."""
        if v:
            return v.rstrip("/")
        return v
```

**Step 5: Sync dependencies**

Run: `cd /home/inumaki/Development/color-scheme/packages/orchestrator && uv sync`
Expected: resolves, no errors

**Step 6: Commit**

```bash
git add packages/orchestrator/
git commit -m "refactor(orchestrator): wire settings package, register schema"
```

---

### Task 11: Create UnifiedConfig for the project

**Files:**
- Create: `packages/orchestrator/src/color_scheme_orchestrator/config/unified.py`
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/config/__init__.py`

**Step 1: Create unified.py in orchestrator**

The orchestrator is the outermost package and the natural place for the project-specific `UnifiedConfig`:

`packages/orchestrator/src/color_scheme_orchestrator/config/unified.py`:
```python
"""Project-level UnifiedConfig composing core + orchestrator schemas."""

from pydantic import BaseModel, ConfigDict, Field

from color_scheme.config.config import AppConfig
from color_scheme_orchestrator.config.settings import ContainerSettings


class UnifiedConfig(BaseModel):
    """Root configuration composing all registered namespaces.

    Access pattern:
        config.core.logging.level
        config.core.output.directory
        config.core.generation.default_backend
        config.core.backends.pywal.backend_algorithm
        config.core.templates.directory
        config.orchestrator.container.engine
        config.orchestrator.container.image_registry
    """

    model_config = ConfigDict(frozen=True)

    core: AppConfig = Field(default_factory=AppConfig)
    orchestrator: ContainerSettings = Field(default_factory=ContainerSettings)
```

**Step 2: Update orchestrator config/__init__.py**

Add `UnifiedConfig` export:

```python
"""Configuration for orchestrator package."""

from pathlib import Path

from color_scheme_settings import SchemaRegistry

from color_scheme_orchestrator.config.settings import ContainerSettings
from color_scheme_orchestrator.config.unified import UnifiedConfig

SchemaRegistry.register(
    namespace="orchestrator",
    model=ContainerSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = ["ContainerSettings", "UnifiedConfig"]
```

**Step 3: Commit**

```bash
git add packages/orchestrator/src/color_scheme_orchestrator/config/
git commit -m "feat(orchestrator): add project-level UnifiedConfig"
```

---

### Task 12: Migrate core CLI to use new settings

**Files:**
- Modify: `packages/core/src/color_scheme/cli/main.py`
- Modify: `packages/core/src/color_scheme/factory.py`
- Modify: `packages/core/src/color_scheme/output/manager.py`
- Modify: `packages/core/src/color_scheme/core/types.py:137` — `GeneratorConfig.from_settings`

**Step 1: Update core CLI main.py**

In `packages/core/src/color_scheme/cli/main.py`:

Replace the import:
```python
from color_scheme.config.settings import Settings
```
with:
```python
from color_scheme_settings import get_config
```

In the `generate` function (line 97), replace:
```python
settings = Settings.get()
```
with:
```python
config = get_config()
```

Then update all references from `settings` to `config.core` throughout the function:
- `factory = BackendFactory(config.core)` (line 109)
- `config_obj = GeneratorConfig.from_settings(config.core, **overrides)` (line 127)
- `output_manager = OutputManager(config.core)` (line 165)

Apply the same pattern to the `show` function:
- Replace `Settings.get()` with `get_config()`
- Replace `settings` with `config.core` for factory and GeneratorConfig

**Step 2: Verify factory.py and output/manager.py don't need changes**

These files accept `AppConfig` as parameter — they don't import `Settings` themselves. They receive `config.core` (which IS an `AppConfig`) from the CLI. No changes needed.

**Step 3: Update GeneratorConfig.from_settings signature**

In `packages/core/src/color_scheme/core/types.py`, the `from_settings` method already accepts `AppConfig` — no change needed. It receives `config.core` which is `AppConfig`.

**Step 4: Run core tests**

Run: `cd /home/inumaki/Development/color-scheme/packages/core && uv run pytest -v`
Expected: Some tests may fail due to import of old `Settings` — fix in next task

**Step 5: Commit**

```bash
git add packages/core/src/color_scheme/cli/main.py
git commit -m "refactor(core): migrate CLI to use get_config()"
```

---

### Task 13: Migrate orchestrator CLI to use new settings

**Files:**
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/cli/commands/install.py`
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/cli/commands/uninstall.py`
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`

**Step 1: Update orchestrator CLI main.py**

In `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`:

Replace imports:
```python
from color_scheme.config.settings import Settings
from color_scheme_orchestrator.config.settings import ContainerSettings, OrchestratorConfig
```
with:
```python
from color_scheme_settings import get_config
from color_scheme_orchestrator.config.unified import UnifiedConfig
```

In the `generate` function, replace lines 86-90:
```python
core_settings = Settings.get()
settings = OrchestratorConfig(
    **core_settings.model_dump(),
    container=ContainerSettings(),
)
```
with:
```python
config = get_config()
```

Update all references:
- `Backend(settings.generation.default_backend)` → `Backend(config.core.generation.default_backend)`
- `settings.output.directory` → `config.core.output.directory`
- `ContainerManager(settings)` → `ContainerManager(config)`

**Step 2: Update install.py and uninstall.py**

Replace:
```python
from color_scheme.config.settings import Settings
settings = Settings.get()
```
with:
```python
from color_scheme_settings import get_config
config = get_config()
```

For the engine default, replace hardcoded `"docker"` with:
```python
container_engine = config.orchestrator.container.engine
```
when `engine` CLI arg is None.

**Step 3: Update ContainerManager**

In `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`:

Change the constructor to accept `UnifiedConfig` instead of `AppConfig`:
```python
def __init__(self, config):
    self.config = config
    self.engine = config.orchestrator.container.engine
```

Update `get_image_name` to use `self.config.orchestrator.container.image_registry`.
Update `build_volume_mounts` to use `self.config.core.templates.directory`.

**Step 4: Run orchestrator tests**

Run: `cd /home/inumaki/Development/color-scheme/packages/orchestrator && uv run pytest -v`
Expected: Some tests may fail — fix in next task

**Step 5: Commit**

```bash
git add packages/orchestrator/src/
git commit -m "refactor(orchestrator): migrate CLI and container manager to unified config"
```

---

### Task 14: Fix core tests

**Files:**
- Modify: `packages/core/tests/config/conftest.py`
- Modify: `packages/core/tests/config/test_settings.py`
- Modify: `packages/core/tests/config/test_config.py` (if needed)
- Modify: `packages/core/tests/config/test_defaults.py` (if needed)
- Modify: other test files that import `Settings`

**Step 1: Update conftest.py**

Remove the `[container]` section from the `temp_settings_file` fixture in `packages/core/tests/config/conftest.py` and the `sample_config_dict` fixture.

**Step 2: Rewrite test_settings.py**

The old tests tested `SettingsModel` and `dynaconf`. Those are gone. Replace with tests that verify core's schema registration works and that `AppConfig` can be constructed from TOML data via the new pipeline. The key tests to preserve:
- Loading from TOML file produces valid AppConfig
- Environment variable resolution
- Case-insensitive sections
- Path type conversion
- Nested backend settings
- Validation errors

These tests should now use `color_scheme_settings` API instead of `SettingsModel`.

**Step 3: Run core tests**

Run: `cd /home/inumaki/Development/color-scheme/packages/core && uv run pytest -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add packages/core/tests/
git commit -m "test(core): update tests for new settings system"
```

---

### Task 15: Fix orchestrator tests

**Files:**
- Modify: `packages/orchestrator/tests/unit/test_container_manager.py`
- Modify: `packages/orchestrator/tests/unit/test_image_names.py`
- Modify: `packages/orchestrator/tests/unit/test_volume_mounts.py`
- Modify: `packages/orchestrator/tests/unit/test_container_execution.py`
- Modify: `packages/orchestrator/tests/integration/test_cli_generate_orchestrator.py`
- Modify: `packages/orchestrator/tests/integration/test_cli_show_delegation.py`

**Step 1: Update test fixtures**

Tests that create `OrchestratorConfig` or pass `AppConfig` to `ContainerManager` need to create `UnifiedConfig` instead. Update fixtures to build the unified config.

**Step 2: Update assertions**

Replace `settings.container.engine` with `config.orchestrator.container.engine` patterns in assertions.

**Step 3: Run orchestrator tests**

Run: `cd /home/inumaki/Development/color-scheme/packages/orchestrator && uv run pytest -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add packages/orchestrator/tests/
git commit -m "test(orchestrator): update tests for unified config"
```

---

### Task 16: Bootstrap the settings system at CLI entry points

**Files:**
- Modify: `packages/core/src/color_scheme/cli/main.py` — add `configure()` call
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py` — add `configure()` call

**Step 1: Add configure() to core's entry point**

At the top of `packages/core/src/color_scheme/cli/main.py`, after imports:
```python
from color_scheme_settings import configure
from color_scheme.config.config import AppConfig
from pydantic import BaseModel, ConfigDict, Field

class CoreOnlyConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    core: AppConfig = Field(default_factory=AppConfig)

# Bootstrap settings for standalone core usage
configure(CoreOnlyConfig)
```

Note: When core runs standalone (not through orchestrator), it only has the `core` namespace. The `CoreOnlyConfig` model reflects this.

**Step 2: Add configure() to orchestrator's entry point**

At the top of `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`, after imports:
```python
from color_scheme_settings import configure
from color_scheme_orchestrator.config.unified import UnifiedConfig

# Bootstrap settings for orchestrator (includes core + orchestrator namespaces)
configure(UnifiedConfig)
```

When orchestrator runs, it configures with the full `UnifiedConfig` that includes both namespaces. Since orchestrator imports core, core's schema registration runs first, then orchestrator's.

**Step 3: Run both test suites**

Run: `cd /home/inumaki/Development/color-scheme/packages/core && uv run pytest -v`
Run: `cd /home/inumaki/Development/color-scheme/packages/orchestrator && uv run pytest -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add packages/core/src/color_scheme/cli/main.py packages/orchestrator/src/color_scheme_orchestrator/cli/main.py
git commit -m "feat: bootstrap settings system at CLI entry points"
```

---

### Task 17: Run full test suite and lint

**Step 1: Run all tests across all packages**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run pytest -v`
Run: `cd /home/inumaki/Development/color-scheme/packages/core && uv run pytest -v`
Run: `cd /home/inumaki/Development/color-scheme/packages/orchestrator && uv run pytest -v`
Expected: All PASS in all three packages

**Step 2: Run linting**

Run: `cd /home/inumaki/Development/color-scheme/packages/settings && uv run ruff check . && uv run ruff format --check .`
Run: `cd /home/inumaki/Development/color-scheme/packages/core && uv run ruff check . && uv run ruff format --check .`
Run: `cd /home/inumaki/Development/color-scheme/packages/orchestrator && uv run ruff check . && uv run ruff format --check .`
Expected: All clean

**Step 3: Fix any issues found, commit**

```bash
git add -A
git commit -m "chore: fix lint issues across all packages"
```

---

### Task 18: Create project root settings.toml example

**Files:**
- Create: `settings.toml` at project root

**Step 1: Create the file**

`settings.toml` at project root:
```toml
# Color Scheme Settings
# This file is the project-level configuration.
# Keys are namespaced: [core.*] for core settings, [orchestrator.*] for container settings.
# See docs/plans/2026-01-30-settings-layered-architecture.md for full reference.

# Override core defaults here:
# [core.generation]
# default_backend = "wallust"
# saturation_adjustment = 1.0

# [core.output]
# directory = "$HOME/.config/color-scheme/output"
# formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]

# [core.logging]
# level = "INFO"

# [orchestrator.container]
# engine = "docker"
```

All sections commented out — the file serves as documentation for available settings. Uncomment to override package defaults.

**Step 2: Commit**

```bash
git add settings.toml
git commit -m "docs: add project root settings.toml template"
```
