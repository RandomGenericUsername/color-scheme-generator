# Show Command Containerization

**Branch:** `experimental/show-containerization`  
**Date:** 2026-03-07  
**Commits:** `996bf7c` → `6405563` → `55f29d2`

---

## What was the problem

The `color-scheme show` command (exposed by the orchestrator) worked differently from
`color-scheme generate`. While `generate` always runs inside a container — meaning the
host machine never needs pywal, wallust, or any other backend tool installed — `show`
bypassed containers entirely and called `color-scheme-core show` directly on the host
via a subprocess.

This created an inconsistency: a user who only has Docker/Podman installed (no backends
on the host) could generate color schemes fine but could not display them. The backends
had to exist on both the host and inside the container image, which defeated the point
of containerization.

---

## What was changed

### 1. Core — TTY-aware output in `show` (`packages/core`)

**File:** `packages/core/src/color_scheme/cli/main.py`

The `show` function previously always rendered Rich tables regardless of whether stdout
was a terminal or a pipe. This was fine for interactive use but broke container
scenarios: when the orchestrator runs `color-scheme-core show` inside a container
without allocating a pseudo-TTY, stdout is a pipe and Rich renders escape sequences that
are unreadable in non-interactive contexts.

The function now branches on `console.is_terminal`:

- **TTY (interactive terminal):** Full existing behaviour — preamble messages
  (`Using backend:`, `Extracting colors from:`, etc.) followed by Rich-formatted
  tables with color previews.
- **Non-TTY (pipe, container without `-t`):** Plain `key: value` bullet list, one
  entry per line, no preamble, no markup:
  ```
  backend: custom
  background: #1a1b26
  foreground: #c0caf5
  cursor: #c0caf5
  color0: #15161e
  color1: #f7768e
  ...
  color15: #c0caf5
  ```
  If a non-default saturation was applied, `saturation: <value>` is included after
  `backend:`.

This output is designed to be machine-readable so scripts can parse it reliably.

**Tests added:** `test_show_non_tty_outputs_bullet_list`, `test_show_tty_outputs_rich_tables`
in `packages/core/tests/integration/test_cli_show.py`.

---

### 2. Orchestrator — `run_show()` in `ContainerManager` (`packages/orchestrator`)

**File:** `packages/orchestrator/src/color_scheme_orchestrator/container/manager.py`

A new `run_show()` method was added alongside the existing `run_generate()`. Key
design decisions:

- **Image-only volume mount.** `show` writes no files, so only the source image is
  mounted (`/input/image.png:ro`). No `/output` and no `/templates` mounts — unlike
  `run_generate()`, which needs all three.

- **Conditional `-t` flag.** A pseudo-TTY is allocated only when `sys.stdout.isatty()`
  is `True` on the host. When the host is interactive, passing `-t` to Docker causes
  the container's stdout to behave like a terminal, so Rich inside the container detects
  a TTY and renders the full color table. When the host is piped/scripted, `-t` is
  omitted and the container falls back to the plain bullet list automatically.

- **No `capture_output`.** Unlike `run_generate()`, which captures stdout/stderr to
  parse errors, `run_show()` lets the container's stdout flow directly to the host
  terminal. This is what makes the color output actually appear.

**Tests added:** `TestContainerShow` class (6 tests) in
`packages/orchestrator/tests/unit/test_container_execution.py`, covering command
construction, absent output/templates mounts, TTY flag presence/absence, and failure
handling.

---

### 3. Orchestrator — rewired `show` command (`packages/orchestrator`)

**File:** `packages/orchestrator/src/color_scheme_orchestrator/cli/main.py`

The `show` command previously contained an inline `import subprocess` and called
`["color-scheme-core", "show", ...]` directly on the host. This was replaced with:

```python
manager = ContainerManager(config)
manager.run_show(
    backend=backend,
    image_path=image_path,
    cli_args=container_args,
)
```

The orchestrator itself emits no informational messages during `show` — only error
messages if something fails. All visible output (the bullet list or the Rich tables)
comes from inside the container.

**Tests updated:**
- `packages/orchestrator/tests/integration/test_cli_show_delegation.py` — replaced
  the two original stub tests with a full `TestShowDelegation` suite (5 tests) that
  verifies `ContainerManager.run_show` is called, the host subprocess is not called for
  core, and arguments are forwarded correctly.
- `packages/orchestrator/tests/unit/test_main_commands.py` — the `TestShowDelegation`
  and `TestShowErrorHandling` classes were rewritten to mock `ContainerManager.run_show`
  instead of `subprocess.run`, reflecting the new contract.

---

## Why this approach

The TTY-propagation mechanism (`-t` flag + `console.is_terminal` branch) is the
standard way to handle this in containerized CLI tools. It requires no extra protocol
or intermediate format — the container just behaves differently depending on whether it
sees a terminal or a pipe, which is the same thing native Unix tools do.

Keeping the plain bullet list machine-readable (one `key: value` per line) was a
deliberate choice. Scripts that consume `color-scheme show` output can parse it with
`grep`, `awk`, or `cut` without depending on Rich's table format.

---

## Coverage

| Package | Tests | Coverage |
|---------|-------|----------|
| `color-scheme-core` | 289 passed | 97% |
| `color-scheme-orchestrator` | 115 passed | 97% |

Both packages remain above the 95% minimum threshold.
