"""Unit tests for orchestrator dry-run reporters."""

from pathlib import Path

import pytest
from color_scheme_orchestrator.cli.dry_run import (
    ContainerGenerateDryRunReporter,
    InstallDryRunReporter,
    UninstallDryRunReporter,
)
from color_scheme_settings.models import ConfigSource, ResolvedConfig, ResolvedValue


@pytest.fixture
def sample_resolved_config():
    """Create a sample resolved configuration."""
    config = ResolvedConfig()
    config.set(
        "generation.default_backend",
        ResolvedValue(
            value="custom",
            source=ConfigSource.CLI,
            source_detail="--backend",
            overrides=[],
        ),
    )
    config.set(
        "orchestrator.engine",
        ResolvedValue(
            value="docker",
            source=ConfigSource.PACKAGE_DEFAULT,
            source_detail="Package default",
            overrides=[],
        ),
    )
    config.set(
        "orchestrator.image_prefix",
        ResolvedValue(
            value="color-scheme",
            source=ConfigSource.PACKAGE_DEFAULT,
            source_detail="Package default",
            overrides=[],
        ),
    )
    return config


class TestContainerGenerateDryRunReporter:
    """Test ContainerGenerateDryRunReporter class."""

    def test_reporter_shows_container_info(self, sample_resolved_config, capsys):
        """Test that container information is displayed."""
        reporter = ContainerGenerateDryRunReporter(
            command="color-scheme generate",
            resolved_config=sample_resolved_config,
            context={"image_path": Path("/test/image.jpg")},
        )

        reporter.run()

        captured = capsys.readouterr()
        assert "Container Configuration" in captured.out
        assert "docker" in captured.out


class TestInstallDryRunReporter:
    """Test InstallDryRunReporter class."""

    def test_reporter_shows_build_plan(self, sample_resolved_config, capsys):
        """Test that build plan is displayed."""
        reporter = InstallDryRunReporter(
            command="color-scheme install",
            resolved_config=sample_resolved_config,
            context={"backend": "custom"},
        )

        reporter.run()

        captured = capsys.readouterr()
        assert "Build Plan" in captured.out
        assert "Building:" in captured.out
        assert "custom" in captured.out

    def test_reporter_shows_all_backends(self, sample_resolved_config, capsys):
        """Test that all backends are shown when backend is 'all'."""
        reporter = InstallDryRunReporter(
            command="color-scheme install",
            resolved_config=sample_resolved_config,
            context={"backend": "all"},
        )

        reporter.run()

        captured = capsys.readouterr()
        assert "pywal" in captured.out
        assert "wallust" in captured.out
        assert "custom" in captured.out


class TestUninstallDryRunReporter:
    """Test UninstallDryRunReporter class."""

    def test_reporter_shows_removal_plan(self, sample_resolved_config, capsys):
        """Test that removal plan is displayed."""
        reporter = UninstallDryRunReporter(
            command="color-scheme uninstall",
            resolved_config=sample_resolved_config,
            context={"backend": "custom"},
        )

        reporter.run()

        captured = capsys.readouterr()
        assert "Removal Plan" in captured.out
        assert "Removing:" in captured.out
        assert "custom" in captured.out
