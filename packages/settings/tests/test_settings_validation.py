"""Tests for settings model validation against real TOML defaults."""

from pathlib import Path

import pytest

from color_scheme_settings.loader import load_toml
from color_scheme_settings.registry import SchemaRegistry


@pytest.fixture(autouse=True)
def clean_registry():
    SchemaRegistry.clear()
    yield
    SchemaRegistry.clear()


class TestOrchestratorEngineDefault:
    def test_orchestrator_engine_default_comes_from_toml(self):
        """MAJ-02: engine=docker must come from the TOML file, not the model default."""
        # Use Path(__file__) to build an absolute path regardless of working directory
        # __file__ = packages/settings/tests/test_settings_validation.py
        # .parent x3 = packages/  then / "orchestrator/..."
        toml_path = (
            Path(__file__).parent.parent.parent
            / "orchestrator"
            / "src"
            / "color_scheme_orchestrator"
            / "config"
            / "settings.toml"
        )
        data = load_toml(toml_path)
        # After fix: top-level key 'engine' = 'docker'
        # Before fix: only key is 'container' (a nested dict), no 'engine' at top level
        assert data.get("engine") == "docker", (
            f"Expected top-level engine='docker' in TOML, got: {data}"
        )
