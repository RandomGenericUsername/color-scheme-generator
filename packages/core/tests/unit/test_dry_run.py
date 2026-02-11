"""Unit tests for dry-run reporters."""

from pathlib import Path

import pytest
from color_scheme_settings.models import ConfigSource, ResolvedConfig, ResolvedValue

from color_scheme.cli.dry_run import (
    DryRunReporter,
    GenerateDryRunReporter,
    ShowDryRunReporter,
)


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
        "output.directory",
        ResolvedValue(
            value="/tmp/output",
            source=ConfigSource.PACKAGE_DEFAULT,
            source_detail="Package default",
            overrides=[],
        ),
    )
    config.set(
        "output.formats",
        ResolvedValue(
            value=["json", "yaml"],
            source=ConfigSource.CLI,
            source_detail="--format",
            overrides=[(ConfigSource.PACKAGE_DEFAULT, ["json"])],
        ),
    )
    return config


class TestDryRunReporter:
    """Test base DryRunReporter class."""

    def test_reporter_initialization(self, sample_resolved_config):
        """Test that reporter initializes correctly."""
        reporter = DryRunReporter(
            command="test command",
            resolved_config=sample_resolved_config,
            context={"test": "value"},
        )

        assert reporter.command == "test command"
        assert reporter.config == sample_resolved_config
        assert reporter.context == {"test": "value"}

    def test_reporter_with_empty_context(self, sample_resolved_config):
        """Test reporter works with no context."""
        reporter = DryRunReporter(
            command="test command",
            resolved_config=sample_resolved_config,
        )

        assert reporter.context == {}

    def test_run_method_executes(self, sample_resolved_config, capsys):
        """Test that run() method executes without errors."""
        reporter = DryRunReporter(
            command="test command",
            resolved_config=sample_resolved_config,
        )

        reporter.run()

        captured = capsys.readouterr()
        assert "DRY-RUN" in captured.out
        assert "test command" in captured.out


class TestGenerateDryRunReporter:
    """Test GenerateDryRunReporter class."""

    def test_reporter_initialization(self, sample_resolved_config):
        """Test that generate reporter initializes correctly."""
        reporter = GenerateDryRunReporter(
            command="color-scheme-core generate",
            resolved_config=sample_resolved_config,
            context={"image_path": Path("/test/image.jpg")},
        )

        assert reporter.command == "color-scheme-core generate"
        assert reporter.context["image_path"] == Path("/test/image.jpg")

    def test_run_shows_execution_plan(self, sample_resolved_config, capsys):
        """Test that run() displays execution plan."""
        reporter = GenerateDryRunReporter(
            command="color-scheme-core generate",
            resolved_config=sample_resolved_config,
            context={"image_path": Path("/test/image.jpg")},
        )

        reporter.run()

        captured = capsys.readouterr()
        assert "DRY-RUN" in captured.out
        assert "Execution Plan" in captured.out
        assert "Step 1: Load Image" in captured.out
        assert "Step 2: Extract Colors" in captured.out

    def test_shows_input_file_status(self, sample_resolved_config, capsys, tmp_path):
        """Test that input file status is displayed."""
        # Create a real file
        test_image = tmp_path / "test.jpg"
        test_image.write_text("fake image")

        reporter = GenerateDryRunReporter(
            command="color-scheme-core generate",
            resolved_config=sample_resolved_config,
            context={"image_path": test_image},
        )

        reporter.run()

        captured = capsys.readouterr()
        assert "Input Files" in captured.out
        assert "Found" in captured.out


class TestShowDryRunReporter:
    """Test ShowDryRunReporter class."""

    def test_reporter_initialization(self, sample_resolved_config):
        """Test that show reporter initializes correctly."""
        reporter = ShowDryRunReporter(
            command="color-scheme-core show",
            resolved_config=sample_resolved_config,
            context={"image_path": Path("/test/image.jpg")},
        )

        assert reporter.command == "color-scheme-core show"
        assert reporter.context["image_path"] == Path("/test/image.jpg")

    def test_run_shows_execution_plan(self, sample_resolved_config, capsys):
        """Test that run() displays execution plan."""
        reporter = ShowDryRunReporter(
            command="color-scheme-core show",
            resolved_config=sample_resolved_config,
            context={"image_path": Path("/test/image.jpg")},
        )

        reporter.run()

        captured = capsys.readouterr()
        assert "DRY-RUN" in captured.out
        assert "Execution Plan" in captured.out
        assert "Step 1: Load Image" in captured.out
        assert "Step 2: Extract Colors" in captured.out
        assert "Step 4: Display in Terminal" in captured.out
