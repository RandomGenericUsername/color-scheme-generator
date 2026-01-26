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
