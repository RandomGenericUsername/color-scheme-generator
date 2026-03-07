"""Tests for container execution."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from color_scheme.config.config import AppConfig
from color_scheme.config.enums import Backend

from color_scheme_orchestrator.config.settings import ContainerSettings
from color_scheme_orchestrator.config.unified import UnifiedConfig
from color_scheme_orchestrator.container.manager import ContainerManager


def _make_mock_proc(returncode=0, stdout_lines=None, stderr_lines=None):
    """Build a mock subprocess.Popen result for PIPE-mode tests."""
    proc = Mock()
    proc.stdout = iter(stdout_lines or [])
    proc.stderr = iter(stderr_lines or [])
    proc.returncode = returncode
    proc.wait.return_value = None
    proc.poll.return_value = returncode
    return proc


class TestContainerExecution:
    """Tests for executing commands in containers."""

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.Popen")
    def test_run_generate_builds_docker_command(self, mock_popen, mock_sys):
        """Test that run_generate constructs correct docker command."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="docker"),
        )
        manager = ContainerManager(config)
        mock_popen.return_value = _make_mock_proc()

        manager.run_generate(
            backend=Backend.PYWAL,
            image_path=Path("/tmp/test.png"),
            output_dir=Path("/tmp/output"),
        )

        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert call_args[0] == "docker"
        assert "run" in call_args
        assert "--rm" in call_args
        assert "color-scheme-pywal:latest" in call_args

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.Popen")
    def test_run_generate_includes_volume_mounts(self, mock_popen, mock_sys):
        """Test that volume mounts are included in docker command."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_popen.return_value = _make_mock_proc()

        manager.run_generate(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
            output_dir=Path("/tmp/output"),
        )

        call_args = mock_popen.call_args[0][0]
        v_indices = [i for i, arg in enumerate(call_args) if arg == "-v"]
        assert len(v_indices) >= 3  # image, output, templates

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.Popen")
    def test_run_generate_passes_cli_args(self, mock_popen, mock_sys):
        """Test that CLI arguments are passed to container."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_popen.return_value = _make_mock_proc()

        manager.run_generate(
            backend=Backend.PYWAL,
            image_path=Path("/tmp/test.png"),
            output_dir=Path("/tmp/output"),
            cli_args=["--saturation", "1.5", "--format", "json"],
        )

        call_args = mock_popen.call_args[0][0]
        assert "generate" in call_args
        assert "/input/image.png" in call_args
        assert "--saturation" in call_args
        assert "1.5" in call_args

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.Popen")
    def test_run_generate_raises_on_failure_with_stderr(self, mock_popen, mock_sys):
        """Test that non-zero exit code raises RuntimeError including stderr."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_popen.return_value = _make_mock_proc(
            returncode=1, stderr_lines=["Error: backend failed\n"]
        )

        with pytest.raises(RuntimeError, match="Container execution failed"):
            manager.run_generate(
                backend=Backend.PYWAL,
                image_path=Path("/tmp/test.png"),
                output_dir=Path("/tmp/output"),
            )

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.Popen")
    def test_run_generate_adds_tty_flag_when_interactive(self, mock_popen, mock_sys):
        """Test that -t is added to run_generate command when stdout is a TTY."""
        mock_sys.stdout.isatty.return_value = True
        mock_sys.stdout.buffer = Mock()

        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)

        with (
            patch("color_scheme_orchestrator.container.manager.pty") as mock_pty,
            patch("color_scheme_orchestrator.container.manager.select") as mock_select,
            patch("color_scheme_orchestrator.container.manager.os") as mock_os,
        ):
            mock_pty.openpty.return_value = (10, 11)
            mock_select.select.return_value = ([], [], [])
            mock_os.close = Mock()
            mock_os.read.return_value = b""
            mock_os.getuid.return_value = 1000
            mock_os.getgid.return_value = 1000
            mock_os.environ.get.return_value = None

            proc = Mock()
            proc.poll.return_value = 0
            proc.wait.return_value = None
            proc.returncode = 0
            mock_popen.return_value = proc

            manager.run_generate(
                backend=Backend.CUSTOM,
                image_path=Path("/tmp/test.png"),
                output_dir=Path("/tmp/output"),
            )

        call_args = mock_popen.call_args[0][0]
        assert "-t" in call_args

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.Popen")
    def test_run_generate_no_tty_flag_when_non_interactive(self, mock_popen, mock_sys):
        """Test that -t is absent from run_generate when stdout is not a TTY."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_popen.return_value = _make_mock_proc()

        manager.run_generate(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
            output_dir=Path("/tmp/output"),
        )

        call_args = mock_popen.call_args[0][0]
        assert "-t" not in call_args

    @patch("color_scheme_orchestrator.container.manager.os")
    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.Popen")
    def test_run_generate_forwards_color_env_vars_when_interactive(
        self, mock_popen, mock_sys, mock_os
    ):
        """Test that TERM, COLORTERM, FORCE_COLOR are forwarded when interactive."""
        mock_sys.stdout.isatty.return_value = True
        mock_sys.stdout.buffer = Mock()
        mock_os.environ.get.side_effect = lambda k: {
            "TERM": "xterm-256color",
            "COLORTERM": "truecolor",
        }.get(k)
        mock_os.getuid.return_value = 1000
        mock_os.getgid.return_value = 1000
        mock_os.close = Mock()
        mock_os.read.return_value = b""

        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)

        with (
            patch("color_scheme_orchestrator.container.manager.pty") as mock_pty,
            patch("color_scheme_orchestrator.container.manager.select") as mock_select,
        ):
            mock_pty.openpty.return_value = (10, 11)
            mock_select.select.return_value = ([], [], [])

            proc = Mock()
            proc.poll.return_value = 0
            proc.wait.return_value = None
            proc.returncode = 0
            mock_popen.return_value = proc

            manager.run_generate(
                backend=Backend.CUSTOM,
                image_path=Path("/tmp/test.png"),
                output_dir=Path("/tmp/output"),
            )

        call_args = mock_popen.call_args[0][0]
        e_pairs = [call_args[i + 1] for i, arg in enumerate(call_args) if arg == "-e"]
        assert "TERM=xterm-256color" in e_pairs
        assert "COLORTERM=truecolor" in e_pairs
        assert "FORCE_COLOR=1" in e_pairs

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.Popen")
    def test_run_generate_pty_raises_on_failure(self, mock_popen, mock_sys):
        """Test that PTY mode raises RuntimeError on non-zero exit code."""
        mock_sys.stdout.isatty.return_value = True
        mock_sys.stdout.buffer = Mock()

        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)

        with (
            patch("color_scheme_orchestrator.container.manager.pty") as mock_pty,
            patch("color_scheme_orchestrator.container.manager.select") as mock_select,
            patch("color_scheme_orchestrator.container.manager.os") as mock_os,
        ):
            mock_pty.openpty.return_value = (10, 11)
            mock_select.select.return_value = ([], [], [])
            mock_os.close = Mock()
            mock_os.read.return_value = b""
            mock_os.getuid.return_value = 1000
            mock_os.getgid.return_value = 1000
            mock_os.environ.get.return_value = None

            proc = Mock()
            proc.poll.return_value = 1
            proc.wait.return_value = None
            proc.returncode = 1
            mock_popen.return_value = proc

            with pytest.raises(RuntimeError, match="Container execution failed"):
                manager.run_generate(
                    backend=Backend.PYWAL,
                    image_path=Path("/tmp/test.png"),
                    output_dir=Path("/tmp/output"),
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

    @patch("color_scheme_orchestrator.container.manager.os")
    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_forwards_color_env_vars_when_interactive(
        self, mock_run, mock_sys, mock_os
    ):
        """Test that TERM, COLORTERM, and FORCE_COLOR are forwarded when interactive."""
        mock_sys.stdout.isatty.return_value = True
        mock_os.environ.get.side_effect = lambda k: {
            "TERM": "xterm-256color",
            "COLORTERM": "truecolor",
        }.get(k)
        mock_os.getuid.return_value = 1000
        mock_os.getgid.return_value = 1000

        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        call_args = mock_run.call_args[0][0]
        e_pairs = [
            call_args[i + 1]
            for i, arg in enumerate(call_args)
            if arg == "-e"
        ]
        assert "TERM=xterm-256color" in e_pairs
        assert "COLORTERM=truecolor" in e_pairs
        assert "FORCE_COLOR=1" in e_pairs

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_no_color_env_vars_when_non_interactive(self, mock_run, mock_sys):
        """Test that color env vars are not forwarded when non-interactive."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        call_args = mock_run.call_args[0][0]
        assert "-e" not in call_args

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


class TestStreamingMethods:
    """Tests for internal streaming helper methods."""

    def _manager(self):
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        return ContainerManager(config)

    @patch("subprocess.Popen")
    def test_pipe_mode_streams_stdout_lines(self, mock_popen):
        """Test that PIPE mode prints each stdout line from the container."""
        manager = self._manager()
        proc = Mock()
        proc.stdout = iter(["line1\n", "line2\n"])
        proc.stderr = iter([])
        proc.returncode = 0
        proc.wait.return_value = None
        mock_popen.return_value = proc

        with patch("builtins.print") as mock_print:
            result = manager._run_streaming_pipe(["echo", "test"])

        assert result.returncode == 0
        assert result.stderr == ""
        assert mock_print.call_count == 2

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("color_scheme_orchestrator.container.manager.select")
    @patch("color_scheme_orchestrator.container.manager.pty")
    @patch("color_scheme_orchestrator.container.manager.os")
    @patch("subprocess.Popen")
    def test_pty_mode_streams_chunk_to_stdout(
        self, mock_popen, mock_os, mock_pty, mock_select, mock_sys
    ):
        """Test that PTY mode writes data chunks to sys.stdout.buffer."""
        mock_pty.openpty.return_value = (10, 11)
        mock_os.close = Mock()
        mock_os.getuid.return_value = 1000
        mock_os.getgid.return_value = 1000
        mock_sys.stdout.buffer = Mock()
        mock_sys.stdout.flush = Mock()

        # First iteration: data available; second: nothing, proc done
        mock_select.select.side_effect = [([10], [], []), ([], [], [])]
        mock_os.read.side_effect = [b"hello output", b""]

        proc = Mock()
        proc.poll.return_value = 0
        proc.wait.return_value = None
        proc.returncode = 0
        mock_popen.return_value = proc

        manager = self._manager()
        result = manager._run_streaming_pty(["docker", "run", "-t", "img"])

        mock_sys.stdout.buffer.write.assert_called_with(b"hello output")
        assert result.returncode == 0
        assert result.stderr == ""

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("color_scheme_orchestrator.container.manager.select")
    @patch("color_scheme_orchestrator.container.manager.pty")
    @patch("color_scheme_orchestrator.container.manager.os")
    @patch("subprocess.Popen")
    def test_pty_mode_final_read_flushes_remaining_output(
        self, mock_popen, mock_os, mock_pty, mock_select, mock_sys
    ):
        """Test that PTY mode does a final read after process exits."""
        mock_pty.openpty.return_value = (10, 11)
        mock_os.close = Mock()
        mock_os.getuid.return_value = 1000
        mock_os.getgid.return_value = 1000
        mock_sys.stdout.buffer = Mock()
        mock_sys.stdout.flush = Mock()

        # select immediately returns nothing, proc is already done
        mock_select.select.return_value = ([], [], [])
        # Final read returns remaining data
        mock_os.read.return_value = b"trailing output"

        proc = Mock()
        proc.poll.return_value = 0
        proc.wait.return_value = None
        proc.returncode = 0
        mock_popen.return_value = proc

        manager = self._manager()
        manager._run_streaming_pty(["docker", "run", "-t", "img"])

        mock_sys.stdout.buffer.write.assert_called_with(b"trailing output")

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("color_scheme_orchestrator.container.manager.select")
    @patch("color_scheme_orchestrator.container.manager.pty")
    @patch("color_scheme_orchestrator.container.manager.os")
    @patch("subprocess.Popen")
    def test_pty_mode_final_read_oserror_is_handled(
        self, mock_popen, mock_os, mock_pty, mock_select, mock_sys
    ):
        """Test that PTY mode handles OSError on the final read gracefully."""
        mock_pty.openpty.return_value = (10, 11)
        mock_os.close = Mock()
        mock_os.getuid.return_value = 1000
        mock_os.getgid.return_value = 1000
        mock_sys.stdout.buffer = Mock()

        mock_select.select.return_value = ([], [], [])
        mock_os.read.side_effect = OSError("EIO")

        proc = Mock()
        proc.poll.return_value = 0
        proc.wait.return_value = None
        proc.returncode = 0
        mock_popen.return_value = proc

        manager = self._manager()
        result = manager._run_streaming_pty(["docker", "run", "-t", "img"])

        assert result.returncode == 0

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("color_scheme_orchestrator.container.manager.select")
    @patch("color_scheme_orchestrator.container.manager.pty")
    @patch("color_scheme_orchestrator.container.manager.os")
    @patch("subprocess.Popen")
    def test_pty_mode_select_oserror_breaks_loop(
        self, mock_popen, mock_os, mock_pty, mock_select, mock_sys
    ):
        """Test that an OSError from select() causes the PTY loop to exit cleanly."""
        mock_pty.openpty.return_value = (10, 11)
        mock_os.close = Mock()
        mock_os.getuid.return_value = 1000
        mock_os.getgid.return_value = 1000
        mock_sys.stdout.buffer = Mock()

        mock_select.select.side_effect = OSError("bad fd")

        proc = Mock()
        proc.wait.return_value = None
        proc.returncode = 0
        mock_popen.return_value = proc

        manager = self._manager()
        result = manager._run_streaming_pty(["docker", "run", "-t", "img"])

        assert result.returncode == 0
