"""Backend validation utilities.

Provides common validation for backend selection across CLI applications.
"""

from typing import Sequence


class BackendValidator:
    """Validates backend names and provides helpful error messages.

    This utility can be used in both CLI applications to ensure consistent
    backend validation behavior.
    """

    VALID_BACKENDS = ["pywal", "wallust", "custom"]
    DEFAULT_BACKEND = "pywal"

    @classmethod
    def is_valid(cls, backend: str) -> bool:
        """Check if a backend name is valid.

        Args:
            backend: Backend name to validate

        Returns:
            True if backend is valid, False otherwise
        """
        return backend.lower() in cls.VALID_BACKENDS

    @classmethod
    def validate(cls, backend: str) -> str:
        """Validate a backend name, raising an error if invalid.

        Args:
            backend: Backend name to validate

        Returns:
            The backend name if valid

        Raises:
            ValueError: If backend is not valid
        """
        if not cls.is_valid(backend):
            valid_list = ", ".join(cls.VALID_BACKENDS)
            raise ValueError(
                f"Invalid backend: {backend!r}. "
                f"Valid options are: {valid_list}"
            )
        return backend.lower()

    @classmethod
    def get_available(cls, installed_backends: Sequence[str]) -> list[str]:
        """Get list of available backends.

        Args:
            installed_backends: List of installed backend names

        Returns:
            Filtered list of valid installed backends
        """
        return [b for b in installed_backends if cls.is_valid(b)]

    @classmethod
    def format_available(cls, backends: Sequence[str]) -> str:
        """Format a list of backends for display.

        Args:
            backends: Backends to format

        Returns:
            Formatted string for display
        """
        if not backends:
            return "No backends available"
        return "\n".join(f"  • {b}" for b in backends)
