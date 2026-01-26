"""Tests for backend factory."""

from unittest.mock import patch

import pytest

from color_scheme.backends.custom import CustomGenerator
from color_scheme.backends.pywal import PywalGenerator
from color_scheme.backends.wallust import WallustGenerator
from color_scheme.config.enums import Backend
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import BackendNotAvailableError
from color_scheme.factory import BackendFactory


class TestBackendFactory:
    """Tests for BackendFactory."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def factory(self, settings):
        """Create BackendFactory."""
        return BackendFactory(settings)

    def test_create_custom_backend(self, factory):
        """Test creating custom backend."""
        generator = factory.create(Backend.CUSTOM)
        assert isinstance(generator, CustomGenerator)
        assert generator.backend_name == "custom"

    @patch("shutil.which")
    def test_create_pywal_backend(self, mock_which, factory):
        """Test creating pywal backend."""
        mock_which.return_value = "/usr/bin/wal"

        generator = factory.create(Backend.PYWAL)
        assert isinstance(generator, PywalGenerator)
        assert generator.backend_name == "pywal"

    @patch("shutil.which")
    def test_create_wallust_backend(self, mock_which, factory):
        """Test creating wallust backend."""
        mock_which.return_value = "/usr/bin/wallust"

        generator = factory.create(Backend.WALLUST)
        assert isinstance(generator, WallustGenerator)
        assert generator.backend_name == "wallust"

    @patch("shutil.which")
    def test_create_unavailable_backend_raises(self, mock_which, factory):
        """Test creating unavailable backend raises error."""
        mock_which.return_value = None

        with pytest.raises(BackendNotAvailableError):
            factory.create(Backend.PYWAL)

    @patch.object(PywalGenerator, "is_available", return_value=True)
    @patch.object(WallustGenerator, "is_available", return_value=False)
    def test_detect_available_backends(self, mock_wallust, mock_pywal, factory):
        """Test detecting available backends."""
        available = factory.detect_available()

        assert Backend.CUSTOM in available  # Always available
        assert Backend.PYWAL in available
        assert Backend.WALLUST not in available

    @patch.object(PywalGenerator, "is_available", return_value=True)
    @patch.object(WallustGenerator, "is_available", return_value=True)
    def test_auto_detect_all_available(self, mock_wallust, mock_pywal, factory):
        """Test auto-detect with all backends available."""
        # Prefer order: wallust > pywal > custom
        backend = factory.auto_detect()
        assert backend == Backend.WALLUST

    @patch.object(PywalGenerator, "is_available", return_value=True)
    @patch.object(WallustGenerator, "is_available", return_value=False)
    def test_auto_detect_pywal_only(self, mock_wallust, mock_pywal, factory):
        """Test auto-detect with pywal only."""
        backend = factory.auto_detect()
        assert backend == Backend.PYWAL

    @patch.object(PywalGenerator, "is_available", return_value=False)
    @patch.object(WallustGenerator, "is_available", return_value=False)
    def test_auto_detect_fallback_to_custom(self, mock_wallust, mock_pywal, factory):
        """Test auto-detect fallback to custom."""
        backend = factory.auto_detect()
        assert backend == Backend.CUSTOM

    @patch.object(CustomGenerator, "is_available", side_effect=Exception("Test error"))
    @patch.object(PywalGenerator, "is_available", side_effect=Exception("Test error"))
    @patch.object(WallustGenerator, "is_available", side_effect=Exception("Test error"))
    def test_detect_available_handles_exceptions(
        self, mock_wallust, mock_pywal, mock_custom, factory
    ):
        """Test that detect_available handles exceptions gracefully."""
        # Should return empty list when all backends throw exceptions
        available = factory.detect_available()
        assert available == []

    @patch.object(CustomGenerator, "is_available", side_effect=Exception("Test error"))
    @patch.object(PywalGenerator, "is_available", side_effect=Exception("Test error"))
    @patch.object(WallustGenerator, "is_available", side_effect=Exception("Test error"))
    def test_auto_detect_handles_exceptions(
        self, mock_wallust, mock_pywal, mock_custom, factory
    ):
        """Test that auto_detect handles exceptions and falls back to custom."""
        # Even if all backends throw exceptions during check, we fall back to custom
        backend = factory.auto_detect()
        assert backend == Backend.CUSTOM
