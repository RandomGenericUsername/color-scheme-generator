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

    def test_default_path_uses_xdg_config_home(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        xdg_dir = tmp_path / "xdg"
        xdg_dir.mkdir()
        monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_dir))
        loader = SettingsLoader()
        expected = xdg_dir / "color-scheme" / "settings.toml"
        assert loader.user_config_path == expected

    def test_default_path_falls_back_to_home_config_when_xdg_unset(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        loader = SettingsLoader()
        expected = Path.home() / ".config" / "color-scheme" / "settings.toml"
        assert loader.user_config_path == expected

    def test_explicit_path_overrides_xdg(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        xdg_dir = tmp_path / "xdg"
        xdg_dir.mkdir()
        monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_dir))
        explicit = tmp_path / "explicit" / "settings.toml"
        loader = SettingsLoader(user_config_path=explicit)
        assert loader.user_config_path == explicit


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


class TestEnvVarLayer:
    """CRIT-01: env-var layer must appear in discover_layers() output."""

    def test_env_var_layer_present_when_set(
        self, core_defaults_toml: Path, monkeypatch: pytest.MonkeyPatch
    ):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        monkeypatch.setenv("COLORSCHEME_LEVEL__VALUE", "DEBUG")
        loader = SettingsLoader(project_root=None, user_config_path=None)
        layers = loader.discover_layers()
        env_layers = [layer for layer in layers if layer.layer == "env"]
        assert len(env_layers) >= 1

    def test_env_var_layer_absent_when_no_colorscheme_vars(
        self, core_defaults_toml: Path, monkeypatch: pytest.MonkeyPatch
    ):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        # Patch parse_env_vars to return empty to isolate from real env
        import color_scheme_settings.loader as loader_mod

        original = getattr(loader_mod, "parse_env_vars", None)
        loader_mod.parse_env_vars = lambda: {}
        try:
            loader = SettingsLoader(project_root=None, user_config_path=None)
            layers = loader.discover_layers()
            env_layers = [layer for layer in layers if layer.layer == "env"]
            assert len(env_layers) == 0
        finally:
            if original is not None:
                loader_mod.parse_env_vars = original
            else:
                del loader_mod.parse_env_vars

    def test_env_var_layer_has_no_file_path(
        self, core_defaults_toml: Path, monkeypatch: pytest.MonkeyPatch
    ):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        monkeypatch.setenv("COLORSCHEME_LEVEL__VALUE", "DEBUG")
        loader = SettingsLoader(project_root=None, user_config_path=None)
        layers = loader.discover_layers()
        env_layers = [layer for layer in layers if layer.layer == "env"]
        for layer in env_layers:
            assert layer.file_path is None

    def test_env_var_unknown_section_ignored(
        self, core_defaults_toml: Path, monkeypatch: pytest.MonkeyPatch
    ):
        SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
        monkeypatch.setenv("COLORSCHEME_UNKNOWNSECTION__KEY", "value")
        loader = SettingsLoader(project_root=None, user_config_path=None)
        layers = loader.discover_layers()
        env_layers = [layer for layer in layers if layer.layer == "env"]
        namespaces = [layer.namespace for layer in env_layers]
        assert "unknownsection" not in namespaces
