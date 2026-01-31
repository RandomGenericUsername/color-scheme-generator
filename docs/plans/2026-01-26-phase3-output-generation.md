# Phase 3: Output Generation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement OutputManager for writing ColorScheme objects to files in 8 formats using Jinja2 templates, and add CLI commands for generating and displaying color schemes.

**Architecture:** OutputManager handles all file I/O - it takes a ColorScheme object and writes it to multiple file formats using Jinja2 templates. This is completely separate from backends (which extract colors). The CLI provides user-facing commands: `generate` creates a scheme from an image and writes files, `show` displays a scheme to the terminal.

**Tech Stack:** Jinja2 (templates), Typer (CLI), Path (file operations), Rich (terminal output)

---

## Task 1: Add Output Exceptions

**Files:**
- Modify: `packages/core/src/color_scheme/core/exceptions.py`
- Modify: `packages/core/src/color_scheme/core/__init__.py`
- Create: `packages/core/tests/unit/test_output_exceptions.py`

**Step 1: Write failing test for TemplateRenderError**

Create `packages/core/tests/unit/test_output_exceptions.py`:
```python
"""Tests for output-related exceptions."""

import pytest

from color_scheme.core.exceptions import (
    ColorSchemeError,
    OutputWriteError,
    TemplateRenderError,
)


class TestTemplateRenderError:
    """Tests for TemplateRenderError."""

    def test_init_with_template_and_reason(self):
        """Test initialization with template name and reason."""
        error = TemplateRenderError("colors.json.j2", "Undefined variable 'foo'")

        assert error.template_name == "colors.json.j2"
        assert error.reason == "Undefined variable 'foo'"
        assert "colors.json.j2" in str(error)
        assert "Undefined variable 'foo'" in str(error)

    def test_inherits_from_colorscheme_error(self):
        """Test that it inherits from ColorSchemeError."""
        error = TemplateRenderError("test.j2", "test reason")

        assert isinstance(error, ColorSchemeError)
        assert isinstance(error, Exception)


class TestOutputWriteError:
    """Tests for OutputWriteError."""

    def test_init_with_path_and_reason(self):
        """Test initialization with file path and reason."""
        error = OutputWriteError("/tmp/colors.json", "Permission denied")

        assert error.file_path == "/tmp/colors.json"
        assert error.reason == "Permission denied"
        assert "/tmp/colors.json" in str(error)
        assert "Permission denied" in str(error)

    def test_inherits_from_colorscheme_error(self):
        """Test that it inherits from ColorSchemeError."""
        error = OutputWriteError("/tmp/test", "test reason")

        assert isinstance(error, ColorSchemeError)
        assert isinstance(error, Exception)
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_output_exceptions.py -v
```

Expected: ImportError - TemplateRenderError and OutputWriteError not defined

**Step 3: Implement exceptions**

Edit `packages/core/src/color_scheme/core/exceptions.py`, add at the end:
```python


class TemplateRenderError(ColorSchemeError):
    """Raised when template rendering fails."""

    def __init__(self, template_name: str, reason: str):
        self.template_name = template_name
        self.reason = reason
        super().__init__(f"Template rendering failed ('{template_name}'): {reason}")


class OutputWriteError(ColorSchemeError):
    """Raised when writing output file fails."""

    def __init__(self, file_path: str, reason: str):
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to write '{file_path}': {reason}")
```

**Step 4: Update module exports**

Edit `packages/core/src/color_scheme/core/__init__.py`, update exports:
```python
"""Core color scheme types and exceptions."""

from color_scheme.core.base import ColorSchemeGenerator
from color_scheme.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    ColorSchemeError,
    InvalidImageError,
    OutputWriteError,
    TemplateRenderError,
)
from color_scheme.core.types import Color, ColorScheme, GeneratorConfig

__all__ = [
    # Base classes
    "ColorSchemeGenerator",
    # Types
    "Color",
    "ColorScheme",
    "GeneratorConfig",
    # Exceptions
    "ColorSchemeError",
    "InvalidImageError",
    "ColorExtractionError",
    "BackendNotAvailableError",
    "TemplateRenderError",
    "OutputWriteError",
]
```

**Step 5: Run tests to verify they pass**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_output_exceptions.py -v
```

Expected: 4 tests pass

**Step 6: Commit**

Run:
```bash
git add packages/core/src/color_scheme/core/exceptions.py packages/core/src/color_scheme/core/__init__.py packages/core/tests/unit/test_output_exceptions.py
git commit -m "feat(core): add output exceptions

Add TemplateRenderError and OutputWriteError exceptions for
output generation error handling.

Includes comprehensive tests.

Part of Phase 3: Output Generation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Implement OutputManager

**Files:**
- Create: `packages/core/src/color_scheme/output/__init__.py`
- Create: `packages/core/src/color_scheme/output/manager.py`
- Create: `packages/core/tests/unit/test_output_manager.py`

**Step 1: Write failing test for OutputManager init**

Create `packages/core/tests/unit/test_output_manager.py`:
```python
"""Tests for OutputManager."""

from pathlib import Path
from unittest.mock import patch

import pytest

from color_scheme.config.enums import ColorFormat
from color_scheme.config.settings import Settings
from color_scheme.core.exceptions import (
    OutputWriteError,
    TemplateRenderError,
)
from color_scheme.output.manager import OutputManager


class TestOutputManagerInit:
    """Test OutputManager initialization."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    def test_init_with_settings(self, settings):
        """Test initialization with settings."""
        manager = OutputManager(settings)

        assert manager.settings == settings
        assert manager.template_env is not None
        assert manager.template_env.loader is not None
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_output_manager.py::TestOutputManagerInit::test_init_with_settings -v
```

Expected: ImportError - module 'color_scheme.output.manager' not found

**Step 3: Create OutputManager skeleton**

Create `packages/core/src/color_scheme/output/__init__.py`:
```python
"""Output generation for color schemes."""

from color_scheme.output.manager import OutputManager

__all__ = ["OutputManager"]
```

Create `packages/core/src/color_scheme/output/manager.py`:
```python
"""Output manager for writing color schemes to files."""

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from color_scheme.config.config import AppConfig

logger = logging.getLogger(__name__)


class OutputManager:
    """Manages writing ColorScheme objects to files.

    This class is responsible for:
    1. Loading Jinja2 templates
    2. Rendering templates with ColorScheme data
    3. Writing rendered content to files

    Attributes:
        settings: Application configuration
        template_env: Jinja2 environment for template rendering
    """

    def __init__(self, settings: AppConfig):
        """Initialize OutputManager.

        Args:
            settings: Application configuration
        """
        self.settings = settings

        # Set up Jinja2 environment
        template_dir = settings.templates.directory
        if not template_dir.is_absolute():
            # Relative to package root
            package_root = Path(__file__).parent.parent
            template_dir = package_root / template_dir

        logger.debug("Template directory: %s", template_dir)

        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        )
        logger.debug("Initialized OutputManager with Jinja2 environment")
```

**Step 4: Run test to verify it passes**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_output_manager.py::TestOutputManagerInit::test_init_with_settings -v
```

Expected: 1 test passes

**Step 5: Write failing test for write_outputs**

Add to `packages/core/tests/unit/test_output_manager.py`:
```python


class TestOutputManagerWriteOutputs:
    """Test OutputManager write_outputs method."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def manager(self, settings):
        """Create OutputManager."""
        return OutputManager(settings)

    @pytest.fixture
    def sample_scheme(self):
        """Create sample ColorScheme."""
        from datetime import datetime
        from color_scheme.core.types import Color, ColorScheme

        colors = [
            Color(hex=f"#{i:02X}{i:02X}{i:02X}", rgb=(i, i, i))
            for i in range(16)
        ]

        return ColorScheme(
            background=Color(hex="#000000", rgb=(0, 0, 0)),
            foreground=Color(hex="#FFFFFF", rgb=(255, 255, 255)),
            cursor=Color(hex="#FF0000", rgb=(255, 0, 0)),
            colors=colors,
            source_image=Path("/test/image.png"),
            backend="custom",
            generated_at=datetime(2026, 1, 26, 12, 0, 0),
        )

    def test_write_outputs_single_format(self, manager, sample_scheme, tmp_path):
        """Test writing outputs in a single format."""
        output_dir = tmp_path / "output"

        output_files = manager.write_outputs(
            sample_scheme, output_dir, [ColorFormat.JSON]
        )

        assert len(output_files) == 1
        assert "json" in output_files
        assert output_files["json"].exists()

        # Verify it's valid JSON
        import json
        content = output_files["json"].read_text()
        data = json.loads(content)
        assert data["special"]["background"] == "#000000"

    def test_write_outputs_multiple_formats(self, manager, sample_scheme, tmp_path):
        """Test writing outputs in multiple formats."""
        output_dir = tmp_path / "output"

        output_files = manager.write_outputs(
            sample_scheme,
            output_dir,
            [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.YAML],
        )

        assert len(output_files) == 3
        assert "json" in output_files
        assert "css" in output_files
        assert "yaml" in output_files
        assert all(path.exists() for path in output_files.values())

    def test_write_outputs_creates_directory(self, manager, sample_scheme, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "nested" / "output" / "dir"
        assert not output_dir.exists()

        output_files = manager.write_outputs(
            sample_scheme, output_dir, [ColorFormat.JSON]
        )

        assert output_dir.exists()
        assert len(output_files) == 1
```

**Step 6: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_output_manager.py::TestOutputManagerWriteOutputs -v
```

Expected: AttributeError - 'OutputManager' object has no attribute 'write_outputs'

**Step 7: Implement write_outputs method**

Add to `packages/core/src/color_scheme/output/manager.py`:
```python
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound, UndefinedError

from color_scheme.config.config import AppConfig
from color_scheme.config.enums import ColorFormat
from color_scheme.core.exceptions import OutputWriteError, TemplateRenderError
from color_scheme.core.types import ColorScheme


# Add to OutputManager class:

    def write_outputs(
        self,
        scheme: ColorScheme,
        output_dir: Path,
        formats: list[ColorFormat],
    ) -> dict[str, Path]:
        """Write ColorScheme to files in specified formats.

        Args:
            scheme: ColorScheme object to write
            output_dir: Directory to write files to
            formats: List of output formats to generate

        Returns:
            Dictionary mapping format name to output file path

        Raises:
            TemplateRenderError: If template rendering fails
            OutputWriteError: If writing file fails
        """
        logger.info("Writing color scheme outputs to %s", output_dir)
        logger.debug("Output formats: %s", [f.value for f in formats])

        # Ensure output directory exists
        output_dir = output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Resolved output directory: %s", output_dir)

        output_files = {}

        for fmt in formats:
            try:
                # Render template
                logger.debug("Rendering template for format: %s", fmt.value)
                content = self._render_template(scheme, fmt)

                # Write to file
                output_path = output_dir / f"colors.{fmt.value}"

                # Special handling for sequences format (binary file)
                if fmt == ColorFormat.SEQUENCES:
                    binary_content = self._convert_to_escape_sequences(content)
                    self._write_binary_file(output_path, binary_content)
                else:
                    # Text file
                    self._write_file(output_path, content)

                output_files[fmt.value] = output_path
                logger.debug("Wrote %s", output_path)

            except (TemplateRenderError, OutputWriteError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                logger.error("Unexpected error writing %s: %s", fmt.value, e)
                # Wrap unexpected errors
                raise OutputWriteError(
                    str(output_dir / f"colors.{fmt.value}"),
                    f"Unexpected error: {e}",
                ) from e

        logger.info("Successfully wrote %d output files", len(output_files))
        return output_files

    def _render_template(self, scheme: ColorScheme, fmt: ColorFormat) -> str:
        """Render template for given format.

        Args:
            scheme: ColorScheme object
            fmt: Output format

        Returns:
            Rendered template content

        Raises:
            TemplateRenderError: If rendering fails
        """
        template_name = f"colors.{fmt.value}.j2"

        try:
            template = self.template_env.get_template(template_name)
            logger.debug("Loaded template: %s", template_name)
        except TemplateNotFound:
            logger.error(
                "Template not found: %s in %s",
                template_name,
                self.settings.templates.directory,
            )
            raise TemplateRenderError(
                template_name,
                f"Template not found in {self.settings.templates.directory}",
            ) from None

        # Prepare template context
        context = {
            "background": scheme.background,
            "foreground": scheme.foreground,
            "cursor": scheme.cursor,
            "colors": scheme.colors,
            "source_image": str(scheme.source_image),
            "backend": scheme.backend,
            "generated_at": scheme.generated_at.isoformat(),
        }

        try:
            rendered = template.render(**context)
            logger.debug("Successfully rendered template: %s", template_name)
            return rendered
        except UndefinedError as e:
            logger.error(
                "Undefined variable in template %s: %s", template_name, e
            )
            raise TemplateRenderError(
                template_name, f"Undefined variable: {e}"
            ) from e
        except Exception as e:
            logger.error("Template render error in %s: %s", template_name, e)
            raise TemplateRenderError(template_name, str(e)) from e

    def _convert_to_escape_sequences(self, content: str) -> bytes:
        """Convert template output to actual ANSI escape sequences.

        Args:
            content: Template-rendered content with placeholders

        Returns:
            Binary content with actual escape sequences
        """
        # Replace ] with ESC + ]
        content = content.replace("]", "\x1b]")
        # Replace \ with ESC
        content = content.replace("\\", "\x1b\\")

        return content.encode("utf-8")

    def _write_binary_file(self, path: Path, content: bytes) -> None:
        """Write binary content to file.

        Args:
            path: File path
            content: Binary content to write

        Raises:
            OutputWriteError: If writing fails
        """
        try:
            path.write_bytes(content)
        except PermissionError:
            raise OutputWriteError(str(path), "Permission denied") from None
        except OSError as e:
            raise OutputWriteError(str(path), str(e)) from e

    def _write_file(self, path: Path, content: str) -> None:
        """Write content to file.

        Args:
            path: File path
            content: Content to write

        Raises:
            OutputWriteError: If writing fails
        """
        try:
            path.write_text(content)
        except PermissionError:
            raise OutputWriteError(str(path), "Permission denied") from None
        except OSError as e:
            raise OutputWriteError(str(path), str(e)) from e
```

**Step 8: Run tests to verify they pass**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_output_manager.py::TestOutputManagerWriteOutputs -v
```

Expected: 3 tests pass

**Step 9: Add error handling tests**

Add to `packages/core/tests/unit/test_output_manager.py`:
```python


class TestOutputManagerErrorHandling:
    """Test OutputManager error handling."""

    @pytest.fixture
    def settings(self):
        """Get settings."""
        return Settings.get()

    @pytest.fixture
    def manager(self, settings):
        """Create OutputManager."""
        return OutputManager(settings)

    @pytest.fixture
    def sample_scheme(self):
        """Create sample ColorScheme."""
        from datetime import datetime
        from color_scheme.core.types import Color, ColorScheme

        colors = [
            Color(hex=f"#{i:02X}{i:02X}{i:02X}", rgb=(i, i, i))
            for i in range(16)
        ]

        return ColorScheme(
            background=Color(hex="#000000", rgb=(0, 0, 0)),
            foreground=Color(hex="#FFFFFF", rgb=(255, 255, 255)),
            cursor=Color(hex="#FF0000", rgb=(255, 0, 0)),
            colors=colors,
            source_image=Path("/test/image.png"),
            backend="custom",
            generated_at=datetime(2026, 1, 26, 12, 0, 0),
        )

    def test_template_not_found(self, settings, sample_scheme, tmp_path):
        """Test handling of missing template."""
        # Set template dir to empty directory
        settings.templates.directory = tmp_path / "empty_templates"
        settings.templates.directory.mkdir()

        manager = OutputManager(settings)

        with pytest.raises(TemplateRenderError) as exc_info:
            manager.write_outputs(sample_scheme, tmp_path, [ColorFormat.JSON])

        assert "colors.json.j2" in str(exc_info.value)
        assert "Template not found" in str(exc_info.value)

    def test_permission_denied(self, manager, sample_scheme, tmp_path):
        """Test handling of permission denied."""
        output_dir = tmp_path / "readonly"
        output_dir.mkdir()
        output_file = output_dir / "colors.json"
        output_file.write_text("")
        output_file.chmod(0o444)  # Read-only
        output_dir.chmod(0o555)  # Read-only directory

        with pytest.raises(OutputWriteError) as exc_info:
            manager.write_outputs(sample_scheme, output_dir, [ColorFormat.JSON])

        assert "Permission denied" in str(exc_info.value)

        # Cleanup
        output_dir.chmod(0o755)
```

**Step 10: Run error handling tests**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_output_manager.py::TestOutputManagerErrorHandling -v
```

Expected: 2 tests pass

**Step 11: Check coverage**

Run:
```bash
cd packages/core
uv run pytest tests/unit/test_output_manager.py --cov=src/color_scheme/output --cov-report=term
```

Expected: Coverage ≥90%

**Step 12: Commit**

Run:
```bash
git add packages/core/src/color_scheme/output/ packages/core/tests/unit/test_output_manager.py
git commit -m "feat(output): implement OutputManager

Implements OutputManager for writing ColorScheme to files:
- Jinja2 template rendering
- Support for 8 output formats
- Special handling for binary sequences format
- Comprehensive error handling
- Full test coverage (90%+)

Part of Phase 3: Output Generation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Verify Templates Work

**Files:**
- Test: All existing templates in `packages/core/src/color_scheme/templates/`

**Step 1: Write integration test for all templates**

Create `packages/core/tests/integration/test_all_templates.py`:
```python
"""Integration tests for all template formats."""

from datetime import datetime
from pathlib import Path

import pytest

from color_scheme.config.enums import ColorFormat
from color_scheme.config.settings import Settings
from color_scheme.core.types import Color, ColorScheme
from color_scheme.output.manager import OutputManager


@pytest.fixture
def sample_scheme():
    """Create sample ColorScheme for testing."""
    colors = [
        Color(hex=f"#{i:02X}{i:02X}{i:02X}", rgb=(i, i, i))
        for i in range(16)
    ]

    return ColorScheme(
        background=Color(hex="#1A1B26", rgb=(26, 27, 38)),
        foreground=Color(hex="#C0CAF5", rgb=(192, 202, 245)),
        cursor=Color(hex="#7AA2F7", rgb=(122, 162, 247)),
        colors=colors,
        source_image=Path("/test/wallpaper.png"),
        backend="custom",
        generated_at=datetime(2026, 1, 26, 12, 0, 0),
    )


@pytest.fixture
def manager():
    """Create OutputManager."""
    return OutputManager(Settings.get())


class TestAllTemplates:
    """Test that all templates render without errors."""

    def test_json_template(self, manager, sample_scheme, tmp_path):
        """Test JSON template rendering."""
        output_files = manager.write_outputs(
            sample_scheme, tmp_path, [ColorFormat.JSON]
        )

        assert output_files["json"].exists()

        # Verify it's valid JSON
        import json
        content = output_files["json"].read_text()
        data = json.loads(content)

        assert data["special"]["background"] == "#1A1B26"
        assert data["metadata"]["backend"] == "custom"
        assert len(data["colors"]) == 16

    def test_css_template(self, manager, sample_scheme, tmp_path):
        """Test CSS template rendering."""
        output_files = manager.write_outputs(
            sample_scheme, tmp_path, [ColorFormat.CSS]
        )

        assert output_files["css"].exists()
        content = output_files["css"].read_text()

        assert ":root {" in content
        assert "--bg:" in content
        assert "#1A1B26" in content

    def test_scss_template(self, manager, sample_scheme, tmp_path):
        """Test SCSS template rendering."""
        output_files = manager.write_outputs(
            sample_scheme, tmp_path, [ColorFormat.SCSS]
        )

        assert output_files["scss"].exists()
        content = output_files["scss"].read_text()

        assert "$bg:" in content
        assert "#1A1B26" in content

    def test_yaml_template(self, manager, sample_scheme, tmp_path):
        """Test YAML template rendering."""
        output_files = manager.write_outputs(
            sample_scheme, tmp_path, [ColorFormat.YAML]
        )

        assert output_files["yaml"].exists()

        # Verify it's valid YAML
        import yaml
        content = output_files["yaml"].read_text()
        data = yaml.safe_load(content)

        assert data["special"]["background"] == "#1A1B26"

    def test_sh_template(self, manager, sample_scheme, tmp_path):
        """Test shell script template rendering."""
        output_files = manager.write_outputs(
            sample_scheme, tmp_path, [ColorFormat.SH]
        )

        assert output_files["sh"].exists()
        content = output_files["sh"].read_text()

        assert "#!/bin/sh" in content or "export" in content
        assert "1A1B26" in content or "1a1b26" in content

    def test_gtk_css_template(self, manager, sample_scheme, tmp_path):
        """Test GTK CSS template rendering."""
        output_files = manager.write_outputs(
            sample_scheme, tmp_path, [ColorFormat.GTK_CSS]
        )

        assert output_files["gtk.css"].exists()
        content = output_files["gtk.css"].read_text()

        assert "@define-color" in content

    def test_rasi_template(self, manager, sample_scheme, tmp_path):
        """Test rofi rasi template rendering."""
        output_files = manager.write_outputs(
            sample_scheme, tmp_path, [ColorFormat.RASI]
        )

        assert output_files["rasi"].exists()
        content = output_files["rasi"].read_text()

        assert "background:" in content or "bg:" in content

    def test_sequences_template(self, manager, sample_scheme, tmp_path):
        """Test terminal sequences template rendering."""
        output_files = manager.write_outputs(
            sample_scheme, tmp_path, [ColorFormat.SEQUENCES]
        )

        assert output_files["sequences"].exists()
        content = output_files["sequences"].read_bytes()

        # Should contain escape sequences
        assert b"\x1b]" in content

    def test_all_formats_together(self, manager, sample_scheme, tmp_path):
        """Test rendering all formats at once."""
        all_formats = [
            ColorFormat.JSON,
            ColorFormat.CSS,
            ColorFormat.SCSS,
            ColorFormat.YAML,
            ColorFormat.SH,
            ColorFormat.GTK_CSS,
            ColorFormat.RASI,
            ColorFormat.SEQUENCES,
        ]

        output_files = manager.write_outputs(
            sample_scheme, tmp_path, all_formats
        )

        assert len(output_files) == 8
        assert all(path.exists() for path in output_files.values())
```

**Step 2: Create integration test directory**

Run:
```bash
mkdir -p packages/core/tests/integration
touch packages/core/tests/integration/__init__.py
```

**Step 3: Run integration tests**

Run:
```bash
cd packages/core
uv run pytest tests/integration/test_all_templates.py -v
```

Expected: 9 tests pass (verifies all 8 templates work)

**Step 4: Commit**

Run:
```bash
git add packages/core/tests/integration/
git commit -m "test(output): add integration tests for all templates

Verifies all 8 template formats render correctly:
- JSON, CSS, SCSS, YAML
- Shell script, GTK CSS, rofi rasi
- Terminal sequences (binary)

Part of Phase 3: Output Generation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Implement CLI Generate Command

**Files:**
- Modify: `packages/core/src/color_scheme/cli/main.py`
- Create: `packages/core/tests/integration/test_cli_generate.py`

**Step 1: Write failing test for generate command**

Create `packages/core/tests/integration/test_cli_generate.py`:
```python
"""Integration tests for CLI generate command."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from color_scheme.cli.main import app

runner = CliRunner()


class TestGenerateCommand:
    """Test CLI generate command."""

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    def test_generate_with_defaults(self, test_image, tmp_path):
        """Test generate with default options."""
        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--output-dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        assert "Generated color scheme" in result.stdout
        assert tmp_path.exists()

    def test_generate_with_backend(self, test_image, tmp_path):
        """Test generate with specific backend."""
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

    def test_generate_with_formats(self, test_image, tmp_path):
        """Test generate with specific formats."""
        result = runner.invoke(
            app,
            [
                "generate",
                str(test_image),
                "--output-dir",
                str(tmp_path),
                "--format",
                "json",
                "--format",
                "css",
            ],
        )

        assert result.exit_code == 0
        assert (tmp_path / "colors.json").exists()
        assert (tmp_path / "colors.css").exists()

    def test_generate_invalid_image(self, tmp_path):
        """Test generate with invalid image path."""
        result = runner.invoke(
            app,
            [
                "generate",
                "/nonexistent/image.png",
                "--output-dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code != 0
        assert "Error" in result.stdout or "does not exist" in result.stdout
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/integration/test_cli_generate.py::TestGenerateCommand::test_generate_with_defaults -v
```

Expected: Test fails - generate command not implemented

**Step 3: Implement generate command**

Edit `packages/core/src/color_scheme/cli/main.py`, replace the generate command:
```python
"""CLI entry point for color-scheme."""

from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(
    name="color-scheme",
    help="Generate color schemes from images",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()


@app.command()
def version():
    """Show version information."""
    from color_scheme import __version__

    typer.echo(f"color-scheme-core version {__version__}")


@app.command()
def generate(
    image_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Path to source image",
    ),
    output_dir: Path = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory (default: from settings)",
    ),
    backend: str = typer.Option(
        None,
        "--backend",
        "-b",
        help="Backend to use (custom/pywal/wallust, default: auto-detect)",
    ),
    format: list[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output formats (can specify multiple)",
    ),
    saturation: float = typer.Option(
        None,
        "--saturation",
        "-s",
        help="Saturation adjustment (0.0-2.0, default: 1.0)",
    ),
):
    """Generate color scheme from an image."""
    try:
        from color_scheme.config.enums import Backend, ColorFormat
        from color_scheme.config.settings import Settings
        from color_scheme.core.types import GeneratorConfig
        from color_scheme.factory import BackendFactory
        from color_scheme.output.manager import OutputManager

        # Load settings
        settings = Settings.get()

        # Determine backend
        if backend:
            try:
                backend_enum = Backend(backend.lower())
            except ValueError:
                console.print(
                    f"[red]Error:[/red] Invalid backend '{backend}'. "
                    f"Valid options: custom, pywal, wallust"
                )
                raise typer.Exit(1)
        else:
            # Auto-detect
            factory = BackendFactory(settings)
            backend_enum = factory.auto_detect()
            console.print(f"Auto-detected backend: [cyan]{backend_enum.value}[/cyan]")

        # Determine output directory
        if not output_dir:
            output_dir = settings.output.directory

        # Determine formats
        if format:
            try:
                format_enums = [ColorFormat(f.lower()) for f in format]
            except ValueError as e:
                console.print(f"[red]Error:[/red] Invalid format: {e}")
                raise typer.Exit(1)
        else:
            format_enums = [ColorFormat(f) for f in settings.output.formats]

        # Create generator config
        config = GeneratorConfig.from_settings(
            settings,
            backend=backend_enum,
            output_dir=output_dir,
            formats=format_enums,
            saturation_adjustment=saturation,
        )

        # Create generator
        factory = BackendFactory(settings)
        generator = factory.create(backend_enum)

        # Generate color scheme
        console.print(f"Generating color scheme from [cyan]{image_path}[/cyan]...")
        scheme = generator.generate(image_path, config)

        # Write outputs
        output_manager = OutputManager(settings)
        output_files = output_manager.write_outputs(
            scheme, output_dir, format_enums
        )

        # Report success
        console.print(
            f"[green]✓[/green] Generated color scheme using [cyan]{backend_enum.value}[/cyan]"
        )
        console.print(f"Output directory: [cyan]{output_dir}[/cyan]")
        console.print(f"Formats: {', '.join(output_files.keys())}")

        for fmt, path in output_files.items():
            console.print(f"  • {fmt}: {path.name}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def main():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/core
uv run pytest tests/integration/test_cli_generate.py -v
```

Expected: 4 tests pass

**Step 5: Test manually**

Run:
```bash
cd packages/core
uv run color-scheme generate tests/fixtures/test_image.png --output-dir /tmp/test-colors
ls -la /tmp/test-colors
```

Expected: Color files generated in /tmp/test-colors

**Step 6: Commit**

Run:
```bash
git add packages/core/src/color_scheme/cli/main.py packages/core/tests/integration/test_cli_generate.py
git commit -m "feat(cli): implement generate command

Implements full generate command with:
- Auto-detection of best backend
- Manual backend selection
- Custom output directory
- Format selection
- Saturation adjustment
- Rich console output

Includes integration tests.

Part of Phase 3: Output Generation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Implement CLI Show Command

**Files:**
- Modify: `packages/core/src/color_scheme/cli/main.py`
- Create: `packages/core/tests/integration/test_cli_show.py`

**Step 1: Write failing test for show command**

Create `packages/core/tests/integration/test_cli_show.py`:
```python
"""Integration tests for CLI show command."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from color_scheme.cli.main import app

runner = CliRunner()


class TestShowCommand:
    """Test CLI show command."""

    @pytest.fixture
    def test_image(self):
        """Path to test image."""
        return Path("tests/fixtures/test_image.png")

    def test_show_with_defaults(self, test_image):
        """Test show with default options."""
        result = runner.invoke(
            app,
            [
                "show",
                str(test_image),
            ],
        )

        assert result.exit_code == 0
        assert "Color Scheme" in result.stdout
        assert "Background" in result.stdout
        assert "Foreground" in result.stdout

    def test_show_with_backend(self, test_image):
        """Test show with specific backend."""
        result = runner.invoke(
            app,
            [
                "show",
                str(test_image),
                "--backend",
                "custom",
            ],
        )

        assert result.exit_code == 0
        assert "custom" in result.stdout.lower()

    def test_show_invalid_image(self):
        """Test show with invalid image path."""
        result = runner.invoke(
            app,
            [
                "show",
                "/nonexistent/image.png",
            ],
        )

        assert result.exit_code != 0
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd packages/core
uv run pytest tests/integration/test_cli_show.py::TestShowCommand::test_show_with_defaults -v
```

Expected: CommandNotFoundError - show command doesn't exist

**Step 3: Implement show command**

Add to `packages/core/src/color_scheme/cli/main.py`:
```python
@app.command()
def show(
    image_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Path to source image",
    ),
    backend: str = typer.Option(
        None,
        "--backend",
        "-b",
        help="Backend to use (custom/pywal/wallust, default: auto-detect)",
    ),
    saturation: float = typer.Option(
        None,
        "--saturation",
        "-s",
        help="Saturation adjustment (0.0-2.0, default: 1.0)",
    ),
):
    """Display color scheme in terminal without writing files."""
    try:
        from rich.panel import Panel
        from rich.table import Table

        from color_scheme.config.enums import Backend
        from color_scheme.config.settings import Settings
        from color_scheme.core.types import GeneratorConfig
        from color_scheme.factory import BackendFactory

        # Load settings
        settings = Settings.get()

        # Determine backend
        if backend:
            try:
                backend_enum = Backend(backend.lower())
            except ValueError:
                console.print(
                    f"[red]Error:[/red] Invalid backend '{backend}'. "
                    f"Valid options: custom, pywal, wallust"
                )
                raise typer.Exit(1)
        else:
            # Auto-detect
            factory = BackendFactory(settings)
            backend_enum = factory.auto_detect()

        # Create generator config
        config = GeneratorConfig.from_settings(
            settings,
            backend=backend_enum,
            saturation_adjustment=saturation,
        )

        # Create generator
        factory = BackendFactory(settings)
        generator = factory.create(backend_enum)

        # Generate color scheme
        scheme = generator.generate(image_path, config)

        # Display color scheme
        console.print(
            Panel(
                f"[bold]Source:[/bold] {image_path}\n"
                f"[bold]Backend:[/bold] {backend_enum.value}",
                title="Color Scheme",
                border_style="cyan",
            )
        )

        # Create table for special colors
        special_table = Table(title="Special Colors", show_header=True)
        special_table.add_column("Name", style="bold")
        special_table.add_column("Hex", style="cyan")
        special_table.add_column("RGB", style="dim")
        special_table.add_column("Preview")

        def color_preview(color):
            """Create color preview box."""
            return f"[on {color.hex}]    [/]"

        special_table.add_row(
            "Background",
            scheme.background.hex,
            str(scheme.background.rgb),
            color_preview(scheme.background),
        )
        special_table.add_row(
            "Foreground",
            scheme.foreground.hex,
            str(scheme.foreground.rgb),
            color_preview(scheme.foreground),
        )
        special_table.add_row(
            "Cursor",
            scheme.cursor.hex,
            str(scheme.cursor.rgb),
            color_preview(scheme.cursor),
        )

        console.print(special_table)

        # Create table for 16 terminal colors
        colors_table = Table(title="Terminal Colors (ANSI)", show_header=True)
        colors_table.add_column("Index", style="bold")
        colors_table.add_column("Hex", style="cyan")
        colors_table.add_column("RGB", style="dim")
        colors_table.add_column("Preview")

        for i, color in enumerate(scheme.colors):
            colors_table.add_row(
                f"color{i}",
                color.hex,
                str(color.rgb),
                color_preview(color),
            )

        console.print(colors_table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd packages/core
uv run pytest tests/integration/test_cli_show.py -v
```

Expected: 3 tests pass

**Step 5: Test manually**

Run:
```bash
cd packages/core
uv run color-scheme show tests/fixtures/test_image.png
```

Expected: Color scheme displayed in terminal with rich formatting

**Step 6: Commit**

Run:
```bash
git add packages/core/src/color_scheme/cli/main.py packages/core/tests/integration/test_cli_show.py
git commit -m "feat(cli): implement show command

Implements show command for displaying color schemes in terminal:
- Rich formatted tables
- Color previews
- Special colors (background, foreground, cursor)
- 16 terminal colors (ANSI)
- No file output

Includes integration tests.

Part of Phase 3: Output Generation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Final Testing and Documentation

**Step 1: Run all tests**

Run:
```bash
cd packages/core
uv run pytest tests/ -v
```

Expected: All tests pass

**Step 2: Check overall coverage**

Run:
```bash
cd packages/core
uv run pytest tests/ --cov=src/color_scheme --cov-report=term --cov-report=html
```

Expected: Coverage ≥95%

**Step 3: Run linting**

Run:
```bash
cd packages/core
uv run ruff check src/ tests/
uv run black --check src/ tests/
uv run isort --check src/ tests/
```

Expected: No linting errors (fix any that appear)

**Step 4: Run type checking**

Run:
```bash
cd packages/core
uv run mypy src/color_scheme/
```

Expected: No type errors

**Step 5: Test end-to-end**

Run:
```bash
cd packages/core
uv run color-scheme generate tests/fixtures/test_image.png --output-dir /tmp/e2e-test
ls -la /tmp/e2e-test
uv run color-scheme show tests/fixtures/test_image.png
```

Expected: Files generated, show displays correctly

**Step 6: Update documentation**

Edit `docs/implementation-progress.md`:
- Mark Phase 3 as complete
- Update phase status to ✅ COMPLETE
- Add completion date (2026-01-26)
- List deliverables

**Step 7: Final commit**

Run:
```bash
git add docs/implementation-progress.md
git commit -m "docs(progress): mark Phase 3 output generation as complete

All output generation implemented and tested:
- OutputManager with Jinja2 templates
- 8 output formats (JSON, CSS, SCSS, YAML, shell, GTK CSS, rofi, sequences)
- CLI generate command (full-featured)
- CLI show command (terminal display)

Test coverage: 95%+
All commands fully functional.

Phase 3 complete. Core package ready for integration.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Completion

Phase 3 implementation complete! You now have:

✅ **Output Exceptions** - TemplateRenderError, OutputWriteError
✅ **OutputManager** - Jinja2-based template rendering and file writing
✅ **8 Output Formats** - JSON, CSS, SCSS, YAML, shell, GTK CSS, rofi rasi, terminal sequences
✅ **CLI Generate Command** - Full-featured color scheme generation
✅ **CLI Show Command** - Terminal-based color scheme display
✅ **Test Coverage** - 95%+ coverage with unit and integration tests
✅ **Error Handling** - Comprehensive error handling for all failure modes

## Next Steps

The core package is now complete and ready for:
- **Phase 4**: Orchestrator Package (multi-step workflows, state management)
- **Phase 5**: Integration (CLI orchestration, error recovery)
- **Phase 6**: Polish (documentation, examples, packaging)
