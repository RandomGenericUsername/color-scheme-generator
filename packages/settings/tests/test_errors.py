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
