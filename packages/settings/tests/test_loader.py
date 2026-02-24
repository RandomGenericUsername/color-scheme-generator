"""Tests for settings layer discovery and TOML loading."""

from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from color_scheme_settings.errors import SettingsFileError
from color_scheme_settings.loader import SettingsLoader, load_toml
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

    def test_discovers_package_defaults(self, tmp_path: Path, core_defaults_toml: Path):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        loader = SettingsLoader(
            project_root=None,
            user_config_path=tmp_path / "no-user-config.toml",
        )
        layers = loader.discover_layers()
        core_layers = [layer for layer in layers if layer.namespace == "core"]
        assert len(core_layers) == 1
        assert core_layers[0].layer == "package"
        assert "logging" in core_layers[0].data

    def test_missing_package_file_skipped(self, tmp_path: Path):
        SchemaRegistry.register("core", MockCoreConfig, tmp_path / "nonexistent.toml")
        loader = SettingsLoader(
            project_root=None,
            user_config_path=tmp_path / "no-user-config.toml",
        )
        layers = loader.discover_layers()
        assert len(layers) == 0


class TestSettingsLoaderProjectLayer:
    """Tests for discovering project root settings file."""

    def test_discovers_project_root_namespaced(
        self, core_defaults_toml: Path, project_root_toml: Path
    ):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        SchemaRegistry.register(
            "orchestrator", MockOrchestratorConfig, core_defaults_toml
        )
        loader = SettingsLoader(
            project_root=project_root_toml.parent,
            user_config_path=None,
        )
        layers = loader.discover_layers()
        project_layers = [layer for layer in layers if layer.layer == "project"]
        assert len(project_layers) >= 1

    def test_no_project_root_no_project_layers(self, core_defaults_toml: Path):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        loader = SettingsLoader(project_root=None, user_config_path=None)
        layers = loader.discover_layers()
        project_layers = [layer for layer in layers if layer.layer == "project"]
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
        user_layers = [layer for layer in layers if layer.layer == "user"]
        assert len(user_layers) >= 1

    def test_missing_user_config_skipped(
        self, core_defaults_toml: Path, tmp_path: Path
    ):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        loader = SettingsLoader(
            project_root=None,
            user_config_path=tmp_path / "nonexistent.toml",
        )
        layers = loader.discover_layers()
        user_layers = [layer for layer in layers if layer.layer == "user"]
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
        core_layers = [layer for layer in layers if layer.namespace == "core"]
        layer_names = [layer.layer for layer in core_layers]
        assert layer_names == ["package", "project", "user"]
