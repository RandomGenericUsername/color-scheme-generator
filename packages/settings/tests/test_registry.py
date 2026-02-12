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
        SchemaRegistry.register(
            "orchestrator", MockOrchestratorConfig, tmp_path / "orch.toml"
        )
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
        SchemaRegistry.register(
            "orchestrator", MockOrchestratorConfig, tmp_path / "orch.toml"
        )
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
