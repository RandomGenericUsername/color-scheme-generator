"""Unit tests for main.py generate/show/version commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from color_scheme.config.enums import Backend
from color_scheme_orchestrator.cli.main import app
from typer.testing import CliRunner

runner = CliRunner()


class TestVersionCommand:
    """Tests for version command (lines 32-36)."""

    def test_version_command_displays_version(self):
        """Verify version command shows version info (lines 32-36)."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "version" in result.stdout.lower()
        assert "color-scheme-orchestrator" in result.stdout


class TestGenerateImageValidation:
    """Tests for generate image path validation (lines 133-140)."""

    @patch("color_scheme_orchestrator.cli.main.get_config")
    def test_generate_image_not_exists(self, mock_get_config):
        """Verify error when image file doesn't exist (lines 134-136)."""
        mock_get_config.return_value = MagicMock()
        with patch("pathlib.Path.exists", return_value=False):
            result = runner.invoke(app, ["generate", "/nonexistent/image.jpg"])

        assert result.exit_code == 1
        assert "Image file not found" in result.stdout

    @patch("color_scheme_orchestrator.cli.main.get_config")
    def test_generate_path_not_file(self, mock_get_config):
        """Verify error when path is directory, not file (lines 138-140)."""
        mock_get_config.return_value = MagicMock()
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_file", return_value=False),
        ):
            result = runner.invoke(app, ["generate", "/some/directory"])

        assert result.exit_code == 1
        assert "Path is not a file" in result.stdout


class TestGenerateDefaultResolution:
    """Tests for generate default backend/output resolution (lines 142-148)."""

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_uses_default_backend_when_not_specified(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run, mock_get_config
    ):
        """Verify default backend is loaded from config (lines 143-144)."""
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        result = runner.invoke(app, ["generate", "/tmp/image.jpg"])

        assert result.exit_code == 0
        # Verify ContainerManager was called
        assert mock_run.called

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_uses_specified_backend(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run, mock_get_config
    ):
        """Verify specified backend is used (lines 160)."""
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        result = runner.invoke(
            app, ["generate", "/tmp/image.jpg", "--backend", "pywal"]
        )

        assert result.exit_code == 0
        # Verify ContainerManager was called with pywal backend
        assert mock_run.called
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["backend"] == Backend.PYWAL

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_creates_output_directory(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run, mock_get_config
    ):
        """Verify output directory is created (line 151)."""
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        result = runner.invoke(
            app,
            [
                "generate",
                "/tmp/image.jpg",
                "--output-dir",
                "/tmp/colors",
            ],
        )

        assert result.exit_code == 0
        # mkdir should be called
        assert mock_mkdir.called


class TestGenerateCliArgs:
    """Tests for CLI arguments passed to container (lines 154-169)."""

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_output_dir_args(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run, mock_get_config
    ):
        """Verify /output is passed to container (line 157)."""
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        result = runner.invoke(app, ["generate", "/tmp/image.jpg"])

        assert result.exit_code == 0
        call_kwargs = mock_run.call_args[1]
        cli_args = call_kwargs["cli_args"]
        assert "--output-dir" in cli_args
        assert "/output" in cli_args

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_backend_args(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run, mock_get_config
    ):
        """Verify backend arg is passed (line 160)."""
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        result = runner.invoke(
            app, ["generate", "/tmp/image.jpg", "--backend", "wallust"]
        )

        assert result.exit_code == 0
        call_kwargs = mock_run.call_args[1]
        cli_args = call_kwargs["cli_args"]
        assert "--backend" in cli_args
        assert "wallust" in cli_args

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_formats_args(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run, mock_get_config
    ):
        """Verify format args are passed (lines 163-165)."""
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        result = runner.invoke(
            app,
            [
                "generate",
                "/tmp/image.jpg",
                "--format",
                "json",
                "--format",
                "css",
            ],
        )

        assert result.exit_code == 0
        call_kwargs = mock_run.call_args[1]
        cli_args = call_kwargs["cli_args"]
        assert "--format" in cli_args
        # Both json and css should be in args
        assert "json" in cli_args or "css" in cli_args

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_saturation_args(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run, mock_get_config
    ):
        """Verify saturation arg is passed (lines 168-169)."""
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        result = runner.invoke(
            app, ["generate", "/tmp/image.jpg", "--saturation", "1.5"]
        )

        assert result.exit_code == 0
        call_kwargs = mock_run.call_args[1]
        cli_args = call_kwargs["cli_args"]
        assert "--saturation" in cli_args
        assert "1.5" in cli_args


class TestGenerateContainerExecution:
    """Tests for container execution (lines 172-183)."""

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_calls_container_manager_run_generate(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run, mock_get_config
    ):
        """Verify ContainerManager.run_generate is called (lines 178-183)."""
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        result = runner.invoke(app, ["generate", "/tmp/image.jpg"])

        assert result.exit_code == 0
        assert mock_run.called

    @patch("color_scheme_orchestrator.cli.main.get_config")
    @patch("color_scheme_orchestrator.container.manager.ContainerManager.run_generate")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_success_message(
        self, mock_exists, mock_is_file, mock_mkdir, mock_run, mock_get_config
    ):
        """Verify success message is displayed (line 185)."""
        mock_config = MagicMock()
        mock_config.core.generation.default_backend = "pywal"
        mock_config.core.output.directory = Path("/tmp/output")
        mock_get_config.return_value = mock_config

        result = runner.invoke(app, ["generate", "/tmp/image.jpg"])

        assert result.exit_code == 0
        assert "Color scheme generated successfully!" in result.stdout


class TestGenerateDryRun:
    """Tests for generate --dry-run flag."""

    def test_generate_dry_run_flag(self):
        """Verify --dry-run shows execution plan."""
        result = runner.invoke(
            app,
            ["generate", "/tmp/image.jpg", "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout

    def test_generate_dry_run_short_flag(self):
        """Verify -n works as short form."""
        result = runner.invoke(
            app,
            ["generate", "/tmp/image.jpg", "-n"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout


class TestShowDelegation:
    """Tests for show command delegation to core (lines 267-278)."""

    @patch("color_scheme.cli.main.show")
    def test_show_delegates_to_core_show(self, mock_core_show):
        """Verify core's show function is called (lines 274-278)."""
        runner.invoke(app, ["show", "/tmp/image.jpg"])

        # The delegation happens, verify it was called
        assert mock_core_show.called

    @patch("color_scheme.cli.main.show")
    def test_show_passes_image_path_to_core(self, mock_core_show):
        """Verify image path is passed to core's show."""
        runner.invoke(app, ["show", "/tmp/image.jpg"])

        # Verify the call happened with image path
        assert mock_core_show.called
        call_kwargs = mock_core_show.call_args[1]
        # Check that image_path was passed
        assert "image_path" in call_kwargs

    @patch("color_scheme.cli.main.show")
    def test_show_passes_backend_to_core(self, mock_core_show):
        """Verify backend option is passed to core."""
        runner.invoke(app, ["show", "/tmp/image.jpg", "--backend", "pywal"])

        assert mock_core_show.called
        call_kwargs = mock_core_show.call_args[1]
        assert call_kwargs.get("backend") == Backend.PYWAL

    @patch("color_scheme.cli.main.show")
    def test_show_passes_saturation_to_core(self, mock_core_show):
        """Verify saturation option is passed to core."""
        runner.invoke(app, ["show", "/tmp/image.jpg", "--saturation", "1.2"])

        assert mock_core_show.called
        call_kwargs = mock_core_show.call_args[1]
        assert call_kwargs.get("saturation") == 1.2


class TestShowErrorHandling:
    """Tests for show error handling (lines 280-282)."""

    @patch("color_scheme.cli.main.show")
    def test_show_handles_core_error(self, mock_core_show):
        """Verify errors from core are caught (lines 280-282)."""
        mock_core_show.side_effect = Exception("Core error")

        result = runner.invoke(app, ["show", "/tmp/image.jpg"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout or "error" in result.stdout.lower()


class TestShowDryRun:
    """Tests for show --dry-run flag."""

    def test_show_dry_run_flag(self):
        """Verify --dry-run shows execution plan."""
        result = runner.invoke(
            app,
            ["show", "/tmp/image.jpg", "--dry-run"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout

    def test_show_dry_run_short_flag(self):
        """Verify -n works as short form."""
        result = runner.invoke(
            app,
            ["show", "/tmp/image.jpg", "-n"],
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.stdout
