"""Integration tests for CLI dry-run functionality."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from color_scheme.cli.main import app


class TestGenerateDryRun:
    """Integration tests for generate --dry-run."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    def test_dry_run_flag_shows_plan(self, runner, test_image):
        """Test that --dry-run shows execution plan."""
        result = runner.invoke(
            app,
            ["generate", str(test_image), "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
        assert "Execution Plan" in result.stdout
        assert "color-scheme-core generate" in result.stdout

    def test_dry_run_short_flag(self, runner, test_image):
        """Test that -n works as short form."""
        result = runner.invoke(
            app,
            ["generate", str(test_image), "-n"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout

    def test_dry_run_creates_no_files(self, runner, test_image, tmp_path):
        """Test that dry-run doesn't create output files."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--output-dir",
                str(output_dir),
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        # Directory should be empty
        assert len(list(output_dir.glob("*"))) == 0

    def test_dry_run_respects_cli_args(self, runner, test_image):
        """Test that dry-run shows CLI arguments in plan."""
        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--backend",
                "custom",
                "--format",
                "json",
                "--saturation",
                "1.5",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "custom" in result.stdout
        assert "json" in result.stdout


class TestShowDryRun:
    """Integration tests for show --dry-run."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    def test_dry_run_flag_shows_plan(self, runner, test_image):
        """Test that --dry-run shows execution plan."""
        result = runner.invoke(
            app,
            ["show", str(test_image), "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
        assert "Execution Plan" in result.stdout
        assert "color-scheme-core show" in result.stdout

    def test_dry_run_short_flag(self, runner, test_image):
        """Test that -n works as short form."""
        result = runner.invoke(
            app,
            ["show", str(test_image), "-n"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout

    def test_dry_run_doesnt_show_colors(self, runner, test_image):
        """Test that dry-run doesn't display actual colors."""
        result_dry = runner.invoke(
            app,
            ["show", str(test_image), "--dry-run"],
        )

        assert result_dry.exit_code == 0
        # Dry-run should show execution plan, not actual colors
        assert "DRY-RUN" in result_dry.stdout
        assert "Execution Plan" in result_dry.stdout
        assert "Terminal Colors (ANSI)" not in result_dry.stdout
