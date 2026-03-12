"""Integration tests for CLI generate command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from color_scheme.cli.main import app
from color_scheme.core.types import Color, ColorScheme


class TestCLIGenerate:
    """Integration tests for the generate command."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    def test_generate_with_defaults(self, runner, test_image, tmp_path):
        """Test generate command with default options."""
        # Use tmp_path as output directory
        # Use --backend custom to avoid requiring ImageMagick in CI
        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--output-dir",
                str(tmp_path),
                "--backend",
                "custom",
            ],
        )

        assert result.exit_code == 0
        assert "Generated color scheme" in result.stdout

        # Verify some output files were created
        output_files = list(tmp_path.glob("*"))
        assert len(output_files) > 0

    def test_generate_with_backend(self, runner, test_image, tmp_path):
        """Test generate command with specific backend selection."""
        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--output-dir",
                str(tmp_path),
                "--backend",
                "custom",
            ],
        )

        assert result.exit_code == 0
        assert "custom" in result.stdout.lower()
        assert "Generated color scheme" in result.stdout

        # Verify output files were created
        output_files = list(tmp_path.glob("*"))
        assert len(output_files) > 0

    def test_generate_with_formats(self, runner, test_image, tmp_path):
        """Test generate command with specific format selection."""
        # Use --backend custom to avoid requiring ImageMagick in CI
        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--output-dir",
                str(tmp_path),
                "--backend",
                "custom",
                "--format",
                "json",
                "--format",
                "css",
            ],
        )

        assert result.exit_code == 0
        assert "Generated color scheme" in result.stdout

        # Verify only requested formats were created
        json_file = tmp_path / "colors.json"
        css_file = tmp_path / "colors.css"

        assert json_file.exists()
        assert css_file.exists()

        # Verify other formats were not created
        sh_file = tmp_path / "colors.sh"
        assert not sh_file.exists()

    def test_generate_invalid_image(self, runner, tmp_path):
        """Test generate command with invalid image path."""
        invalid_path = tmp_path / "nonexistent.png"

        result = runner.invoke(
            app,
            ["generate", str(invalid_path), "--output-dir", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout or "error" in result.stdout.lower()

    def test_generate_no_summary_suppresses_table(self, runner, test_image, tmp_path):
        """Test that --no-summary suppresses the success message and file table."""
        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--output-dir",
                str(tmp_path),
                "--backend",
                "custom",
                "--no-summary",
            ],
        )

        assert result.exit_code == 0
        assert "Generated color scheme" not in result.stdout
        assert "Generated Files" not in result.stdout


class TestGenerateSaturationAppliedOnce:
    """CRIT-04: CLI must not re-apply saturation after the backend applied it."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_color_scheme(self):
        mock_color = MagicMock(spec=Color)
        mock_color.adjust_saturation.return_value = mock_color
        mock_color.hex = "#aabbcc"
        mock_scheme = MagicMock(spec=ColorScheme)
        mock_scheme.background = mock_color
        mock_scheme.foreground = mock_color
        mock_scheme.cursor = mock_color
        mock_scheme.colors = [mock_color] * 16
        mock_scheme.output_files = {}
        return mock_scheme, mock_color

    def test_cli_does_not_call_adjust_saturation_after_backend(
        self, runner, mock_color_scheme, tmp_path
    ):
        """The CLI must not call adjust_saturation — the backend already did."""
        mock_scheme, mock_color = mock_color_scheme
        test_image = Path(__file__).parent.parent / "fixtures" / "test_image.png"

        with (
            patch("color_scheme.cli.main.BackendFactory") as mock_factory_cls,
            patch("color_scheme.cli.main.OutputManager"),
        ):
            mock_backend = MagicMock()
            mock_backend.generate.return_value = mock_scheme
            mock_factory_cls.return_value.create.return_value = mock_backend

            runner.invoke(
                app,
                [
                    "generate",
                    str(test_image),
                    "--output-dir",
                    str(tmp_path),
                    "--backend",
                    "custom",
                    "--saturation",
                    "1.5",
                ],
            )

        assert mock_color.adjust_saturation.call_count == 0, (
            f"CLI called adjust_saturation {mock_color.adjust_saturation.call_count} "
            f"time(s) — the backend already applies saturation in generate()"
        )
