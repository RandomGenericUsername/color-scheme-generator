"""Tests for the shared logging module."""

import logging

import pytest
from rich.console import Console

from colorscheme_shared.logging import (
    LoggingConfig,
    get_console,
    get_logger,
    setup_logging,
)


class TestLoggingConfig:
    """Test LoggingConfig class."""

    def test_default_config(self):
        """Test default configuration."""
        config = LoggingConfig()
        assert config.level == logging.INFO
        assert config.show_time is True
        assert config.show_path is False
        assert config.rich_tracebacks is True

    def test_config_from_string_debug(self):
        """Test creating config from debug string."""
        config = LoggingConfig.from_string("DEBUG")
        assert config.level == logging.DEBUG

    def test_config_from_string_info(self):
        """Test creating config from info string."""
        config = LoggingConfig.from_string("INFO")
        assert config.level == logging.INFO

    def test_config_from_string_warning(self):
        """Test creating config from warning string."""
        config = LoggingConfig.from_string("WARNING")
        assert config.level == logging.WARNING

    def test_config_from_string_error(self):
        """Test creating config from error string."""
        config = LoggingConfig.from_string("ERROR")
        assert config.level == logging.ERROR

    def test_config_from_string_critical(self):
        """Test creating config from critical string."""
        config = LoggingConfig.from_string("CRITICAL")
        assert config.level == logging.CRITICAL

    def test_config_from_string_invalid(self):
        """Test creating config from invalid string defaults to INFO."""
        config = LoggingConfig.from_string("INVALID")
        assert config.level == logging.INFO

    def test_config_from_string_case_insensitive(self):
        """Test that from_string is case insensitive."""
        config = LoggingConfig.from_string("debug")
        assert config.level == logging.DEBUG

    def test_config_custom_values(self):
        """Test creating config with custom values."""
        config = LoggingConfig(
            level=logging.DEBUG,
            show_time=False,
            show_path=True,
            rich_tracebacks=False,
        )
        assert config.level == logging.DEBUG
        assert config.show_time is False
        assert config.show_path is True
        assert config.rich_tracebacks is False


class TestSetupLogging:
    """Test setup_logging function."""

    def test_setup_logging_default(self):
        """Test setup_logging with defaults."""
        setup_logging(logger_name="test_logger")
        logger = logging.getLogger("test_logger")
        assert logger.level == logging.INFO

    def test_setup_logging_with_config(self):
        """Test setup_logging with custom config."""
        config = LoggingConfig(level=logging.DEBUG)
        setup_logging(config, logger_name="test_logger_2")
        logger = logging.getLogger("test_logger_2")
        assert logger.level == logging.DEBUG

    def test_setup_logging_with_custom_console(self):
        """Test setup_logging with custom console."""
        console = Console(stderr=True)
        setup_logging(console=console, logger_name="test_logger_3")
        # Verify it doesn't raise an error
        assert get_console() is not None


class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger_default_namespace(self):
        """Test get_logger with default namespace."""
        logger = get_logger("test_module")
        assert logger.name == "colorscheme.test_module"

    def test_get_logger_custom_namespace(self):
        """Test get_logger with custom namespace."""
        logger = get_logger("test_module", logger_namespace="custom")
        assert logger.name == "custom.test_module"

    def test_get_logger_already_prefixed(self):
        """Test get_logger with already prefixed name."""
        logger = get_logger("colorscheme.already.prefixed")
        assert logger.name == "colorscheme.already.prefixed"

    def test_get_logger_caching(self):
        """Test that get_logger caches loggers."""
        logger1 = get_logger("cached_module")
        logger2 = get_logger("cached_module")
        assert logger1 is logger2

    def test_get_logger_multiple_instances(self):
        """Test get_logger with different modules."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        assert logger1 is not logger2
        assert logger1.name == "colorscheme.module1"
        assert logger2.name == "colorscheme.module2"


class TestGetConsole:
    """Test get_console function."""

    def test_get_console_returns_console(self):
        """Test that get_console returns a Console instance."""
        console = get_console()
        assert isinstance(console, Console)

    def test_get_console_consistent(self):
        """Test that get_console returns same instance."""
        console1 = get_console()
        console2 = get_console()
        assert console1 is console2
