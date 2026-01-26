"""Exceptions for color scheme generation."""


class ColorSchemeError(Exception):
    """Base exception for color scheme generation errors."""

    pass


class InvalidImageError(ColorSchemeError):
    """Raised when image is invalid or cannot be read."""

    def __init__(self, image_path: str, reason: str):
        self.image_path = image_path
        self.reason = reason
        super().__init__(f"Invalid image '{image_path}': {reason}")


class ColorExtractionError(ColorSchemeError):
    """Raised when color extraction fails."""

    def __init__(self, backend: str, reason: str):
        self.backend = backend
        self.reason = reason
        super().__init__(f"Color extraction failed ({backend}): {reason}")


class BackendNotAvailableError(ColorSchemeError):
    """Raised when backend is not available."""

    def __init__(self, backend: str, reason: str):
        self.backend = backend
        self.reason = reason
        super().__init__(f"Backend '{backend}' not available: {reason}")


class TemplateRenderError(ColorSchemeError):
    """Raised when template rendering fails."""

    def __init__(self, template_name: str, reason: str):
        self.template_name = template_name
        self.reason = reason
        super().__init__(f"Template rendering failed ('{template_name}'): {reason}")


class OutputWriteError(ColorSchemeError):
    """Raised when writing output file fails."""

    def __init__(self, file_path: str, reason: str):
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to write '{file_path}': {reason}")
