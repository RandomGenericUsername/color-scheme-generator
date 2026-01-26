"""Tests for output-related exceptions."""

import pytest

from color_scheme.core.exceptions import (
    ColorSchemeError,
    OutputWriteError,
    TemplateRenderError,
)


class TestTemplateRenderError:
    """Tests for TemplateRenderError."""

    def test_init_with_template_and_reason(self):
        """Test initialization with template name and reason."""
        error = TemplateRenderError("colors.json.j2", "Undefined variable 'foo'")

        assert error.template_name == "colors.json.j2"
        assert error.reason == "Undefined variable 'foo'"
        assert "colors.json.j2" in str(error)
        assert "Undefined variable 'foo'" in str(error)

    def test_inherits_from_colorscheme_error(self):
        """Test that it inherits from ColorSchemeError."""
        error = TemplateRenderError("test.j2", "test reason")

        assert isinstance(error, ColorSchemeError)
        assert isinstance(error, Exception)


class TestOutputWriteError:
    """Tests for OutputWriteError."""

    def test_init_with_path_and_reason(self):
        """Test initialization with file path and reason."""
        error = OutputWriteError("/tmp/colors.json", "Permission denied")

        assert error.file_path == "/tmp/colors.json"
        assert error.reason == "Permission denied"
        assert "/tmp/colors.json" in str(error)
        assert "Permission denied" in str(error)

    def test_inherits_from_colorscheme_error(self):
        """Test that it inherits from ColorSchemeError."""
        error = OutputWriteError("/tmp/test", "test reason")

        assert isinstance(error, ColorSchemeError)
        assert isinstance(error, Exception)
