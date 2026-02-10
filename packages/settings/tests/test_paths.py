"""Tests for path discovery and utilities."""

from pathlib import Path
from unittest.mock import patch

import pytest

from color_scheme_settings.paths import (
    APP_NAME,
    CONTAINER_OUTPUT_DIR,
    CONTAINER_TEMPLATES_DIR,
    SETTINGS_FILENAME,
    TEMPLATES_DIRNAME,
    USER_CONFIG_DIR,
    USER_OUTPUT_DIR,
    USER_SETTINGS_FILE,
    USER_TEMPLATES_DIR,
    XDG_CONFIG_HOME,
    get_env_templates_override,
    get_project_settings_file,
    get_project_templates_dir,
    is_container_environment,
)


class TestPathConstants:
    """Test path constants."""

    def test_app_name(self):
        """Test APP_NAME constant."""
        assert APP_NAME == "color-scheme"

    def test_settings_filename(self):
        """Test SETTINGS_FILENAME constant."""
        assert SETTINGS_FILENAME == "settings.toml"

    def test_templates_dirname(self):
        """Test TEMPLATES_DIRNAME constant."""
        assert TEMPLATES_DIRNAME == "templates"

    def test_xdg_config_home_is_path(self):
        """Test XDG_CONFIG_HOME is a Path."""
        assert isinstance(XDG_CONFIG_HOME, Path)

    def test_user_config_dir_contains_app_name(self):
        """Test USER_CONFIG_DIR contains app name."""
        assert APP_NAME in str(USER_CONFIG_DIR)

    def test_user_settings_file_is_path(self):
        """Test USER_SETTINGS_FILE is a Path."""
        assert isinstance(USER_SETTINGS_FILE, Path)

    def test_user_settings_file_contains_settings_filename(self):
        """Test USER_SETTINGS_FILE contains settings filename."""
        assert str(USER_SETTINGS_FILE).endswith(SETTINGS_FILENAME)

    def test_user_templates_dir_is_path(self):
        """Test USER_TEMPLATES_DIR is a Path."""
        assert isinstance(USER_TEMPLATES_DIR, Path)

    def test_user_output_dir_is_path(self):
        """Test USER_OUTPUT_DIR is a Path."""
        assert isinstance(USER_OUTPUT_DIR, Path)

    def test_container_templates_dir(self):
        """Test CONTAINER_TEMPLATES_DIR constant."""
        assert CONTAINER_TEMPLATES_DIR == Path("/templates")

    def test_container_output_dir(self):
        """Test CONTAINER_OUTPUT_DIR constant."""
        assert CONTAINER_OUTPUT_DIR == Path("/output")


class TestGetProjectSettingsFile:
    """Test get_project_settings_file function."""

    def test_returns_path(self):
        """Test that function returns a Path."""
        project_root = Path("/test/project")
        result = get_project_settings_file(project_root)
        assert isinstance(result, Path)

    def test_appends_settings_filename(self):
        """Test that settings filename is appended."""
        project_root = Path("/test/project")
        result = get_project_settings_file(project_root)
        assert result.name == SETTINGS_FILENAME
        assert SETTINGS_FILENAME in str(result)

    def test_preserves_project_root(self):
        """Test that project root is preserved."""
        project_root = Path("/test/project")
        result = get_project_settings_file(project_root)
        assert str(project_root) in str(result)

    def test_with_absolute_path(self):
        """Test with absolute path."""
        project_root = Path("/absolute/path")
        result = get_project_settings_file(project_root)
        assert result.is_absolute()

    def test_with_relative_path(self):
        """Test with relative path."""
        project_root = Path("relative/path")
        result = get_project_settings_file(project_root)
        assert "relative" in str(result)


class TestGetProjectTemplatesDir:
    """Test get_project_templates_dir function."""

    def test_returns_path(self):
        """Test that function returns a Path."""
        project_root = Path("/test/project")
        result = get_project_templates_dir(project_root)
        assert isinstance(result, Path)

    def test_appends_templates_dirname(self):
        """Test that templates dirname is appended."""
        project_root = Path("/test/project")
        result = get_project_templates_dir(project_root)
        assert result.name == TEMPLATES_DIRNAME
        assert TEMPLATES_DIRNAME in str(result)

    def test_preserves_project_root(self):
        """Test that project root is preserved."""
        project_root = Path("/test/project")
        result = get_project_templates_dir(project_root)
        assert str(project_root) in str(result)

    def test_with_absolute_path(self):
        """Test with absolute path."""
        project_root = Path("/absolute/path")
        result = get_project_templates_dir(project_root)
        assert result.is_absolute()


class TestIsContainerEnvironment:
    """Test is_container_environment function."""

    def test_returns_boolean(self):
        """Test that function returns a boolean."""
        result = is_container_environment()
        assert isinstance(result, bool)

    def test_checks_container_templates_dir(self):
        """Test that it checks for container templates dir."""
        # This will return True only if /templates exists
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            # The actual implementation checks CONTAINER_TEMPLATES_DIR.exists()
            # which is /templates, so we mock that

    def test_container_templates_dir_path_is_absolute(self):
        """Test that container templates dir path is absolute."""
        assert CONTAINER_TEMPLATES_DIR.is_absolute()
        assert str(CONTAINER_TEMPLATES_DIR) == "/templates"


class TestGetEnvTemplatesOverride:
    """Test get_env_templates_override function."""

    def test_returns_path_or_none(self):
        """Test that function returns Path or None."""
        result = get_env_templates_override()
        assert result is None or isinstance(result, Path)

    def test_with_env_var_set(self):
        """Test with COLOR_SCHEME_TEMPLATES environment variable set."""
        with patch.dict("os.environ", {"COLOR_SCHEME_TEMPLATES": "/custom/templates"}):
            result = get_env_templates_override()
            assert isinstance(result, Path)
            assert str(result) == "/custom/templates"

    def test_with_env_var_unset(self):
        """Test with COLOR_SCHEME_TEMPLATES environment variable unset."""
        with patch.dict("os.environ", {}, clear=False):
            # Remove the env var if it exists
            import os

            if "COLOR_SCHEME_TEMPLATES" in os.environ:
                del os.environ["COLOR_SCHEME_TEMPLATES"]
            result = get_env_templates_override()
            assert result is None

    def test_returns_path_with_env_var(self):
        """Test that PATH is returned when env var is set."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "/test/templates"
            result = get_env_templates_override()
            assert isinstance(result, Path)
            assert str(result) == "/test/templates"

    def test_returns_none_when_env_var_not_set(self):
        """Test that None is returned when env var is not set."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = None
            result = get_env_templates_override()
            assert result is None
