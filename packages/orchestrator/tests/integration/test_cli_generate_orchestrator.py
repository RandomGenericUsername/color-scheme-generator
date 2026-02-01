"""Integration tests for orchestrator CLI generate command."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from color_scheme_orchestrator.cli.main import app

runner = CliRunner()


class TestOrchestratorGenerate:
    """Tests for orchestrator generate command."""

    @patch("color_scheme_orchestrator.cli.main.ContainerManager.run_generate")
    def test_generate_calls_container_manager(self, mock_run):
        """Test that generate command uses container manager."""
        # Create a temporary test image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            result = runner.invoke(
                app, ["generate", str(test_image), "--backend", "pywal"]
            )

            # Should call container manager
            assert mock_run.called
            assert result.exit_code == 0
        finally:
            test_image.unlink()

    @patch("color_scheme_orchestrator.cli.main.ContainerManager.run_generate")
    def test_generate_passes_cli_args_to_container(self, mock_run):
        """Test CLI arguments are passed to container."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            result = runner.invoke(
                app,
                [
                    "generate",
                    str(test_image),
                    "--saturation",
                    "1.5",
                    "--format",
                    "json",
                    "--format",
                    "css",
                ],
            )

            # Verify CLI args were passed
            call_kwargs = mock_run.call_args[1]
            cli_args = call_kwargs.get("cli_args", [])

            assert "--saturation" in cli_args
            assert "1.5" in cli_args
            assert "--format" in cli_args
            assert result.exit_code == 0
        finally:
            test_image.unlink()

    def test_generate_requires_image_path(self):
        """Test that generate command requires image path."""
        result = runner.invoke(app, ["generate"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "required" in result.output.lower()
