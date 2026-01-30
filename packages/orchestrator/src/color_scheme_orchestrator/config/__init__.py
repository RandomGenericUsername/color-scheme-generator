"""Configuration for orchestrator package."""

from pathlib import Path

from color_scheme_settings import SchemaRegistry

from color_scheme_orchestrator.config.settings import ContainerSettings

SchemaRegistry.register(
    namespace="orchestrator",
    model=ContainerSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = ["ContainerSettings"]
