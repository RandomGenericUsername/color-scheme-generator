"""Layered template discovery system for color-scheme."""

from pathlib import Path
from typing import Any

from color_scheme_templates.errors import (
    TemplateError,
    TemplateNotFoundError,
    TemplateRegistryError,
)
from color_scheme_templates.loader import TemplateLoader
from color_scheme_templates.registry import TemplateRegistry
from color_scheme_templates.resolver import TemplateResolver

_resolver: TemplateResolver | None = None
_loader_kwargs: dict[str, Any] = {}


def configure(
    project_root: Path | None = None,
    user_templates_path: Path | None = None,
) -> None:
    """Configure the template system before first use."""
    global _loader_kwargs, _resolver
    _loader_kwargs = {}
    if project_root is not None:
        _loader_kwargs["project_root"] = project_root
    if user_templates_path is not None:
        _loader_kwargs["user_templates_path"] = user_templates_path
    _resolver = None


def load_templates() -> TemplateResolver:
    """Load all template layers and return the resolver."""
    global _resolver
    if _resolver is not None:
        return _resolver
    loader = TemplateLoader(**_loader_kwargs)
    layers = loader.discover_layers()
    _resolver = TemplateResolver(layers)
    return _resolver


def reload_templates() -> TemplateResolver:
    """Force reload of all template layers."""
    global _resolver
    _resolver = None
    return load_templates()


def get_template(name: str) -> Path:
    """Get the path to a template by name."""
    resolver = load_templates()
    return resolver.resolve(name)


def list_templates() -> dict[str, Path]:
    """List all available templates with their resolved paths."""
    resolver = load_templates()
    return resolver.list_all()


def reset() -> None:
    """Reset the template system. For testing only."""
    global _resolver, _loader_kwargs
    _resolver = None
    _loader_kwargs = {}
    TemplateRegistry.clear()


__all__ = [
    "TemplateRegistry",
    "configure",
    "load_templates",
    "reload_templates",
    "get_template",
    "list_templates",
    "reset",
    "TemplateError",
    "TemplateNotFoundError",
    "TemplateRegistryError",
]
