"""Pytest fixtures for templates tests."""

from pathlib import Path

import pytest

from color_scheme_templates import reset


@pytest.fixture(autouse=True)
def reset_templates() -> None:
    """Reset the template system before each test."""
    reset()


@pytest.fixture
def sample_templates_dir(tmp_path: Path) -> Path:
    """Create a directory with sample templates."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "colors.css.j2").write_text("/* CSS */")
    (templates_dir / "colors.json.j2").write_text("{}")
    return templates_dir
