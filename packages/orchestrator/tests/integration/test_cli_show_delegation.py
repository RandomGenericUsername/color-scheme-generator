"""Integration tests for show command delegation."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from color_scheme_orchestrator.cli.main import app

runner = CliRunner()


class TestShowDelegation:
    """Tests for delegating show command to core."""

    @patch("subprocess.run")
    def test_show_command_exists(self, mock_subprocess):
        """Test that show command is registered and can be invoked."""
        # Mock subprocess for any backend execution
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Verify show command is in help
        result = runner.invoke(app, ["--help"])
        assert "show" in result.output

    @patch("subprocess.run")
    def test_show_requires_image_path(self, mock_subprocess):
        """Test that show command requires image path argument."""
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["show"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output or "required" in result.output.lower()
