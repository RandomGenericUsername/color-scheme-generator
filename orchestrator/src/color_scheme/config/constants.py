"""Pinned versions and constants for container images and tools."""

# Base images with pinned versions for reproducibility
BASE_IMAGES = {
    "python": "python:3.12-slim-bookworm",
    "alpine": "alpine:3.20",
}

# Backend versions
BACKEND_VERSIONS = {
    "pywal": {
        "version": "3.3.0",
        "base_image": BASE_IMAGES["python"],
        "dependencies": [
            "pillow>=10.0.0",
            "haishoku>=0.2.5",
            "configparser>=5.0.0",
        ],
    },
    "wallust": {
        "version": "2.6.0",
        "base_image": BASE_IMAGES["alpine"],
        "dependencies": [],  # Pre-compiled binary
    },
}

# Environment defaults
DEFAULT_BACKENDS = ["pywal", "wallust"]
DEFAULT_OUTPUT_DIR = "/tmp/color-schemes"
DEFAULT_CONFIG_DIR = "~/.config/color-scheme"

# Container settings
CONTAINER_TIMEOUT = 300  # 5 minutes
CONTAINER_MEMORY_LIMIT = "512m"
CONTAINER_CPUSET_CPUS = None  # No limit by default

# Volume mount points
VOLUME_PATHS = {
    "output": "/tmp/color-schemes",
    "cache": "/root/.cache",
    "config": "/root/.config",
}

# Docker/Podman configuration
RUNTIME_DETECTION_ORDER = ["docker", "podman"]
RUNTIME_DEFAULTS = {
    "docker": {"command": "docker"},
    "podman": {"command": "podman"},
}
