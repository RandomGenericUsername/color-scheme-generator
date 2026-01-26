"""Enumerations for configuration."""

from enum import Enum


class Backend(str, Enum):
    """Available color extraction backends."""

    PYWAL = "pywal"
    WALLUST = "wallust"
    CUSTOM = "custom"


class ColorAlgorithm(str, Enum):
    """Custom backend color extraction algorithms."""

    KMEANS = "kmeans"
    DOMINANT = "dominant"


class ColorFormat(str, Enum):
    """Output format types."""

    JSON = "json"
    SH = "sh"
    CSS = "css"
    GTK_CSS = "gtk.css"
    YAML = "yaml"
    SEQUENCES = "sequences"
    RASI = "rasi"
    SCSS = "scss"
