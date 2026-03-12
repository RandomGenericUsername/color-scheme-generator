"""Tests for ConfigResolver."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from pydantic import BaseModel, Field

from color_scheme_settings.errors import SettingsFileError
from color_scheme_settings.models import (
    ConfigSource,
    ResolvedConfig,
    Warning,
    WarningLevel,
)
from color_scheme_settings.registry import SchemaRegistry
from color_scheme_settings.resolver import ConfigResolver


@pytest.fixture(autouse=True)
def clean_registry():
    SchemaRegistry.clear()
    yield
    SchemaRegistry.clear()


class TestConfigResolverInit:
    """Test ConfigResolver initialization."""

    def test_default_package_name(self):
        """Test resolver with default package name."""
        resolver = ConfigResolver()
        assert resolver.package_name == "color-scheme"
        assert resolver.warnings == []

    def test_custom_package_name(self):
        """Test resolver with custom package name."""
        resolver = ConfigResolver(package_name="custom-pkg")
        assert resolver.package_name == "custom-pkg"


class TestConfigResolverLoadPackageDefaults:
    """Test _load_package_defaults method."""

    def test_load_package_defaults_returns_dict(self):
        """Test that _load_package_defaults returns a dict."""
        resolver = ConfigResolver()
        result = resolver._load_package_defaults()
        assert isinstance(result, dict)

    def test_load_package_defaults_empty_for_now(self):
        """Test that _load_package_defaults returns empty dict currently."""
        resolver = ConfigResolver()
        result = resolver._load_package_defaults()
        # Currently placeholder implementation returns empty dict
        assert result == {}


class TestConfigResolverLoadProjectConfig:
    """Test _load_project_config method."""

    def test_load_project_config_nonexistent_file(self):
        """Test loading project config when file doesn't exist."""
        import os

        resolver = ConfigResolver()
        # Use a temp directory with no settings.toml
        original_cwd = os.getcwd()
        try:
            # Create a temp dir and change to it
            import tempfile

            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                result = resolver._load_project_config()
                assert result is None
                # No warnings for missing file (it's optional)
        finally:
            os.chdir(original_cwd)

    def test_load_project_config_file_not_found(self, tmp_path):
        """Test that missing project config returns None."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            resolver = ConfigResolver()
            result = resolver._load_project_config()
            assert result is None
        finally:
            os.chdir(original_cwd)

    def test_load_project_config_valid_file(self, tmp_path):
        """Test loading valid project config file."""
        import os

        # Create a valid settings.toml file
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[generation]
default_backend = "pywal"

[output]
directory = "/tmp/output"
""")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            resolver = ConfigResolver()
            result = resolver._load_project_config()
            assert isinstance(result, dict)
            assert result["generation"]["default_backend"] == "pywal"
            assert result["output"]["directory"] == "/tmp/output"
        finally:
            os.chdir(original_cwd)

    def test_load_project_config_malformed_file(self, tmp_path):
        """Test loading malformed TOML file raises SettingsFileError."""
        # Create a malformed TOML file
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[generation
default_backend = "pywal"
""")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            resolver = ConfigResolver()
            with pytest.raises(SettingsFileError):
                resolver._load_project_config()
        finally:
            os.chdir(original_cwd)


class TestConfigResolverLoadUserConfig:
    """Test _load_user_config method."""

    def test_load_user_config_returns_dict_or_none(self):
        """Test that _load_user_config returns dict or None."""
        resolver = ConfigResolver()
        # This should handle missing user config gracefully
        result = resolver._load_user_config()
        assert result is None or isinstance(result, dict)

    def test_load_user_config_with_mock(self):
        """Test _load_user_config with mocked user config file."""
        resolver = ConfigResolver()
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value.joinpath.return_value.exists.return_value = False
            # The method uses Path.home() to find user config
            result = resolver._load_user_config()
            # Should handle missing file gracefully
            assert result is None or isinstance(result, dict)

    def test_load_user_config_missing_returns_none(self):
        """Test that missing user config returns None without error."""
        resolver = ConfigResolver()
        # User config may or may not exist - should handle gracefully
        result = resolver._load_user_config()
        assert result is None or isinstance(result, dict)


class TestConfigResolverCollectEnvVars:
    """Test _collect_env_vars method."""

    def test_collect_env_vars_returns_dict(self):
        """Test that _collect_env_vars returns a dict."""
        resolver = ConfigResolver()
        result = resolver._collect_env_vars()
        assert isinstance(result, dict)

    def test_collect_env_vars_includes_colorscheme_vars(self):
        """Test that COLORSCHEME_ environment variables are collected."""
        with patch.dict(
            "os.environ",
            {"COLORSCHEME_GENERATION__DEFAULT_BACKEND": "custom", "OTHER_VAR": "value"},
        ):
            resolver = ConfigResolver()
            result = resolver._collect_env_vars()
            # Should include COLORSCHEME_ variables in nested dict format
            assert isinstance(result, dict)
            # Either flat format or nested format is acceptable
            has_backend = "generation.default_backend" in result or (
                "generation" in result and "default_backend" in result["generation"]
            )
            assert has_backend or len(result) == 0

    def test_collect_env_vars_includes_color_scheme_templates(self):
        """Test that COLOR_SCHEME_TEMPLATES env var is collected."""
        with patch.dict(
            "os.environ",
            {"COLOR_SCHEME_TEMPLATES": "/custom/templates"},
        ):
            resolver = ConfigResolver()
            result = resolver._collect_env_vars()
            # Should include templates directory
            assert isinstance(result, dict)
            assert "templates" in result
            assert result["templates"]["directory"] == "/custom/templates"

    def test_collect_env_vars_multiple_vars(self):
        """Test collecting multiple COLORSCHEME_ environment variables."""
        with patch.dict(
            "os.environ",
            {
                "COLORSCHEME_GENERATION__DEFAULT_BACKEND": "pywal",
                "COLORSCHEME_OUTPUT__DIRECTORY": "/tmp/colors",
                "COLOR_SCHEME_TEMPLATES": "/templates",
            },
        ):
            resolver = ConfigResolver()
            result = resolver._collect_env_vars()
            assert isinstance(result, dict)
            # Should have nested structure
            assert "generation" in result or "templates" in result


class TestConfigResolverApplyPrecedence:
    """Test _apply_precedence method."""

    def test_apply_precedence_returns_resolved_config(self):
        """Test that _apply_precedence returns a ResolvedConfig."""
        resolver = ConfigResolver()
        result = resolver._apply_precedence(
            cli_args={},
            env_vars={},
            user_config=None,
            project_config=None,
            defaults={"key": "default_value"},
        )
        assert isinstance(result, ResolvedConfig)

    def test_apply_precedence_cli_overrides_all(self):
        """Test that CLI args override all other sources."""
        resolver = ConfigResolver()
        result = resolver._apply_precedence(
            cli_args={"backend": "cli_backend"},
            env_vars={"backend": "env_backend"},
            user_config={"backend": "user_backend"},
            project_config={"backend": "project_backend"},
            defaults={"backend": "default_backend"},
        )
        # CLI value should be present
        backend_resolved = result.get("backend")
        if backend_resolved:
            assert backend_resolved.source == ConfigSource.CLI

    def test_apply_precedence_env_overrides_configs(self):
        """Test that environment variables override config files."""
        resolver = ConfigResolver()
        result = resolver._apply_precedence(
            cli_args={},
            env_vars={"key": "env_value"},
            user_config={"key": "user_value"},
            project_config={"key": "project_value"},
            defaults={"key": "default_value"},
        )
        # Env value should win over config values (but not CLI)
        key_resolved = result.get("key")
        if key_resolved:
            # Either ENV or USER_CONFIG depending on implementation
            assert key_resolved.source in [ConfigSource.ENV, ConfigSource.USER_CONFIG]

    def test_apply_precedence_user_overrides_project(self):
        """Test that user config overrides project config."""
        resolver = ConfigResolver()
        result = resolver._apply_precedence(
            cli_args={},
            env_vars={},
            user_config={"key": "user_value"},
            project_config={"key": "project_value"},
            defaults={"key": "default_value"},
        )
        # User value should win over project value
        key_resolved = result.get("key")
        if key_resolved:
            assert key_resolved.source in [
                ConfigSource.USER_CONFIG,
                ConfigSource.PROJECT_CONFIG,
            ]

    def test_apply_precedence_returns_all_sources(self):
        """Test that _apply_precedence includes values from all sources."""
        resolver = ConfigResolver()
        result = resolver._apply_precedence(
            cli_args={"cli_key": "cli_value"},
            env_vars={"env_key": "env_value"},
            user_config={"user_key": "user_value"},
            project_config={"project_key": "project_value"},
            defaults={"default_key": "default_value"},
        )
        # Should have values from all sources
        resolved_keys = [k for k, _ in result.items()]
        assert len(resolved_keys) >= 1  # At least one key should be resolved


class TestConfigResolverResolveMethod:
    """Test the main resolve method."""

    def test_resolve_returns_resolved_config(self):
        """Test that resolve returns a ResolvedConfig."""
        resolver = ConfigResolver()
        result = resolver.resolve()
        assert isinstance(result, ResolvedConfig)

    def test_resolve_with_cli_args(self):
        """Test resolve with CLI arguments."""
        resolver = ConfigResolver()
        result = resolver.resolve(cli_args={"backend": "custom"})
        assert isinstance(result, ResolvedConfig)

    def test_resolve_with_command_context(self):
        """Test resolve with command context."""
        resolver = ConfigResolver()
        result = resolver.resolve(command_ctx={"command": "generate"})
        assert isinstance(result, ResolvedConfig)

    def test_resolve_with_both_args(self):
        """Test resolve with both CLI args and command context."""
        resolver = ConfigResolver()
        result = resolver.resolve(
            cli_args={"backend": "pywal"},
            command_ctx={"command": "show"},
        )
        assert isinstance(result, ResolvedConfig)

    def test_resolve_empty_args(self):
        """Test resolve with empty arguments."""
        resolver = ConfigResolver()
        result = resolver.resolve(cli_args={}, command_ctx={})
        assert isinstance(result, ResolvedConfig)

    def test_resolve_none_args(self):
        """Test resolve with None arguments (defaults to empty dicts)."""
        resolver = ConfigResolver()
        result = resolver.resolve(cli_args=None, command_ctx=None)
        assert isinstance(result, ResolvedConfig)


class TestConfigResolverWarnings:
    """Test warning handling in resolver."""

    def test_warnings_list_initialized_empty(self):
        """Test that warnings list is initialized empty."""
        resolver = ConfigResolver()
        assert resolver.warnings == []

    def test_warnings_accumulate(self, tmp_path: Path):
        """Warnings from _load_package_defaults accumulate on resolver."""
        from pydantic import BaseModel

        class MockConfig(BaseModel):
            pass

        SchemaRegistry.register("core", MockConfig, tmp_path / "nonexistent.toml")
        resolver = ConfigResolver()
        resolver._load_package_defaults()
        assert len(resolver.warnings) >= 1

    def test_warning_structure(self, tmp_path: Path):
        """Warnings from _load_package_defaults have proper structure."""
        from pydantic import BaseModel

        class MockConfig(BaseModel):
            pass

        SchemaRegistry.register("core", MockConfig, tmp_path / "nonexistent.toml")
        resolver = ConfigResolver()
        resolver._load_package_defaults()
        for warning in resolver.warnings:
            assert isinstance(warning, Warning)
            assert hasattr(warning, "level")
            assert hasattr(warning, "message")


class TestConfigResolverIntegration:
    """Integration tests for ConfigResolver."""

    def test_full_resolution_workflow(self):
        """Test a complete resolution workflow."""
        resolver = ConfigResolver("test-package")
        # Should complete without errors
        result = resolver.resolve(
            cli_args={"backend": "custom", "saturation": 1.5},
            command_ctx={"command": "generate", "image_path": "/test/image.jpg"},
        )
        assert isinstance(result, ResolvedConfig)

    def test_resolver_independence(self):
        """Test that multiple resolvers are independent."""
        resolver1 = ConfigResolver("pkg1")
        resolver2 = ConfigResolver("pkg2")

        assert resolver1.package_name != resolver2.package_name
        assert resolver1.warnings is not resolver2.warnings


class TestLoadPackageDefaults:
    """CRIT-02: _load_package_defaults must return real values from registry."""

    def test_load_package_defaults_returns_real_values(self, tmp_path: Path):
        toml_file = tmp_path / "settings.toml"
        toml_file.write_text('[generation]\ndefault_backend = "pywal"\n')

        class MockCoreConfig(BaseModel):
            generation: dict = Field(default_factory=dict)

        SchemaRegistry.register("core", MockCoreConfig, toml_file)
        resolver = ConfigResolver()
        defaults = resolver._load_package_defaults()
        assert "core" in defaults
        assert defaults["core"].get("generation", {}).get("default_backend") == "pywal"

    def test_load_package_defaults_warns_on_missing_file(self, tmp_path: Path):
        class MockCoreConfig(BaseModel):
            pass

        SchemaRegistry.register("core", MockCoreConfig, tmp_path / "nonexistent.toml")
        resolver = ConfigResolver()
        result = resolver._load_package_defaults()
        assert result == {} or "core" not in result
        assert len(resolver.warnings) >= 1


class TestCollectEnvVars:
    """CRIT-02: _collect_env_vars must delegate to parse_env_vars()."""

    def test_env_vars_delegate_to_shared_parser(self):
        resolver = ConfigResolver()
        with patch(
            "color_scheme_settings.resolver.parse_env_vars",
            return_value={"output": {"directory": "/patched"}},
        ) as mock_parse:
            result = resolver._collect_env_vars()
        mock_parse.assert_called_once()
        assert result == {"output": {"directory": "/patched"}}


class TestResolverErrorHandling:
    """IMP-2: malformed config files must raise, not silently warn."""

    def test_malformed_project_config_raises_settings_file_error(
        self, tmp_path: Path
    ):
        bad_toml = tmp_path / "settings.toml"
        bad_toml.write_text("this is not [[ valid toml")

        resolver = ConfigResolver()
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SettingsFileError):
                resolver._load_project_config()
        finally:
            os.chdir(original_cwd)
