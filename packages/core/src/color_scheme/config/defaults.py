"""Default configuration values."""

import os
from pathlib import Path

# Logging defaults
default_log_level = "INFO"
default_show_time = True
default_show_path = False

# Output defaults
output_directory = Path.home() / ".config" / "color-scheme" / "output"
default_formats = [
    "json",
    "sh",
    "css",
    "gtk.css",
    "yaml",
    "sequences",
    "rasi",
    "scss",
]

# Generation defaults
default_backend = "pywal"
saturation_adjustment = 1.0

# Backend-specific defaults
pywal_backend_algorithm = "haishoku"
wallust_backend_type = "resized"
custom_algorithm = "kmeans"
custom_n_clusters = 16

# Template defaults
# Default to package templates directory, but allow override via env var
_package_templates = Path(__file__).parent.parent / "templates"
template_directory = Path(
    os.getenv(
        "COLOR_SCHEME_TEMPLATES",
        str(_package_templates)
    )
)
