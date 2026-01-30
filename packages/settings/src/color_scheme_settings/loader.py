"""Settings layer discovery and TOML loading."""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from color_scheme_settings.errors import SettingsFileError
from color_scheme_settings.registry import SchemaRegistry


@dataclass
class LayerSource:
    """A single settings layer loaded from a file."""

    layer: str
    namespace: str
    file_path: Path | None
    data: dict[str, Any]


def load_toml(file_path: Path) -> dict[str, Any]:
    """Load and parse a TOML file.

    Args:
        file_path: Path to the TOML file

    Returns:
        Parsed TOML as a dictionary

    Raises:
        SettingsFileError: If file cannot be read or parsed
    """
    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise SettingsFileError(file_path=file_path, reason=str(e)) from e
    except OSError as e:
        raise SettingsFileError(file_path=file_path, reason=str(e)) from e


class SettingsLoader:
    """Discovers and loads settings files from all layers.

    Layers (lowest to highest priority):
    1. Package defaults -- flat sections, namespace inferred from registry
    2. Project root -- namespaced sections ([core.*], [orchestrator.*])
    3. User config -- namespaced sections ([core.*], [orchestrator.*])

    Args:
        project_root: Path to project root directory (contains settings.toml).
                      If None, project layer is skipped.
        user_config_path: Path to user settings file.
                          If None, defaults to ~/.config/color-scheme/settings.toml.
    """

    def __init__(
        self,
        project_root: Path | None = None,
        user_config_path: Path | None = None,
    ) -> None:
        self.project_root = project_root
        self.user_config_path = (
            user_config_path
            if user_config_path is not None
            else Path.home() / ".config" / "color-scheme" / "settings.toml"
        )

    def discover_layers(self) -> list[LayerSource]:
        """Discover all settings files across all layers.

        Returns:
            List of LayerSource objects in priority order (lowest first).
        """
        layers: list[LayerSource] = []

        # Layer 1: Package defaults (flat sections)
        for entry in SchemaRegistry.all_entries():
            if entry.defaults_file.exists():
                data = load_toml(entry.defaults_file)
                layers.append(
                    LayerSource(
                        layer="package",
                        namespace=entry.namespace,
                        file_path=entry.defaults_file,
                        data=data,
                    )
                )

        # Layer 2: Project root (namespaced sections)
        if self.project_root is not None:
            project_file = self.project_root / "settings.toml"
            if project_file.exists():
                data = load_toml(project_file)
                for ns in SchemaRegistry.all_namespaces():
                    if ns in data:
                        layers.append(
                            LayerSource(
                                layer="project",
                                namespace=ns,
                                file_path=project_file,
                                data=data[ns],
                            )
                        )

        # Layer 3: User config (namespaced sections)
        if self.user_config_path is not None and self.user_config_path.exists():
            data = load_toml(self.user_config_path)
            for ns in SchemaRegistry.all_namespaces():
                if ns in data:
                    layers.append(
                        LayerSource(
                            layer="user",
                            namespace=ns,
                            file_path=self.user_config_path,
                            data=data[ns],
                        )
                    )

        return layers
