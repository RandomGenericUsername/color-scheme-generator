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
# Priority:
# 1. Environment variable COLOR_SCHEME_TEMPLATES
# 2. /templates (for containers)
# 3. Project root templates/ directory
_container_templates = Path("/templates")
_package_root = Path(__file__).parent.parent  # color_scheme/
_project_root = _package_root.parent.parent.parent.parent  # Go up to project root
_project_templates = _project_root / "templates"

if (env_templates := os.getenv("COLOR_SCHEME_TEMPLATES")) is not None:
    template_directory = Path(env_templates)
elif _container_templates.exists():
    # Running in container
    template_directory = _container_templates
else:
    # Running on host
    template_directory = _project_templates
