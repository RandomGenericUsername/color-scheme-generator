"""Tests for orchestrator settings validation."""

import pytest
from pydantic import ValidationError

from color_scheme_orchestrator.config.settings import ContainerSettings


class TestEngineValidation:
    """Tests for engine validation (settings.py line 29)."""

    def test_invalid_engine_raises_error(self):
        """Verify invalid engine raises ValidationError (line 29)."""
        with pytest.raises(ValidationError) as exc_info:
            ContainerSettings(engine="invalid_engine")

        assert "Invalid container engine" in str(exc_info.value)

    def test_valid_engines_accepted(self):
        """Verify docker and podman are valid."""
        settings_docker = ContainerSettings(engine="docker")
        assert settings_docker.engine == "docker"

        settings_podman = ContainerSettings(engine="podman")
        assert settings_podman.engine == "podman"

    def test_engine_case_insensitive(self):
        """Verify engines are converted to lowercase."""
        settings = ContainerSettings(engine="DOCKER")
        assert settings.engine == "docker"

        settings = ContainerSettings(engine="Podman")
        assert settings.engine == "podman"


class TestRegistryNormalization:
    """Tests for registry normalization (settings.py line 41)."""

    def test_registry_trailing_slash_removed(self):
        """Verify trailing slashes are stripped (line 41)."""
        settings = ContainerSettings(image_registry="docker.io/")
        assert settings.image_registry == "docker.io"

    def test_registry_multiple_trailing_slashes(self):
        """Verify multiple trailing slashes are stripped."""
        settings = ContainerSettings(image_registry="registry.com///")
        assert settings.image_registry == "registry.com"

    def test_registry_none_remains_none(self):
        """Verify None registry remains None."""
        settings = ContainerSettings(image_registry=None)
        assert settings.image_registry is None

    def test_registry_without_trailing_slash(self):
        """Verify registry without slash is unchanged."""
        settings = ContainerSettings(image_registry="docker.io")
        assert settings.image_registry == "docker.io"
