"""Schema registration system for namespace-based configuration."""

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from color_scheme_settings.errors import SettingsRegistryError


@dataclass
class SchemaEntry:
    """A registered configuration schema."""

    namespace: str
    model: type[BaseModel]
    defaults_file: Path


class SchemaRegistry:
    """Registry for configuration schemas.

    Each package registers its namespace, Pydantic model, and defaults file.
    The registry has zero knowledge of specific schemas.
    """

    _entries: dict[str, SchemaEntry] = {}

    @classmethod
    def register(
        cls,
        namespace: str,
        model: type[BaseModel],
        defaults_file: Path,
    ) -> None:
        """Register a package's config schema.

        Args:
            namespace: Unique namespace identifier (e.g., "core", "orchestrator")
            model: Pydantic model class for validation
            defaults_file: Path to the package's settings.toml

        Raises:
            SettingsRegistryError: If namespace is already registered
        """
        if namespace in cls._entries:
            raise SettingsRegistryError(
                namespace=namespace,
                reason="namespace already registered",
            )
        cls._entries[namespace] = SchemaEntry(
            namespace=namespace,
            model=model,
            defaults_file=defaults_file,
        )

    @classmethod
    def get(cls, namespace: str) -> SchemaEntry:
        """Retrieve a registered schema by namespace.

        Raises:
            SettingsRegistryError: If namespace is not registered
        """
        if namespace not in cls._entries:
            raise SettingsRegistryError(
                namespace=namespace,
                reason="namespace not registered",
            )
        return cls._entries[namespace]

    @classmethod
    def all_entries(cls) -> list[SchemaEntry]:
        """Return all registered entries."""
        return list(cls._entries.values())

    @classmethod
    def all_namespaces(cls) -> list[str]:
        """Return all registered namespace names."""
        return list(cls._entries.keys())

    @classmethod
    def clear(cls) -> None:
        """Remove all registered schemas. Used for testing."""
        cls._entries.clear()
