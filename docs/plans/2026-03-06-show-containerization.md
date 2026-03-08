# Show Command Containerization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Route the orchestrator `show` command through a container like `generate` does, so no backend tools (pywal, wallust) are needed on the host.

**Architecture:** Three sequential changes — (1) add a TTY-aware plain-text fallback to `color-scheme-core show`, (2) add `run_show()` to `ContainerManager`, (3) replace the orchestrator `show` host subprocess with a `manager.run_show()` call. TTY state on the host propagates naturally to the container via the `-t` docker flag.

**Tech Stack:** Python 3.12, Typer, Rich, subprocess, pytest, unittest.mock

---

### Task 1: Core TTY fallback in `show`

**Context:**
`packages/core/src/color_scheme/cli/main.py` has a module-level `console = Console()` at
line 52. The `show` function (line 288) currently always renders Rich tables. When the
orchestrator runs `show` in a container without `-t`, Rich's `console.is_terminal` is
`False` (stdout is a pipe). We need a plain bullet list in that case.

The existing `CliRunner` in tests runs with a captured buffer (not a TTY), so
`console.is_terminal` will be `False` there too — meaning new tests will naturally
exercise the fallback path.

**Files:**
- Modify: `packages/core/src/color_scheme/cli/main.py`
- Modify: `packages/core/tests/integration/test_cli_show.py`

---

**Step 1: Write the failing tests**

Add to `packages/core/tests/integration/test_cli_show.py`:

```python
def test_show_non_tty_outputs_bullet_list(self, runner, test_image):
    """In non-TTY context (CliRunner default), show outputs plain bullet list."""
    result = runner.invoke(
        app,
        ["show", str(test_image), "--backend", "custom"],
    )

    assert result.exit_code == 0
    # Bullet list format: "key: #RRGGBB"
    assert "background:" in result.stdout
    assert "foreground:" in result.stdout
    assert "cursor:" in result.stdout
    assert "color0:" in result.stdout
    # Should NOT contain Rich table markup characters
    assert "┃" not in result.stdout
    assert "━" not in result.stdout

def test_show_tty_outputs_rich_tables(self, runner, test_image):
    """In TTY context, show outputs Rich tables."""
    from unittest.mock import patch, PropertyMock
    from rich.console import Console

    with patch.object(Console, "is_terminal", new_callable=PropertyMock, return_value=True):
        result = runner.invoke(
            app,
            ["show", str(test_image), "--backend", "custom"],
        )

    assert result.exit_code == 0
    # Rich table has these headers
    assert "Background" in result.stdout or "Special Colors" in result.stdout
```

**Step 2: Run tests to verify they fail**

```bash
cd packages/core
uv run pytest tests/integration/test_cli_show.py::TestShowCommand::test_show_non_tty_outputs_bullet_list tests/integration/test_cli_show.py::TestShowCommand::test_show_tty_outputs_rich_tables -v
```

Expected: FAIL — both tests fail because there is no branch yet.

**Step 3: Implement the TTY branch**

In `packages/core/src/color_scheme/cli/main.py`, find the display section in `show`
(after the saturation adjustment block, around line 413). Replace everything from the
`console.print()` that starts the display down to the end of the function body with:

```python
        # Display color scheme — plain list if not a terminal, Rich tables if TTY
        if not console.is_terminal:
            # Simple bullet list for non-interactive / piped / container-without-TTY use
            print(f"backend: {backend.value}")
            print(f"background: {color_scheme.background.hex}")
            print(f"foreground: {color_scheme.foreground.hex}")
            print(f"cursor: {color_scheme.cursor.hex}")
            for i, color in enumerate(color_scheme.colors):
                print(f"color{i}: {color.hex}")
        else:
            # Full Rich display (existing code — move it here, unchanged)
            console.print()

            info_lines = [
                f"[cyan]Source Image:[/cyan] {image_path}",
                f"[cyan]Backend:[/cyan] {backend.value}",
            ]
            if (
                generator_config.saturation_adjustment is not None
                and generator_config.saturation_adjustment != 1.0
            ):
                info_lines.append(
                    f"[cyan]Saturation:[/cyan] {generator_config.saturation_adjustment}"
                )

            info_panel = Panel(
                "\n".join(info_lines),
                title="Color Scheme Information",
                border_style="cyan",
            )
            console.print(info_panel)
            console.print()

            special_table = Table(title="Special Colors", show_header=True)
            special_table.add_column("Color", style="cyan")
            special_table.add_column("Preview", width=10)
            special_table.add_column("Hex", style="white")
            special_table.add_column("RGB", style="white")

            special_colors = [
                ("Background", color_scheme.background),
                ("Foreground", color_scheme.foreground),
                ("Cursor", color_scheme.cursor),
            ]

            for name, color in special_colors:
                preview = f"[on {color.hex}]          [/]"
                rgb_str = f"rgb({color.rgb[0]}, {color.rgb[1]}, {color.rgb[2]})"
                special_table.add_row(name, preview, color.hex, rgb_str)

            console.print(special_table)
            console.print()

            terminal_table = Table(title="Terminal Colors (ANSI)", show_header=True)
            terminal_table.add_column("Index", style="cyan", width=6)
            terminal_table.add_column("Name", style="cyan")
            terminal_table.add_column("Preview", width=10)
            terminal_table.add_column("Hex", style="white")
            terminal_table.add_column("RGB", style="white")

            color_names = [
                "Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White",
                "Bright Black", "Bright Red", "Bright Green", "Bright Yellow",
                "Bright Blue", "Bright Magenta", "Bright Cyan", "Bright White",
            ]

            for idx, (name, color) in enumerate(zip(color_names, color_scheme.colors)):
                preview = f"[on {color.hex}]          [/]"
                rgb_str = f"rgb({color.rgb[0]}, {color.rgb[1]}, {color.rgb[2]})"
                terminal_table.add_row(str(idx), name, preview, color.hex, rgb_str)

            console.print(terminal_table)
```

**Step 4: Run tests to verify they pass**

```bash
cd packages/core
uv run pytest tests/integration/test_cli_show.py -v
```

Expected: all tests in the file PASS.

**Step 5: Run full core test suite to check for regressions**

```bash
cd packages/core
uv run pytest -v
```

Expected: all pass.

**Step 6: Commit**

```bash
git add packages/core/src/color_scheme/cli/main.py \
        packages/core/tests/integration/test_cli_show.py
git commit -m "feat(core): add TTY-aware fallback to show command

Renders plain bullet list when stdout is not a terminal (piped,
container without -t). Keeps existing Rich tables for interactive use.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Add `run_show()` to `ContainerManager`

**Context:**
`packages/orchestrator/src/color_scheme_orchestrator/container/manager.py` has
`run_generate()`. We add `run_show()` alongside it. Key differences:
- No `output_dir` / no `/output` volume mount
- TTY flag: pass `-t` to `docker run` only when `sys.stdout.isatty()` is True
- No `capture_output=True` — stdout flows to the terminal

**Files:**
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`
- Modify: `packages/orchestrator/tests/unit/test_container_execution.py`

---

**Step 1: Write the failing tests**

Add a new class to
`packages/orchestrator/tests/unit/test_container_execution.py`:

```python
class TestContainerShow:
    """Tests for run_show container execution."""

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_builds_docker_command(self, mock_run, mock_sys):
        """Test that run_show constructs correct docker show command."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(
            core=AppConfig(),
            orchestrator=ContainerSettings(engine="docker"),
        )
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"
        assert "run" in call_args
        assert "--rm" in call_args
        assert "color-scheme-custom:latest" in call_args
        assert "show" in call_args
        assert "/input/image.png" in call_args

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_no_output_mount(self, mock_run, mock_sys):
        """Test that run_show does not add an /output volume mount."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        call_args = mock_run.call_args[0][0]
        # Find all -v mounts
        v_mounts = [
            call_args[i + 1]
            for i, arg in enumerate(call_args)
            if arg == "-v"
        ]
        assert not any("/output" in m for m in v_mounts)

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_adds_tty_flag_when_interactive(self, mock_run, mock_sys):
        """Test that -t is added to docker command when stdout is a TTY."""
        mock_sys.stdout.isatty.return_value = True
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        call_args = mock_run.call_args[0][0]
        assert "-t" in call_args

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_no_tty_flag_when_non_interactive(self, mock_run, mock_sys):
        """Test that -t is absent when stdout is not a TTY."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=0)

        manager.run_show(
            backend=Backend.CUSTOM,
            image_path=Path("/tmp/test.png"),
        )

        call_args = mock_run.call_args[0][0]
        assert "-t" not in call_args

    @patch("color_scheme_orchestrator.container.manager.sys")
    @patch("subprocess.run")
    def test_run_show_raises_on_failure(self, mock_run, mock_sys):
        """Test that non-zero exit code raises RuntimeError."""
        mock_sys.stdout.isatty.return_value = False
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        mock_run.return_value = Mock(returncode=1)

        with pytest.raises(RuntimeError, match="Container execution failed"):
            manager.run_show(
                backend=Backend.PYWAL,
                image_path=Path("/tmp/test.png"),
            )
```

**Step 2: Run tests to verify they fail**

```bash
cd packages/orchestrator
uv run pytest tests/unit/test_container_execution.py::TestContainerShow -v
```

Expected: FAIL — `run_show` does not exist yet.

**Step 3: Implement `run_show()`**

Add `import sys` at the top of
`packages/orchestrator/src/color_scheme_orchestrator/container/manager.py` (alongside the
existing `import os`). Then add this method to `ContainerManager` after `run_generate()`:

```python
def run_show(
    self,
    backend: Backend,
    image_path: Path,
    cli_args: list[str] | None = None,
) -> None:
    """Execute show command in container.

    Args:
        backend: Backend to use
        image_path: Path to source image
        cli_args: Additional CLI arguments to pass

    Raises:
        RuntimeError: If container execution fails
    """
    if cli_args is None:
        cli_args = []

    image = self.get_image_name(backend)

    # Build volume mounts — image only, no /output (show writes nothing)
    image_mount = f"{image_path.as_posix()}:/input/image.png:ro"
    template_dir = self.config.core.templates.directory
    if not template_dir.is_absolute():
        template_dir = Path.cwd() / template_dir
    templates_mount = f"{template_dir.as_posix()}:/templates:ro"

    cmd = [self.engine, "run", "--rm"]

    # Allocate pseudo-TTY only when the host stdout is a terminal.
    # This lets Rich inside the container detect a terminal and render
    # color tables; without -t the container sees a pipe and falls back
    # to a plain bullet list.
    if sys.stdout.isatty():
        cmd.append("-t")

    # Run as current user to avoid permission issues
    user_id = os.getuid()
    group_id = os.getgid()
    cmd.extend(["--user", f"{user_id}:{group_id}"])

    cmd.extend(["-v", image_mount])
    cmd.extend(["-v", templates_mount])
    cmd.append(image)

    cmd.extend(["show", "/input/image.png"])
    cmd.extend(cli_args)

    result = subprocess.run(cmd)

    if result.returncode != 0:
        raise RuntimeError(
            f"Container execution failed with exit code {result.returncode}"
        )
```

**Step 4: Run tests to verify they pass**

```bash
cd packages/orchestrator
uv run pytest tests/unit/test_container_execution.py -v
```

Expected: all tests in the file PASS.

**Step 5: Run full orchestrator test suite**

```bash
cd packages/orchestrator
uv run pytest -v
```

Expected: all pass.

**Step 6: Commit**

```bash
git add packages/orchestrator/src/color_scheme_orchestrator/container/manager.py \
        packages/orchestrator/tests/unit/test_container_execution.py
git commit -m "feat(orchestrator): add run_show() to ContainerManager

Runs color-scheme-core show inside a container. Passes -t to docker
only when the host stdout is a TTY, so Rich renders colors interactively
and falls back to plain text when piped or scripted.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Rewrite the orchestrator `show` command

**Context:**
`packages/orchestrator/src/color_scheme_orchestrator/cli/main.py` — the `show` function
(starting at line 201) currently has an `import subprocess` block that calls
`color-scheme-core show` on the host. Replace that block with a `ContainerManager`
invocation mirroring the `generate` command pattern.

**Files:**
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`
- Modify: `packages/orchestrator/tests/integration/test_cli_show_delegation.py`

---

**Step 1: Write the failing test**

Replace the contents of
`packages/orchestrator/tests/integration/test_cli_show_delegation.py` with:

```python
"""Integration tests for show command delegation to container."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from color_scheme_orchestrator.cli.main import app

runner = CliRunner()


class TestShowDelegation:
    """Tests for delegating show command to container."""

    def test_show_command_exists(self):
        """Test that show command is registered."""
        result = runner.invoke(app, ["--help"])
        assert "show" in result.output

    def test_show_requires_image_path(self):
        """Test that show command requires image path argument."""
        result = runner.invoke(app, ["show"])
        assert result.exit_code != 0
        assert (
            "Missing argument" in result.output or "required" in result.output.lower()
        )

    @patch("color_scheme_orchestrator.cli.main.ContainerManager.run_show")
    def test_show_calls_container_manager(self, mock_run_show):
        """Test that show routes to ContainerManager.run_show, not a host subprocess."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            result = runner.invoke(
                app, ["show", str(test_image), "--backend", "custom"]
            )

            assert mock_run_show.called
            assert result.exit_code == 0
        finally:
            test_image.unlink()

    @patch("color_scheme_orchestrator.cli.main.ContainerManager.run_show")
    def test_show_does_not_call_host_subprocess_for_core(self, mock_run_show):
        """Test that show no longer calls color-scheme-core on the host."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            with patch("subprocess.run") as mock_subprocess:
                runner.invoke(
                    app, ["show", str(test_image), "--backend", "custom"]
                )
                # subprocess.run should NOT be called for color-scheme-core
                for call in mock_subprocess.call_args_list:
                    args = call[0][0] if call[0] else []
                    assert "color-scheme-core" not in args
        finally:
            test_image.unlink()

    @patch("color_scheme_orchestrator.cli.main.ContainerManager.run_show")
    def test_show_passes_saturation_to_container(self, mock_run_show):
        """Test that --saturation is forwarded as a CLI arg to the container."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            test_image = Path(f.name)

        try:
            runner.invoke(
                app,
                ["show", str(test_image), "--backend", "custom", "--saturation", "1.5"],
            )

            assert mock_run_show.called
            call_kwargs = mock_run_show.call_args[1]
            cli_args = call_kwargs.get("cli_args", [])
            assert "--saturation" in cli_args
            assert "1.5" in cli_args
        finally:
            test_image.unlink()
```

**Step 2: Run tests to verify they fail**

```bash
cd packages/orchestrator
uv run pytest tests/integration/test_cli_show_delegation.py -v
```

Expected: `test_show_calls_container_manager` and
`test_show_does_not_call_host_subprocess_for_core` FAIL because `show` still uses the
host subprocess.

**Step 3: Rewrite the orchestrator `show` command**

In `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`, find the `show`
function body after the `if dry_run:` block and replace everything from
`# Delegate to core - it runs on host, no container needed` to the end of the function
body with:

```python
    try:
        # Load settings
        config = cast(UnifiedConfig, get_config())

        # Validate image path
        if not image_path.exists():
            console.print(f"[red]Error:[/red] Image file not found: {image_path}")
            raise typer.Exit(1)

        if not image_path.is_file():
            console.print(f"[red]Error:[/red] Path is not a file: {image_path}")
            raise typer.Exit(1)

        # Use default backend if not specified
        if backend is None:
            backend = Backend(config.core.generation.default_backend)

        # Build CLI arguments to pass to container
        container_args: list[str] = []

        container_args.extend(["--backend", backend.value])

        if saturation is not None:
            container_args.extend(["--saturation", str(saturation)])

        # Create container manager and execute in container
        manager = ContainerManager(config)

        console.print(f"[cyan]Running in container:[/cyan] {backend.value}")

        manager.run_show(
            backend=backend,
            image_path=image_path,
            cli_args=container_args,
        )

    except typer.Exit:
        raise

    except RuntimeError as e:
        console.print(f"[red]Container error:[/red] {str(e)}")
        raise typer.Exit(1) from None

    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None
```

Also remove the `import subprocess` that was inside the old `show` function body (it was
a local import at the start of the delegation block).

**Step 4: Run tests to verify they pass**

```bash
cd packages/orchestrator
uv run pytest tests/integration/test_cli_show_delegation.py -v
```

Expected: all pass.

**Step 5: Run full orchestrator test suite**

```bash
cd packages/orchestrator
uv run pytest -v
```

Expected: all pass.

**Step 6: Commit**

```bash
git add packages/orchestrator/src/color_scheme_orchestrator/cli/main.py \
        packages/orchestrator/tests/integration/test_cli_show_delegation.py
git commit -m "feat(orchestrator): route show command through container

Replaces host subprocess delegation with ContainerManager.run_show(),
giving show the same isolation guarantee as generate. Backend tools
(pywal, wallust) are no longer required on the host.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Coverage check and smoke test update

**Step 1: Check orchestrator coverage threshold**

```bash
cd packages/orchestrator
uv run pytest --cov=src --cov-report=term
uv run coverage report --fail-under=95
```

Expected: passes at ≥95%.

**Step 2: Check core coverage threshold**

```bash
cd packages/core
uv run pytest --cov=src --cov-report=term
```

Expected: passes at existing threshold.

**Step 3: Update smoke test comment**

In `tests/smoke/run-smoke-tests.sh`, find `test_orchestrator_cli_basic`. The comment
block says `color-scheme show` — no code change needed, but verify the test still passes
locally if Docker is available:

```bash
bash tests/smoke/run-smoke-tests.sh tests/fixtures/test-wallpaper.jpg
```

Expected: `Testing Orchestrator CLI Basic Commands` section passes.

**Step 4: Final commit if anything was updated**

```bash
git add -A
git commit -m "chore: verify coverage and smoke test after show containerization

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```
