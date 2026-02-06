"""Tests for the template registry."""

from pathlib import Path

import pytest
from color_scheme_templates.errors import TemplateRegistryError
from color_scheme_templates.registry import TemplateRegistry


class TestTemplateRegistry:
    """Tests for TemplateRegistry class."""

    def test_register_new_namespace(self, tmp_path: Path) -> None:
        TemplateRegistry.register(namespace="test", templates_dir=tmp_path)
        entry = TemplateRegistry.get("test")
        assert entry.namespace == "test"
        assert entry.templates_dir == tmp_path

    def test_register_duplicate_raises(self, tmp_path: Path) -> None:
        TemplateRegistry.register(namespace="test", templates_dir=tmp_path)
        with pytest.raises(TemplateRegistryError, match="already registered"):
            TemplateRegistry.register(namespace="test", templates_dir=tmp_path)

    def test_get_unregistered_raises(self) -> None:
        with pytest.raises(TemplateRegistryError, match="not registered"):
            TemplateRegistry.get("nonexistent")

    def test_all_entries(self, tmp_path: Path) -> None:
        TemplateRegistry.register(namespace="a", templates_dir=tmp_path / "a")
        TemplateRegistry.register(namespace="b", templates_dir=tmp_path / "b")
        assert len(TemplateRegistry.all_entries()) == 2

    def test_all_namespaces(self, tmp_path: Path) -> None:
        TemplateRegistry.register(namespace="a", templates_dir=tmp_path / "a")
        TemplateRegistry.register(namespace="b", templates_dir=tmp_path / "b")
        assert set(TemplateRegistry.all_namespaces()) == {"a", "b"}

    def test_clear(self, tmp_path: Path) -> None:
        TemplateRegistry.register(namespace="test", templates_dir=tmp_path)
        TemplateRegistry.clear()
        assert TemplateRegistry.all_entries() == []
