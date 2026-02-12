"""Unified path discovery for the color-scheme layered system.

This module is the SINGLE SOURCE OF TRUTH for all filesystem paths
used by the settings and templates packages.
"""

import os
from pathlib import Path

# =============================================================================
# Application Constants
# =============================================================================

APP_NAME = "color-scheme"
SETTINGS_FILENAME = "settings.toml"
TEMPLATES_DIRNAME = "templates"

# =============================================================================
# XDG Base Directory Specification
# =============================================================================

_xdg_default = Path.home() / ".config"
XDG_CONFIG_HOME: Path = Path(os.getenv("XDG_CONFIG_HOME", _xdg_default))

# =============================================================================
# User Layer Paths
# =============================================================================

USER_CONFIG_DIR: Path = XDG_CONFIG_HOME / APP_NAME
USER_SETTINGS_FILE: Path = USER_CONFIG_DIR / SETTINGS_FILENAME
USER_TEMPLATES_DIR: Path = USER_CONFIG_DIR / TEMPLATES_DIRNAME
USER_OUTPUT_DIR: Path = USER_CONFIG_DIR / "output"

# =============================================================================
# Container Layer Paths
# =============================================================================

CONTAINER_TEMPLATES_DIR: Path = Path("/templates")
CONTAINER_OUTPUT_DIR: Path = Path("/output")


# =============================================================================
# Path Discovery Functions
# =============================================================================


def get_project_settings_file(project_root: Path) -> Path:
    """Get the settings file path for a project."""
    return project_root / SETTINGS_FILENAME


def get_project_templates_dir(project_root: Path) -> Path:
    """Get the templates directory path for a project."""
    return project_root / TEMPLATES_DIRNAME


def is_container_environment() -> bool:
    """Check if running inside a container."""
    return CONTAINER_TEMPLATES_DIR.exists()


def get_env_templates_override() -> Path | None:
    """Get template directory from COLOR_SCHEME_TEMPLATES env var."""
    env_value = os.getenv("COLOR_SCHEME_TEMPLATES")
    if env_value is not None:
        return Path(env_value)
    return None
