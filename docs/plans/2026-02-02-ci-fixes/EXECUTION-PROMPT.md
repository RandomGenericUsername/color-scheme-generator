# Execution Prompt

Copy everything below the line and paste to your AI tool.

---

Working directory: `/home/inumaki/Development/color-scheme/packages/core`

Execute ALL changes below. Each change shows the file, the EXACT text to find, and the EXACT replacement.

---

## CHANGE 1: src/color_scheme/output/manager.py

FIND:
```python
        # Setup Jinja2 environment with StrictUndefined
        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
```

REPLACE WITH:
```python
        # Setup Jinja2 environment with StrictUndefined
        # NOTE: Autoescape disabled - we generate config files (CSS/JSON/YAML), not HTML.
        # Enabling autoescape would corrupt hex colors: #FF0000 → &#35;FF0000
        self.template_env = Environment(  # nosec B701
            loader=FileSystemLoader(str(template_dir)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
```

---

## CHANGE 2: src/color_scheme/backends/pywal.py (import)

FIND:
```python
import json
import logging
import shutil
import subprocess
from pathlib import Path
```

REPLACE WITH:
```python
import json
import logging
import shutil
import subprocess  # nosec B404 - Required for external tool invocation
from pathlib import Path
```

---

## CHANGE 3: src/color_scheme/backends/pywal.py (subprocess call)

FIND:
```python
            logger.debug("Running pywal command: %s", " ".join(cmd))
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
```

REPLACE WITH:
```python
            logger.debug("Running pywal command: %s", " ".join(cmd))
            # Security: command hardcoded, image_path validated, shell=False, timeout set
            subprocess.run(  # nosec B603
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
```

---

## CHANGE 4: src/color_scheme/backends/wallust.py (import)

FIND:
```python
import json
import logging
import shutil
import subprocess
from pathlib import Path
```

REPLACE WITH:
```python
import json
import logging
import shutil
import subprocess  # nosec B404 - Required for external tool invocation
from pathlib import Path
```

---

## CHANGE 5: src/color_scheme/backends/wallust.py (subprocess call)

FIND:
```python
            logger.debug("Running wallust command: %s", " ".join(cmd))
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
```

REPLACE WITH:
```python
            logger.debug("Running wallust command: %s", " ".join(cmd))
            # Security: command hardcoded, image_path validated, shell=False, timeout set
            subprocess.run(  # nosec B603
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
```

---

## CHANGE 6: src/color_scheme/cli/main.py

FIND:
```python
        # Write output files
        output_manager = OutputManager(config.core)
        assert generator_config.output_dir is not None
        assert generator_config.formats is not None
        console.print(
```

REPLACE WITH:
```python
        # Write output files
        output_manager = OutputManager(config.core)
        if generator_config.output_dir is None:
            raise ValueError("output_dir must be configured for generate command")
        if generator_config.formats is None:
            raise ValueError("formats must be configured for generate command")
        console.print(
```

---

## CHANGE 7: src/color_scheme/core/base.py

FIND:
```python
            ColorExtractionError: If color extraction fails
            BackendNotAvailableError: If backend is not available
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
```

REPLACE WITH:
```python
            ColorExtractionError: If color extraction fails
            BackendNotAvailableError: If backend is not available
        """
        pass  # pragma: no cover

    @abstractmethod
    def is_available(self) -> bool:
```

ALSO FIND:
```python
        Returns:
            True if backend is available, False otherwise
        """
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
```

REPLACE WITH:
```python
        Returns:
            True if backend is available, False otherwise
        """
        pass  # pragma: no cover

    @property
    @abstractmethod
    def backend_name(self) -> str:
```

ALSO FIND:
```python
        Returns:
            Backend name (e.g., "pywal", "wallust", "custom")
        """
        pass

    def ensure_available(self) -> None:
```

REPLACE WITH:
```python
        Returns:
            Backend name (e.g., "pywal", "wallust", "custom")
        """
        pass  # pragma: no cover

    def ensure_available(self) -> None:
```

---

## CHANGE 8: CREATE NEW FILE tests/unit/test_cli_main.py

Create this file with this EXACT content:

```python
"""Unit tests for CLI main module."""

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image
from typer.testing import CliRunner

from color_scheme.cli.main import app
from color_scheme.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    ColorSchemeError,
    InvalidImageError,
    OutputWriteError,
    TemplateRenderError,
)


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def test_image(tmp_path):
    """Create a valid test image."""
    img_path = tmp_path / "test_image.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return img_path


def _mock_color():
    """Create mock Color."""
    c = MagicMock()
    c.adjust_saturation = MagicMock(return_value=c)
    c.hex = "#FF0000"
    c.rgb = (255, 0, 0)
    return c


def _mock_scheme():
    """Create mock ColorScheme."""
    s = MagicMock()
    s.background = _mock_color()
    s.foreground = _mock_color()
    s.cursor = _mock_color()
    s.colors = [_mock_color() for _ in range(16)]
    return s


class TestVersionCommand:
    """Tests for version command."""

    def test_version_outputs_version(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "color-scheme-core version" in result.stdout

    def test_version_has_semver(self, runner):
        """Test version contains semver pattern."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert re.search(r"\d+\.\d+\.\d+", result.stdout)


class TestGenerateErrors:
    """Tests for generate command error handling."""

    def test_image_not_found(self, runner, tmp_path):
        """Test error when image doesn't exist."""
        result = runner.invoke(
            app, ["generate", str(tmp_path / "nope.png"), "-o", str(tmp_path)]
        )
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_path_is_directory(self, runner, tmp_path):
        """Test error when path is directory."""
        result = runner.invoke(
            app, ["generate", str(tmp_path), "-o", str(tmp_path)]
        )
        assert result.exit_code == 1
        assert "not a file" in result.stdout.lower()

    def test_invalid_image_error(self, runner, test_image, tmp_path):
        """Test InvalidImageError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = InvalidImageError(str(test_image), "corrupt")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "invalid image" in result.stdout.lower()

    def test_backend_not_available_error(self, runner, test_image, tmp_path):
        """Test BackendNotAvailableError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            mock.return_value.auto_detect.side_effect = BackendNotAvailableError(
                "pywal", "not installed"
            )

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "not available" in result.stdout.lower()

    def test_color_extraction_error(self, runner, test_image, tmp_path):
        """Test ColorExtractionError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = ColorExtractionError("pywal", "failed")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "extraction failed" in result.stdout.lower()

    def test_template_render_error(self, runner, test_image, tmp_path):
        """Test TemplateRenderError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock_factory:
            with patch("color_scheme.cli.main.OutputManager") as mock_output:
                gen = MagicMock()
                gen.generate.return_value = _mock_scheme()
                mock_factory.return_value.auto_detect.return_value = MagicMock(value="custom")
                mock_factory.return_value.create.return_value = gen
                mock_output.return_value.write_outputs.side_effect = TemplateRenderError(
                    "colors.css.j2", "syntax error"
                )

                result = runner.invoke(
                    app, ["generate", str(test_image), "-o", str(tmp_path)]
                )
                assert result.exit_code == 1
                assert "template" in result.stdout.lower()

    def test_output_write_error(self, runner, test_image, tmp_path):
        """Test OutputWriteError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock_factory:
            with patch("color_scheme.cli.main.OutputManager") as mock_output:
                gen = MagicMock()
                gen.generate.return_value = _mock_scheme()
                mock_factory.return_value.auto_detect.return_value = MagicMock(value="custom")
                mock_factory.return_value.create.return_value = gen
                mock_output.return_value.write_outputs.side_effect = OutputWriteError(
                    Path("/readonly"), "permission denied"
                )

                result = runner.invoke(
                    app, ["generate", str(test_image), "-o", str(tmp_path)]
                )
                assert result.exit_code == 1
                assert "error" in result.stdout.lower()

    def test_colorscheme_error(self, runner, test_image, tmp_path):
        """Test ColorSchemeError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = ColorSchemeError("something broke")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "error" in result.stdout.lower()

    def test_unexpected_exception(self, runner, test_image, tmp_path):
        """Test unexpected Exception handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = RuntimeError("crash")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(
                app, ["generate", str(test_image), "-o", str(tmp_path)]
            )
            assert result.exit_code == 1
            assert "unexpected error" in result.stdout.lower()


class TestGenerateSaturation:
    """Tests for saturation in generate command."""

    def test_saturation_adjustment(self, runner, test_image, tmp_path):
        """Test saturation option."""
        result = runner.invoke(
            app,
            ["generate", str(test_image), "-o", str(tmp_path), "-b", "custom", "-s", "1.5"],
        )
        assert result.exit_code == 0
        assert "saturation" in result.stdout.lower() or "1.5" in result.stdout


class TestShowErrors:
    """Tests for show command error handling."""

    def test_image_not_found(self, runner, tmp_path):
        """Test error when image doesn't exist."""
        result = runner.invoke(app, ["show", str(tmp_path / "nope.png")])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_path_is_directory(self, runner, tmp_path):
        """Test error when path is directory."""
        result = runner.invoke(app, ["show", str(tmp_path)])
        assert result.exit_code == 1
        assert "not a file" in result.stdout.lower()

    def test_invalid_image_error(self, runner, test_image):
        """Test InvalidImageError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = InvalidImageError(str(test_image), "corrupt")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "invalid image" in result.stdout.lower()

    def test_backend_not_available_error(self, runner, test_image):
        """Test BackendNotAvailableError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            mock.return_value.auto_detect.side_effect = BackendNotAvailableError(
                "pywal", "not installed"
            )

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "not available" in result.stdout.lower()

    def test_color_extraction_error(self, runner, test_image):
        """Test ColorExtractionError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = ColorExtractionError("pywal", "failed")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "extraction failed" in result.stdout.lower()

    def test_colorscheme_error(self, runner, test_image):
        """Test ColorSchemeError handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = ColorSchemeError("broke")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "error" in result.stdout.lower()

    def test_unexpected_exception(self, runner, test_image):
        """Test unexpected Exception handling."""
        with patch("color_scheme.cli.main.BackendFactory") as mock:
            gen = MagicMock()
            gen.generate.side_effect = RuntimeError("crash")
            mock.return_value.auto_detect.return_value = MagicMock(value="custom")
            mock.return_value.create.return_value = gen

            result = runner.invoke(app, ["show", str(test_image)])
            assert result.exit_code == 1
            assert "unexpected error" in result.stdout.lower()


class TestShowSaturation:
    """Tests for saturation in show command."""

    def test_saturation_display(self, runner, test_image):
        """Test saturation option displays info."""
        result = runner.invoke(
            app, ["show", str(test_image), "-b", "custom", "-s", "1.5"]
        )
        assert result.exit_code == 0
        assert "saturation" in result.stdout.lower() or "1.5" in result.stdout


class TestMainEntryPoint:
    """Tests for main() entry point."""

    def test_main_callable(self):
        """Test main is callable."""
        from color_scheme.cli.main import main
        assert callable(main)

    def test_app_has_commands(self):
        """Test app has command decorator."""
        from color_scheme.cli.main import app
        assert hasattr(app, "command")
```

---

## CHANGE 9: MODIFY tests/unit/test_wallust_backend.py

Add these 3 methods at the END of the `TestWallustGenerator` class (before the final closing of the class):

FIND the last test method in TestWallustGenerator (look for a method starting with `def test_` that is followed by either another class definition, end of file, or less indentation). Add the following THREE methods right after that last test, at the same indentation level:

```python
    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_cache_dir_not_found(
        self, mock_which, mock_run, generator, test_image, config, tmp_path
    ):
        """Test error when cache directory doesn't exist."""
        mock_which.return_value = "/usr/bin/wallust"

        with patch("pathlib.Path.home", return_value=tmp_path):
            with pytest.raises(ColorExtractionError) as exc_info:
                generator.generate(test_image, config)

            assert "cache directory not found" in str(exc_info.value.reason).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_no_cache_subdirectory(
        self, mock_which, mock_run, generator, test_image, config, tmp_path
    ):
        """Test error when no subdirectory in cache."""
        mock_which.return_value = "/usr/bin/wallust"

        cache_dir = tmp_path / ".cache" / "wallust"
        cache_dir.mkdir(parents=True)

        with patch("pathlib.Path.home", return_value=tmp_path):
            with pytest.raises(ColorExtractionError) as exc_info:
                generator.generate(test_image, config)

            assert "subdirectory" in str(exc_info.value.reason).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_generate_no_palette_file(
        self, mock_which, mock_run, generator, test_image, config, tmp_path
    ):
        """Test error when no palette file in cache."""
        mock_which.return_value = "/usr/bin/wallust"

        subdir = tmp_path / ".cache" / "wallust" / "abc123"
        subdir.mkdir(parents=True)
        (subdir / "large.bin").write_bytes(b"x" * 15000)

        with patch("pathlib.Path.home", return_value=tmp_path):
            with pytest.raises(ColorExtractionError) as exc_info:
                generator.generate(test_image, config)

            assert "palette file" in str(exc_info.value.reason).lower()
```

---

## VERIFY

After all changes, run:

```bash
cd /home/inumaki/Development/color-scheme/packages/core
uv run bandit -r src/ -f screen
uv run pytest -v
uv run coverage report --fail-under=95
```

All must exit 0.
