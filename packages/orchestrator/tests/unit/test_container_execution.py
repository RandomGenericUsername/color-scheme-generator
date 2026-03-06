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

        # Docker command should include the image and pass CLI args to the container
        # The "color-scheme" command is handled by the container entrypoint
        assert "docker" in call_args
        assert "run" in call_args
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


class TestContainerShow:
    """Tests for run_show container execution."""

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_builds_docker_command(self, mock_run, mock_sys):
        """Test that run_show constructs correct docker show command."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="docker"),
        )
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"
        assert "run" in call_args
        assert "--rm" in call_args
        assert "color-scheme-custom:latest" in call_args
        assert "show" in call_args
        assert "/input/image.png" in call_args

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_no_output_mount(self, mock_run, mock_sys):
        """Test that run_show does not add an /output volume mount."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        call_args = mock_run.call_args[0][0]
        v_mounts = [
            call_args[i + 1]
            for i, arg in enumerate(call_args)
            if arg == "-v"
        ]
        assert not any("/output" in m for m in v_mounts)

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_no_templates_mount(self, mock_run, mock_sys):
        """Test that run_show does not add a /templates volume mount."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        call_args = mock_run.call_args[0][0]
        v_mounts = [
            call_args[i + 1]
            for i, arg in enumerate(call_args)
            if arg == "-v"
        ]
        assert not any("/templates" in m for m in v_mounts)

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_adds_tty_flag_when_interactive(self, mock_run, mock_sys):
        """Test that -t is added to docker command when stdout is a TTY."""
        mock_sys.stdout.isatty.return_value = True
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        call_args = mock_run.call_args[0][0]
        assert "-t" in call_args

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_no_tty_flag_when_non_interactive(self, mock_run, mock_sys):
        """Test that -t is absent when stdout is not a TTY."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        call_args = mock_run.call_args[0][0]
        assert "-t" not in call_args

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_raises_on_failure(self, mock_run, mock_sys):
        """Test that non-zero exit code raises RuntimeError."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=1)

        with pytest.raises(RuntimeError, match="Container execution failed"):
            manager.run_show(
                backend=Backend.PYWAL,
                image_path=Path("/tmp/test.png"),
            )
