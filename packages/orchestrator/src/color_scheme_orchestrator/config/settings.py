"""Orchestrator-specific configuration settings."""

from pydantic import BaseModel, Field, field_validator

from color_scheme.config.config import (
    AppConfig,
    GenerationSettings,
    LoggingSettings,
    OutputSettings,
    TemplateSettings,
)


class ContainerSettings(BaseModel):
    """Container engine configuration.

    Configures which container engine (Docker or Podman) to use for
    running containerized backends.
    """

    engine: str = Field(
        default="docker",
        description="Container engine to use (docker or podman)",
    )
    image_registry: str | None = Field(
        default=None,
        description="Registry prefix for container images",
    )

    @field_validator("engine", mode="before")
    @classmethod
    def validate_engine(cls, v: str) -> str:
        """Validate container engine is valid."""
        valid_engines = {"docker", "podman"}
        v_lower = v.lower()
        if v_lower not in valid_engines:
            raise ValueError(
                f"Invalid container engine: {v}. "
                f"Must be one of: {', '.join(sorted(valid_engines))}"
            )
        return v_lower

    @field_validator("image_registry", mode="before")
    @classmethod
    def normalize_registry(cls, v: str | None) -> str | None:
        """Normalize registry by removing trailing slashes."""
        if v:
            return v.rstrip("/")
        return v


class OrchestratorConfig(AppConfig):
    """Orchestrator configuration extending core AppConfig.

    Includes all core settings plus container orchestration configuration.
    """

    container: ContainerSettings = Field(
        default_factory=ContainerSettings,
        description="Container engine configuration",
    )


# Alias for backwards compatibility
OrchestratorSettings = OrchestratorConfig
