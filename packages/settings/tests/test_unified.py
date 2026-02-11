"""Tests for UnifiedConfig construction and transforms."""

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
