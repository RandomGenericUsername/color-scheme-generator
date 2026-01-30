"""Project-level UnifiedConfig composing core + orchestrator schemas."""

from pydantic import BaseModel, ConfigDict, Field

from color_scheme.config.config import AppConfig
from color_scheme_orchestrator.config.settings import ContainerSettings


class UnifiedConfig(BaseModel):
    """Root configuration composing all registered namespaces.

    Access pattern:
        config.core.logging.level
        config.core.output.directory
        config.core.generation.default_backend
        config.core.backends.pywal.backend_algorithm
        config.core.templates.directory
        config.orchestrator.engine
        config.orchestrator.image_registry
    """

    model_config = ConfigDict(frozen=True)

    core: AppConfig = Field(default_factory=AppConfig)
    orchestrator: ContainerSettings = Field(default_factory=ContainerSettings)
