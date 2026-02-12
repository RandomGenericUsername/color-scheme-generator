"""Data models for configuration resolution with source attribution.

These models track where each configuration value came from during the
resolution process, enabling the dry-run feature to display configuration
sources and detect overrides.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConfigSource(Enum):
    """Source of a configuration value."""

    CLI = "CLI argument"
    ENV = "Environment variable"
    USER_CONFIG = "User config"
    PROJECT_CONFIG = "Project config"
    PACKAGE_DEFAULT = "Package default"


class WarningLevel(Enum):
    """Severity level for warnings detected during resolution."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ResolvedValue:
    """A configuration value with source attribution.

    Tracks a resolved configuration value along with metadata about
    where it came from and what other values it may have overridden.
    """

    value: Any
    """The actual resolved value."""

    source: ConfigSource
    """Where this value came from (CLI, ENV, user config, etc.)."""

    source_detail: str
    """Specific detail identifying the exact source.

    Examples:
        - "--backend" for CLI argument
        - "COLORSCHEME_GENERATION__DEFAULT_BACKEND" for environment variable
        - "~/.config/color-scheme/settings.toml" for user config
        - "./settings.toml" for project config
        - "Package built-in default" for package defaults
    """

    overrides: list[tuple[ConfigSource, Any]] = field(default_factory=list)
    """List of (source, value) pairs that were overridden by this value.

    Enables detection and display of configuration precedence in dry-run output.
    """


@dataclass
class Warning:
    """A warning or issue detected during configuration resolution.

    Used to report potential problems without failing the dry-run.
    """

    level: WarningLevel
    """Severity of the warning (info, warning, or error)."""

    message: str
    """Short description of the warning."""

    detail: str = ""
    """Detailed explanation or context."""

    action: str = ""
    """Suggested action to resolve the warning."""


class ResolvedConfig:
    """Complete resolved configuration with full attribution.

    Stores configuration values indexed by dot-notation keys (e.g., "output.directory"),
    with each value being a ResolvedValue that includes source attribution.
    """

    def __init__(self):
        """Initialize empty resolved configuration."""
        self._values: dict[str, ResolvedValue] = {}

    def set(self, key: str, resolved: ResolvedValue) -> None:
        """Set a resolved value.

        Args:
            key: Dot-notation key path (e.g., "generation.default_backend")
            resolved: ResolvedValue with source attribution
        """
        self._values[key] = resolved

    def get(self, key: str) -> ResolvedValue | None:
        """Get a resolved value by key.

        Args:
            key: Dot-notation key path

        Returns:
            ResolvedValue if found, None otherwise
        """
        return self._values.get(key)

    def items(self) -> list[tuple[str, ResolvedValue]]:
        """Iterate over all resolved values.

        Returns:
            List of (key, ResolvedValue) tuples
        """
        return list(self._values.items())

    def to_dict(self) -> dict[str, Any]:
        """Convert to nested dict of values (without attribution).

        Useful for getting just the resolved values in the same structure
        as the input configuration.

        Returns:
            Nested dictionary of resolved values
        """
        result: dict[str, Any] = {}
        for key, resolved in self._values.items():
            # key format: "section.subsection.key"
            parts = key.split(".")
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = resolved.value
        return result

    def __len__(self) -> int:
        """Return number of resolved values."""
        return len(self._values)

    def __repr__(self) -> str:
        """String representation showing number of resolved values."""
        return f"ResolvedConfig({len(self._values)} values)"
