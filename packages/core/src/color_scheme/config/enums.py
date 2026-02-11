"""Enumerations for configuration."""

from enum import StrEnum


class Backend(StrEnum):
    """Available color extraction backends."""

    PYWAL = "pywal"
    WALLUST = "wallust"
    CUSTOM = "custom"


class ColorAlgorithm(StrEnum):
    """Custom backend color extraction algorithms."""

    KMEANS = "kmeans"
    DOMINANT = "dominant"


class ColorFormat(StrEnum):
    """Output format types."""

    JSON = "json"
    SH = "sh"
    CSS = "css"
    GTK_CSS = "gtk.css"
    YAML = "yaml"
    SEQUENCES = "sequences"
    RASI = "rasi"
    SCSS = "scss"
