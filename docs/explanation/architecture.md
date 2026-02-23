# Explanation: Architecture and Design Concepts

This document explains the key concepts behind color-scheme's design: the two-CLI
architecture, backend auto-detection order, the layered settings system, and the
container isolation model.

## Concepts

### Two CLIs: core and orchestrator

The project provides two separate command-line entry points:

- **`color-scheme-core`** — Direct execution. Runs backend binaries (pywal, wallust,
  or a built-in Python implementation) directly on the host system. Fast startup,
  no container overhead, but requires backend tools to be installed on the host.

- **`color-scheme`** (orchestrator) — Container-based execution. Runs
  `color-scheme-core` inside a Docker or Podman container image. Backend dependencies
  are isolated inside the container, keeping the host system clean. Slower (container
  startup adds overhead), but backend installation is managed once via
  `color-scheme install`.

The `show` command is an exception: the orchestrator's `show` delegates directly to
the core CLI on the host, because terminal color display must happen in the calling
terminal, not inside a container.

### Three backends

| Backend | Binary | Availability | Algorithm |
|---------|--------|-------------|-----------|
| `wallust` | `wallust` | Optional (external) | K-means with perceptual weighting |
| `pywal` | `wal` | Optional (external) | Multiple algorithms (Haishoku, etc.) |
| `custom` | none | Always available | K-means clustering on resized image |

The `custom` backend is a pure Python implementation that requires no external
binaries. It always serves as the final fallback.

### Backend auto-detection order

When no `--backend` flag is provided, the `BackendFactory` tests each backend in a
fixed order:

1. **wallust** — checked first
2. **pywal** — checked second
3. **custom** — always available, used if neither of the above is found

The first backend whose binary is present in PATH is selected and used. This means
that if `wallust` is installed, it always wins over `pywal`. To use a specific backend,
pass `-b pywal` or `-b custom` explicitly.

This order is enforced in code and confirmed by tests: when all three backends are
available, `auto_detect()` returns `Backend.WALLUST`.

### The 16-color constraint

`ColorScheme.colors` always contains exactly 16 `Color` objects. This matches the
16 standard ANSI terminal color slots (indices 0–15). It is a hard validation
constraint — creating a `ColorScheme` with 15 or 17 colors raises `ValueError`.

`GeneratorConfig.color_count` is hardcoded to 16 and is not configurable at runtime.

---

## Mental model

### Settings layers as an override stack

Think of the configuration as a stack where each layer can selectively override the
layer below it:

```
┌──────────────────────────────────────┐  highest priority
│  CLI overrides  (get_config/flags)   │
├──────────────────────────────────────┤
│  COLORSCHEME_* environment variables │
├──────────────────────────────────────┤
│  User config (~/.config/…)           │
├──────────────────────────────────────┤
│  Project config (./settings.toml)    │
├──────────────────────────────────────┤
│  Package defaults (built-in TOML)    │  lowest priority
└──────────────────────────────────────┘
```

Any key set in a higher layer overrides the same key in all lower layers. Keys not
set in a higher layer inherit their values from below.

**List values are replaced, not merged.** If the user config sets
`formats = ["json", "sh"]`, the entire default formats list is discarded and replaced
by `["json", "sh"]`. This prevents accidental inheritance of formats from a lower layer
when a user explicitly limits output.

### Config caching

`load_config()` returns a cached result. The same validated object is returned on every
subsequent call in the same process. This design avoids redundant file reads and
Pydantic validation on every command invocation.

When settings files change (primarily in tests), call `reload_config()` to clear the
cache and reload from disk.

### Container image naming

Container image names follow a fixed pattern: `color-scheme-<backend>:latest`. This
name is predictable — it does not change between versions by default — making it
straightforward to check whether an image is already built.

When a registry is configured, a prefix is prepended:
`<registry>/color-scheme-<backend>:latest`. Trailing slashes in the registry name are
stripped before the image name is assembled.

---

## Rationale

### Why separate core and orchestrator packages?

Separating the two CLIs means the core package has no container dependencies. Users who
control their own environment and want to install pywal or wallust directly can use
`color-scheme-core` without ever installing Docker or Podman.

The orchestrator is an optional layer for users who prefer dependency isolation or work
in environments where direct binary installation is impractical.

### Why wallust before pywal in auto-detection?

The detection order reflects a preference for tools that tend to produce more
consistent results on modern systems. The order is a deliberate default, not an
arbitrary one, and it can be overridden by passing `-b pywal` explicitly.

### Why exactly 16 colors?

The 16-color constraint maps directly to the 16 standard ANSI terminal color slots.
Tools that consume color schemes (terminal emulators, theme generators, shell
integrations) all expect exactly these 16 entries. Allowing fewer would leave undefined
slots; allowing more would require callers to know how to handle extras.

### Why does dry-run bypass uninstall confirmation?

The confirmation prompt exists to prevent accidental data loss in interactive sessions.
Dry-run mode is explicitly a preview mode — its intent is to show what would happen, not
to do it. Showing a confirmation for an action that will never run would be misleading.
Bypassing it also makes dry-run useful in non-interactive scripts.


---

## See also

- [Getting Started tutorial](../tutorials/getting-started.md) — see the CLIs in action
- [color-scheme-core CLI reference](../reference/cli-core.md) — detailed command reference
- [color-scheme CLI reference](../reference/cli-orchestrator.md) — orchestrator command reference
