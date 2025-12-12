"""Tests for configuration module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from color_scheme.config.config import OrchestratorConfig
from color_scheme.config.constants import (
    DEFAULT_BACKENDS,
    DEFAULT_CONFIG_DIR,
    DEFAULT_OUTPUT_DIR,
)


class TestOrchestratorConfigDefaults:
    """Test default configuration."""

    def test_default_backends(self) -> None:
        """Test default backends are set."""
        config = OrchestratorConfig.default()
        assert config.backends == DEFAULT_BACKENDS

    def test_default_output_dir(self) -> None:
        """Test default output directory."""
        config = OrchestratorConfig.default()
        assert config.output_dir == Path(DEFAULT_OUTPUT_DIR).expanduser()

    def test_default_config_dir(self) -> None:
        """Test default config directory."""
        config = OrchestratorConfig.default()
        assert config.config_dir == Path(DEFAULT_CONFIG_DIR).expanduser()

    def test_default_verbose_false(self) -> None:
        """Test verbose is false by default."""
        config = OrchestratorConfig.default()
        assert config.verbose is False

    def test_default_debug_false(self) -> None:
        """Test debug is false by default."""
        config = OrchestratorConfig.default()
        assert config.debug is False


class TestOrchestratorConfigCustomization:
    """Test configuration customization."""

    def test_custom_backends(self) -> None:
        """Test setting custom backends."""
        config = OrchestratorConfig(backends=["pywal"])
        assert config.backends == ["pywal"]

    def test_custom_output_dir(self) -> None:
        """Test setting custom output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = OrchestratorConfig(output_dir=tmpdir)
            assert config.output_dir == Path(tmpdir)
            assert config.output_dir.exists()

    def test_custom_verbose_flag(self) -> None:
        """Test setting verbose flag."""
        config = OrchestratorConfig(verbose=True)
        assert config.verbose is True

    def test_custom_debug_flag(self) -> None:
        """Test setting debug flag."""
        config = OrchestratorConfig(debug=True)
        assert config.debug is True


class TestOrchestratorConfigEnvironment:
    """Test configuration from environment."""

    def test_config_from_env_runtime(self) -> None:
        """Test runtime from environment."""
        with patch.dict(os.environ, {"COLOR_SCHEME_RUNTIME": "podman"}):
            config = OrchestratorConfig.from_env()
            assert config.runtime == "podman"

    def test_config_from_env_verbose(self) -> None:
        """Test verbose from environment."""
        with patch.dict(os.environ, {"COLOR_SCHEME_VERBOSE": "true"}):
            config = OrchestratorConfig.from_env()
            assert config.verbose is True

    def test_config_from_env_verbose_case_insensitive(self) -> None:
        """Test verbose is case insensitive."""
        with patch.dict(os.environ, {"COLOR_SCHEME_VERBOSE": "TRUE"}):
            config = OrchestratorConfig.from_env()
            assert config.verbose is False  # Only lowercase "true" works

    def test_config_from_env_debug(self) -> None:
        """Test debug from environment."""
        with patch.dict(os.environ, {"COLOR_SCHEME_DEBUG": "true"}):
            config = OrchestratorConfig.from_env()
            assert config.debug is True

    def test_config_from_env_timeout(self) -> None:
        """Test container timeout from environment."""
        with patch.dict(os.environ, {"COLOR_SCHEME_CONTAINER_TIMEOUT": "600"}):
            config = OrchestratorConfig.from_env()
            assert config.container_timeout == 600


class TestOrchestratorConfigDirectoryCreation:
    """Test that directories are created."""

    def test_output_dir_created(self) -> None:
        """Test output directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "output"
            assert not output_dir.exists()

            config = OrchestratorConfig(output_dir=str(output_dir))
            assert output_dir.exists()

    def test_config_dir_created(self) -> None:
        """Test config directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            assert not config_dir.exists()

            config = OrchestratorConfig(config_dir=str(config_dir))
            assert config_dir.exists()

    def test_cache_dir_created(self) -> None:
        """Test cache directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "cache"
            assert not cache_dir.exists()

            config = OrchestratorConfig(cache_dir=str(cache_dir))
            assert cache_dir.exists()


class TestOrchestratorConfigXDGCache:
    """Test XDG cache directory handling."""

    def test_xdg_cache_home_used(self) -> None:
        """Test XDG_CACHE_HOME is used if set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            xdg_cache = Path(tmpdir) / "xdg-cache"
            xdg_cache.mkdir()

            with patch.dict(os.environ, {"XDG_CACHE_HOME": str(xdg_cache)}):
                config = OrchestratorConfig()
                assert "xdg-cache" in str(config.cache_dir)

    def test_fallback_to_home_cache(self) -> None:
        """Test fallback to ~/.cache when XDG not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove XDG_CACHE_HOME if present
            if "XDG_CACHE_HOME" in os.environ:
                del os.environ["XDG_CACHE_HOME"]

            config = OrchestratorConfig()
            assert ".cache" in str(config.cache_dir)
