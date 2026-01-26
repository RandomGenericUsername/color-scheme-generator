"""Factory for creating backend generators."""

import logging

from color_scheme.backends.custom import CustomGenerator
from color_scheme.backends.pywal import PywalGenerator
from color_scheme.backends.wallust import WallustGenerator
from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend
from color_scheme.core.base import ColorSchemeGenerator
from color_scheme.core.exceptions import BackendNotAvailableError

logger = logging.getLogger(__name__)


class BackendFactory:
    """Factory for creating backend generators.

    Provides methods to:
    - Create generators for specific backends
    - Detect available backends
    - Auto-detect the best available backend

    Attributes:
        settings: Application configuration
    """

    def __init__(self, settings: AppConfig):
        """Initialize BackendFactory.

        Args:
            settings: Application configuration
        """
        self.settings = settings
        logger.debug("Initialized BackendFactory")

    def create(self, backend: Backend) -> ColorSchemeGenerator:
        """Create a generator for the specified backend.

        Args:
            backend: Backend to create

        Returns:
            ColorSchemeGenerator instance

        Raises:
            BackendNotAvailableError: If backend is not available

        Example:
            >>> factory = BackendFactory(settings)
            >>> generator = factory.create(Backend.PYWAL)
            >>> scheme = generator.generate(image_path, config)
        """
        logger.debug("Creating generator for backend: %s", backend.value)

        if backend == Backend.CUSTOM:
            generator = CustomGenerator(self.settings)
        elif backend == Backend.PYWAL:
            generator = PywalGenerator(self.settings)
        elif backend == Backend.WALLUST:
            generator = WallustGenerator(self.settings)
        else:
            raise ValueError(f"Unknown backend: {backend}")

        # Ensure backend is available
        generator.ensure_available()

        logger.info("Created %s generator", backend.value)
        return generator

    def detect_available(self) -> list[Backend]:
        """Detect all available backends.

        Returns:
            List of available backends

        Example:
            >>> factory = BackendFactory(settings)
            >>> available = factory.detect_available()
            >>> print(available)
            [<Backend.CUSTOM: 'custom'>, <Backend.PYWAL: 'pywal'>]
        """
        available = []

        for backend in Backend:
            try:
                if backend == Backend.CUSTOM:
                    generator = CustomGenerator(self.settings)
                elif backend == Backend.PYWAL:
                    generator = PywalGenerator(self.settings)
                elif backend == Backend.WALLUST:
                    generator = WallustGenerator(self.settings)
                else:
                    continue

                if generator.is_available():
                    available.append(backend)
                    logger.debug("Backend %s is available", backend.value)
                else:
                    logger.debug("Backend %s is not available", backend.value)

            except Exception as e:
                logger.debug(
                    "Failed to check backend %s: %s", backend.value, e
                )

        logger.info("Available backends: %s", [b.value for b in available])
        return available

    def auto_detect(self) -> Backend:
        """Auto-detect the best available backend.

        Preference order: wallust > pywal > custom

        Returns:
            Best available backend (always returns at least CUSTOM)

        Example:
            >>> factory = BackendFactory(settings)
            >>> backend = factory.auto_detect()
            >>> generator = factory.create(backend)
        """
        logger.debug("Auto-detecting best available backend")

        # Check in preference order
        for backend in [Backend.WALLUST, Backend.PYWAL, Backend.CUSTOM]:
            try:
                if backend == Backend.CUSTOM:
                    generator = CustomGenerator(self.settings)
                elif backend == Backend.PYWAL:
                    generator = PywalGenerator(self.settings)
                elif backend == Backend.WALLUST:
                    generator = WallustGenerator(self.settings)
                else:
                    continue

                if generator.is_available():
                    logger.info("Auto-detected backend: %s", backend.value)
                    return backend

            except Exception as e:
                logger.debug(
                    "Failed to check backend %s: %s", backend.value, e
                )

        # Fallback to custom (always available)
        logger.info("Falling back to custom backend")
        return Backend.CUSTOM
