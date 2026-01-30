"""Error hierarchy for the settings system."""

from pathlib import Path
from typing import Any


class SettingsError(Exception):
    """Base exception for all settings errors."""


class SettingsFileError(SettingsError):
    """TOML file cannot be read or parsed.

    Raised for malformed TOML syntax or file permission issues.
    NOT raised for missing files (missing files are silently skipped).
    """

    def __init__(self, file_path: Path, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to load {file_path}: {reason}")


class SettingsValidationError(SettingsError):
    """Merged config fails Pydantic validation.

    Includes layer attribution to help the user identify which file
    introduced the invalid value.
    """

    def __init__(
        self,
        namespace: str,
        validation_error: Any,
        source_layer: str | None = None,
    ) -> None:
        self.namespace = namespace
        self.validation_error = validation_error
        self.source_layer = source_layer
        layer_info = f" (from {source_layer} layer)" if source_layer else ""
        super().__init__(
            f"Validation failed for '{namespace}' namespace{layer_info}: "
            f"{validation_error}"
        )


class SettingsOverrideError(SettingsError):
    """CLI override targets a nonexistent key path.

    Catches typos early rather than silently ignoring bad keys.
    """

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Override key path does not exist: {key}")


class SettingsRegistryError(SettingsError):
    """Namespace conflict or missing registration."""

    def __init__(self, namespace: str, reason: str = "") -> None:
        self.namespace = namespace
        detail = f": {reason}" if reason else ""
        super().__init__(f"Registry error for namespace '{namespace}'{detail}")
