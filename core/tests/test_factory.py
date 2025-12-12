"""Tests for ColorSchemeGeneratorFactory."""

from unittest.mock import patch

import pytest

from colorscheme_generator.backends import (
    CustomGenerator,
    PywalGenerator,
    WallustGenerator,
)
from colorscheme_generator.config.enums import Backend
from colorscheme_generator.core.exceptions import BackendNotAvailableError
from colorscheme_generator.factory import ColorSchemeGeneratorFactory


class TestFactoryCreate:
    """Test factory create method."""

    def test_create_pywal_backend(self, mock_app_config):
        """Test creating pywal backend."""
        generator = ColorSchemeGeneratorFactory.create(
            Backend.PYWAL, mock_app_config
        )
        assert isinstance(generator, PywalGenerator)
        assert generator.backend_name == "pywal"

    def test_create_wallust_backend(self, mock_app_config):
        """Test creating wallust backend."""
        generator = ColorSchemeGeneratorFactory.create(
            Backend.WALLUST, mock_app_config
        )
        assert isinstance(generator, WallustGenerator)
        assert generator.backend_name == "wallust"

    def test_create_custom_backend(self, mock_app_config):
        """Test creating custom backend."""
        generator = ColorSchemeGeneratorFactory.create(
            Backend.CUSTOM, mock_app_config
        )
        assert isinstance(generator, CustomGenerator)
        assert generator.backend_name == "custom"

    def test_create_unknown_backend(self, mock_app_config):
        """Test creating unknown backend raises error."""
        with pytest.raises(ValueError) as exc_info:
            ColorSchemeGeneratorFactory.create("unknown", mock_app_config)

        assert "Unknown backend" in str(exc_info.value)


class TestFactoryCreateAuto:
    """Test factory create_auto method."""

    def test_create_auto_prefers_wallust(self, mock_app_config):
        """Test auto-detection prefers wallust when available."""
        with (
            patch.object(WallustGenerator, "is_available", return_value=True),
            patch.object(PywalGenerator, "is_available", return_value=True),
            patch.object(CustomGenerator, "is_available", return_value=True),
        ):

            generator = ColorSchemeGeneratorFactory.create_auto(
                mock_app_config
            )
            assert isinstance(generator, WallustGenerator)

    def test_create_auto_falls_back_to_pywal(self, mock_app_config):
        """Test auto-detection falls back to pywal."""
        with (
            patch.object(WallustGenerator, "is_available", return_value=False),
            patch.object(PywalGenerator, "is_available", return_value=True),
            patch.object(CustomGenerator, "is_available", return_value=True),
        ):

            generator = ColorSchemeGeneratorFactory.create_auto(
                mock_app_config
            )
            assert isinstance(generator, PywalGenerator)

    def test_create_auto_falls_back_to_custom(self, mock_app_config):
        """Test auto-detection falls back to custom."""
        with (
            patch.object(WallustGenerator, "is_available", return_value=False),
            patch.object(PywalGenerator, "is_available", return_value=False),
            patch.object(CustomGenerator, "is_available", return_value=True),
        ):

            generator = ColorSchemeGeneratorFactory.create_auto(
                mock_app_config
            )
            assert isinstance(generator, CustomGenerator)

    def test_create_auto_no_backends_available(self, mock_app_config):
        """Test auto-detection when no backends available."""
        with (
            patch.object(WallustGenerator, "is_available", return_value=False),
            patch.object(PywalGenerator, "is_available", return_value=False),
            patch.object(CustomGenerator, "is_available", return_value=False),
        ):

            with pytest.raises(BackendNotAvailableError) as exc_info:
                ColorSchemeGeneratorFactory.create_auto(mock_app_config)

            assert "No backends available" in str(exc_info.value)


class TestFactoryListAvailable:
    """Test factory list_available method."""

    def test_list_available_all_backends(self, mock_app_config):
        """Test listing all available backends."""
        with (
            patch.object(WallustGenerator, "is_available", return_value=True),
            patch.object(PywalGenerator, "is_available", return_value=True),
            patch.object(CustomGenerator, "is_available", return_value=True),
        ):

            available = ColorSchemeGeneratorFactory.list_available(
                mock_app_config
            )
            assert "pywal" in available
            assert "wallust" in available
            assert "custom" in available
            assert len(available) == 3

    def test_list_available_only_custom(self, mock_app_config):
        """Test listing when only custom is available."""
        with (
            patch.object(WallustGenerator, "is_available", return_value=False),
            patch.object(PywalGenerator, "is_available", return_value=False),
            patch.object(CustomGenerator, "is_available", return_value=True),
        ):

            available = ColorSchemeGeneratorFactory.list_available(
                mock_app_config
            )
            assert available == ["custom"]

    def test_list_available_pywal_and_custom(self, mock_app_config):
        """Test listing when pywal and custom are available."""
        with (
            patch.object(WallustGenerator, "is_available", return_value=False),
            patch.object(PywalGenerator, "is_available", return_value=True),
            patch.object(CustomGenerator, "is_available", return_value=True),
        ):

            available = ColorSchemeGeneratorFactory.list_available(
                mock_app_config
            )
            assert "pywal" in available
            assert "custom" in available
            assert "wallust" not in available
            assert len(available) == 2
