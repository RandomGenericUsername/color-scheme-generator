"""Deep merge algorithm for layered settings."""

from typing import Any

from color_scheme_settings.loader import LayerSource


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base. Returns a new dict.

    Rules:
    - Dicts: recurse into matching keys, base keys preserved if not overridden
    - Lists: replaced entirely (atomic)
    - Scalars: replaced entirely
    - Keys in override not in base: added
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def merge_layers(layers: list[LayerSource]) -> dict[str, dict[str, Any]]:
    """Merge all layers into one dict per namespace.

    Layers must arrive in priority order (lowest priority first).

    Returns:
        Dict mapping namespace to merged settings dict.
        Example: {"core": {...merged...}, "orchestrator": {...merged...}}
    """
    merged: dict[str, dict[str, Any]] = {}
    for layer in layers:
        ns = layer.namespace
        if ns not in merged:
            merged[ns] = {}
        merged[ns] = deep_merge(merged[ns], layer.data)
    return merged
