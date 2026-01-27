"""Integration tests for all template formats."""

import json
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from color_scheme.config.enums import ColorFormat
from color_scheme.config.settings import Settings
from color_scheme.core.types import Color, ColorScheme
from color_scheme.output.manager import OutputManager


@pytest.fixture
def sample_scheme():
    """Create sample color scheme for testing."""
    colors = [
        Color(hex=f"#{i:02X}{i:02X}{i:02X}", rgb=(i, i, i))
        for i in range(16)
    ]

    return ColorScheme(
        background=Color(hex="#1A1B26", rgb=(26, 27, 38)),
        foreground=Color(hex="#C0CAF5", rgb=(192, 202, 245)),
        cursor=Color(hex="#7AA2F7", rgb=(122, 162, 247)),
        colors=colors,
        source_image=Path("/test/wallpaper.png"),
        backend="custom",
        generated_at=datetime(2026, 1, 26, 12, 0, 0),
    )


@pytest.fixture
def manager():
    """Create OutputManager instance."""
    settings = Settings.get()
    return OutputManager(settings)


def test_json_template(manager, sample_scheme, tmp_path):
    """Verify JSON template renders and is valid JSON."""
    output_dir = tmp_path / "output"
    formats = [ColorFormat.JSON]

    manager.write_outputs(sample_scheme, output_dir, formats)

    json_file = output_dir / "colors.json"
    assert json_file.exists()

    # Parse JSON and verify structure
    with open(json_file) as f:
        data = json.load(f)

    assert data["special"]["background"] == "#1A1B26"
    assert data["metadata"]["backend"] == "custom"
    assert len(data["colors"]) == 16


def test_css_template(manager, sample_scheme, tmp_path):
    """Verify CSS template renders with :root."""
    output_dir = tmp_path / "output"
    formats = [ColorFormat.CSS]

    manager.write_outputs(sample_scheme, output_dir, formats)

    css_file = output_dir / "colors.css"
    assert css_file.exists()

    content = css_file.read_text()
    assert ":root {" in content
    assert "--background:" in content
    assert "#1A1B26" in content


def test_scss_template(manager, sample_scheme, tmp_path):
    """Verify SCSS template renders with $variables."""
    output_dir = tmp_path / "output"
    formats = [ColorFormat.SCSS]

    manager.write_outputs(sample_scheme, output_dir, formats)

    scss_file = output_dir / "colors.scss"
    assert scss_file.exists()

    content = scss_file.read_text()
    assert "$background:" in content
    assert "#1A1B26" in content


def test_yaml_template(manager, sample_scheme, tmp_path):
    """Verify YAML template renders and is valid YAML."""
    output_dir = tmp_path / "output"
    formats = [ColorFormat.YAML]

    manager.write_outputs(sample_scheme, output_dir, formats)

    yaml_file = output_dir / "colors.yaml"
    assert yaml_file.exists()

    # Parse YAML and verify structure
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    assert data["special"]["background"] == "#1A1B26"


def test_sh_template(manager, sample_scheme, tmp_path):
    """Verify shell script template renders."""
    output_dir = tmp_path / "output"
    formats = [ColorFormat.SH]

    manager.write_outputs(sample_scheme, output_dir, formats)

    sh_file = output_dir / "colors.sh"
    assert sh_file.exists()

    content = sh_file.read_text()
    # Check for shell script markers and color value
    assert "#!/bin/sh" in content or "export" in content
    assert "1A1B26" in content or "1a1b26" in content


def test_gtk_css_template(manager, sample_scheme, tmp_path):
    """Verify GTK CSS template with @define-color."""
    output_dir = tmp_path / "output"
    formats = [ColorFormat.GTK_CSS]

    manager.write_outputs(sample_scheme, output_dir, formats)

    gtk_file = output_dir / "colors.gtk.css"
    assert gtk_file.exists()

    content = gtk_file.read_text()
    assert "@define-color" in content


def test_rasi_template(manager, sample_scheme, tmp_path):
    """Verify rofi rasi template renders."""
    output_dir = tmp_path / "output"
    formats = [ColorFormat.RASI]

    manager.write_outputs(sample_scheme, output_dir, formats)

    rasi_file = output_dir / "colors.rasi"
    assert rasi_file.exists()

    content = rasi_file.read_text()
    assert "background:" in content or "bg:" in content


def test_sequences_template(manager, sample_scheme, tmp_path):
    """Verify terminal sequences with escape codes."""
    output_dir = tmp_path / "output"
    formats = [ColorFormat.SEQUENCES]

    manager.write_outputs(sample_scheme, output_dir, formats)

    seq_file = output_dir / "colors.sequences"
    assert seq_file.exists()

    # Read binary content and verify escape sequences
    content = seq_file.read_bytes()
    assert b"\x1b]" in content


def test_all_formats_together(manager, sample_scheme, tmp_path):
    """Verify all 8 formats render at once."""
    output_dir = tmp_path / "output"
    formats = [
        ColorFormat.JSON,
        ColorFormat.CSS,
        ColorFormat.SCSS,
        ColorFormat.YAML,
        ColorFormat.SH,
        ColorFormat.GTK_CSS,
        ColorFormat.RASI,
        ColorFormat.SEQUENCES,
    ]

    manager.write_outputs(sample_scheme, output_dir, formats)

    # Build expected file paths
    expected_files = [
        output_dir / "colors.json",
        output_dir / "colors.css",
        output_dir / "colors.scss",
        output_dir / "colors.yaml",
        output_dir / "colors.sh",
        output_dir / "colors.gtk.css",
        output_dir / "colors.rasi",
        output_dir / "colors.sequences",
    ]

    # Verify we got 8 output files
    assert len(expected_files) == 8

    # Verify all files exist
    for file_path in expected_files:
        assert file_path.exists()
