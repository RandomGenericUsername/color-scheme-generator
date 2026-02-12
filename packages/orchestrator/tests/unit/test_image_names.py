"""Tests for container image name resolution."""

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend

from color_scheme_orchestrator.config.settings import ContainerSettings
from color_scheme_orchestrator.config.unified import UnifiedConfig
from color_scheme_orchestrator.container.manager import ContainerManager


class TestImageNameResolution:
    """Tests for resolving backend enum to image name."""

    def test_pywal_backend_image_name(self):
        """Test pywal backend resolves to correct image."""
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="docker"),
        )
        manager = ContainerManager(config)

        image = manager.get_image_name(Backend.PYWAL)

        assert image == "color-scheme-pywal:latest"

    def test_wallust_backend_image_name(self):
        """Test wallust backend resolves to correct image."""
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="docker"),
        )
        manager = ContainerManager(config)

        image = manager.get_image_name(Backend.WALLUST)

        assert image == "color-scheme-wallust:latest"

    def test_custom_backend_image_name(self):
        """Test custom backend resolves to correct image."""
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="docker"),
        )
        manager = ContainerManager(config)

        image = manager.get_image_name(Backend.CUSTOM)

        assert image == "color-scheme-custom:latest"

    def test_image_name_with_registry(self):
        """Test image name includes registry if configured."""
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(
                engine="docker", image_registry="ghcr.io/myorg"
            ),
        )
        manager = ContainerManager(config)

        image = manager.get_image_name(Backend.PYWAL)

        assert image == "ghcr.io/myorg/color-scheme-pywal:latest"
