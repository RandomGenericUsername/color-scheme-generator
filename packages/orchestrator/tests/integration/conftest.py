"""Docker integration test fixtures."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def docker_available():
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


@pytest.fixture(scope="session")
def skip_if_no_docker(docker_available):
    """Skip test if docker is not available."""
    if not docker_available:
        pytest.skip("Docker not available")


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory."""
    # From tests/integration/conftest.py, navigate to project root
    return Path(__file__).parent.parent.parent.parent
