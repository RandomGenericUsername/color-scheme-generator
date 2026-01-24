"""Tests for settings loading with dynaconf + Pydantic."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from color_scheme.config.config import AppConfig
from color_scheme.config.settings import SettingsModel


class TestSettingsModelBasics:
    """Basic tests for SettingsModel class."""

    def test_init_with_default_settings_file(self):
        """Test SettingsModel initializes with default settings file."""
        settings = SettingsModel()
        assert settings.settings is not None
        assert isinstance(settings.settings, AppConfig)

    def test_init_with_custom_settings_file(self, temp_settings_file: Path):
        """Test SettingsModel with custom settings file."""
        settings = SettingsModel(settings_files=[str(temp_settings_file)])
        assert settings.settings is not None
        assert settings.settings.logging.level == "DEBUG"

    def test_get_returns_pydantic_config(self, temp_settings_file: Path):
        """Test get() method returns AppConfig instance."""
        settings = SettingsModel(settings_files=[str(temp_settings_file)])
        config = settings.get()
        assert isinstance(config, AppConfig)


class TestConvertDictToLowerCase:
    """Tests for _convert_dict_to_lower_case method."""

    def test_simple_dict(self):
        """Test converting simple dictionary keys to lowercase."""
        input_dict = {"LOGGING": {"LEVEL": "INFO"}, "OUTPUT": {"FORMATS": ["json"]}}
        result = SettingsModel._convert_dict_to_lower_case(input_dict)

        assert "logging" in result
        assert "output" in result
        assert result["logging"]["level"] == "INFO"
        assert result["output"]["formats"] == ["json"]

    def test_nested_dict(self):
        """Test converting nested dictionary keys to lowercase."""
        input_dict = {
            "BACKENDS": {
                "PYWAL": {"BACKEND_ALGORITHM": "haishoku"},
                "CUSTOM": {"ALGORITHM": "kmeans"},
            }
        }
        result = SettingsModel._convert_dict_to_lower_case(input_dict)

        assert "backends" in result
        assert "pywal" in result["backends"]
        assert "custom" in result["backends"]
        assert result["backends"]["pywal"]["backend_algorithm"] == "haishoku"

    def test_mixed_case_keys(self):
        """Test converting mixed case keys."""
        input_dict = {"MixedCase": {"AnotherKey": "value"}}
        result = SettingsModel._convert_dict_to_lower_case(input_dict)

        assert "mixedcase" in result
        assert "anotherkey" in result["mixedcase"]

    def test_values_unchanged(self):
        """Test that values are not modified, only keys."""
        input_dict = {"KEY": "VALUE_UNCHANGED"}
        result = SettingsModel._convert_dict_to_lower_case(input_dict)

        assert result["key"] == "VALUE_UNCHANGED"

    def test_empty_dict(self):
        """Test empty dictionary."""
        result = SettingsModel._convert_dict_to_lower_case({})
        assert result == {}


class TestResolveEnvironmentVariables:
    """Tests for _resolve_environment_variables method."""

    def test_resolve_home_variable(self, monkeypatch: pytest.MonkeyPatch):
        """Test resolving $HOME environment variable."""
        monkeypatch.setenv("HOME", "/home/testuser")
        input_dict = {"output": {"directory": "$HOME/.config/color-scheme"}}
        result = SettingsModel._resolve_environment_variables(input_dict)

        assert result["output"]["directory"] == "/home/testuser/.config/color-scheme"

    def test_resolve_multiple_variables(self, monkeypatch: pytest.MonkeyPatch):
        """Test resolving multiple environment variables."""
        monkeypatch.setenv("HOME", "/home/testuser")
        monkeypatch.setenv("USER", "testuser")

        input_dict = {"path1": "$HOME/dir", "path2": "$USER/dir"}
        result = SettingsModel._resolve_environment_variables(input_dict)

        assert result["path1"] == "/home/testuser/dir"
        assert result["path2"] == "testuser/dir"

    def test_resolve_in_nested_dict(self, monkeypatch: pytest.MonkeyPatch):
        """Test resolving environment variables in nested structures."""
        monkeypatch.setenv("HOME", "/home/testuser")

        input_dict = {
            "output": {"directory": "$HOME/.config"},
            "templates": {"directory": "$HOME/.templates"},
        }
        result = SettingsModel._resolve_environment_variables(input_dict)

        assert result["output"]["directory"] == "/home/testuser/.config"
        assert result["templates"]["directory"] == "/home/testuser/.templates"

    def test_resolve_in_list(self, monkeypatch: pytest.MonkeyPatch):
        """Test resolving environment variables in lists."""
        monkeypatch.setenv("HOME", "/home/testuser")

        input_dict = {"paths": ["$HOME/dir1", "$HOME/dir2"]}
        result = SettingsModel._resolve_environment_variables(input_dict)

        assert result["paths"] == ["/home/testuser/dir1", "/home/testuser/dir2"]

    def test_non_string_values_unchanged(self):
        """Test that non-string values are not affected."""
        input_dict = {
            "string": "$HOME",
            "number": 42,
            "boolean": True,
            "none": None,
            "list": [1, 2, 3],
        }
        # Don't set HOME to see if non-strings pass through
        result = SettingsModel._resolve_environment_variables(input_dict)

        assert isinstance(result["number"], int)
        assert result["number"] == 42
        assert result["boolean"] is True
        assert result["none"] is None
        assert result["list"] == [1, 2, 3]

    def test_undefined_variable(self):
        """Test undefined environment variables remain as-is or expand to empty."""
        input_dict = {"path": "$UNDEFINED_VAR/dir"}
        result = SettingsModel._resolve_environment_variables(input_dict)

        # os.path.expandvars leaves undefined vars as-is on Unix
        # or expands to empty string depending on the shell
        # We just check it doesn't crash
        assert "path" in result


class TestGetPydanticConfig:
    """Tests for get_pydantic_config static method."""

    def test_valid_config(self):
        """Test creating Pydantic config from valid dictionary."""
        config_dict = {
            "logging": {"level": "INFO"},
            "output": {"formats": ["json"]},
        }
        config = SettingsModel.get_pydantic_config(config_dict)

        assert isinstance(config, AppConfig)
        assert config.logging.level == "INFO"
        assert config.output.formats == ["json"]

    def test_invalid_config_raises_validation_error(self):
        """Test invalid config raises ValidationError."""
        config_dict = {
            "logging": {"level": "INVALID_LEVEL"},
        }

        with pytest.raises(ValidationError):
            SettingsModel.get_pydantic_config(config_dict)

    def test_empty_config_uses_defaults(self):
        """Test empty config dictionary uses defaults."""
        config = SettingsModel.get_pydantic_config({})

        assert isinstance(config, AppConfig)
        assert config.logging.level == "INFO"
        assert config.container.engine == "docker"


class TestSettingsLoading:
    """Integration tests for loading settings from files."""

    def test_load_from_toml_file(self, temp_settings_file: Path):
        """Test loading settings from TOML file."""
        settings = SettingsModel(settings_files=[str(temp_settings_file)])
        config = settings.get()

        assert config.logging.level == "DEBUG"
        assert config.logging.show_path is True
        assert config.generation.saturation_adjustment == 1.5
        assert config.backends.custom.n_clusters == 32

    def test_load_minimal_settings(self, minimal_settings_file: Path):
        """Test loading minimal settings file (uses defaults)."""
        settings = SettingsModel(settings_files=[str(minimal_settings_file)])
        config = settings.get()

        # Should all be defaults
        assert config.logging.level == "INFO"
        assert config.generation.default_backend == "pywal"
        assert config.container.engine == "docker"

    def test_load_invalid_settings(self, invalid_settings_file: Path):
        """Test loading invalid settings raises ValidationError."""
        with pytest.raises(ValidationError):
            SettingsModel(settings_files=[str(invalid_settings_file)])

    def test_environment_variable_resolution(
        self, settings_with_env_vars: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Test environment variables are resolved when loading."""
        monkeypatch.setenv("HOME", "/home/testuser")

        settings = SettingsModel(settings_files=[str(settings_with_env_vars)])
        config = settings.get()

        # $HOME should be expanded
        expected_path = Path("/home/testuser/.config/color-scheme/output")
        assert config.output.directory == expected_path

    def test_nonexistent_file(self, tmp_path: Path):
        """Test loading from nonexistent file."""
        nonexistent = tmp_path / "does_not_exist.toml"
        # Dynaconf will create an empty config if file doesn't exist
        settings = SettingsModel(settings_files=[str(nonexistent)])
        config = settings.get()

        # Should use all defaults
        assert isinstance(config, AppConfig)


class TestComplexSettings:
    """Tests for complex settings scenarios."""

    def test_nested_backend_settings(self, tmp_path: Path):
        """Test loading nested backend settings."""
        settings_content = """
[backends.pywal]
backend_algorithm = "colorz"

[backends.wallust]
backend_type = "full"

[backends.custom]
algorithm = "dominant"
n_clusters = 64
"""
        settings_file = tmp_path / "backends.toml"
        settings_file.write_text(settings_content)

        settings = SettingsModel(settings_files=[str(settings_file)])
        config = settings.get()

        assert config.backends.pywal.backend_algorithm == "colorz"
        assert config.backends.wallust.backend_type == "full"
        assert config.backends.custom.algorithm == "dominant"
        assert config.backends.custom.n_clusters == 64

    def test_output_formats_list(self, tmp_path: Path):
        """Test loading output formats as list."""
        settings_content = """
[output]
formats = ["json", "yaml", "css"]
"""
        settings_file = tmp_path / "output.toml"
        settings_file.write_text(settings_content)

        settings = SettingsModel(settings_files=[str(settings_file)])
        config = settings.get()

        assert config.output.formats == ["json", "yaml", "css"]

    def test_all_logging_options(self, tmp_path: Path):
        """Test loading all logging options."""
        settings_content = """
[logging]
level = "WARNING"
show_time = false
show_path = true
"""
        settings_file = tmp_path / "logging.toml"
        settings_file.write_text(settings_content)

        settings = SettingsModel(settings_files=[str(settings_file)])
        config = settings.get()

        assert config.logging.level == "WARNING"
        assert config.logging.show_time is False
        assert config.logging.show_path is True

    def test_saturation_boundaries(self, tmp_path: Path):
        """Test saturation adjustment at boundaries."""
        # Minimum
        settings_min = """
[generation]
saturation_adjustment = 0.0
"""
        file_min = tmp_path / "sat_min.toml"
        file_min.write_text(settings_min)
        config_min = SettingsModel(settings_files=[str(file_min)]).get()
        assert config_min.generation.saturation_adjustment == 0.0

        # Maximum
        settings_max = """
[generation]
saturation_adjustment = 2.0
"""
        file_max = tmp_path / "sat_max.toml"
        file_max.write_text(settings_max)
        config_max = SettingsModel(settings_files=[str(file_max)]).get()
        assert config_max.generation.saturation_adjustment == 2.0


class TestGlobalSettings:
    """Tests for the global Settings instance."""

    def test_global_settings_exists(self):
        """Test that global Settings instance exists."""
        from color_scheme.config.settings import Settings

        assert Settings is not None
        assert isinstance(Settings, SettingsModel)

    def test_global_settings_get(self):
        """Test global Settings.get() method."""
        from color_scheme.config.settings import Settings

        config = Settings.get()
        assert isinstance(config, AppConfig)


class TestSettingsEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_malformed_toml(self, tmp_path: Path):
        """Test handling of malformed TOML file."""
        malformed = tmp_path / "malformed.toml"
        malformed.write_text("this is not [[ valid toml")

        # Dynaconf should handle the parsing error
        # Testing malformed TOML - exception type varies by parser
        with pytest.raises(Exception):  # noqa: B017
            SettingsModel(settings_files=[str(malformed)])

    def test_validation_error_on_init(self, invalid_settings_file: Path):
        """Test that ValidationError is raised during initialization."""
        with pytest.raises(ValidationError) as exc_info:
            SettingsModel(settings_files=[str(invalid_settings_file)])

        # Check that error contains information about the validation failure
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_case_insensitive_sections(self, tmp_path: Path):
        """Test that TOML sections are case-insensitive after processing."""
        settings_content = """
[LOGGING]
LEVEL = "DEBUG"

[OUTPUT]
FORMATS = ["json"]
"""
        settings_file = tmp_path / "uppercase.toml"
        settings_file.write_text(settings_content)

        settings = SettingsModel(settings_files=[str(settings_file)])
        config = settings.get()

        # Keys should be lowercased
        assert config.logging.level == "DEBUG"
        assert config.output.formats == ["json"]

    def test_path_conversion(self, tmp_path: Path):
        """Test that string paths are converted to Path objects."""
        settings_content = """
[output]
directory = "/tmp/test/output"

[templates]
directory = "/tmp/test/templates"
"""
        settings_file = tmp_path / "paths.toml"
        settings_file.write_text(settings_content)

        settings = SettingsModel(settings_files=[str(settings_file)])
        config = settings.get()

        assert isinstance(config.output.directory, Path)
        assert isinstance(config.templates.directory, Path)
        assert config.output.directory == Path("/tmp/test/output")
        assert config.templates.directory == Path("/tmp/test/templates")
