"""Custom exceptions for colorscheme generator."""


class ColorSchemeGeneratorError(Exception):
    """Base exception for colorscheme generator errors."""

    pass


class BackendNotAvailableError(ColorSchemeGeneratorError):
    """Raised when a backend is not available on the system.

    Example:
        >>> raise BackendNotAvailableError("pywal", "pywal command not found")
    """

    def __init__(self, backend: str, reason: str | None = None):
        self.backend = backend
        self.reason = reason
        message = f"Backend '{backend}' is not available"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class ColorExtractionError(ColorSchemeGeneratorError):
    """Raised when color extraction fails.

    Example:
        >>> raise ColorExtractionError("Failed to parse pywal output")
    """

    pass


class TemplateRenderError(ColorSchemeGeneratorError):
    """Raised when template rendering fails.

    Example:
        >>> raise TemplateRenderError(
        ...     "colors.json.j2", "Missing variable 'background'"
        ... )
    """

    def __init__(self, template: str, reason: str):
        self.template = template
        self.reason = reason
        message = f"Failed to render template '{template}': {reason}"
        super().__init__(message)


class OutputWriteError(ColorSchemeGeneratorError):
    """Raised when writing output files fails.

    Example:
        >>> raise OutputWriteError("/path/to/colors.json", "Permission denied")
    """

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        message = f"Failed to write output file '{path}': {reason}"
        super().__init__(message)


class InvalidImageError(ColorSchemeGeneratorError):
    """Raised when image file is invalid or cannot be read.

    Example:
        >>> raise InvalidImageError("/path/to/image.png", "File not found")
    """

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        message = f"Invalid image '{path}': {reason}"
        super().__init__(message)
