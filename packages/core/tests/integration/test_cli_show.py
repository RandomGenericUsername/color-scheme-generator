"""Integration tests for CLI show command."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from color_scheme.cli.main import app


class TestShowCommand:
    """Integration tests for the show command."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    def test_show_with_defaults(self, runner, test_image):
        """Test show command with default options (auto-detect backend)."""
        result = runner.invoke(
            app,
            ["show", str(test_image)],
        )

        assert result.exit_code == 0
        # Should display backend info
        assert "backend" in result.stdout.lower() or "Backend" in result.stdout
        # Should display color information
        assert "background" in result.stdout.lower() or "Background" in result.stdout
        assert "#" in result.stdout  # Hex color codes should be present

    def test_show_with_backend(self, runner, test_image):
        """Test show command with specific backend selection."""
        result = runner.invoke(
            app,
            ["show", str(test_image), "--backend", "custom"],
        )

        assert result.exit_code == 0
        assert "custom" in result.stdout.lower()
        # Should display color information
        assert "background" in result.stdout.lower() or "Background" in result.stdout
        assert "#" in result.stdout  # Hex color codes should be present

    def test_show_invalid_image(self, runner, tmp_path):
        """Test show command with invalid image path."""
        invalid_path = tmp_path / "nonexistent.png"

        result = runner.invoke(
            app,
            ["show", str(invalid_path)],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout or "error" in result.stdout.lower()
