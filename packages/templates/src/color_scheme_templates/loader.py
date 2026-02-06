"""Template layer discovery and loading."""

from dataclasses import dataclass, field
from pathlib import Path

from color_scheme_settings.paths import (
    CONTAINER_TEMPLATES_DIR,
    USER_TEMPLATES_DIR,
    get_env_templates_override,
    get_project_templates_dir,
    is_container_environment,
)

from color_scheme_templates.registry import TemplateRegistry


@dataclass
class TemplateLayer:
    """A single template layer discovered from the filesystem."""

    layer: str
    namespace: str
    templates_dir: Path
    templates: list[str] = field(default_factory=list)


def discover_templates_in_dir(directory: Path) -> list[str]:
    """Discover all template files (.j2) in a directory."""
    if not directory.exists() or not directory.is_dir():
        return []
    return sorted(
        p.name for p in directory.iterdir() if p.is_file() and p.suffix == ".j2"
    )


class TemplateLoader:
    """Discovers template directories from all layers."""

    def __init__(
        self,
        project_root: Path | None = None,
        user_templates_path: Path | None = None,
    ) -> None:
        self.project_root = project_root
        self.user_templates_path = user_templates_path or USER_TEMPLATES_DIR

    def discover_layers(self) -> list[TemplateLayer]:
        """Discover all template directories across all layers.

        Returns layers in priority order (lowest first).
        """
        layers: list[TemplateLayer] = []

        # Check for environment variable override
        env_override = get_env_templates_override()
        if env_override is not None:
            templates = discover_templates_in_dir(env_override)
            return [
                TemplateLayer(
                    layer="env",
                    namespace="override",
                    templates_dir=env_override,
                    templates=templates,
                )
            ]

        # Layer 1: Package defaults (or container)
        if is_container_environment():
            templates = discover_templates_in_dir(CONTAINER_TEMPLATES_DIR)
            layers.append(
                TemplateLayer(
                    layer="container",
                    namespace="core",
                    templates_dir=CONTAINER_TEMPLATES_DIR,
                    templates=templates,
                )
            )
        else:
            for entry in TemplateRegistry.all_entries():
                if entry.templates_dir.exists():
                    templates = discover_templates_in_dir(entry.templates_dir)
                    layers.append(
                        TemplateLayer(
                            layer="package",
                            namespace=entry.namespace,
                            templates_dir=entry.templates_dir,
                            templates=templates,
                        )
                    )

        # Layer 2: Project templates
        if self.project_root is not None:
            project_templates = get_project_templates_dir(self.project_root)
            if project_templates.exists():
                templates = discover_templates_in_dir(project_templates)
                layers.append(
                    TemplateLayer(
                        layer="project",
                        namespace="project",
                        templates_dir=project_templates,
                        templates=templates,
                    )
                )

        # Layer 3: User templates
        if self.user_templates_path.exists():
            templates = discover_templates_in_dir(self.user_templates_path)
            layers.append(
                TemplateLayer(
                    layer="user",
                    namespace="user",
                    templates_dir=self.user_templates_path,
                    templates=templates,
                )
            )

        return layers
