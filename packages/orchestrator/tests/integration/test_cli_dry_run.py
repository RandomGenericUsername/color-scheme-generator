"""Integration tests for orchestrator CLI dry-run functionality."""

import pytest
from typer.testing import CliRunner

from color_scheme_orchestrator.cli.main import app


class TestInstallDryRun:
    """Integration tests for install --dry-run."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_install_dry_run_flag(self, runner):
        """Test that --dry-run shows build plan."""
        result = runner.invoke(
            app,
            ["install", "custom", "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
        assert "Build Plan" in result.stdout

    def test_install_dry_run_short_flag(self, runner):
        """Test that -n works as short form."""
        result = runner.invoke(
            app,
            ["install", "custom", "-n"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout


class TestUninstallDryRun:
    """Integration tests for uninstall --dry-run."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_uninstall_dry_run_flag(self, runner):
        """Test that --dry-run shows removal plan."""
        result = runner.invoke(
            app,
            ["uninstall", "custom", "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
        assert "Removal Plan" in result.stdout

    def test_uninstall_dry_run_short_flag(self, runner):
        """Test that -n works as short form."""
        result = runner.invoke(
            app,
            ["uninstall", "custom", "-n"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout

    def test_uninstall_dry_run_bypasses_confirmation(self, runner):
        """Test that dry-run doesn't ask for confirmation."""
        result = runner.invoke(
            app,
            ["uninstall", "custom", "--dry-run"],
            input="n\n",  # Would say no if asked
        )

        # Should exit successfully without asking
        assert result.exit_code == 0
        # Should not show confirmation prompt
        assert "Are you sure" not in result.stdout
