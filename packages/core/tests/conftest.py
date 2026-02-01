"""Pytest configuration and fixtures."""

import pytest

from color_scheme.config.config import AppConfig


@pytest.fixture
def sample_settings_dict():
    """Sample settings dictionary for testing."""
    return {
        "logging": {
            "level": "DEBUG",
            "show_time": True,
            "show_path": False,
        },
        "output": {
            "directory": "/tmp/test-output",
            "formats": ["json", "css"],
        },
        "generation": {
            "default_backend": "custom",
            "saturation_adjustment": 1.5,
        },
        "backends": {
            "pywal": {"backend_algorithm": "haishoku"},
            "wallust": {"backend_type": "resized"},
            "custom": {"algorithm": "kmeans", "n_clusters": 16},
        },
        "templates": {"directory": "templates"},
    }


@pytest.fixture
def app_config(sample_settings_dict):
    """Create an AppConfig instance for testing."""
    return AppConfig(**sample_settings_dict)
