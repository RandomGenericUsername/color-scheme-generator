"""Tests for install/uninstall dry-run paths."""

from typer.testing import CliRunner

from color_scheme_orchestrator.cli.main import app

runner = CliRunner()


class TestInstallDryRunPaths:
    """Tests for install dry-run initialization (install.py line 70)."""

    def test_install_dry_run_with_no_backend(self):
        """Verify dry-run works when installing all backends (line 70)."""
        result = runner.invoke(app, ["install", "--dry-run"])

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
        assert "Build Plan" in result.stdout

    def test_install_dry_run_with_engine_flag(self):
        """Verify dry-run respects engine flag (line 70)."""
        result = runner.invoke(
            app, ["install", "custom", "--engine", "podman", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
        assert "podman" in result.stdout.lower()

    def test_install_dry_run_with_specific_backend(self):
        """Verify dry-run with specific backend."""
        result = runner.invoke(app, ["install", "wallust", "--dry-run"])

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout


class TestUninstallDryRunPaths:
    """Tests for uninstall dry-run initialization (uninstall.py line 67)."""

    def test_uninstall_dry_run_with_no_backend(self):
        """Verify dry-run works when removing all backends (line 67)."""
        result = runner.invoke(app, ["uninstall", "--dry-run"])

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
        assert "Removal Plan" in result.stdout

    def test_uninstall_dry_run_with_engine_flag(self):
        """Verify dry-run respects engine flag (line 67)."""
        result = runner.invoke(
            app, ["uninstall", "custom", "--engine", "podman", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
        assert "podman" in result.stdout.lower()

    def test_uninstall_dry_run_with_specific_backend(self):
        """Verify dry-run with specific backend."""
        result = runner.invoke(app, ["uninstall", "pywal", "--dry-run"])

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
