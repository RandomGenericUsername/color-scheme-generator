"""Integration tests for CLI generate command."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from color_scheme.cli.main import app
from color_scheme.config.enums import Backend, ColorFormat


class TestCLIGenerate:
    """Integration tests for the generate command."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    def test_generate_with_defaults(self, runner, test_image, tmp_path):
        """Test generate command with default options."""
        # Use tmp_path as output directory
        result = runner.invoke(
            app,
            ["generate", str(test_image), "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "Auto-detected backend:" in result.stdout
        assert "Generated color scheme" in result.stdout

        # Verify some output files were created
        output_files = list(tmp_path.glob("*"))
        assert len(output_files) > 0

    def test_generate_with_backend(self, runner, test_image, tmp_path):
        """Test generate command with specific backend selection."""
        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--output-dir",
                str(tmp_path),
                "--backend",
                "custom",
            ],
        )

        assert result.exit_code == 0
        assert "custom" in result.stdout.lower()
        assert "Generated color scheme" in result.stdout

        # Verify output files were created
        output_files = list(tmp_path.glob("*"))
        assert len(output_files) > 0

    def test_generate_with_formats(self, runner, test_image, tmp_path):
        """Test generate command with specific format selection."""
        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--output-dir",
                str(tmp_path),
                "--format",
                "json",
                "--format",
                "css",
            ],
        )

        assert result.exit_code == 0
        assert "Generated color scheme" in result.stdout

        # Verify only requested formats were created
        json_file = tmp_path / "colors.json"
        css_file = tmp_path / "colors.css"

        assert json_file.exists()
        assert css_file.exists()

        # Verify other formats were not created
        sh_file = tmp_path / "colors.sh"
        assert not sh_file.exists()

    def test_generate_invalid_image(self, runner, tmp_path):
        """Test generate command with invalid image path."""
        invalid_path = tmp_path / "nonexistent.png"

        result = runner.invoke(
            app,
            ["generate", str(invalid_path), "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout or "error" in result.stdout.lower()
