"""Pydantic configuration models for colorscheme generator.

This module defines the configuration structure that matches the
settings.toml file. It uses Pydantic for validation and type safety,
following the same pattern as the dotfiles installer.
"""

import logging
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from color_scheme.config.defaults import (
    custom_algorithm,
    custom_n_clusters,
    default_backend,
    default_formats,
    output_directory,
    pywal_backend_algorithm,
    saturation_adjustment,
    template_directory,
    wallust_backend_type,
)
from color_scheme.config.enums import Backend, ColorAlgorithm


class ContainerSettings(BaseModel):
    """Container engine configuration.

    Configures which container engine (Docker or Podman) to use for
    running containerized backends.
    """

    engine: str = Field(
        default="docker",
        description="Container engine to use (docker or podman)",
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


class LoggingSettings(BaseModel):
    """Logging configuration.

    Uses standard Python logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """

    level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    show_time: bool = Field(
        default=True,
        description="Show timestamps in log messages",
    )
    show_path: bool = Field(
        default=False,
        description="Show file path in log messages",
    )

    @field_validator("level", mode="before")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate logging level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid logging level: {v}. "
                f"Must be one of: {', '.join(sorted(valid_levels))}"
            )
        return v_upper

    def get_level_int(self) -> int:
        """Get logging level as integer.

        Returns:
            Python logging level constant
        """
        level_value: int = getattr(logging, self.level)
        return level_value


class OutputSettings(BaseModel):
    """Output configuration (controlled by OutputManager).

    These settings control where and how the OutputManager writes
    generated color scheme files. Backends don't use these settings.
    """

    directory: Path = Field(
        default=output_directory,
        description="Directory where OutputManager writes generated files",
    )
    formats: list[str] = Field(
        default_factory=lambda: default_formats.copy(),
        description="Output formats to generate",
    )


class GenerationSettings(BaseModel):
    """Color scheme generation defaults.

    These settings provide default values for color extraction
    that can be overridden at runtime via GeneratorConfig.
    """

    default_backend: str = Field(
        default=default_backend,
        description="Default backend for color extraction",
    )

    saturation_adjustment: float = Field(
        default=saturation_adjustment,
        ge=0.0,
        le=2.0,
        description="Default saturation adjustment factor",
    )

    @field_validator("default_backend", mode="before")
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate backend string."""
        try:
            Backend(v)
            return v
        except ValueError:
            valid = ", ".join([b.value for b in Backend])
            raise ValueError(
                f"Invalid backend '{v}'. Valid options: {valid}"
            ) from None


class PywalBackendSettings(BaseModel):
    """Pywal backend configuration (for color extraction only).

    Note: Pywal always writes to ~/.cache/wal/ internally (hardcoded).
    We read from there to extract colors, but OutputManager
    writes our own files to the configured output directory.
    Pywal is always used via CLI (library mode has API issues).
    """

    backend_algorithm: str = Field(
        default=pywal_backend_algorithm,
        description="Pywal color extraction algorithm",
    )

    @field_validator("backend_algorithm")
    @classmethod
    def validate_backend_algorithm(cls, v: str) -> str:
        """Validate backend algorithm is one of the supported options."""
        allowed = {"wal", "colorz", "colorthief", "haishoku", "schemer2"}
        if v not in allowed:
            raise ValueError(
                f"Invalid backend_algorithm: {v}. "
                f"Must be one of: {', '.join(sorted(allowed))}"
            )
        return v


class WallustBackendSettings(BaseModel):
    """Wallust backend configuration (for color extraction only).

    Note: We run wallust with JSON output to stdout and parse it (hardcoded).
    We don't use wallust's template system - OutputManager handles file
    generation.
    """

    backend_type: str = Field(
        default=wallust_backend_type,
        description="Wallust backend type (resized, full, etc.)",
    )


class CustomBackendSettings(BaseModel):
    """Custom Python backend configuration."""

    algorithm: str = Field(
        default=custom_algorithm, description="Color extraction algorithm"
    )
    n_clusters: int = Field(
        default=custom_n_clusters,
        ge=8,
        le=256,
        description="Number of color clusters for extraction",
    )

    @field_validator("algorithm", mode="before")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate algorithm string."""
        try:
            ColorAlgorithm(v)
            return v
        except ValueError:
            valid = ", ".join([a.value for a in ColorAlgorithm])
            raise ValueError(
                f"Invalid algorithm '{v}'. Valid options: {valid}"
            ) from None


class BackendSettings(BaseModel):
    """Backend-specific configurations (for color extraction only)."""

    pywal: PywalBackendSettings = Field(
        default_factory=PywalBackendSettings,
        description="Pywal backend settings",
    )
    wallust: WallustBackendSettings = Field(
        default_factory=WallustBackendSettings,
        description="Wallust backend settings",
    )
    custom: CustomBackendSettings = Field(
        default_factory=CustomBackendSettings,
        description="Custom backend settings",
    )


class TemplateSettings(BaseModel):
    """Template rendering configuration (for OutputManager)."""

    directory: Path = Field(
        default=template_directory,
        description="Directory containing Jinja2 templates",
    )


class AppConfig(BaseModel):
    """Application configuration matching dynaconf structure.

    This is the root configuration model that aggregates all settings
    from settings.toml. It follows the same pattern as the dotfiles
    installer's AppConfig.
    """

    container: ContainerSettings = Field(
        default_factory=ContainerSettings,
        description="Container engine configuration",
    )
    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Logging configuration",
    )
    output: OutputSettings = Field(
        default_factory=OutputSettings,
        description="Output configuration (OutputManager)",
    )
    generation: GenerationSettings = Field(
        default_factory=GenerationSettings,
        description="Generation defaults",
    )
    backends: BackendSettings = Field(
        default_factory=BackendSettings,
        description="Backend-specific settings (color extraction only)",
    )
    templates: TemplateSettings = Field(
        default_factory=TemplateSettings,
        description="Template configuration (OutputManager)",
    )
