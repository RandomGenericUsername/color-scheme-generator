"""Default configuration values for colorscheme generator."""

from pathlib import Path

# Output defaults (OutputManager)
output_directory = Path.home() / ".config/color-scheme/output"
default_formats = ["json", "sh", "css", "gtk.css", "scss", "yaml", "rasi"]

# Generation defaults
default_backend = "pywal"

saturation_adjustment = 1.0

# Pywal backend defaults (color extraction)
# Pywal is always used via CLI (library mode has API issues)
# Using haishoku as default because wal backend has imagemagick policy issues
pywal_backend_algorithm = "haishoku"  # Default pywal algorithm

# Wallust backend defaults (color extraction)
wallust_backend_type = "resized"

# Custom backend defaults
custom_algorithm = "kmeans"
custom_n_clusters = 16

# Template defaults (OutputManager)
template_directory = Path("templates")
