"""Tests for configuration system."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from color_scheme.config.config import (
    AppConfig,
    BackendSettings,
    CustomBackendSettings,
    GenerationSettings,
    LoggingSettings,
    OutputSettings,
    PywalBackendSettings,
)
from color_scheme.config.enums import Backend, ColorAlgorithm
from color_scheme.config.settings import Settings, SettingsModel


class TestEnums:
    """Test configuration enums."""

    def test_backend_enum_values(self):
        """Test Backend enum has correct values."""
        assert Backend.PYWAL.value == "pywal"
        assert Backend.WALLUST.value == "wallust"
        assert Backend.CUSTOM.value == "custom"

    def test_color_algorithm_enum_values(self):
        """Test ColorAlgorithm enum has correct values."""
        assert ColorAlgorithm.KMEANS.value == "kmeans"
        assert ColorAlgorithm.DOMINANT.value == "dominant"


class TestLoggingSettings:
    """Test LoggingSettings model."""

    def test_default_values(self):
        """Test default logging settings."""
        settings = LoggingSettings()
        assert settings.level == "INFO"
        assert settings.show_time is True
        assert settings.show_path is False

    def test_valid_log_level(self):
        """Test valid log levels are accepted."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = LoggingSettings(level=level)
            assert settings.level == level

    def test_invalid_log_level(self):
        """Test invalid log level raises error."""
        with pytest.raises(ValidationError):
            LoggingSettings(level="INVALID")

    def test_case_insensitive_log_level(self):
        """Test log level is case-insensitive."""
        settings = LoggingSettings(level="debug")
        assert settings.level == "DEBUG"

    def test_get_level_int(self):
        """Test getting log level as integer."""
        import logging

        settings = LoggingSettings(level="DEBUG")
        assert settings.get_level_int() == logging.DEBUG


class TestOutputSettings:
    """Test OutputSettings model."""

    def test_default_values(self):
        """Test default output settings."""
        settings = OutputSettings()
        assert isinstance(settings.directory, Path)
        assert "json" in settings.formats
        assert "css" in settings.formats


class TestGenerationSettings:
    """Test GenerationSettings model."""

    def test_default_values(self):
        """Test default generation settings."""
        settings = GenerationSettings()
        assert settings.default_backend == "pywal"
        assert settings.saturation_adjustment == 1.0

    def test_valid_backend(self):
        """Test valid backend values."""
        for backend in ["pywal", "wallust", "custom"]:
            settings = GenerationSettings(default_backend=backend)
            assert settings.default_backend == backend

    def test_invalid_backend(self):
        """Test invalid backend raises error."""
        with pytest.raises(ValidationError):
            GenerationSettings(default_backend="invalid")

    def test_saturation_range(self):
        """Test saturation adjustment range validation."""
        # Valid values
        GenerationSettings(saturation_adjustment=0.0)
        GenerationSettings(saturation_adjustment=1.0)
        GenerationSettings(saturation_adjustment=2.0)

        # Invalid values
        with pytest.raises(ValidationError):
            GenerationSettings(saturation_adjustment=-0.1)
        with pytest.raises(ValidationError):
            GenerationSettings(saturation_adjustment=2.1)


class TestPywalBackendSettings:
    """Test PywalBackendSettings model."""

    def test_default_values(self):
        """Test default pywal settings."""
        settings = PywalBackendSettings()
        assert settings.backend_algorithm == "haishoku"

    def test_valid_algorithms(self):
        """Test valid pywal algorithms."""
        for algo in ["wal", "colorz", "colorthief", "haishoku", "schemer2"]:
            settings = PywalBackendSettings(backend_algorithm=algo)
            assert settings.backend_algorithm == algo

    def test_invalid_algorithm(self):
        """Test invalid algorithm raises error."""
        with pytest.raises(ValidationError):
            PywalBackendSettings(backend_algorithm="invalid")


class TestCustomBackendSettings:
    """Test CustomBackendSettings model."""

    def test_default_values(self):
        """Test default custom backend settings."""
        settings = CustomBackendSettings()
        assert settings.algorithm == "kmeans"
        assert settings.n_clusters == 16

    def test_valid_algorithms(self):
        """Test valid custom algorithms."""
        for algo in ["kmeans", "dominant"]:
            settings = CustomBackendSettings(algorithm=algo)
            assert settings.algorithm == algo

    def test_invalid_algorithm(self):
        """Test invalid algorithm raises error."""
        with pytest.raises(ValidationError):
            CustomBackendSettings(algorithm="invalid")

    def test_n_clusters_range(self):
        """Test n_clusters range validation."""
        # Valid values
        CustomBackendSettings(n_clusters=8)
        CustomBackendSettings(n_clusters=16)
        CustomBackendSettings(n_clusters=256)

        # Invalid values
        with pytest.raises(ValidationError):
            CustomBackendSettings(n_clusters=7)
        with pytest.raises(ValidationError):
            CustomBackendSettings(n_clusters=257)


class TestAppConfig:
    """Test AppConfig model."""

    def test_default_values(self):
        """Test AppConfig with all defaults."""
        config = AppConfig()
        assert config.logging.level == "INFO"
        assert config.generation.default_backend == "pywal"
        assert isinstance(config.backends, BackendSettings)

    def test_from_dict(self, sample_settings_dict):
        """Test creating AppConfig from dictionary."""
        config = AppConfig(**sample_settings_dict)
        assert config.logging.level == "DEBUG"
        assert config.generation.default_backend == "custom"
        assert config.generation.saturation_adjustment == 1.5


class TestSettingsModel:
    """Test SettingsModel loader."""

    def test_global_settings_loads(self):
        """Test that global Settings instance loads successfully."""
        config = Settings.get()
        assert isinstance(config, AppConfig)
        assert config.logging.level in [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]

    def test_convert_to_lowercase(self):
        """Test key conversion to lowercase."""
        input_dict = {"LOGGING": {"LEVEL": "INFO"}, "OUTPUT": {"DIRECTORY": "/tmp"}}
        result = SettingsModel._convert_dict_to_lower_case(input_dict)
        assert "logging" in result
        assert "LOGGING" not in result
        assert result["logging"]["level"] == "INFO"

    def test_resolve_environment_variables(self):
        """Test environment variable resolution."""
        import os

        os.environ["TEST_VAR"] = "test_value"
        input_dict = {"path": "$TEST_VAR/subdir"}
        result = SettingsModel._resolve_environment_variables(input_dict)
        assert result["path"] == "test_value/subdir"
