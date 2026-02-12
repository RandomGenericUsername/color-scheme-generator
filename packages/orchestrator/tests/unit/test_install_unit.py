"""Unit tests for install command with mocked subprocess calls."""

from unittest.mock import MagicMock, Mock, patch

from typer.testing import CliRunner

from color_scheme_orchestrator.cli.main import app

runner = CliRunner()


class TestInstallEngineValidation:
    """Tests for engine validation logic (lines 91-102)."""

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_default_engine_docker(self, mock_run, mock_path):
        """Verify docker is used by default when engine not specified (line 94)."""
        # Setup mocks
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal"])

        # Verify: docker was first arg in subprocess.run call
        assert result.exit_code == 0
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_custom_engine_docker(self, mock_run, mock_path):
        """Verify explicit --engine docker is accepted (line 96)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal", "--engine", "docker"])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_custom_engine_podman(self, mock_run, mock_path):
        """Verify explicit --engine podman is accepted (line 96)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal", "--engine", "podman"])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "podman"

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    def test_install_invalid_engine_rejection(self, mock_path):
        """Verify rejection of invalid engine (lines 97-102)."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal", "--engine", "invalid"])

        assert result.exit_code == 1
        assert "Invalid engine" in result.stdout
        assert "Must be 'docker' or 'podman'" in result.stdout

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    def test_install_invalid_engine_case_insensitive(self, mock_path):
        """Verify engine names are case-insensitive (line 96)."""
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            result = runner.invoke(app, ["install", "pywal", "--engine", "DOCKER"])

            # Should be lowercased and accepted
            assert result.exit_code == 0


class TestInstallBackendSelection:
    """Tests for backend selection logic (lines 105-108)."""

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_single_backend(self, mock_run, mock_path):
        """Verify single backend installation (lines 107-108)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal"])

        assert result.exit_code == 0
        # Should have called subprocess once (one backend)
        assert mock_run.call_count >= 1
        # Verify the image name is for pywal
        call_args = mock_run.call_args_list[0][0][0]
        assert "color-scheme-pywal:latest" in call_args

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_all_backends_when_none_specified(self, mock_run, mock_path):
        """Verify all backends installed when backend arg is None (line 106)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install"])

        assert result.exit_code == 0
        # Should have called subprocess for each backend (at least 3)
        assert mock_run.call_count >= 3


class TestInstallDockerfileValidation:
    """Tests for Dockerfile existence checks (lines 136-142)."""

    # NOTE: Docker directory and Dockerfile validation are tested via integration tests
    # because Path mocking is complex across the function call chain.
    # These validations are critical but integration tests provide better coverage.


class TestInstallBuildCommandConstruction:
    """Tests for docker build command construction (lines 147-155)."""

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_build_command_structure(self, mock_run, mock_path):
        """Verify docker build command has correct args (lines 147-155)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal"])

        assert result.exit_code == 0
        # Check command structure: docker build -f <dockerfile> -t <image> <context>
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"
        assert call_args[1] == "build"
        assert "-f" in call_args
        assert "-t" in call_args
        assert "color-scheme-pywal:latest" in call_args


class TestInstallReturnCodeHandling:
    """Tests for build success/failure handling (lines 176-190)."""

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_build_success_returncode_zero(self, mock_run, mock_path):
        """Verify success message on returncode=0 (lines 176-181)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal"])

        assert result.exit_code == 0
        assert "Built successfully" in result.stdout

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_build_failure_nonzero_returncode(self, mock_run, mock_path):
        """Verify failure message on returncode!=0 (lines 182-190)."""
        mock_run.return_value = Mock(
            returncode=1, stdout="", stderr="Build failed: syntax error"
        )
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal"])

        assert result.exit_code == 1
        assert "Build failed" in result.stdout


class TestInstallSubprocessErrorHandling:
    """Tests for SubprocessError handling (lines 192-195)."""

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_subprocess_error(self, mock_run, mock_path):
        """Verify SubprocessError is caught and reported (lines 192-195)."""
        import subprocess

        mock_run.side_effect = subprocess.SubprocessError("Process error")
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal"])

        assert result.exit_code == 1
        assert "Process error" in result.stdout or "failed" in result.stdout.lower()


class TestInstallSummaryOutput:
    """Tests for summary output (lines 199-209)."""

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_all_succeed_summary(self, mock_run, mock_path):
        """Verify success summary when all backends succeed (line 209)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install", "pywal"])

        assert result.exit_code == 0
        assert "Build Summary" in result.stdout
        assert "Success:" in result.stdout
        assert "All backend images built successfully!" in result.stdout

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    @patch("subprocess.run")
    def test_install_partial_failure_summary(self, mock_run, mock_path):
        """Verify summary when some backends fail."""
        # First call succeeds, second fails
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),
            Mock(returncode=1, stdout="", stderr="Build failed"),
            Mock(returncode=0, stdout="", stderr=""),
        ]
        mock_docker_dir = MagicMock()
        mock_docker_dir.exists.return_value = True
        mock_docker_dir.__truediv__ = MagicMock(return_value=mock_docker_dir)

        mock_path_instance = MagicMock()
        mock_path_instance.parent.parent.parent.parent.parent.parent.parent = (
            MagicMock()
        )
        proj_root = mock_path_instance.parent.parent.parent.parent.parent.parent.parent
        proj_root.__truediv__ = MagicMock(return_value=mock_docker_dir)
        mock_path.return_value = mock_path_instance

        result = runner.invoke(app, ["install"])

        assert result.exit_code == 1
        assert "Build Summary" in result.stdout
        assert "Failed:" in result.stdout


class TestInstallExceptionHandling:
    """Tests for unexpected exception handling (lines 211-215)."""

    @patch("color_scheme_orchestrator.cli.commands.install.Path")
    def test_install_unexpected_exception(self, mock_path):
        """Verify unexpected exceptions are caught (lines 213-215)."""
        mock_path.side_effect = RuntimeError("Unexpected error")

        result = runner.invoke(app, ["install", "pywal"])

        assert result.exit_code == 1
        assert "Unexpected error" in result.stdout or "error" in result.stdout.lower()
