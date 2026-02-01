"""CLI override application for validated config objects."""

from typing import Any

from pydantic import BaseModel

from color_scheme_settings.errors import SettingsOverrideError


def apply_overrides(
    config: BaseModel,
    overrides: dict[str, Any],
) -> BaseModel:
    """Apply CLI argument overrides to a validated config.

    Keys use dot notation with namespace prefix:
        "core.generation.saturation_adjustment" -> 1.5
        "core.output.directory" -> Path("/tmp/out")
        "orchestrator.engine" -> "podman"

    Args:
        config: Validated config object (must have model_dump and model_validate)
        overrides: Dict of dotted key paths to override values

    Returns:
        New config instance with overrides applied and re-validated.

    Raises:
        SettingsOverrideError: If a key path doesn't exist in the config.
    """
    if not overrides:
        return config

    config_dict = config.model_dump()

    for dotted_key, value in overrides.items():
        parts = dotted_key.split(".")
        target = config_dict

        # Walk to the parent of the leaf key
        for segment in parts[:-1]:
            if not isinstance(target, dict) or segment not in target:
                raise SettingsOverrideError(key=dotted_key)
            target = target[segment]

        # Set the leaf value
        leaf = parts[-1]
        if not isinstance(target, dict) or leaf not in target:
            raise SettingsOverrideError(key=dotted_key)
        target[leaf] = value

    # Re-validate through Pydantic
    return config.__class__.model_validate(config_dict)
