"""UnifiedConfig construction from merged layers."""

from typing import Any

from pydantic import BaseModel

from color_scheme_settings.errors import SettingsValidationError
from color_scheme_settings.registry import SchemaRegistry
from color_scheme_settings.transforms import (
    convert_keys_to_lowercase,
    resolve_environment_variables,
)


def build_validated_namespace(
    namespace: str,
    model: type[BaseModel],
    data: dict[str, Any],
) -> BaseModel:
    """Validate a single namespace's merged data through its Pydantic model.

    Args:
        namespace: The namespace identifier
        model: Pydantic model class
        data: Merged settings data

    Returns:
        Validated Pydantic model instance

    Raises:
        SettingsValidationError: If validation fails
    """
    try:
        transformed = resolve_environment_variables(data)
        transformed = convert_keys_to_lowercase(transformed)
        return model(**transformed)
    except Exception as e:
        raise SettingsValidationError(
            namespace=namespace,
            validation_error=e,
        ) from e


def build_unified_config(
    unified_model: type[BaseModel],
    merged: dict[str, dict[str, Any]],
) -> BaseModel:
    """Build a UnifiedConfig from merged layer data.

    Args:
        unified_model: The UnifiedConfig Pydantic model class
        merged: Dict mapping namespace to merged settings dict

    Returns:
        Validated UnifiedConfig instance
    """
    validated: dict[str, BaseModel] = {}
    for entry in SchemaRegistry.all_entries():
        ns_data = merged.get(entry.namespace, {})
        validated[entry.namespace] = build_validated_namespace(
            entry.namespace, entry.model, ns_data
        )
    return unified_model(**validated)
