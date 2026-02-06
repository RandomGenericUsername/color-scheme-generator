"""Configuration resolution with source attribution.

The ConfigResolver class collects configuration from multiple sources
(CLI arguments, environment variables, config files) and applies
precedence rules to resolve the final configuration while tracking
where each value came from.
"""

import os
import tomllib
from pathlib import Path
from typing import Any

from color_scheme_settings.models import (
    ConfigSource,
    ResolvedConfig,
    ResolvedValue,
    Warning,
    WarningLevel,
)


class ConfigResolver:
    """Resolve configuration from multiple sources with full attribution.

    Collects configuration values from all sources (CLI args, environment
    variables, user config, project config, package defaults), applies
    precedence rules, and returns a ResolvedConfig object that tracks
    the source of each value.

    Precedence order (highest to lowest):
    1. CLI arguments (e.g., --backend)
    2. Environment variables (e.g., COLORSCHEME_*)
    3. User config (~/.config/color-scheme/settings.toml)
    4. Project config (./settings.toml)
    5. Package defaults
    """

    def __init__(self, package_name: str = "color-scheme"):
        """Initialize the resolver.

        Args:
            package_name: Name of the package (default: "color-scheme")
        """
        self.package_name = package_name
        self.warnings: list[Warning] = []

    def resolve(
        self,
        cli_args: dict[str, Any] | None = None,
        command_ctx: dict[str, Any] | None = None,
    ) -> ResolvedConfig:
        """Main resolution method.

        Collects configuration from all sources and applies precedence
        rules to build a complete ResolvedConfig with source attribution.

        Args:
            cli_args: Arguments from CLI (e.g., {"backend": "pywal"}).
                     Flat dictionary with keys that map to config paths.
            command_ctx: Context information about the command being executed.
                        (command name, image path, etc.)

        Returns:
            ResolvedConfig with all values and their source attribution
        """
        cli_args = cli_args or {}
        command_ctx = command_ctx or {}

        # 1. Load package defaults
        defaults = self._load_package_defaults()

        # 2. Load project config (if exists)
        project_config = self._load_project_config()

        # 3. Load user config (if exists)
        user_config = self._load_user_config()

        # 4. Collect environment variables
        env_vars = self._collect_env_vars()

        # 5. Resolve with precedence
        return self._apply_precedence(
            cli_args=cli_args,
            env_vars=env_vars,
            user_config=user_config,
            project_config=project_config,
            defaults=defaults,
        )

    def _load_package_defaults(self) -> dict[str, Any]:
        """Load package default settings.

        Returns:
            Dictionary of package defaults (empty for now, will be populated
            from actual package settings.toml in integration)
        """
        # This will be integrated with the actual settings loading system
        # For now, return empty dict as placeholder
        return {}

    def _load_project_config(self) -> dict[str, Any] | None:
        """Load ./settings.toml from current working directory.

        Returns:
            Dictionary of project config values, or None if file doesn't exist
        """
        project_settings = Path.cwd() / "settings.toml"

        if not project_settings.exists():
            return None

        try:
            with project_settings.open("rb") as f:
                return tomllib.load(f)
        except Exception as e:
            self.warnings.append(
                Warning(
                    level=WarningLevel.WARNING,
                    message="Failed to load project config",
                    detail=f"File: {project_settings}",
                    action=f"Error: {e}",
                )
            )
            return None

    def _load_user_config(self) -> dict[str, Any] | None:
        """Load ~/.config/color-scheme/settings.toml.

        Returns:
            Dictionary of user config values, or None if file doesn't exist
        """
        # Respect XDG_CONFIG_HOME
        config_home = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser()
        user_settings = config_home / self.package_name / "settings.toml"

        if not user_settings.exists():
            return None

        try:
            with user_settings.open("rb") as f:
                return tomllib.load(f)
        except Exception as e:
            self.warnings.append(
                Warning(
                    level=WarningLevel.WARNING,
                    message="Failed to load user config",
                    detail=f"File: {user_settings}",
                    action=f"Error: {e}",
                )
            )
            return None

    def _collect_env_vars(self) -> dict[str, Any]:
        """Collect COLORSCHEME_* environment variables.

        Pattern: COLORSCHEME_SECTION__KEY (double underscore for nesting)
        Example: COLORSCHEME_OUTPUT__DIRECTORY

        Returns:
            Dictionary of environment variables in config structure format
        """
        env_vars: dict[str, Any] = {}
        prefix = "COLORSCHEME_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix
                config_key = key[len(prefix) :]

                # Split on double underscore
                parts = config_key.split("__")

                # Build nested dict
                current = env_vars
                for part in parts[:-1]:
                    part_lower = part.lower()
                    if part_lower not in current:
                        current[part_lower] = {}
                    current = current[part_lower]

                # Set final value
                current[parts[-1].lower()] = value

        # Also check special variables
        if "COLOR_SCHEME_TEMPLATES" in os.environ:
            if "templates" not in env_vars:
                env_vars["templates"] = {}
            env_vars["templates"]["directory"] = os.environ["COLOR_SCHEME_TEMPLATES"]

        return env_vars

    def _apply_precedence(
        self,
        cli_args: dict[str, Any],
        env_vars: dict[str, Any],
        user_config: dict[str, Any] | None,
        project_config: dict[str, Any] | None,
        defaults: dict[str, Any],
    ) -> ResolvedConfig:
        """Apply precedence rules and build ResolvedConfig.

        Walks through all configuration keys and applies precedence rules
        to determine which source provides the final value.

        Args:
            cli_args: CLI arguments (highest precedence)
            env_vars: Environment variables
            user_config: User configuration file
            project_config: Project configuration file
            defaults: Package defaults (lowest precedence)

        Returns:
            ResolvedConfig with all values and source attribution
        """
        user_config = user_config or {}
        project_config = project_config or {}

        resolved = ResolvedConfig()

        # Collect all possible keys from all sources
        all_keys: set[str] = set()
        self._collect_keys(all_keys, cli_args)
        self._collect_keys(all_keys, env_vars)
        self._collect_keys(all_keys, user_config)
        self._collect_keys(all_keys, project_config)
        self._collect_keys(all_keys, defaults)

        # Resolve each key
        for key in all_keys:
            cli_value = self._get_value(cli_args, key)
            env_value = self._get_value(env_vars, key)
            user_value = self._get_value(user_config, key)
            project_value = self._get_value(project_config, key)
            default_value = self._get_value(defaults, key)

            resolved_value = self._resolve_setting(
                key=key,
                cli_value=cli_value,
                env_value=env_value,
                user_value=user_value,
                project_value=project_value,
                default_value=default_value,
            )

            resolved.set(key, resolved_value)

        return resolved

    def _collect_keys(
        self,
        keys: set[str],
        config: dict[str, Any],
        prefix: str = "",
    ) -> None:
        """Recursively collect all dot-notation keys from a nested dict.

        Args:
            keys: Set to accumulate keys
            config: Dictionary to traverse
            prefix: Current path prefix for nested dicts
        """
        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                self._collect_keys(keys, value, full_key)
            else:
                keys.add(full_key)

    def _get_value(
        self,
        config: dict[str, Any],
        key: str,
    ) -> Any:
        """Get a value from a nested dict using dot notation.

        Args:
            config: Dictionary to search
            key: Dot-notation key path (e.g., "output.directory")

        Returns:
            The value, or None if not found
        """
        parts = key.split(".")
        current = config

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current if current != {} else None

    def _resolve_setting(
        self,
        key: str,
        cli_value: Any | None,
        env_value: Any | None,
        user_value: Any | None,
        project_value: Any | None,
        default_value: Any,
    ) -> ResolvedValue:
        """Resolve a single setting with precedence.

        Applies precedence rules to determine which source provides
        the final value and tracks what was overridden.

        Precedence (highest to lowest):
        1. CLI argument (if provided)
        2. Environment variable (if set)
        3. User config (if exists)
        4. Project config (if exists)
        5. Package default

        Args:
            key: Configuration key
            cli_value: Value from CLI
            env_value: Value from environment
            user_value: Value from user config
            project_value: Value from project config
            default_value: Default value from package

        Returns:
            ResolvedValue with source attribution and overrides
        """
        # Check CLI (highest precedence)
        if cli_value is not None:
            overrides = []
            if env_value is not None:
                overrides.append((ConfigSource.ENV, env_value))
            if user_value is not None:
                overrides.append((ConfigSource.USER_CONFIG, user_value))
            if project_value is not None:
                overrides.append((ConfigSource.PROJECT_CONFIG, project_value))
            if default_value is not None:
                overrides.append((ConfigSource.PACKAGE_DEFAULT, default_value))

            return ResolvedValue(
                value=cli_value,
                source=ConfigSource.CLI,
                source_detail=f"--{key.replace('_', '-')}",
                overrides=overrides,
            )

        # Check ENV
        if env_value is not None:
            overrides = []
            if user_value is not None:
                overrides.append((ConfigSource.USER_CONFIG, user_value))
            if project_value is not None:
                overrides.append((ConfigSource.PROJECT_CONFIG, project_value))
            if default_value is not None:
                overrides.append((ConfigSource.PACKAGE_DEFAULT, default_value))

            return ResolvedValue(
                value=env_value,
                source=ConfigSource.ENV,
                source_detail=f"COLORSCHEME_{key.upper().replace('.', '__')}",
                overrides=overrides,
            )

        # Check User Config
        if user_value is not None:
            overrides = []
            if project_value is not None:
                overrides.append((ConfigSource.PROJECT_CONFIG, project_value))
            if default_value is not None:
                overrides.append((ConfigSource.PACKAGE_DEFAULT, default_value))

            return ResolvedValue(
                value=user_value,
                source=ConfigSource.USER_CONFIG,
                source_detail=f"~/.config/{self.package_name}/settings.toml",
                overrides=overrides,
            )

        # Check Project Config
        if project_value is not None:
            overrides = []
            if default_value is not None:
                overrides.append((ConfigSource.PACKAGE_DEFAULT, default_value))

            return ResolvedValue(
                value=project_value,
                source=ConfigSource.PROJECT_CONFIG,
                source_detail="./settings.toml",
                overrides=overrides,
            )

        # Use default (or None if no default)
        return ResolvedValue(
            value=default_value,
            source=ConfigSource.PACKAGE_DEFAULT,
            source_detail="Package built-in default",
            overrides=[],
        )
