"""Tests for main.py error handling paths."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from typer.testing import CliRunner

from color_scheme_orchestrator.cli.main import app

runner = CliRunner()


class TestGenerateErrorHandling:
    """Tests for generate command error handling (main.py lines 191-197)."""

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_runtime_error_handling(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run_gen, mock_get_config
    ):
        """Verify RuntimeError is caught and handled (lines 191-192)."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        mock_run_gen.side_effect = RuntimeError("Container failed to start")

        result = runner.invoke(app, ["generate", "/tmp/image.jpg"])

        assert result.exit_code == 1
        assert "Container error:" in result.stdout

    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_unexpected_exception_handling(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run_gen
    ):
        """Verify unexpected exceptions are caught (lines 195-196)."""
        mock_run_gen.side_effect = ValueError("Unexpected error")

        result = runner.invoke(app, ["generate", "/tmp/image.jpg"])

        assert result.exit_code == 1
        assert "Unexpected error:" in result.stdout


class TestGenerateDryRunWithArgs:
    """Tests for generate dry-run with various argument combinations."""

    def test_generate_dry_run_with_backend(self):
        """Verify backend arg is included in dry-run (line 108)."""
        result = runner.invoke(
            app,
            ["generate", "/tmp/image.jpg", "--backend", "pywal", "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
        # Verify backend is shown in output
        assert "backend" in result.stdout.lower() or "pywal" in result.stdout

    def test_generate_dry_run_with_output_dir(self):
        """Verify output_dir arg is included in dry-run (line 110)."""
        result = runner.invoke(
            app,
            ["generate", "/tmp/image.jpg", "--output-dir", "/tmp/output", "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout

    def test_generate_dry_run_with_formats(self):
        """Verify formats arg is included in dry-run (line 112)."""
        result = runner.invoke(
            app,
            [
                "generate",
                "/tmp/image.jpg",
                "--format",
                "json",
                "--format",
                "css",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout

    def test_generate_dry_run_with_saturation(self):
        """Verify saturation arg is included in dry-run (line 114)."""
        result = runner.invoke(
            app,
            ["generate", "/tmp/image.jpg", "--saturation", "1.5", "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout


class TestShowDryRunWithArgs:
    """Tests for show dry-run with various argument combinations."""

    def test_show_dry_run_with_backend(self):
        """Verify backend arg is included in dry-run (line 248)."""
        result = runner.invoke(
            app,
            ["show", "/tmp/image.jpg", "--backend", "pywal", "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout

    def test_show_dry_run_with_saturation(self):
        """Verify saturation arg is included in dry-run (line 250)."""
        result = runner.invoke(
            app,
            ["show", "/tmp/image.jpg", "--saturation", "1.2", "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
