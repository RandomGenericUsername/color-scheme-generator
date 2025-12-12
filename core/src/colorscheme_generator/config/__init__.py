"""Configuration module for colorscheme generator.

This module provides configuration management using dynaconf and Pydantic,
following the same pattern as the dotfiles installer.
"""

from colorscheme_generator.config.config import (
    AppConfig,
    BackendSettings,
    CustomBackendSettings,
    GenerationSettings,
    OutputSettings,
    PywalBackendSettings,
    TemplateSettings,
    WallustBackendSettings,
)
from colorscheme_generator.config.enums import (
    Backend,
    ColorAlgorithm,
    ColorFormat,
)
from colorscheme_generator.config.settings import Settings, SettingsModel

__all__ = [
    # Settings
    "Settings",
    "SettingsModel",
    # Config models
    "AppConfig",
    "OutputSettings",
    "GenerationSettings",
    "BackendSettings",
    "PywalBackendSettings",
    "WallustBackendSettings",
    "CustomBackendSettings",
    "TemplateSettings",
    # Enums
    "Backend",
    "ColorFormat",
    "ColorAlgorithm",
]
