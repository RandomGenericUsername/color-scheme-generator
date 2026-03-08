# Design: Containerize `show` Command

**Date:** 2026-03-06
**Status:** Approved

## Problem

The orchestrator's `show` command currently delegates to `color-scheme-core show` via a
host subprocess. This breaks the container isolation guarantee: for `--backend pywal` or
`--backend wallust`, the `wal` / `wallust` binaries must exist on the host. Both backends
also write side effects to `~/.cache/wal/` and `~/.cache/wallust/` respectively.

Only `--backend custom` happened to be safe on the host (pure Python, no external
binaries, no cache writes).

The `generate` command already runs fully in a container. `show` must too, so the
contract is consistent: **the orchestrator never requires backend tools on the host**.

## Chosen Approach

**TTY-aware container execution + explicit fallback in core.**

The host knows whether it has a terminal via `sys.stdout.isatty()`. This value is used to
decide whether to pass `-t` (pseudo-TTY) to `docker run`. Inside the container,
`color-scheme-core show` checks `Console().is_terminal` to decide between Rich tables and
a plain bullet list. The host's TTY state therefore propagates naturally to the
container's rendering behavior without any extra signaling.

## Flow

### Interactive terminal

```
color-scheme show wallpaper.jpg
  → sys.stdout.isatty() = True
  → docker run -t color-scheme-<backend>:latest show /input/image.png
      → Console().is_terminal = True  (pseudo-TTY allocated)
      → Rich tables with color swatches rendered
      → stdout streams to host terminal
```

### Non-interactive (script / CI / pipe)

```
color-scheme show wallpaper.jpg
  → sys.stdout.isatty() = False
  → docker run color-scheme-<backend>:latest show /input/image.png  (no -t)
      → Console().is_terminal = False  (stdout is a pipe)
      → simple bullet list rendered:
          background: #1a1a2e
          foreground: #c0caf5
          color0: #15161e
          ...
      → plain text flows through pipe
```

## Changes

### 1. `packages/core/src/color_scheme/cli/main.py`

In the `show` command, after color extraction and saturation adjustment, replace the
unconditional Rich table rendering with a TTY branch:

```python
console = Console()
if console.is_terminal:
    # existing Rich panels, special_table, terminal_table (unchanged)
else:
    print(f"backend: {backend.value}")
    print(f"background: {color_scheme.background.hex}")
    print(f"foreground: {color_scheme.foreground.hex}")
    print(f"cursor: {color_scheme.cursor.hex}")
    for i, color in enumerate(color_scheme.colors):
        print(f"color{i}: {color.hex}")
```

No other core files are touched.

### 2. `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`

New `run_show()` method alongside `run_generate()`:

```python
def run_show(
    self,
    backend: Backend,
    image_path: Path,
    cli_args: list[str] | None = None,
) -> None:
```

Differences from `run_generate()`:
- No `output_dir` parameter
- Only two volume mounts: image (`:ro`) and templates (`:ro`) — no `/output`
- TTY flag: `import sys` → add `-t` to the command only if `sys.stdout.isatty()`
- No `capture_output=True` — stdout streams directly to the calling terminal
- Container subcommand: `show /input/image.png` instead of `generate /input/image.png`

### 3. `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`

In the `show` function, replace the host subprocess block:

```python
# before
subprocess.run(["color-scheme-core", "show", str(image_path), ...])

# after
manager = ContainerManager(config)
manager.run_show(
    backend=backend,
    image_path=image_path,
    cli_args=container_args,
)
```

Backend defaulting logic (fall back to `config.core.generation.default_backend` if none
specified) mirrors the `generate` command exactly.

## Tests

### Unit — `packages/orchestrator/tests/unit/test_container_execution.py`

Add `TestContainerShow` class:
- Verify `docker run` is called with `show` subcommand
- Verify no `-v /output` mount is present
- Verify `-t` is present when `sys.stdout.isatty()` is mocked to `True`
- Verify `-t` is absent when `sys.stdout.isatty()` is mocked to `False`
- Verify `RuntimeError` raised on non-zero exit code

### Unit — `packages/core/tests/`

Add test for `show` TTY fallback:
- Mock `Console().is_terminal = False`
- Assert output is plain `key: value` lines, not Rich markup

### Smoke test

`test_orchestrator_cli_basic` already invokes `color-scheme show` — it will now exercise
the container path end-to-end when Docker is available.

## What Does Not Change

- `generate` command — untouched
- `install` / `uninstall` commands — untouched
- All three Dockerfiles — entrypoints are already `color-scheme-core`, correct as-is
- Dry-run path for `show` — already runs on host (no container needed, no side effects)
- The `custom` backend behavior — still works, just now runs in a container like the others
