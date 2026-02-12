"""Tests for container manager."""

from color_scheme.config.config import AppConfig

from color_scheme_orchestrator.config.settings import ContainerSettings
from color_scheme_orchestrator.config.unified import UnifiedConfig
from color_scheme_orchestrator.container.manager import ContainerManager


class TestContainerManagerInit:
    """Tests for ContainerManager initialization."""

    def test_init_with_settings(self):
        """Test initialization with settings."""
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="docker"),
        )
        manager = ContainerManager(config)

        assert manager.config == config
        assert manager.engine in ["docker", "podman"]

    def test_init_detects_docker_engine(self):
        """Test that it detects docker engine from settings."""
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="docker"),
        )
        manager = ContainerManager(config)

        assert manager.engine == "docker"

    def test_init_detects_podman_engine(self):
        """Test that it detects podman engine from settings."""
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="podman"),
        )
        manager = ContainerManager(config)

        assert manager.engine == "podman"
