"""Integration tests for show command delegation to container."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from color_scheme_orchestrator.cli.main import app

runner = CliRunner()


class TestShowDelegation:
    """Tests for delegating show command to container."""

    def test_show_command_exists(self):
        """Test that show command is registered."""
        result = runner.invoke(app, ["--help"])
        assert "show" in result.output

    def test_show_requires_image_path(self):
        """Test that show command requires image path argument."""
        result = runner.invoke(app, ["show"])
        assert result.exit_code != 0
        assert (
            "Missing argument" in result.output or "required" in result.output.lower()
        )

    @patch("color_scheme_orchestrator.cli.main.ContainerManager.run_show")
    def test_show_calls_container_manager(self, mock_run_show):
        """Test that show routes to ContainerManager.run_show, not a host subprocess."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            result = runner.invoke(
                app, ["show", str(test_image), "--backend", "custom"]
            )

            assert mock_run_show.called
            assert result.exit_code == 0
        finally:
            test_image.unlink()

    @patch("color_scheme_orchestrator.cli.main.ContainerManager.run_show")
    def test_show_does_not_call_host_subprocess_for_core(self, mock_run_show):
        """Test that show no longer calls color-scheme-core on the host."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            with patch("subprocess.run") as mock_subprocess:
                runner.invoke(
                    app, ["show", str(test_image), "--backend", "custom"]
                )
                for call in mock_subprocess.call_args_list:
                    args = call[0][0] if call[0] else []
                    assert "color-scheme-core" not in args
        finally:
            test_image.unlink()

    @patch("color_scheme_orchestrator.cli.main.ContainerManager.run_show")
    def test_show_passes_saturation_to_container(self, mock_run_show):
        """Test that --saturation is forwarded as a CLI arg to the container."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            runner.invoke(
                app,
                ["show", str(test_image), "--backend", "custom", "--saturation", "1.5"],
            )

            assert mock_run_show.called
            call_kwargs = mock_run_show.call_args[1]
            cli_args = call_kwargs.get("cli_args", [])
            assert "--saturation" in cli_args
            assert "1.5" in cli_args
        finally:
            test_image.unlink()
