"""Business logic services for color-scheme-generator.

These services encapsulate the core business logic that was previously
mixed with CLI code, making it reusable across different interfaces
(CLI, API, scripts, etc.).
"""

from colorscheme_generator.services.generation import ColorSchemeGenerationService

__all__ = [
    "ColorSchemeGenerationService",
]
