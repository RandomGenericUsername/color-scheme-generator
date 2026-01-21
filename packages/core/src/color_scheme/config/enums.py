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
