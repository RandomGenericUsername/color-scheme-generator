# csg-stale-container-sweep

## Why

Container-mode `csg generate` and `csg show` create a detached wrapper container, exec the inner
`csg` in it, and remove the wrapper only from an in-process `finally`. If the host loses power or the
host-side `csg` process is `SIGKILL`ed, that `finally` never runs. The detached container survives
as a running or exited container, and no later `csg` invocation removes it because the container is
not labelled as csg-owned.

The dotfiles runtime cannot repair this: its charter deliberately does not invoke `podman`/`docker`
directly, and its timeout path (dotfiles `BUG-002`, fixed separately) only covers the normal timeout
it can observe. Container lifecycle is owned by this repo, so the sweep belongs here.

Evidence: `src/color_scheme_generator/adapters/oci_container_runtime.py:43-70` builds a
`RunConfig(detach=True, remove=False)` and removes the container only in `finally`; the
`ContainerProcessor` passes no labels (`src/color_scheme_generator/adapters/container_processor.py:242-250`,
`:389-397`). A host `SIGKILL` was observed leaving a running wrapper with only
`io.buildah.version` in its labels; a subsequent `csg generate` did not remove it.
Verify: `bash tickets/BUG-001-csg-stale-container-sweep/repro.sh` (stale-labelled simulation) and
the SIGKILL transcript in the ticket.

## What Changes

- Label every container-mode wrapper with a csg ownership marker and run metadata:
  `csg.managed=true`, `csg.session=<uuid4>`, `csg.created_at=<RFC3339 UTC>`,
  `csg.timeout_seconds=<int>`, and `csg.boot_id=<host boot id>` when readable.
- Before creating a new wrapper, sweep containers filtered by `label=csg.managed=true`:
  - remove a labelled wrapper from a previous boot immediately;
  - remove a same-boot labelled wrapper only after its own timeout label plus a 60 s grace;
  - skip young same-boot wrappers (concurrent runs), containers without the ownership label, and
    containers whose age cannot be established.
- Make the sweep best-effort: list/inspect/remove failures are logged and never fail a generation.
- Use `name` from the filtered list and `inspect` for labels/created time instead of trusting the
  list payload, because oci-runtime v0.5.0's Docker list parser returns an empty `id` and a
  comma-separated string for `Labels`; Docker's inspect payload is normalised to a mapping.
- Keep the existing `finally` removal. The sweep is the crash/power-loss recovery path, not a
  replacement for normal cleanup.
- No timer, systemd unit, host provisioning, or runtime change is required for this first slice.
- No unlabelled or foreign container is ever removed, including a manual container run from a csg
  image.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `csg-container-mode`: add the managed-wrapper labels and the startup sweep requirement, including
  the normal-run, stale, previous-boot, live-concurrent, foreign-container and best-effort scenarios.

## Impact

- `src/color_scheme_generator/ports/container_runtime.py` — inventory/removal methods and a `labels`
  argument on `run`.
- `src/color_scheme_generator/adapters/oci_container_runtime.py` — pass labels into `RunConfig`;
  expose filtered list, inspect-by-name and remove.
- `src/color_scheme_generator/adapters/container_processor.py` — generate a session id, call the
  sweep before image preflight, pass labels into `run`.
- `tests/unit/adapters/`, `tests/unit/ports/` — fake-runtime and protocol updates plus the
  regression suite.
- No public CLI flag, image, Dockerfile, template, invocation-contract or dependency change.
- Out of scope: csg version bump/tag/release, the dotfiles-v3 pin and engine release, any
  `dotfiles-v3`/`ags-apps`/runtime edit, host provisioning, timers, and fixes to the oci-runtime
  Docker list parser.
