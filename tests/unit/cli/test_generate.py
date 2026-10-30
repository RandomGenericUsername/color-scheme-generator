from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from color_scheme_generator.adapters.local_processor import LocalProcessor
from color_scheme_generator.domain.enums import Backend, ColorFormat, RuntimeMode
from color_scheme_generator.domain.exceptions import (
    InvalidImageError,
    TemplateNotFoundError,
)
from color_scheme_generator.domain.models import (
    AppSettings,
    ContainerSettings,
    GenerationSettings,
    OutputSettings,
    RuntimeSettings,
)
from color_scheme_generator.factory import CliDependencies
from tests.conftest import FakeProcessor, _scheme


def _invoke(
    runner: CliRunner,
    deps: CliDependencies,
    args: list[str],
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("color_scheme_generator.cli.main.build_deps", lambda: deps)
    from color_scheme_generator.cli.main import app

    return runner.invoke(app, args)


class TestCliGenerate:
    def test_generate_smoke_writes_dummy_files(
        self,
        runner: CliRunner,
        cli_deps_with_processor: CliDependencies,
        fake_processor: FakeProcessor,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        output_dir = tmp_path / "out"
        result = _invoke(
            runner,
            cli_deps_with_processor,
            [
                "generate",
                "/tmp/test.png",
                "--backend",
                "custom",
                "--param",
                "saturation=0.5",
                "--format",
                "json",
                "-o",
                str(output_dir),
            ],
            monkeypatch,
        )
        assert result.exit_code == 0, f"stderr={result.stderr}"
        assert len(fake_processor.calls) == 1
        call = fake_processor.calls[0]
        assert call["command"] == "process_generate"
        request = call["request"]
        config = request.config
        assert config.backend is Backend.CUSTOM
        assert config.params.get("saturation") == "0.5"
        assert config.output_dir == output_dir
        assert (output_dir / "colors.json").exists()
        assert (output_dir / "colors.json").read_text() == "dummy"

    def test_generate_outputs_valid_json(
        self,
        runner: CliRunner,
        cli_deps_with_processor: CliDependencies,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        result = _invoke(
            runner,
            cli_deps_with_processor,
            [
                "generate",
                "/tmp/test.png",
                "-f",
                "json",
                "-o",
                str(tmp_path),
            ],
            monkeypatch,
        )
        assert result.exit_code == 0, f"stderr={result.stderr}"
        payload = json.loads(result.stdout)
        assert payload["success"] is True
        assert payload["backend"] == "custom"
        assert payload["color_scheme"]["colors"] is not None

    def test_generate_with_adw_css_format_requests_and_writes_adw_output(
        self,
        runner: CliRunner,
        cli_deps_with_processor: CliDependencies,
        fake_processor: FakeProcessor,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        output_dir = tmp_path / "out"
        result = _invoke(
            runner,
            cli_deps_with_processor,
            [
                "generate",
                "/tmp/test.png",
                "--backend",
                "custom",
                "-f",
                "adw.css",
                "-o",
                str(output_dir),
            ],
            monkeypatch,
        )
        assert result.exit_code == 0, f"stderr={result.stderr}"
        assert fake_processor.calls[0]["request"].config.formats == (ColorFormat.ADW_CSS,)
        assert (output_dir / "colors.adw.css").exists()

    def test_generate_invalid_image_exits_with_code_1(
        self,
        runner: CliRunner,
        cli_deps_with_processor: CliDependencies,
        fake_processor: FakeProcessor,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        fake_processor.error = InvalidImageError(
            image_path=Path("/nonexistent.jpg"), reason="file not found"
        )
        result = _invoke(
            runner,
            cli_deps_with_processor,
            ["generate", "/nonexistent.jpg", "-o", str(tmp_path)],
            monkeypatch,
        )
        assert result.exit_code == 1
        error_payload = json.loads(result.stderr)
        assert error_payload["kind"] == "InvalidImageError"
        assert "nonexistent.jpg" in error_payload["message"]

    def test_help_output_shows_expected_usage(self, runner: CliRunner) -> None:
        from color_scheme_generator.cli.main import app

        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout
        assert "image_path" in result.stdout or "IMAGE_PATH" in result.stdout

    def test_help_shows_new_flags(self, runner: CliRunner) -> None:
        from color_scheme_generator.cli.main import app

        result = runner.invoke(app, ["generate", "--help"])
        assert "--backend" in result.stdout
        assert "--param" in result.stdout
        assert "--format" in result.stdout or "-f" in result.stdout
        assert "--output-dir" in result.stdout or "-o" in result.stdout

    def test_build_deps_returns_proper_cli_dependencies(self) -> None:
        from color_scheme_generator.cli.main import build_deps
        from color_scheme_generator.factory import CliDependencies

        deps = build_deps()
        assert isinstance(deps, CliDependencies)
        assert deps.backend_registry is not None
        assert deps.output_adapter is None
        # processor is now built lazily (not a deps-level concern)
        assert deps.template_dir_resolver is not None
        assert deps.template_renderer is not None


class TestCliPackage:
    def test_cli_package_importable(self) -> None:
        from color_scheme_generator.cli import main  # noqa: F401

        assert main is not None

    def test_console_scripts_entry_point(self) -> None:
        from color_scheme_generator.cli.main import app

        assert app is not None
        assert callable(app)


class TestCliGenerateFailsClosed:
    def _settings(self, output_dir: Path) -> AppSettings:
        return AppSettings(
            output=OutputSettings(
                directory=output_dir,
                default_formats=(),
                overwrite=True,
            ),
            generation=GenerationSettings(backend=Backend.CUSTOM, default_params={}),
            runtime=RuntimeSettings(mode=RuntimeMode.LOCAL),
            container=ContainerSettings(engine="podman"),
        )

    def test_local_render_failure_exits_1_and_names_template(
        self,
        runner: CliRunner,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        generator = MagicMock()
        generator.is_available.return_value = True
        generator.generate.return_value = _scheme()
        renderer = MagicMock()

        def render(template_name: str, scheme: object, output_path: Path) -> None:
            if template_name == "colors.yaml.j2":
                raise TemplateNotFoundError(template_name, (tmp_path / "templates",))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("rendered", encoding="utf-8")

        renderer.render.side_effect = render
        processor = LocalProcessor(
            {Backend.CUSTOM: generator}, template_renderer=renderer
        )
        config_resolver = MagicMock()
        config_resolver.resolve.return_value = self._settings(tmp_path / "out")
        deps = CliDependencies(
            backend_registry={},
            config_resolver=config_resolver,
            processor=processor,
        )

        result = _invoke(
            runner,
            deps,
            [
                "generate",
                str(tmp_path / "wallpaper.png"),
                "--backend",
                "custom",
                "--format",
                "json",
                "--format",
                "yaml",
                "-o",
                str(tmp_path / "out"),
            ],
            monkeypatch,
        )

        assert result.exit_code == 1, (
            f"expected failure\nstdout={result.stdout}\nstderr={result.stderr}"
        )
        payload = json.loads(result.stdout)
        assert payload["success"] is False
        assert any("colors.yaml.j2" in error for error in payload["errors"])
        assert any("yaml" in error for error in payload["errors"])
        assert payload["stderr"]
        assert (tmp_path / "out" / "colors.json").is_file()
