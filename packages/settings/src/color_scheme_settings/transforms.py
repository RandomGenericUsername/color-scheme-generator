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


def parse_env_vars(environ: dict | None = None) -> dict[str, dict]:
    """Parse COLORSCHEME_* environment variables into a section-keyed dict.

    Pattern: COLORSCHEME_SECTION__KEY (double underscore separates section from key)
    Special case: COLOR_SCHEME_TEMPLATES=/path → {"templates": {"directory": "/path"}}

    Keys are normalised to lowercase.
    Unrecognised environment variables are ignored.

    Args:
        environ: Environment dict to parse. Defaults to os.environ if None.

    Returns:
        Dict mapping section name to {key: value} pairs.
        Example: {"output": {"directory": "/tmp"}, "generation": {"default_backend": "pywal"}}
    """
    if environ is None:
        environ = dict(os.environ)

    result: dict[str, dict] = {}
    prefix = "COLORSCHEME_"

    for key, value in environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):]
            parts = config_key.split("__", 1)
            if len(parts) == 2:
                section, field = parts[0].lower(), parts[1].lower()
                if section not in result:
                    result[section] = {}
                result[section][field] = value

    # Special case: COLOR_SCHEME_TEMPLATES
    if "COLOR_SCHEME_TEMPLATES" in environ:
        if "templates" not in result:
            result["templates"] = {}
        result["templates"]["directory"] = environ["COLOR_SCHEME_TEMPLATES"]

    return result
