"""Unit tests for uninstall command with mocked subprocess calls."""

from unittest.mock import Mock, patch

from color_scheme_orchestrator.cli.main import app
from typer.testing import CliRunner

runner = CliRunner()


class TestUninstallEngineValidation:
    """Tests for engine validation logic (lines 88-98)."""

    @patch("subprocess.run")
    def test_uninstall_default_engine_docker(self, mock_run):
        """Verify docker is used by default when engine not specified (line 90)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["uninstall", "pywal", "--yes"])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"

    @patch("subprocess.run")
    def test_uninstall_custom_engine_docker(self, mock_run):
        """Verify explicit --engine docker is accepted (line 92)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(
            app, ["uninstall", "pywal", "--engine", "docker", "--yes"]
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"

    @patch("subprocess.run")
    def test_uninstall_custom_engine_podman(self, mock_run):
        """Verify explicit --engine podman is accepted (line 92)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(
            app, ["uninstall", "pywal", "--engine", "podman", "--yes"]
        )

        assert result.exit_code == 0
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "podman"

    def test_uninstall_invalid_engine_rejection(self):
        """Verify rejection of invalid engine (lines 93-98)."""
        result = runner.invoke(
            app, ["uninstall", "pywal", "--engine", "invalid", "--yes"]
        )

        assert result.exit_code == 1
        assert "Invalid engine" in result.stdout
        assert "Must be 'docker' or 'podman'" in result.stdout

    @patch("subprocess.run")
    def test_uninstall_invalid_engine_case_insensitive(self, mock_run):
        """Verify engine names are case-insensitive (line 92)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(
            app, ["uninstall", "pywal", "--engine", "DOCKER", "--yes"]
        )

        # Should be lowercased and accepted
        assert result.exit_code == 0


class TestUninstallBackendSelection:
    """Tests for backend selection logic (lines 101-107)."""

    @patch("subprocess.run")
    def test_uninstall_single_backend(self, mock_run):
        """Verify single backend uninstall (lines 103-104)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["uninstall", "pywal", "--yes"])

        assert result.exit_code == 0
        # Should have called subprocess once (one backend)
        assert mock_run.call_count >= 1
        # Verify the image name is for pywal
        call_args = mock_run.call_args_list[0][0][0]
        assert "color-scheme-pywal:latest" in call_args

    @patch("subprocess.run")
    def test_uninstall_all_backends_when_none_specified(self, mock_run):
        """Verify all backends uninstalled when backend arg is None (line 102)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["uninstall", "--yes"])

        assert result.exit_code == 0
        # Should have called subprocess for each backend (at least 3)
        assert mock_run.call_count >= 3

    @patch("subprocess.run")
    def test_uninstall_image_names_correct(self, mock_run):
        """Verify image names are constructed correctly (lines 106-107)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["uninstall", "wallust", "--yes"])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0][0]
        assert "color-scheme-wallust:latest" in call_args
        assert call_args[1] == "rmi"


class TestUninstallConfirmationPrompt:
    """Tests for confirmation prompt handling (lines 110-121)."""

    @patch("subprocess.run")
    def test_uninstall_warning_message_displayed(self, mock_run):
        """Verify warning message is displayed (lines 111-115)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["uninstall", "pywal"], input="y\n")

        assert result.exit_code == 0
        assert "Warning:" in result.stdout
        assert "This will remove the following images:" in result.stdout

    @patch("subprocess.run")
    def test_uninstall_confirmation_yes(self, mock_run):
        """Verify user can confirm (line 118)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["uninstall", "pywal"], input="y\n")

        assert result.exit_code == 0
        assert mock_run.called

    @patch("subprocess.run")
    def test_uninstall_confirmation_no(self, mock_run):
        """Verify cancellation when user declines (lines 119-121)."""
        result = runner.invoke(app, ["uninstall", "pywal"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout
        # Should not have called subprocess
        assert not mock_run.called

    @patch("subprocess.run")
    def test_uninstall_yes_flag_skips_confirmation(self, mock_run):
        """Verify --yes flag bypasses prompt (line 110)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["uninstall", "pywal", "--yes"])

        assert result.exit_code == 0
        assert "Warning:" not in result.stdout  # No prompt shown
        assert mock_run.called


class TestUninstallImageRemoval:
    """Tests for image removal execution (lines 129-165)."""

    @patch("subprocess.run")
    def test_uninstall_remove_success(self, mock_run):
        """Verify success message on returncode=0 (lines 140-144)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["uninstall", "pywal", "--yes"])

        assert result.exit_code == 0
        assert (
            "Removed" in result.stdout
            or "removed successfully" in result.stdout.lower()
        )

    @patch("subprocess.run")
    def test_uninstall_image_not_found_treated_as_success(self, mock_run):
        """Verify 'image not found' errors are treated as success (lines 147-155)."""
        # Simulate docker rmi returning error for non-existent image
        error_msg = (
            "Error response from daemon: No such image: color-scheme-pywal:latest"
        )
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr=error_msg,
        )

        result = runner.invoke(app, ["uninstall", "pywal", "--yes"])

        assert result.exit_code == 0
        assert (
            "(already removed)" in result.stdout or "not found" in result.stdout.lower()
        )

    @patch("subprocess.run")
    def test_uninstall_remove_failure_other_error(self, mock_run):
        """Verify other failures are reported (lines 156-161)."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: Image is in use",
        )

        result = runner.invoke(app, ["uninstall", "pywal", "--yes"])

        assert result.exit_code == 1
        assert "Failed" in result.stdout or "failed" in result.stdout.lower()


class TestUninstallSubprocessErrorHandling:
    """Tests for SubprocessError handling (lines 163-165)."""

    @patch("subprocess.run")
    def test_uninstall_subprocess_error(self, mock_run):
        """Verify SubprocessError is caught and reported (lines 163-165)."""
        import subprocess

        mock_run.side_effect = subprocess.SubprocessError("Process error")

        result = runner.invoke(app, ["uninstall", "pywal", "--yes"])

        assert result.exit_code == 1
        assert "Process error" in result.stdout or "error" in result.stdout.lower()


class TestUninstallSummaryOutput:
    """Tests for summary output (lines 167-175)."""

    @patch("subprocess.run")
    def test_uninstall_all_succeed_message(self, mock_run):
        """Verify success message when all images removed (line 175)."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        result = runner.invoke(app, ["uninstall", "pywal", "--yes"])

        assert result.exit_code == 0
        assert "Removal Summary" in result.stdout
        assert "All images removed successfully!" in result.stdout

    @patch("subprocess.run")
    def test_uninstall_partial_failure_summary(self, mock_run):
        """Verify summary when some removals fail."""
        # First call succeeds, second fails
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),
            Mock(
                returncode=1,
                stdout="",
                stderr="Error: Image is in use",
            ),
            Mock(returncode=0, stdout="", stderr=""),
        ]

        result = runner.invoke(app, ["uninstall", "--yes"])

        assert result.exit_code == 1
        assert "Removal Summary" in result.stdout
        assert "Failed:" in result.stdout


class TestUninstallExceptionHandling:
    """Tests for unexpected exception handling (lines 179-181)."""

    def test_uninstall_unexpected_exception(self):
        """Verify unexpected exceptions are caught (lines 179-181)."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = RuntimeError("Unexpected error")

            result = runner.invoke(app, ["uninstall", "pywal", "--yes"])

        assert result.exit_code == 1
        assert "Unexpected error" in result.stdout or "error" in result.stdout.lower()
