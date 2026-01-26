"""Abstract base class for color scheme generators."""

from abc import ABC, abstractmethod
from pathlib import Path

from color_scheme.core.types import ColorScheme, GeneratorConfig


class ColorSchemeGenerator(ABC):
    """Abstract base class for color scheme generators.

    All backend implementations must inherit from this class.
    """

    @abstractmethod
    def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
        """Generate color scheme from image.

        Args:
            image_path: Path to the source image
            config: Runtime configuration for generation

        Returns:
            ColorScheme object with extracted colors

        Raises:
            InvalidImageError: If image cannot be read or is invalid
            ColorExtractionError: If color extraction fails
            BackendNotAvailableError: If backend is not available
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on the system.

        Returns:
            True if backend is available, False otherwise
        """
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Get the backend name.

        Returns:
            Backend name (e.g., "pywal", "wallust", "custom")
        """
        pass

    def ensure_available(self) -> None:
        """Ensure backend is available, raise error if not.

        Raises:
            BackendNotAvailableError: If backend is not available
        """
        from color_scheme.core.exceptions import BackendNotAvailableError

        if not self.is_available():
            raise BackendNotAvailableError(
                self.backend_name,
                f"{self.backend_name} is not installed or not in PATH",
            )
