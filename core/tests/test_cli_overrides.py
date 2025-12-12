"""Tests for CLI settings overrides."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from colorscheme_generator.cli_overrides import SettingsOverrider
from colorscheme_generator.config.config import AppConfig
from colorscheme_generator.config.settings import Settings


class TestSettingsOverrider:
    """Test SettingsOverrider class."""

    def test_apply_overrides_saturation(self, mock_app_config):
        """Test overriding saturation adjustment."""
        overrides = {"generation.saturation_adjustment": 1.5}
        result = SettingsOverrider.apply_overrides(mock_app_config, overrides)

        assert result.generation.saturation_adjustment == 1.5

    def test_apply_overrides_pywal_algorithm(self, mock_app_config):
        """Test overriding pywal algorithm."""
        overrides = {"backends.pywal.backend_algorithm": "colorz"}
        result = SettingsOverrider.apply_overrides(mock_app_config, overrides)

        assert result.backends.pywal.backend_algorithm == "colorz"

    def test_apply_overrides_wallust_backend(self, mock_app_config):
        """Test overriding wallust backend type."""
        overrides = {"backends.wallust.backend_type": "full"}
        result = SettingsOverrider.apply_overrides(mock_app_config, overrides)

        assert result.backends.wallust.backend_type == "full"

    def test_apply_overrides_custom_backend(self, mock_app_config):
        """Test overriding custom backend settings."""
        overrides = {
            "backends.custom.algorithm": "median_cut",
            "backends.custom.n_clusters": 24,
        }
        result = SettingsOverrider.apply_overrides(mock_app_config, overrides)

        assert result.backends.custom.algorithm == "median_cut"
        assert result.backends.custom.n_clusters == 24

    def test_apply_overrides_template_dir(self, mock_app_config, tmp_path):
        """Test overriding template directory."""
        template_dir = tmp_path / "templates"
        overrides = {"templates.directory": template_dir}
        result = SettingsOverrider.apply_overrides(mock_app_config, overrides)

        assert result.templates.directory == template_dir

    def test_apply_overrides_multiple(self, mock_app_config):
        """Test applying multiple overrides."""
        overrides = {
            "generation.saturation_adjustment": 0.5,
            "backends.pywal.backend_algorithm": "haishoku",
        }
        result = SettingsOverrider.apply_overrides(mock_app_config, overrides)

        assert result.generation.saturation_adjustment == 0.5
        assert result.backends.pywal.backend_algorithm == "haishoku"

    def test_apply_overrides_invalid_value(self, mock_app_config):
        """Test that invalid values raise validation error."""
        overrides = {"generation.saturation_adjustment": 5.0}  # Max is 2.0

        with pytest.raises(ValidationError):
            SettingsOverrider.apply_overrides(mock_app_config, overrides)

    def test_apply_overrides_invalid_choice(self, mock_app_config):
        """Test that invalid choices raise validation error."""
        overrides = {"backends.pywal.backend_algorithm": "invalid"}

        with pytest.raises(ValidationError):
            SettingsOverrider.apply_overrides(mock_app_config, overrides)
