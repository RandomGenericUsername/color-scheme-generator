"""Shared test fixtures and utilities for orchestrator tests."""

import subprocess
from pathlib import Path

import pytest


def check_docker_available():
    """Check if docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError):
        return False


def check_podman_available():
    """Check if podman is available and running."""
    try:
        result = subprocess.run(
            ["podman", "ps"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError):
        return False


@pytest.fixture(scope="session")
def docker_available():
    """Check if docker is available for integration tests."""
    return check_docker_available()


@pytest.fixture(scope="session")
def podman_available():
    """Check if podman is available for integration tests."""
    return check_podman_available()


@pytest.fixture(scope="session")
def any_container_engine():
    """Check if any container engine is available."""
    return check_docker_available() or check_podman_available()


@pytest.fixture
def project_root():
    """Get project root directory."""
    # From tests/conftest.py, navigate to project root
    return Path(__file__).parent.parent.parent.parent


@pytest.fixture
def docker_dir(project_root):
    """Get docker directory."""
    return project_root / "packages" / "orchestrator" / "docker"
