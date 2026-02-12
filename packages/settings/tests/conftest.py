"""Shared fixtures for settings tests."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_settings_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure for settings files."""
    return tmp_path


@pytest.fixture
def core_defaults_toml(tmp_settings_dir: Path) -> Path:
    """Create a core package settings.toml (flat sections)."""
    content = """\
[logging]
level = "INFO"
show_time = true
show_path = false

[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]

[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

[backends.pywal]
backend_algorithm = "wal"

[backends.wallust]
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16
"""
    file_path = tmp_settings_dir / "core_settings.toml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def orchestrator_defaults_toml(tmp_settings_dir: Path) -> Path:
    """Create an orchestrator package settings.toml (flat sections)."""
    content = """\
[container]
engine = "docker"
"""
    file_path = tmp_settings_dir / "orchestrator_settings.toml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def project_root_toml(tmp_settings_dir: Path) -> Path:
    """Create a project root settings.toml (namespaced sections)."""
    content = """\
[core.generation]
default_backend = "wallust"

[core.output]
formats = ["json", "css", "yaml"]

[orchestrator.container]
engine = "podman"
"""
    project_dir = tmp_settings_dir / "project"
    project_dir.mkdir()
    file_path = project_dir / "settings.toml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def user_config_toml(tmp_settings_dir: Path) -> Path:
    """Create a user config settings.toml (namespaced sections)."""
    content = """\
[core.generation]
saturation_adjustment = 1.3

[core.backends.custom]
n_clusters = 32
"""
    file_path = tmp_settings_dir / "user_settings.toml"
    file_path.write_text(content)
    return file_path
