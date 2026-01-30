"""Shared fixtures for config tests."""

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def temp_settings_file(tmp_path: Path) -> Path:
    """Create a temporary settings.toml file.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to temporary settings file
    """
    settings_content = """
[logging]
level = "DEBUG"
show_time = true
show_path = true

[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css"]

[generation]
default_backend = "pywal"
saturation_adjustment = 1.5

[backends.pywal]
backend_algorithm = "haishoku"

[backends.wallust]
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 32
"""
    settings_file = tmp_path / "settings.toml"
    settings_file.write_text(settings_content)
    return settings_file


@pytest.fixture
def invalid_settings_file(tmp_path: Path) -> Path:
    """Create an invalid settings.toml file.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to invalid settings file
    """
    settings_content = """
[logging]
level = "INVALID_LEVEL"

[generation]
saturation_adjustment = 3.0  # Out of range (max 2.0)
"""
    settings_file = tmp_path / "invalid_settings.toml"
    settings_file.write_text(settings_content)
    return settings_file


@pytest.fixture
def minimal_settings_file(tmp_path: Path) -> Path:
    """Create a minimal settings.toml file with only required fields.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to minimal settings file
    """
    settings_content = """
# Minimal config - everything uses defaults
"""
    settings_file = tmp_path / "minimal_settings.toml"
    settings_file.write_text(settings_content)
    return settings_file


@pytest.fixture
def sample_config_dict() -> dict[str, Any]:
    """Sample configuration dictionary for testing.

    Returns:
        Sample configuration dictionary
    """
    return {
        "logging": {
            "level": "INFO",
            "show_time": True,
            "show_path": False,
        },
        "output": {
            "directory": Path.home() / ".config" / "color-scheme" / "output",
            "formats": ["json", "sh", "css"],
        },
        "generation": {
            "default_backend": "pywal",
            "saturation_adjustment": 1.0,
        },
        "backends": {
            "pywal": {
                "backend_algorithm": "haishoku",
            },
            "wallust": {
                "backend_type": "resized",
            },
            "custom": {
                "algorithm": "kmeans",
                "n_clusters": 16,
            },
        },
        "templates": {
            "directory": Path(__file__).parent.parent.parent
            / "src"
            / "color_scheme"
            / "templates"
        },
    }


@pytest.fixture
def mock_home_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Mock HOME environment variable with temporary directory.

    Args:
        tmp_path: Pytest temporary directory fixture
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Path to mocked home directory
    """
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    monkeypatch.setenv("HOME", str(home_dir))
    return home_dir


@pytest.fixture
def settings_with_env_vars(tmp_path: Path) -> Path:
    """Create settings file with environment variables.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to settings file with env vars
    """
    settings_content = """
[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json"]

[generation]
default_backend = "pywal"
"""
    settings_file = tmp_path / "settings_env.toml"
    settings_file.write_text(settings_content)
    return settings_file
