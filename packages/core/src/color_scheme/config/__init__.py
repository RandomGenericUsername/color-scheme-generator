"""Configuration system for color-scheme core."""

from pathlib import Path

from color_scheme_settings import SchemaRegistry

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend, ColorAlgorithm

SchemaRegistry.register(
    namespace="core",
    model=AppConfig,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = ["AppConfig", "Backend", "ColorAlgorithm"]
