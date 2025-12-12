"""Settings loader using dynaconf + Pydantic.

This module provides the SettingsModel class that loads configuration from
settings.toml using dynaconf and validates it with Pydantic models.

It follows the exact same pattern as the dotfiles installer's settings module.
"""

import os
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf
from pydantic import ValidationError

from colorscheme_generator.config.config import AppConfig as PydanticAppConfig

# Get the config directory (now inside the package)
CONFIG_DIR = Path(__file__).parent
SETTINGS_FILE = CONFIG_DIR / "settings.toml"


class SettingsModel:
    """Settings loader using dynaconf + Pydantic (matches installer pattern).

    This class:
    1. Loads settings from TOML files using dynaconf
    2. Converts keys to lowercase
    3. Resolves environment variables ($HOME, etc.)
    4. Validates with Pydantic models

    Example:
        >>> settings = SettingsModel()
        >>> config = settings.get()
        >>> print(config.output.directory)
        PosixPath('/home/user/.cache/colorscheme')
    """

    def __init__(self, settings_files: list[str] | None = None):
        """Initialize settings loader.

        Args:
            settings_files: List of settings file paths. If None, uses default.
        """
        if settings_files is None:
            settings_files = [str(SETTINGS_FILE)]

        self.dynaconf_settings: Dynaconf = Dynaconf(
            settings_files=settings_files,
        )
        self.settings: PydanticAppConfig = self.get_pydantic_config(
            self._convert_dict_to_lower_case(
                self._resolve_environment_variables(
                    self.dynaconf_settings.to_dict()
                )
            )
        )

    @staticmethod
    def _convert_dict_to_lower_case(
        settings_dict: dict[str, Any],
    ) -> dict[str, Any]:
        """Convert all keys to lowercase recursively.

        Args:
            settings_dict: Dictionary with potentially mixed-case keys

        Returns:
            Dictionary with all lowercase keys
        """
        lower_case_dict = {}
        for key, value in settings_dict.items():
            if isinstance(value, dict):
                lower_case_dict[key.lower()] = (
                    SettingsModel._convert_dict_to_lower_case(value)
                )
            else:
                lower_case_dict[key.lower()] = value
        return lower_case_dict

    @staticmethod
    def _resolve_environment_variables(
        settings_dict: dict[str, Any],
    ) -> dict[str, Any]:
        """Resolve environment variables in string values.

        Expands variables like $HOME, $USER, etc. in string values.

        Args:
            settings_dict: Dictionary potentially containing env vars

        Returns:
            Dictionary with resolved environment variables
        """

        def _resolve_string_values(data: Any) -> Any:
            """Recursively resolve env variables in nested structures."""
            if isinstance(data, str):
                return os.path.expandvars(data)
            elif isinstance(data, dict):
                return {
                    key: _resolve_string_values(value)
                    for key, value in data.items()
                }
            elif isinstance(data, list):
                return [_resolve_string_values(item) for item in data]
            else:
                return data

        return _resolve_string_values(settings_dict)

    @staticmethod
    def get_pydantic_config(settings: dict) -> PydanticAppConfig:
        """Validate settings with Pydantic.

        Args:
            settings: Dictionary of settings

        Returns:
            Validated AppConfig instance

        Raises:
            ValidationError: If settings don't match schema
        """
        try:
            return PydanticAppConfig(**settings)
        except ValidationError as e:
            raise e

    def get(self) -> PydanticAppConfig:
        """Get validated settings.

        Returns:
            Validated AppConfig instance
        """
        return self.settings


# Global settings instance
Settings: SettingsModel = SettingsModel()
