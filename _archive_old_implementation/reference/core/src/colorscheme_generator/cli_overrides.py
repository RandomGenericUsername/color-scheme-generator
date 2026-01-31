"""CLI settings override utility.

This module provides functionality to override application settings
via command-line arguments.
"""

from typing import Any

from colorscheme_generator.config.config import AppConfig


def _set_nested_value(d: dict, path: str, value: Any) -> None:
    """Set a nested dictionary value using dot notation.

    Args:
        d: Dictionary to modify
        path: Dot-separated path (e.g., "generation.saturation_adjustment")
        value: Value to set

    Example:
        >>> d = {"generation": {"saturation_adjustment": 1.0}}
        >>> _set_nested_value(d, "generation.saturation_adjustment", 1.5)
        >>> d["generation"]["saturation_adjustment"]
        1.5
    """
    keys = path.split(".")
    current = d

    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    # Set the final value
    current[keys[-1]] = value


class SettingsOverrider:
    """Apply CLI overrides to settings."""

    @staticmethod
    def apply_overrides(
        base_settings: AppConfig, overrides: dict[str, Any]
    ) -> AppConfig:
        """Apply CLI overrides to base settings.

        Args:
            base_settings: Settings loaded from settings.toml
            overrides: Dict mapping setting paths to values
                      e.g., {"generation.saturation_adjustment": 1.5}

        Returns:
            New AppConfig with overrides applied
        """
        # Convert base settings to dict
        settings_dict = base_settings.model_dump()

        # Apply overrides using dot notation
        for path, value in overrides.items():
            _set_nested_value(settings_dict, path, value)

        # Re-validate with Pydantic
        return AppConfig(**settings_dict)
