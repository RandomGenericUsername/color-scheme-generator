"""Abstract base class for color scheme generators.

This module defines the interface that all backend implementations must follow.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from colorscheme_generator.core.types import ColorScheme, GeneratorConfig


class ColorSchemeGenerator(ABC):
    """Abstract base class for color scheme generators.

    All backend implementations (PywalGenerator, WallustGenerator,
    CustomGenerator) must inherit from this class and implement its
    abstract methods.

    The generator's responsibility is to extract colors from an image
    and return a ColorScheme object. It does NOT write output files -
    that's the job of OutputManager.

    Example:
        >>> class MyGenerator(ColorSchemeGenerator):
        ...     def generate(self, image_path, config):
        ...         # Extract colors from image
        ...         return ColorScheme(...)
        ...
        ...     def is_available(self):
        ...         return True
        ...
        ...     @property
        ...     def backend_name(self):
        ...         return "my_backend"
    """

    @abstractmethod
    def generate(
        self, image_path: Path, config: GeneratorConfig
    ) -> ColorScheme:
        """Generate color scheme from image.

        This method extracts colors from the given image and returns a
        ColorScheme object containing the color data. It should NOT write
        any output files.

        Args:
            image_path: Path to the source image
            config: Runtime configuration for generation

        Returns:
            ColorScheme object with extracted colors

        Raises:
            InvalidImageError: If image cannot be read or is invalid
            ColorExtractionError: If color extraction fails
            BackendNotAvailableError: If backend is not available

        Example:
            >>> generator = PywalGenerator(settings)
            >>> scheme = generator.generate(
            ...     Path("~/wallpapers/mountain.png"),
            ...     GeneratorConfig()
            ... )
            >>> print(scheme.background.hex)
            '#1a1a1a'
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on the system.

        This method checks if the backend's dependencies are installed and
        accessible. For example, PywalGenerator checks if pywal is installed.

        Returns:
            True if backend is available, False otherwise

        Example:
            >>> generator = PywalGenerator(settings)
            >>> if generator.is_available():
            ...     scheme = generator.generate(image_path, config)
            ... else:
            ...     print("Pywal is not installed")
        """
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Get the backend name.

        Returns:
            Backend name (e.g., "pywal", "wallust", "custom")

        Example:
            >>> generator = PywalGenerator(settings)
            >>> print(generator.backend_name)
            'pywal'
        """
        pass

    def ensure_available(self) -> None:
        """Ensure backend is available, raise error if not.

        This is a convenience method that calls is_available() and raises
        BackendNotAvailableError if the backend is not available.

        Raises:
            BackendNotAvailableError: If backend is not available

        Example:
            >>> generator = PywalGenerator(settings)
            >>> generator.ensure_available()  # Raises if pywal not installed
        """
        from colorscheme_generator.core.exceptions import (
            BackendNotAvailableError,
        )

        if not self.is_available():
            raise BackendNotAvailableError(
                self.backend_name,
                f"{self.backend_name} is not installed or not in PATH",
            )
