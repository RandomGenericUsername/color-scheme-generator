"""Tests for backend validation utilities."""

import pytest

from colorscheme_shared.cli.backends import BackendValidator


class TestBackendValidator:
    """Test BackendValidator class."""

    def test_valid_backends_list(self):
        """Test that valid backends are defined."""
        assert len(BackendValidator.VALID_BACKENDS) > 0
        assert "pywal" in BackendValidator.VALID_BACKENDS
        assert "wallust" in BackendValidator.VALID_BACKENDS
        assert "custom" in BackendValidator.VALID_BACKENDS

    def test_is_valid_pywal(self):
        """Test is_valid with pywal."""
        assert BackendValidator.is_valid("pywal")

    def test_is_valid_wallust(self):
        """Test is_valid with wallust."""
        assert BackendValidator.is_valid("wallust")

    def test_is_valid_custom(self):
        """Test is_valid with custom."""
        assert BackendValidator.is_valid("custom")

    def test_is_valid_invalid(self):
        """Test is_valid with invalid backend."""
        assert not BackendValidator.is_valid("invalid")

    def test_is_valid_case_insensitive(self):
        """Test is_valid is case insensitive."""
        assert BackendValidator.is_valid("PYWAL")
        assert BackendValidator.is_valid("Wallust")
        assert BackendValidator.is_valid("CUSTOM")

    def test_validate_valid(self):
        """Test validate with valid backend."""
        result = BackendValidator.validate("pywal")
        assert result == "pywal"

    def test_validate_invalid(self):
        """Test validate with invalid backend raises error."""
        with pytest.raises(ValueError) as exc_info:
            BackendValidator.validate("invalid")
        assert "Invalid backend" in str(exc_info.value)

    def test_validate_case_normalized(self):
        """Test validate normalizes to lowercase."""
        result = BackendValidator.validate("PYWAL")
        assert result == "pywal"

    def test_get_available(self):
        """Test get_available filters correctly."""
        backends = ["pywal", "wallust", "invalid", "custom"]
        available = BackendValidator.get_available(backends)
        assert "pywal" in available
        assert "wallust" in available
        assert "custom" in available
        assert "invalid" not in available

    def test_get_available_empty(self):
        """Test get_available with empty list."""
        available = BackendValidator.get_available([])
        assert available == []

    def test_format_available(self):
        """Test format_available produces proper output."""
        backends = ["pywal", "wallust"]
        result = BackendValidator.format_available(backends)
        assert "pywal" in result
        assert "wallust" in result
        assert "•" in result

    def test_format_available_empty(self):
        """Test format_available with empty list."""
        result = BackendValidator.format_available([])
        assert "No backends available" in result
