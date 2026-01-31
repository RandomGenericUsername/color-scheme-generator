"""Color scheme generation service.

This service encapsulates the core business logic of generating color schemes,
separated from CLI concerns. It can be used by CLIs, APIs, or other interfaces.
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from colorscheme_generator import ColorSchemeGeneratorFactory
from colorscheme_generator.config.enums import Backend, ColorFormat
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
    OutputWriteError,
)
from colorscheme_generator.core.managers import OutputManager
from colorscheme_generator.core.types import ColorScheme, GeneratorConfig


logger = logging.getLogger(__name__)


@dataclass
class GenerationRequest:
    """Request for color scheme generation."""

    image: Path
    backend: str = "auto"
    output_dir: Optional[Path] = None
    formats: Optional[list[ColorFormat]] = None
    saturation: Optional[float] = None
    pywal_algorithm: Optional[str] = None
    wallust_backend: Optional[str] = None
    custom_algorithm: Optional[str] = None
    custom_clusters: Optional[int] = None
    template_dir: Optional[Path] = None


@dataclass
class GenerationResult:
    """Result of color scheme generation."""

    scheme: ColorScheme
    elapsed_time: float
    output_files: list[Path]
    success: bool
    error: Optional[str] = None


class ColorSchemeGenerationService:
    """Service for generating color schemes.

    This service encapsulates the business logic for color scheme generation,
    separated from CLI concerns, allowing it to be used by different interfaces.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the generation service.

        Args:
            settings: Settings to use (loads defaults if not provided)
        """
        self.settings = settings or Settings.get()
        self.output_manager = OutputManager(self.settings)

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate a color scheme based on the request.

        Args:
            request: GenerationRequest with image and options

        Returns:
            GenerationResult with scheme and output files

        Raises:
            InvalidImageError: If image is invalid
            ColorExtractionError: If color extraction fails
            OutputWriteError: If writing output fails
        """
        start_time = time.time()

        try:
            # Validate image
            if not request.image.exists():
                raise InvalidImageError(f"Image file not found: {request.image}")

            # Determine backend
            config_kwargs = {}
            if request.backend != "auto":
                try:
                    config_kwargs["backend"] = Backend(request.backend)
                except ValueError as e:
                    raise ValueError(f"Invalid backend: {request.backend}") from e
            else:
                config_kwargs["backend"] = Backend(
                    self.settings.generation.default_backend
                )

            # Set output directory
            if request.output_dir:
                config_kwargs["output_dir"] = request.output_dir.expanduser()

            # Set formats
            if request.formats:
                config_kwargs["formats"] = request.formats

            # Create runtime config
            config = GeneratorConfig(**config_kwargs)

            # Apply overrides to settings
            self._apply_overrides(request)

            logger.debug("Image: %s", request.image)
            logger.debug("Backend: %s", config.backend.value)
            logger.debug("Output dir: %s", config.output_dir)

            # Create generator
            try:
                generator = ColorSchemeGeneratorFactory.create(
                    backend=config.backend,
                    settings=self.settings,
                )
            except BackendNotAvailableError as e:
                raise BackendNotAvailableError(
                    f"Backend not available: {e}"
                ) from e

            # Generate color scheme
            logger.info("Extracting colors from %s...", request.image)
            scheme = generator.generate(request.image, config)
            elapsed = time.time() - start_time
            logger.info("Color extraction successful (%.2fs)", elapsed)

            # Write output files
            final_output_dir = (
                request.output_dir
                if request.output_dir
                else self.settings.output.directory
            )
            final_formats = (
                request.formats
                if request.formats
                else [ColorFormat(f) for f in self.settings.output.formats]
            )

            logger.debug("Writing output to: %s", final_output_dir)

            output_files = self.output_manager.write_outputs(
                scheme,
                final_output_dir,
                final_formats,
            )

            return GenerationResult(
                scheme=scheme,
                elapsed_time=elapsed,
                output_files=output_files,
                success=True,
            )

        except (
            InvalidImageError,
            ColorExtractionError,
            OutputWriteError,
        ) as e:
            elapsed = time.time() - start_time
            logger.error("Generation failed: %s", e)
            return GenerationResult(
                scheme=None,  # type: ignore
                elapsed_time=elapsed,
                output_files=[],
                success=False,
                error=str(e),
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.exception("Unexpected error during generation")
            return GenerationResult(
                scheme=None,  # type: ignore
                elapsed_time=elapsed,
                output_files=[],
                success=False,
                error=f"Unexpected error: {e}",
            )

    def _apply_overrides(self, request: GenerationRequest) -> None:
        """Apply request overrides to settings.

        Args:
            request: GenerationRequest with override values
        """
        if request.saturation is not None:
            self.settings.generation.saturation_adjustment = request.saturation

        if request.pywal_algorithm:
            self.settings.backends.pywal.backend_algorithm = (
                request.pywal_algorithm
            )

        if request.wallust_backend:
            self.settings.backends.wallust.backend_type = request.wallust_backend

        if request.custom_algorithm:
            self.settings.backends.custom.algorithm = request.custom_algorithm

        if request.custom_clusters:
            self.settings.backends.custom.n_clusters = request.custom_clusters

        if request.template_dir:
            self.settings.templates.directory = Path(request.template_dir)

    def list_available_backends(self) -> list[str]:
        """Get list of available backends.

        Returns:
            List of backend names that are available
        """
        return ColorSchemeGeneratorFactory.list_available(self.settings)
