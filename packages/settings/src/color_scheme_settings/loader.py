"""Settings layer discovery and TOML loading."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LayerSource:
    """A single settings layer loaded from a file."""

    layer: str
    namespace: str
    file_path: Path | None
    data: dict[str, Any]
