# How-to: Use Dry-Run Mode

Dry-run mode lets you inspect what a command will do without executing any side effects
(no files written, no container images built or removed, no confirmation prompts shown).

Both the core CLI (`color-scheme-core`) and the orchestrator CLI (`color-scheme`) support
dry-run on all applicable commands.

## Prerequisites

- `color-scheme-core` and/or `color-scheme` installed.

## Steps

### Core CLI: generate --dry-run

```bash
color-scheme-core generate /path/to/image.jpg --dry-run
```

Or equivalently with the short flag:

```bash
color-scheme-core generate /path/to/image.jpg -n
```

Expected behavior:
- Exit code 0.
- Stdout contains "DRY-RUN", "Execution Plan", and "color-scheme-core generate".
- No files are created in the output directory.

### Core CLI: show --dry-run

```bash
color-scheme-core show /path/to/image.jpg --dry-run
```

Expected behavior:
- Exit code 0.
- Stdout contains "DRY-RUN" and "Execution Plan".
- The terminal colors section ("Terminal Colors (ANSI)") is NOT displayed.

### Orchestrator CLI: generate --dry-run

```bash
color-scheme generate /path/to/image.jpg --dry-run
```

Same semantics as the core `generate --dry-run`: shows the execution plan, does not
launch a container or write files.

### Orchestrator CLI: install --dry-run

```bash
color-scheme install custom --dry-run
```

Or with `-n`:

```bash
color-scheme install custom -n
```

Expected behavior:
- Exit code 0.
- Stdout contains "DRY-RUN" and "Build Plan".
- No container image is built.

### Orchestrator CLI: uninstall --dry-run

```bash
color-scheme uninstall custom --dry-run
```

Expected behavior:
- Exit code 0.
- The "Are you sure?" confirmation prompt is NOT shown.
- No container images are removed.

Dry-run bypasses the confirmation step entirely, which means it also works correctly when
stdin is not a tty (useful in scripts).

## Verification

| Behavior | Expected |
|----------|----------|
| `color-scheme-core generate --dry-run` exits 0, no files created | BHV-0004, BHV-0006 |
| `-n` is an alias for `--dry-run` | BHV-0005 |
| `color-scheme-core show --dry-run` suppresses color tables | BHV-0008 |
| `color-scheme install --dry-run` shows "Build Plan", exits 0 | BHV-0029 |
| `color-scheme uninstall --dry-run` skips confirmation, exits 0 | BHV-0030 |
