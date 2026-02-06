"""Exception classes for the templates package."""

from pathlib import Path


class TemplateError(Exception):
    """Base exception for all template-related errors."""

    pass


class TemplateNotFoundError(TemplateError):
    """Raised when a requested template cannot be found in any layer."""

    def __init__(
        self,
        template_name: str,
        searched_paths: list[Path] | None = None,
    ) -> None:
        self.template_name = template_name
        self.searched_paths = searched_paths or []
        paths_str = ", ".join(str(p) for p in self.searched_paths)
        super().__init__(f"Template '{template_name}' not found. Searched: {paths_str}")


class TemplateRegistryError(TemplateError):
    """Raised when there's an issue with template registration."""

    def __init__(self, namespace: str, reason: str) -> None:
        self.namespace = namespace
        self.reason = reason
        msg = f"Template registry error for '{namespace}': {reason}"
        super().__init__(msg)
