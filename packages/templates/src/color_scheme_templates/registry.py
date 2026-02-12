"""Template registration system for namespace-based template discovery."""

from dataclasses import dataclass
from pathlib import Path

from color_scheme_templates.errors import TemplateRegistryError


@dataclass(frozen=True)
class TemplateEntry:
    """A registered template directory for a namespace."""

    namespace: str
    templates_dir: Path


class TemplateRegistry:
    """Registry for template directories."""

    _entries: dict[str, TemplateEntry] = {}

    @classmethod
    def register(cls, namespace: str, templates_dir: Path) -> None:
        """Register a package's template directory."""
        if namespace in cls._entries:
            raise TemplateRegistryError(
                namespace=namespace,
                reason="namespace already registered",
            )
        cls._entries[namespace] = TemplateEntry(
            namespace=namespace,
            templates_dir=templates_dir,
        )

    @classmethod
    def get(cls, namespace: str) -> TemplateEntry:
        """Retrieve a registered entry by namespace."""
        if namespace not in cls._entries:
            raise TemplateRegistryError(
                namespace=namespace,
                reason="namespace not registered",
            )
        return cls._entries[namespace]

    @classmethod
    def all_entries(cls) -> list[TemplateEntry]:
        """Return all registered entries."""
        return list(cls._entries.values())

    @classmethod
    def all_namespaces(cls) -> list[str]:
        """Return all registered namespace names."""
        return list(cls._entries.keys())

    @classmethod
    def clear(cls) -> None:
        """Remove all registered entries. Used for testing."""
        cls._entries.clear()
