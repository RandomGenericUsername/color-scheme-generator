"""Color extraction backends."""

from color_scheme.backends.custom import CustomGenerator
from color_scheme.backends.pywal import PywalGenerator
from color_scheme.backends.wallust import WallustGenerator

__all__ = ["CustomGenerator", "PywalGenerator", "WallustGenerator"]
