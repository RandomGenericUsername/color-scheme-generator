"""Factory for creating color scheme generator instances.

This module provides a factory pattern for creating backend instances
with automatic backend detection.
"""

from colorscheme_generator.backends import (
    CustomGenerator,
    PywalGenerator,
    WallustGenerator,
)
from colorscheme_generator.config.config import AppConfig
from colorscheme_generator.config.enums import Backend
from colorscheme_generator.core.base import ColorSchemeGenerator
from colorscheme_generator.core.exceptions import BackendNotAvailableError


class ColorSchemeGeneratorFactory:
    """Factory for creating ColorSchemeGenerator instances.

    Provides methods to create specific backends or automatically
    detect and use the best available backend.

    Example:
        >>> from colorscheme_generator.config.settings import Settings
        >>> settings = Settings.get()
        >>>
        >>> # Create specific backend
        >>> generator = ColorSchemeGeneratorFactory.create(
        ...     Backend.PYWAL, settings
        ... )
        >>>
        >>> # Auto-detect best backend
        >>> generator = ColorSchemeGeneratorFactory.create_auto(settings)
    """

    @staticmethod
    def create(backend: Backend, settings: AppConfig) -> ColorSchemeGenerator:
        """Create a specific backend instance.

        Args:
            backend: Backend type to create
            settings: Application configuration

        Returns:
            ColorSchemeGenerator instance

        Raises:
            ValueError: If backend type is unknown

        Example:
            >>> generator = ColorSchemeGeneratorFactory.create(
            ...     Backend.PYWAL,
            ...     settings
            ... )
        """
        if backend == Backend.PYWAL:
            return PywalGenerator(settings)
        elif backend == Backend.WALLUST:
            return WallustGenerator(settings)
        elif backend == Backend.CUSTOM:
            return CustomGenerator(settings)
        else:
            raise ValueError(f"Unknown backend: {backend}")

    @staticmethod
    def create_auto(settings: AppConfig) -> ColorSchemeGenerator:
        """Automatically detect and create best available backend.

        Tries backends in order of preference:
        1. Wallust (fastest)
        2. Pywal (most popular)
        3. Custom (always available)

        Args:
            settings: Application configuration

        Returns:
            ColorSchemeGenerator instance for best available backend

        Raises:
            BackendNotAvailableError: If no backends are available
                (shouldn't happen)

        Example:
            >>> # Automatically use best available backend
            >>> generator = ColorSchemeGeneratorFactory.create_auto(settings)
            >>> print(f"Using backend: {generator.backend_name}")
        """
        # Try backends in order of preference
        backends_to_try = [
            (Backend.WALLUST, WallustGenerator),
            (Backend.PYWAL, PywalGenerator),
            (Backend.CUSTOM, CustomGenerator),
        ]

        for _backend_type, backend_class in backends_to_try:
            generator = backend_class(settings)
            if generator.is_available():
                return generator

        # This should never happen since CustomGenerator is always available
        raise BackendNotAvailableError(
            "none",
            "No backends available. This should not happen.",
        )

    @staticmethod
    def list_available(settings: AppConfig) -> list[str]:
        """List all available backends.

        Args:
            settings: Application configuration

        Returns:
            List of available backend names

        Example:
            >>> available = ColorSchemeGeneratorFactory.list_available(
            ...     settings
            ... )
            >>> print(f"Available backends: {', '.join(available)}")
        """
        backends = [
            PywalGenerator(settings),
            WallustGenerator(settings),
            CustomGenerator(settings),
        ]

        return [b.backend_name for b in backends if b.is_available()]
