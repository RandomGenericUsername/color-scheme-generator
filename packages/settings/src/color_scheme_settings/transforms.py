"""Data transformations for settings dictionaries."""

import os
from typing import Any


def convert_keys_to_lowercase(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively convert all dictionary keys to lowercase.

    Values are preserved as-is, including string values.
    """
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key.lower()] = convert_keys_to_lowercase(value)
        else:
            result[key.lower()] = value
    return result


def resolve_environment_variables(data: dict[str, Any]) -> dict[str, Any]:
    """Resolve environment variables ($HOME, $USER, etc.) in string values.

    Recursively processes nested dicts and lists.
    Non-string values pass through unchanged.
    """

    def _resolve(value: Any) -> Any:
        if isinstance(value, str):
            return os.path.expandvars(value)
        elif isinstance(value, dict):
            return {k: _resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_resolve(item) for item in value]
        return value

    return _resolve(data)
