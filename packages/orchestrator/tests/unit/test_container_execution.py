"""Tests for container execution."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend

from color_scheme_orchestrator.config.settings import ContainerSettings
from color_scheme_orchestrator.config.unified import UnifiedConfig
from color_scheme_orchestrator.container.manager import ContainerManager


class TestContainerExecution:
    """Tests for executing commands in containers."""

    @patch("subprocess.run")
    def test_run_generate_builds_docker_command(self, mock_run):
        """Test that run_generate constructs correct docker command."""
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="docker"),
        )
        manager = ContainerManager(config)

        image_path = Path("/tmp/test.png")
        output_dir = Path("/tmp/output")
        backend = Backend.PYWAL

        # Mock successful execution
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        manager.run_generate(
            backend=backend,
            image_path=image_path,
            output_dir=output_dir,
        )

        # Verify docker was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]

        assert call_args[0] == "docker"
        assert "run" in call_args
        assert "--rm" in call_args
        assert "color-scheme-pywal:latest" in call_args

    @patch("subprocess.run")
    def test_run_generate_includes_volume_mounts(self, mock_run):
        """Test that volume mounts are included in docker command."""
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)

        image_path = Path("/tmp/test.png")
        output_dir = Path("/tmp/output")
        backend = Backend.CUSTOM

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        manager.run_generate(
            backend=backend,
            image_path=image_path,
            output_dir=output_dir,
        )

        call_args = mock_run.call_args[0][0]

        # Check for -v flags
        v_indices = [i for i, arg in enumerate(call_args) if arg == "-v"]
        assert len(v_indices) >= 3  # At least image, output, templates

    @patch("subprocess.run")
    def test_run_generate_passes_cli_args(self, mock_run):
        """Test that CLI arguments are passed to container."""
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)

        image_path = Path("/tmp/test.png")
        output_dir = Path("/tmp/output")
        backend = Backend.PYWAL
        cli_args = ["--saturation", "1.5", "--format", "json"]

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        manager.run_generate(
            backend=backend,
            image_path=image_path,
            output_dir=output_dir,
            cli_args=cli_args,
        )

        call_args = mock_run.call_args[0][0]

        # Container command should include: color-scheme generate /input/image.png ...
        assert "color-scheme" in call_args
        assert "generate" in call_args
        assert "/input/image.png" in call_args
        assert "--saturation" in call_args
        assert "1.5" in call_args

    @patch("subprocess.run")
    def test_run_generate_raises_on_failure(self, mock_run):
        """Test that non-zero exit code raises exception."""
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)

        image_path = Path("/tmp/test.png")
        output_dir = Path("/tmp/output")
        backend = Backend.PYWAL

        # Mock failed execution
        mock_run.return_value = Mock(
            returncode=1, stdout="", stderr="Error: backend failed"
        )

        with pytest.raises(RuntimeError, match="Container execution failed"):
            manager.run_generate(
                backend=backend,
                image_path=image_path,
                output_dir=output_dir,
            )
