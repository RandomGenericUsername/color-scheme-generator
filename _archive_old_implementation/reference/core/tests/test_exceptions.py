"""Tests for custom exceptions."""

import pytest

from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    ColorSchemeGeneratorError,
    InvalidImageError,
    OutputWriteError,
    TemplateRenderError,
)


class TestColorSchemeGeneratorError:
    """Test base exception."""

    def test_base_exception(self):
        """Test base exception can be raised."""
        with pytest.raises(ColorSchemeGeneratorError):
            raise ColorSchemeGeneratorError("Test error")

    def test_base_exception_message(self):
        """Test base exception message."""
        error = ColorSchemeGeneratorError("Test error")
        assert str(error) == "Test error"

    def test_base_exception_inheritance(self):
        """Test base exception inherits from Exception."""
        assert issubclass(ColorSchemeGeneratorError, Exception)


class TestBackendNotAvailableError:
    """Test BackendNotAvailableError."""

    def test_backend_not_available_basic(self):
        """Test basic backend not available error."""
        error = BackendNotAvailableError("pywal")
        assert error.backend == "pywal"
        assert error.reason is None
        assert str(error) == "Backend 'pywal' is not available"

    def test_backend_not_available_with_reason(self):
        """Test backend not available error with reason."""
        error = BackendNotAvailableError("pywal", "pywal command not found")
        assert error.backend == "pywal"
        assert error.reason == "pywal command not found"
        assert (
            str(error)
            == "Backend 'pywal' is not available: pywal command not found"
        )

    def test_backend_not_available_inheritance(self):
        """Test BackendNotAvailableError inherits from base."""
        assert issubclass(BackendNotAvailableError, ColorSchemeGeneratorError)

    def test_backend_not_available_can_be_caught(self):
        """Test error can be caught."""
        with pytest.raises(BackendNotAvailableError) as exc_info:
            raise BackendNotAvailableError("wallust", "not installed")

        assert exc_info.value.backend == "wallust"
        assert exc_info.value.reason == "not installed"


class TestColorExtractionError:
    """Test ColorExtractionError."""

    def test_color_extraction_error(self):
        """Test color extraction error."""
        error = ColorExtractionError("Failed to extract colors")
        assert str(error) == "Failed to extract colors"

    def test_color_extraction_error_inheritance(self):
        """Test ColorExtractionError inherits from base."""
        assert issubclass(ColorExtractionError, ColorSchemeGeneratorError)

    def test_color_extraction_error_can_be_caught(self):
        """Test error can be caught."""
        with pytest.raises(ColorExtractionError) as exc_info:
            raise ColorExtractionError("K-means failed to converge")

        assert "K-means failed" in str(exc_info.value)


class TestTemplateRenderError:
    """Test TemplateRenderError."""

    def test_template_render_error_basic(self):
        """Test basic template render error."""
        error = TemplateRenderError(
            "colors.json.j2", "Missing variable 'background'"
        )
        assert error.template == "colors.json.j2"
        assert error.reason == "Missing variable 'background'"
        expected = (
            "Failed to render template 'colors.json.j2': "
            "Missing variable 'background'"
        )
        assert str(error) == expected

    def test_template_render_error_inheritance(self):
        """Test TemplateRenderError inherits from base."""
        assert issubclass(TemplateRenderError, ColorSchemeGeneratorError)

    def test_template_render_error_can_be_caught(self):
        """Test error can be caught."""
        with pytest.raises(TemplateRenderError) as exc_info:
            raise TemplateRenderError("colors.css.j2", "Syntax error")

        assert exc_info.value.template == "colors.css.j2"
        assert exc_info.value.reason == "Syntax error"


class TestOutputWriteError:
    """Test OutputWriteError."""

    def test_output_write_error_basic(self):
        """Test basic output write error."""
        error = OutputWriteError("/path/to/colors.json", "Permission denied")
        assert error.path == "/path/to/colors.json"
        assert error.reason == "Permission denied"
        expected = (
            "Failed to write output file '/path/to/colors.json': "
            "Permission denied"
        )
        assert str(error) == expected

    def test_output_write_error_inheritance(self):
        """Test OutputWriteError inherits from base."""
        assert issubclass(OutputWriteError, ColorSchemeGeneratorError)

    def test_output_write_error_can_be_caught(self):
        """Test error can be caught."""
        with pytest.raises(OutputWriteError) as exc_info:
            raise OutputWriteError("/tmp/colors.yaml", "Disk full")

        assert exc_info.value.path == "/tmp/colors.yaml"
        assert exc_info.value.reason == "Disk full"


class TestInvalidImageError:
    """Test InvalidImageError."""

    def test_invalid_image_error_basic(self):
        """Test basic invalid image error."""
        error = InvalidImageError("/path/to/image.png", "File not found")
        assert error.path == "/path/to/image.png"
        assert error.reason == "File not found"
        assert (
            str(error) == "Invalid image '/path/to/image.png': File not found"
        )

    def test_invalid_image_error_inheritance(self):
        """Test InvalidImageError inherits from base."""
        assert issubclass(InvalidImageError, ColorSchemeGeneratorError)

    def test_invalid_image_error_can_be_caught(self):
        """Test error can be caught."""
        with pytest.raises(InvalidImageError) as exc_info:
            raise InvalidImageError("/tmp/corrupt.jpg", "Corrupt image data")

        assert exc_info.value.path == "/tmp/corrupt.jpg"
        assert exc_info.value.reason == "Corrupt image data"

    def test_invalid_image_error_not_a_file(self):
        """Test invalid image error for non-file."""
        error = InvalidImageError("/path/to/directory", "Not a file")
        assert "Not a file" in str(error)

    def test_invalid_image_error_unsupported_format(self):
        """Test invalid image error for unsupported format."""
        error = InvalidImageError("/path/to/image.bmp", "Unsupported format")
        assert "Unsupported format" in str(error)


class TestExceptionHierarchy:
    """Test exception hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test all custom exceptions inherit from base."""
        exceptions = [
            BackendNotAvailableError,
            ColorExtractionError,
            TemplateRenderError,
            OutputWriteError,
            InvalidImageError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, ColorSchemeGeneratorError)

    def test_can_catch_all_with_base(self):
        """Test can catch all custom exceptions with base."""
        exceptions_to_test = [
            BackendNotAvailableError("test"),
            ColorExtractionError("test"),
            TemplateRenderError("test.j2", "test"),
            OutputWriteError("/test", "test"),
            InvalidImageError("/test.png", "test"),
        ]

        for exc in exceptions_to_test:
            with pytest.raises(ColorSchemeGeneratorError):
                raise exc
