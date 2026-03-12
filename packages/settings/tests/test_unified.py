"""Tests for UnifiedConfig construction and transforms."""

import pytest
from pydantic import BaseModel, Field

from color_scheme_settings.errors import SettingsValidationError
from color_scheme_settings.transforms import (
    convert_keys_to_lowercase,
    parse_env_vars,
    resolve_environment_variables,
)
from color_scheme_settings.unified import build_validated_namespace


class StrictModel(BaseModel):
    value: int = Field(ge=0)


class TestValidationErrorIncludesSourceLayer:
    """MIN-4: SettingsValidationError must include source_layer when provided."""

    def test_validation_error_includes_source_layer(self):
        with pytest.raises(SettingsValidationError) as exc_info:
            build_validated_namespace(
                namespace="test",
                model=StrictModel,
                data={"value": -1},
                source_layer="user",
            )
        assert exc_info.value.source_layer == "user"


class TestConvertKeysToLowercase:
    """Tests for recursive key lowercasing."""

    def test_simple_dict(self):
        result = convert_keys_to_lowercase({"LEVEL": "INFO"})
        assert result == {"level": "INFO"}

    def test_nested_dict(self):
        result = convert_keys_to_lowercase({"BACKENDS": {"PYWAL": {"ALGO": "wal"}}})
        assert result == {"backends": {"pywal": {"algo": "wal"}}}

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
        result = resolve_environment_variables({"paths": ["$HOME/a", "$HOME/b"]})
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


class TestParseEnvVars:
    """Tests for parse_env_vars() shared utility."""

    def test_single_key(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("COLORSCHEME_OUTPUT__DIRECTORY", "/tmp/out")
        result = parse_env_vars()
        assert result == {"output": {"directory": "/tmp/out"}}

    def test_nested_double_underscore(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("COLORSCHEME_GENERATION__DEFAULT_BACKEND", "wallust")
        result = parse_env_vars()
        assert result["generation"]["default_backend"] == "wallust"

    def test_color_scheme_templates_special_case(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("COLOR_SCHEME_TEMPLATES", "/custom/templates")
        result = parse_env_vars(environ={"COLOR_SCHEME_TEMPLATES": "/custom/templates"})
        assert result == {"templates": {"directory": "/custom/templates"}}

    def test_unrelated_vars_ignored(self):
        result = parse_env_vars(environ={"HOME": "/home/user", "PATH": "/usr/bin"})
        assert "home" not in result
        assert "path" not in result

    def test_empty_environ(self):
        result = parse_env_vars(environ={})
        assert result == {}

    def test_keys_normalised_to_lowercase(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("COLORSCHEME_OUTPUT__DIRECTORY", "/tmp")
        result = parse_env_vars()
        assert "output" in result
        assert "directory" in result["output"]

    def test_explicit_environ_overrides_os_environ(self):
        result = parse_env_vars(
            environ={"COLORSCHEME_OUTPUT__DIRECTORY": "/explicit"}
        )
        assert result == {"output": {"directory": "/explicit"}}
