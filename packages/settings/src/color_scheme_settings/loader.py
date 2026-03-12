"""Settings layer discovery and TOML loading."""

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from color_scheme_settings.errors import SettingsFileError
from color_scheme_settings.registry import SchemaRegistry
from color_scheme_settings.transforms import parse_env_vars


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
        with file_path.open("rb") as f:
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
    """

    def __init__(
        self,
        project_root: Path | None = None,
        user_config_path: Path | None = None,
    ) -> None:
        self.project_root = project_root
        xdg_config_home = Path(
            os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        )
        self.user_config_path = (
            user_config_path
            if user_config_path is not None
            else xdg_config_home / "color-scheme" / "settings.toml"
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
                # Normalize top-level keys to lowercase for case-insensitive matching
                data_lower = {k.lower(): v for k, v in data.items()}
                for ns in SchemaRegistry.all_namespaces():
                    if ns in data_lower:
                        layers.append(
                            LayerSource(
                                layer="project",
                                namespace=ns,
                                file_path=project_file,
                                data=data_lower[ns],
                            )
                        )

        # Layer 3: User config (namespaced sections)
        if self.user_config_path is not None and self.user_config_path.exists():
            data = load_toml(self.user_config_path)
            # Normalize top-level keys to lowercase for case-insensitive matching
            data_lower = {k.lower(): v for k, v in data.items()}
            for ns in SchemaRegistry.all_namespaces():
                if ns in data_lower:
                    layers.append(
                        LayerSource(
                            layer="user",
                            namespace=ns,
                            file_path=self.user_config_path,
                            data=data_lower[ns],
                        )
                    )

        # Layer 4: Environment variables (COLORSCHEME_SECTION__KEY)
        raw_env = parse_env_vars()
        for entry in SchemaRegistry.all_entries():
            # Only include env sections that match known model field names
            model_sections = set(entry.model.model_fields.keys())
            namespace_data = {k: v for k, v in raw_env.items() if k in model_sections}
            if namespace_data:
                layers.append(
                    LayerSource(
                        layer="env",
                        namespace=entry.namespace,
                        file_path=None,
                        data=namespace_data,
                    )
                )

        return layers
