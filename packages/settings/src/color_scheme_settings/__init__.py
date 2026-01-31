"""Shared layered configuration system for color-scheme.

Public API:
    SchemaRegistry  -- Register package config schemas
    load_config()   -- Load and merge all layers (cached)
    reload_config() -- Force reload (for testing)
    get_config()    -- Load with optional CLI overrides
    apply_overrides -- Apply dot-notation overrides to a config
"""

from typing import Any

from pydantic import BaseModel

from color_scheme_settings.errors import (
    SettingsError,
    SettingsFileError,
    SettingsOverrideError,
    SettingsRegistryError,
    SettingsValidationError,
)
from color_scheme_settings.loader import SettingsLoader
from color_scheme_settings.merger import merge_layers
from color_scheme_settings.overrides import apply_overrides
from color_scheme_settings.registry import SchemaRegistry
from color_scheme_settings.unified import build_unified_config

_config: BaseModel | None = None
_unified_model: type[BaseModel] | None = None
_loader_kwargs: dict[str, Any] = {}


def configure(
    unified_model: type[BaseModel],
    project_root: Any | None = None,
    user_config_path: Any | None = None,
) -> None:
    """Configure the settings system before first load.

    Args:
        unified_model: The Pydantic model class that composes all namespaces.
        project_root: Path to project root directory (optional).
        user_config_path: Path to user settings file (optional).
    """
    global _unified_model, _loader_kwargs, _config
    _unified_model = unified_model
    _loader_kwargs = {}
    if project_root is not None:
        _loader_kwargs["project_root"] = project_root
    if user_config_path is not None:
        _loader_kwargs["user_config_path"] = user_config_path
    _config = None


def load_config() -> BaseModel:
    """Load, merge, and validate all settings layers.

    Cached after first call. Use reload_config() to force refresh.

    Returns:
        Validated UnifiedConfig instance
    """
    global _config
    if _config is not None:
        return _config

    if _unified_model is None:
        raise SettingsError("Settings system not configured. Call configure() first.")

    loader = SettingsLoader(**_loader_kwargs)
    layers = loader.discover_layers()
    merged = merge_layers(layers)
    _config = build_unified_config(_unified_model, merged)
    return _config


def reload_config() -> BaseModel:
    """Force reload from all layers. Useful for testing."""
    global _config
    _config = None
    return load_config()


def get_config(overrides: dict[str, Any] | None = None) -> BaseModel:
    """Load config with optional CLI overrides applied.

    Primary entry point for CLI commands.

    Args:
        overrides: Dict of dot-notation key paths to values.
                   Example: {"core.generation.saturation_adjustment": 1.5}

    Returns:
        Validated config with overrides applied.
    """
    config = load_config()
    if overrides:
        config = apply_overrides(config, overrides)
    return config


def reset() -> None:
    """Reset the entire settings system. For testing only."""
    global _config, _unified_model, _loader_kwargs
    _config = None
    _unified_model = None
    _loader_kwargs = {}
    SchemaRegistry.clear()


__all__ = [
    "SchemaRegistry",
    "configure",
    "load_config",
    "reload_config",
    "get_config",
    "apply_overrides",
    "reset",
    "SettingsError",
    "SettingsFileError",
    "SettingsOverrideError",
    "SettingsRegistryError",
    "SettingsValidationError",
]
