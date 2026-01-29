"""Tests for container manager."""

from color_scheme.config.config import AppConfig, ContainerSettings
from color_scheme_orchestrator.container.manager import ContainerManager


class TestContainerManagerInit:
    """Tests for ContainerManager initialization."""

    def test_init_with_settings(self):
        """Test initialization with settings."""
        settings = AppConfig(container=ContainerSettings(engine="docker"))
        manager = ContainerManager(settings)

        assert manager.settings == settings
        assert manager.engine in ["docker", "podman"]

    def test_init_detects_docker_engine(self):
        """Test that it detects docker engine from settings."""
        settings = AppConfig(container=ContainerSettings(engine="docker"))
        manager = ContainerManager(settings)

        assert manager.engine == "docker"

    def test_init_detects_podman_engine(self):
        """Test that it detects podman engine from settings."""
        settings = AppConfig(container=ContainerSettings(engine="podman"))
        manager = ContainerManager(settings)

        assert manager.engine == "podman"
