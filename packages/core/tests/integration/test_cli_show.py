"""Integration tests for CLI show command."""

from pathlib import Path
from unittest.mock import PropertyMock, patch

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
        """Test show command with default options."""
        # Use --backend custom to avoid requiring ImageMagick in CI
        result = runner.invoke(
            app,
            ["show", str(test_image), "--backend", "custom"],
        )

        assert result.exit_code == 0
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

    def test_show_non_tty_outputs_bullet_list(self, runner, test_image):
        """In non-TTY context (CliRunner default), show outputs plain bullet list."""
        result = runner.invoke(
            app,
            ["show", str(test_image), "--backend", "custom"],
        )

        assert result.exit_code == 0
        # Bullet list format: "key: #RRGGBB"
        assert "background:" in result.stdout
        assert "foreground:" in result.stdout
        assert "cursor:" in result.stdout
        assert "color0:" in result.stdout
        # Should NOT contain Rich table markup characters
        assert "┃" not in result.stdout
        assert "━" not in result.stdout
        # No preamble process-log lines in non-TTY
        assert "Extracting colors from" not in result.stdout
        assert "Using backend" not in result.stdout
        assert "Auto-detected backend" not in result.stdout

    def test_show_tty_outputs_rich_tables(self, runner, test_image):
        """In TTY context, show outputs Rich tables with full preamble."""
        from rich.console import Console

        with patch.object(
            Console, "is_terminal", new_callable=PropertyMock, return_value=True
        ):
            result = runner.invoke(
                app,
                ["show", str(test_image), "--backend", "custom"],
            )

        assert result.exit_code == 0
        # Rich table has these headers
        assert "Background" in result.stdout or "Special Colors" in result.stdout

    def test_show_invalid_image(self, runner, tmp_path):
        """Test show command with invalid image path."""
        invalid_path = tmp_path / "nonexistent.png"

        result = runner.invoke(
            app,
            ["show", str(invalid_path)],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout or "error" in result.stdout.lower()
