"""Template resolution across layers."""

from pathlib import Path

from color_scheme_templates.errors import TemplateNotFoundError
from color_scheme_templates.loader import TemplateLayer


class TemplateResolver:
    """Resolves template names to filesystem paths using layer precedence."""

    def __init__(self, layers: list[TemplateLayer]) -> None:
        self._layers = layers
        self._lookup: dict[str, Path] = {}
        self._build_lookup()

    def _build_lookup(self) -> None:
        """Build lookup table. Higher priority layers overwrite lower."""
        for layer in self._layers:
            for template_name in layer.templates:
                self._lookup[template_name] = layer.templates_dir / template_name

    def resolve(self, template_name: str) -> Path:
        """Resolve a template name to its filesystem path."""
        if template_name in self._lookup:
            return self._lookup[template_name]
        searched = [layer.templates_dir for layer in self._layers]
        raise TemplateNotFoundError(template_name, searched_paths=searched)

    def list_all(self) -> dict[str, Path]:
        """List all available templates with their resolved paths."""
        return dict(self._lookup)

    @property
    def layers(self) -> list[TemplateLayer]:
        """Access the underlying layers."""
        return list(self._layers)
