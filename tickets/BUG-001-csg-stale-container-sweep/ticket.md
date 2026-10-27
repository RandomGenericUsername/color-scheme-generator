---
id: BUG-001
title: "Sweep stale csg containers left by host SIGKILL or power loss"
kind: bug
status: in-progress
lane: 2
severity: medium
links:
  openspec: csg-stale-container-sweep
  bmad: none
worktree: .worktrees/BUG-001/
branch: ticket/BUG-001-csg-stale-container-sweep
repro: "bash tickets/BUG-001-csg-stale-container-sweep/repro.sh"
observed: "A host SIGKILL leaves the detached wrapper running with no csg labels; a later successful csg generate leaves it in place. A pre-existing container carrying the intended csg labels also survives a normal run."
expected: "The next container-mode csg run sweeps stale csg-labelled wrappers (previous boot immediately; same boot after timeout+grace), leaves young/unlabelled/foreign containers alone, and never fails the run on sweep errors."
---

# Sweep stale csg containers left by host SIGKILL or power loss

## Triage

- **Kind:** bug — reproducible, bounded, and no architectural unknown.
- **Lane:** 2 (openspec-single) — one item plus one bounded OpenSpec change
  (`csg-stale-container-sweep`, delta on `csg-container-mode`). This is a single recovery behaviour,
  not a multi-part feature, so lane 3/BMAD would be overkill.
- **Severity:** medium — a leaked stopped/running wrapper is not data loss, but repeated crashes
  accumulate containers, disk, and confusing `podman ps -a` output, and the runtime explicitly
  cannot clean them up. No user-visible palette failure in normal flows.
- **Status:** `triage`; this planning commit contains no code, no tag, and no release. The next
  session starts the fix with a status-only `in-progress` commit, then implements.

## Repro

### Deterministic stale-container repro

From a synced checkout with a built csg backend image:

```bash
make sync
ENGINE=podman bash tickets/BUG-001-csg-stale-container-sweep/repro.sh
```

The script creates `csg-bug001-stale` with the labels the fix will use, runs a **normal**
container-mode `csg generate`, and prints the labelled inventory before and after. It accepts
`ENGINE=docker`, `CSG_TAG=...`, `CSG_BACKEND=...`, and `CSG_REPRO_ROOT=...`; it never removes the
stale container, so the observation is not hidden by its own cleanup. The script is prototype
evidence, not product code.

### Host SIGKILL / power-loss equivalent

The real failure is not the labelled simulation; it is a host `SIGKILL` during a run. The wrapper is
created detached with `remove=False`, so when the host process dies the engine keeps the container
and the in-process `finally` cannot run:

```bash
ROOT=/tmp/opencode/csg-bug001-kill
mkdir -p "$ROOT/out"
env COLORSCHEME__RUNTIME__MODE=container COLORSCHEME__GENERATION__BACKEND=wallust \
  COLORSCHEME__CONTAINER__ENGINE=podman COLORSCHEME__CONTAINER__IMAGE_TAG=v0.2.0 \
  COLORSCHEME__OUTPUT__DIRECTORY="$ROOT/out" \
  .venv/bin/csg generate /tmp/opencode/csg-bug001-repro/wallpaper.png \
    --format yaml --backend wallust --container-engine podman &
CSG_PID=$!
# wait until podman ps shows the detached wrapper, then:
kill -9 "$CSG_PID"
podman ps -a --filter ancestor=localhost/csg-wallust-podman:v0.2.0 \
  --format '{{.Names}}|{{.State}}|{{.Status}}|{{.Labels}}'
```

A power loss is the same state with a colder host: the engine stops the container during boot and
the container remains in `podman ps -a` as `Exited`; no later `csg` command knows it is csg-owned.
`podman stop` on the wrapper is a deterministic stand-in for the power-off half; the missing
`finally` is the code half.

### How to observe

```bash
podman ps -a --filter label=csg.managed=true \
  --format '{{.Names}}|{{.State}}|{{.Labels}}'
podman ps -a --filter name=csg --format '{{.Names}}|{{.State}}|{{.Status}}'
```

Before the fix the stale container is in both outputs. After the fix the next container-mode
`generate`/`show` must remove the first, and a normal run must leave the inventory empty.

## Observed

Deterministic repro on this host (podman, wallust, `v0.2.0`), `csg exit: 0`:

```text
--- before the csg run ---
csg-bug001-stale|created|csg.created_at=2026-01-01T00:00:00Z,csg.managed=true,csg.session=00000000-0000-4000-8000-000000000000,csg.timeout_seconds=300,io.buildah.version=1.45.1
--- after the csg run ---
csg-bug001-stale|created|csg.created_at=2026-01-01T00:00:00Z,csg.managed=true,csg.session=00000000-0000-4000-8000-000000000000,csg.timeout_seconds=300,io.buildah.version=1.45.1
```

Real host `SIGKILL` (the wrapper is the one `csg` just created; it has no csg labels):

```text
--- wrapper immediately after host SIGKILL ---
objective_keldysh|running|Up Less than a second|io.buildah.version=1.45.1
--- next normal csg run ---
second_run_exit=0
--- wrapper after the next normal csg run ---
objective_keldysh|running|Up 11 seconds|io.buildah.version=1.45.1
```

The unlabelled wrapper also survives a subsequent successful run, which is expected today because
nothing looks for it. A clean normal run with no stale container leaves no csg wrapper:

```text
csg_exit=0
--- csg-labeled containers after a clean normal run ---
(no output)
--- all containers whose name contains csg ---
(no output)
```

### Root cause (code evidence)

- `src/color_scheme_generator/adapters/oci_container_runtime.py:43-70` creates the wrapper with
  `detach=True, remove=False` and removes it only in `finally`.
- `src/color_scheme_generator/adapters/container_processor.py:242-250` and `:389-397` call `run`
  with image/command/mounts/timeout/environment/memory only; no labels, no session id.
- `src/color_scheme_generator/ports/container_runtime.py:14-42` has no list/inspect/remove
  operation, so there is no way for a later process to identify a csg-owned wrapper.

A host `SIGKILL` or power loss skips the `finally`; the engine keeps the detached container.
Runtime-side context (handoff from the runtime owner, not re-verified in this repo): the dotfiles
runtime deliberately does not invoke podman/docker, so container lifecycle cleanup belongs to this
repo.

## Expected

- Every container-mode `generate`/`show` wrapper is labelled `csg.managed=true` plus a per-run
  `csg.session`, creation time, timeout, and (when readable) boot id.
- Before creating a new wrapper, `csg` removes stale csg-labelled wrappers:
  - previous boot: immediately;
  - same boot: only after the wrapper's own timeout plus 60 s grace;
  - young same-boot: kept (a concurrent run may own it);
  - unlabelled, foreign-labelled, or unknown-age: always kept.
- A sweep failure is logged and never fails the palette run.
- A normal run still removes its own wrapper in `finally` and leaves no csg-labelled container.
- No timer, systemd unit, host provisioning, runtime change, or CLI flag is required for this slice.

## Design options

### Option A — label + startup sweep (recommended)

Label every wrapper and, at the start of every container-mode run, list `label=csg.managed=true`
and remove stale labelled wrappers by age, with a previous-boot fast path from `csg.boot_id`.

- **Pros:** no daemon/timer; every run self-heals; the label is an explicit ownership boundary;
  works with both docker and podman through the existing `oci-runtime`; small code surface.
- **Cons:** a stale wrapper younger than the threshold waits for a later run; age policy needs
  care for long-running concurrent jobs (solved by the per-container timeout label and grace).
- **Dependencies:** `oci-runtime` v0.5.0 already supports `RunConfig.labels`, filtered
  `containers.list`, `inspect` and `remove`. No sibling change required.

### Option B — label + reconcile sweep (lease/registry)

Write a per-run lease under `XDG_RUNTIME_DIR/csg/sessions/<uuid>.json` (owner pid, boot id,
created); at startup remove labelled wrappers with no live lease. After a reboot the runtime dir is
tmpfs and clears, so every labelled wrapper from the previous boot is immediately stale.

- **Pros:** precise same-boot orphan detection; immediate after a crash; no age guessing; can grow
  into a `csg reconcile` verb.
- **Cons:** file lifecycle, permissions, PID reuse, stale lease files, cross-user and
  `XDG_RUNTIME_DIR`-missing cases; more tests and failure modes. A broken lease store becomes a new
  reason cleanup fails.
- **Dependencies:** none new, but it is a larger first slice.

### Option C — best-effort age fallback (no ownership label)

Match containers by image name (`csg-*-<engine>:<tag>`) and age, and remove old ones even when
unlabelled.

- **Pros:** can clean containers created by older csg versions that never labelled; no new label
  contract.
- **Cons:** cannot distinguish a manual `podman run csg-base-podman:v0.2.0` from a csg-owned
  wrapper; can delete a user's deliberately kept container; violates the acceptance that
  unlabelled/foreign containers are untouched. It is unsafe as a primary policy.
- **Verdict:** reject. Keep a fallback only **within the labelled set** (if the engine `created`
  value is unparseable, try `csg.created_at`; if both fail, skip).

### Comparison

| Criterion | A: label + startup sweep | B: label + lease reconcile | C: age-only fallback |
| --- | --- | --- | --- |
| Power-loss cleanup | Previous boot immediate; same boot after threshold | Immediate | Guesses by age/image |
| Concurrent run safety | Per-container timeout + 60 s grace | Lease owner liveness | Unsafe |
| Foreign/manual containers | Untouched (no label) | Untouched (no label) | Can be removed |
| New state/daemon | None | Session files | None |
| Implementation size | Small | Medium/large | Small but unsafe |
| Recommendation | **Yes, first slice** | Later if same-boot precision is needed | No |

## Recommended design (Option A, with boot-id fast path)

### Label contract

| Label | Value | Why |
| --- | --- | --- |
| `csg.managed` | `true` | The only sweep filter; explicit ownership |
| `csg.session` | `uuid4()` | Correlate a wrapper with a run; future reconcile |
| `csg.created_at` | RFC3339 UTC | Diagnostics and age fallback |
| `csg.timeout_seconds` | settings timeout at creation | Per-container staleness budget |
| `csg.boot_id` | `/proc/sys/kernel/random/boot_id` when readable | Previous-boot/power-loss fast path |

No secrets or user data are stored. The label is reserved: a container carrying
`csg.managed=true` is opting into csg ownership.

### Sweep algorithm

At the start of `ContainerProcessor.process_generate` and `process_show`, after settings are
resolved and **before** `image_exists`:

1. `list_containers(filters={"label": "csg.managed=true"}, show_all=True)`.
2. For each candidate, `inspect_container(name)` (use **name**, not the list id — see D4 quirk).
3. Skip if `labels.get("csg.managed") != "true"` or `labels.get("csg.session") == current_session`.
4. If both `csg.boot_id` and the current boot id are non-empty and differ, remove.
5. Otherwise parse `created`; if that fails, parse `csg.created_at`; if both fail, skip.
6. `timeout = int(csg.timeout_seconds)` else the current settings timeout.
7. Remove only if `now - created > timeout + 60 s`.
8. Remove with `force=True`; catch per-container errors, log, continue. A failure to list/inspect
   is logged and swallowed; the requested run proceeds.

The 60 s grace covers engine timestamp granularity and a host that is slow to start the next run.
The container's own timeout label prevents a shorter second run from killing a legitimately long
first run. A previous-boot wrapper cannot be live, so it is removed immediately.

### Ordering and concurrency

- Run the sweep before image preflight: a missing backend image must not block cleanup.
- A young same-boot wrapper is left alone; two concurrent `csg` runs therefore do not kill each
  other.
- A wrapper older than its timeout plus grace is stale by definition: the normal runtime timeout
  path would already have attempted cleanup.
- The existing `finally` removal remains; the sweep is crash recovery, not a replacement.

### Engine specifics (evidence-backed)

`oci-runtime` v0.5.0 supports the needed surface, but its Docker **list** parser has two quirks:
Docker reports `ID` while the parser reads `Id` (so `ContainerInfo.id` is empty), and Docker list
`Labels` is a comma-separated string while only inspect yields a mapping. Therefore:

- use the **name** from the filtered list for inspect/remove;
- use **inspect** for labels and `created`;
- normalise a non-mapping list `labels` value to `{}` in the csg adapter.

This is a csg-side workaround; fixing the sibling parser is a separate repo change, not a
prerequisite.

### Port/adapter shape

- `domain/models.py`: frozen `ManagedContainer(name, state, labels, created)`.
- `ports/container_runtime.py`: add `labels` to `run` (last parameter), plus
  `list_containers(filters=None, show_all=True)`, `inspect_container(name)` and
  `remove_container(name, force=True)`.
- `adapters/oci_container_runtime.py`: pass `labels` into `RunConfig`; implement the three methods;
  map `oci_runtime` `ContainerInfo` to `ManagedContainer`; normalise Docker list labels.
- `adapters/container_processor.py`: generate the session id, build labels, sweep, pass labels to
  `run` in both verbs.
- Tests: update `_FakeContainerRuntime` and the `MockRuntime` protocol fixture; add focused unit
  tests for the adapter and processor.

## Acceptance / tests

- [ ] Normal run leaves no csg-labelled wrapper:
  `uv run pytest tests/unit/adapters/test_stale_container_sweep.py -q` (normal-run case) and a
  real-engine run with `podman ps -a --filter label=csg.managed=true` empty afterward.
- [ ] Stale labelled container is removed: a labelled wrapper older than `timeout+grace` is gone
  after the next successful `generate`/`show`, and the run still succeeds.
- [ ] Previous-boot labelled container is removed immediately even when young.
- [ ] Young same-boot labelled container is kept (concurrent-run safety).
- [ ] Unlabelled container from a csg image and a foreign-labelled container are untouched.
- [ ] Unknown age is skipped, not guessed.
- [ ] Sweep failure does not block generation; the requested run proceeds.
- [ ] Sweep runs before image preflight: a missing image still leaves the stale wrapper removed.
- [ ] The `repro.sh` command passes after the fix: stale container gone, `csg exit: 0`.
- [ ] `make gates` → exit 0; `openspec validate csg-stale-container-sweep --strict` → valid.
- [ ] Real-engine acceptance recorded in this ticket for both podman and, when available, docker:
  stale removed; unlabelled/foreign untouched; normal run leaves none.

Planned test files:

- `tests/unit/adapters/test_stale_container_sweep.py` — processor policy with a fake runtime:
  normal, stale, previous boot, young, foreign/unlabelled, missing age, inventory failure,
  preflight order, `show`.
- `tests/unit/adapters/test_oci_container_runtime_labels.py` — adapter: labels into `RunConfig`,
  filter/`show_all` forwarding, inspect-by-name, Docker string labels, remove force.
- `tests/unit/ports/test_contracts.py` and `tests/unit/ports/test_interfaces.py` — port shape and
  fake updates.
- `tests/unit/adapters/test_container_processor.py` — existing fake gains the new methods; existing
  assertions stay green.

## Release / pin chain (documented follow-up, not this ticket)

This planning ticket must not tag, release, or edit another repo. After the fix and its regression
tests are green on `main`:

1. **csg release:** bump `pyproject.toml` and `CHANGELOG.md` to `0.2.1` (patch; behavior fix, no
   public API change), run `make gates && make build && make image`, annotate tag `v0.2.1`, let tag
   CI attach the sdist/wheel to the GitHub Release. The image tags become
   `csg-{base,custom,pywal,wallust}-<engine>:v0.2.1`.
2. **dotfiles-v3 pin:** in `provisioning/cli-tools.yaml`, move the `csg` entry from the current tag
   to `v0.2.1`; mirror the same `v0.2.1` image tag wherever provisioning renders
   `[container] image_tag` (and in the `verify` image assertions), then run the provisioning
   dry-run/verify. `provisioning/assets.yaml` template-catalog pin is unchanged because no template
   changed.
3. **Engine release:** rebuild/release the dotfiles runtime engine image that carries the new csg
   pin and its image-tag mirror; verify `csg --version` in the engine and that the four
   `v0.2.1` images exist.
4. **v3 pin:** bump the v3 manifest/engine pin to the released engine tag; deploy on a test host and
   run the normal + SIGKILL/reboot stale-container checks. Keep the runtime's timeout path
   (dotfiles `BUG-002`) unchanged; it is already fixed.

## Out of scope

- Any code in this planning ticket; no csg tag/release, no version bump, no CHANGELOG.
- `dotfiles-v3`, `ags-apps`, the runtime, and host provisioning edits; no timer/systemd/cron.
- Fixing the runtime timeout path (dotfiles `BUG-002` is done) or invoking podman from the runtime.
- Removing unlabelled containers or containers from older csg versions; operators may remove those
  manually.
- Fixing the `oci-runtime` Docker list parser; this change works around it via inspect-by-name.
- A public `csg clean`/`reconcile` verb; it can be a follow-up once the label contract is stable.

## Evidence

| Claim | Command | Observed |
| --- | --- | --- |
| wrapper is detached and removed only in-process | `sed -n '43,70p' src/color_scheme_generator/adapters/oci_container_runtime.py` | `detach=True`, `remove=False`; `finally: ... containers.remove(container_id, force=True)` |
| processor passes no ownership labels | `sed -n '242,250p' src/color_scheme_generator/adapters/container_processor.py` | `run(image=..., command=..., mounts=..., timeout=..., environment=..., memory_limit=...)` only |
| port has no inventory/removal | `sed -n '14,42p' src/color_scheme_generator/ports/container_runtime.py` | `run`, `image_exists`, `pull_image`, `build_image`, `remove_image` only |
| oci-runtime v0.5.0 is the lock pin and supports labels/inventory | `git -C /tmp/opencode/oci-runtime rev-parse v0.5.0`; `git -C /tmp/opencode/oci-runtime rev-parse 'v0.5.0^{commit}'`; `rg -n "labels|def list|def inspect|def remove" /tmp/opencode/oci-runtime/src/oci_runtime/{domain/types.py,ports/managers.py,adapters/managers/container.py}` | tag `38ce267c…` peels to `b631dfa5…`; `RunConfig.labels` at `types.py:137`; `-l` at `container.py:155-156`; `list/inspect/remove` at `managers.py:74-91` |
| podman filtered list + inspect + remove works | create a labelled container; `.venv/bin/python` uses `RuntimeFactory` + `containers.list(show_all=True, filters={"label":"csg.managed=true"})` + `inspect` + `remove` | `count 1`; `csg-bug001-probe created {'csg.managed': 'true', 'csg.session': '…'}`; `removed` |
| docker filtered list + inspect by name works, with parser quirks | create a labelled docker container; same Python probe | list `repr(id) ''`, `name csg-bug001-probe-docker`, `labels` is `str`; inspect `{'csg.managed': 'true', ...}`; `removed` |
| `RunConfig.labels` reaches both engines | `containers.run(RunConfig(..., labels={"csg.managed":"true","csg.session":"…"}))` on podman and docker | podman `labels {'csg.managed':'true','csg.session':'…','io.buildah.version':'…'} state running`; docker `labels {'csg.managed':'true','csg.session':'…'} state running` |
| deterministic repro: stale survives a successful run | `ENGINE=podman bash tickets/BUG-001-csg-stale-container-sweep/repro.sh`; `ENGINE=docker CSG_TAG=latest bash …` | podman and docker both: before/after list `csg-bug001-stale|created|csg.created_at=…,csg.managed=true,…`; `csg exit: 0` |
| clean normal run leaves no wrapper | `podman ps -a --filter label=csg.managed=true …` after a normal `csg generate` | no output; `podman ps -a --filter name=csg` no output; `colors.yaml` written |
| host SIGKILL leaves an unlabelled wrapper; next run does not remove it | background `csg generate`, poll `podman ps --filter ancestor=localhost/csg-wallust-podman:v0.2.0`, `kill -9`, then run `csg generate` again | `objective_keldysh|running|Up Less than a second|io.buildah.version=1.45.1`; second run exit 0; still `Up 11 seconds|io.buildah.version=1.45.1` |
| ticket worktree/branch | `bash scripts/worktree-guard.sh create BUG-001 csg-stale-container-sweep` | `.worktrees/BUG-001/`; `ticket/BUG-001-csg-stale-container-sweep` |
| change validates | `openspec validate csg-stale-container-sweep --strict` | `Change 'csg-stale-container-sweep' is valid` |

## Implementation prompt (self-contained, next session)

````text
You are implementing BUG-001 in the color-scheme-generator (csg) repo at
/home/inumaki/Development/color-scheme-generator. Read AGENTS.md, tickets/LIFECYCLE.md,
tickets/BUG-001-csg-stale-container-sweep/ticket.md, and
openspec/changes/csg-stale-container-sweep/{proposal,design,tasks}.md first. Follow the repo's
evidence rule, worktree discipline, and planning-vs-implementation commit split. Do not work on
main, do not tag/release, do not run sudo, do not provision a host, and do not edit the dotfiles
runtime, dotfiles-v3, or ags-apps.

Goal: when the host loses power or the host-side csg process is SIGKILLed, a detached wrapper
container can be left behind. Add csg-owned labels and a best-effort startup sweep so the next
container-mode generate/show removes stale csg wrappers, without touching young concurrent runs or
unlabelled/foreign containers. This is a bug fix, not a new CLI feature.

Branch/worktree: if .worktrees/BUG-001 exists on ticket/BUG-001-csg-stale-container-sweep, reuse it
after `git merge --ff-only main`; otherwise run
`bash scripts/worktree-guard.sh create BUG-001 csg-stale-container-sweep-fix` and work in that new
worktree. Make a status-only `in-progress` commit (ticket frontmatter + tickets/INDEX.md in the same
commit) before code, per LIFECYCLE. Keep the planning commit and the implementation commit(s)
separate.

Design to implement (do not re-litigate; it is already validated):

1. Add a frozen `ManagedContainer` domain record in
   src/color_scheme_generator/domain/models.py with `name: str`, `state: str`,
   `labels: Mapping[str, str]`, `created: str | None = None`. Freeze the labels mapping.
2. Extend `ContainerRuntimePort` in src/color_scheme_generator/ports/container_runtime.py:
   - `run(..., memory_limit=None, labels: dict[str, str] | None = None)` — labels last, keyword
     compatible;
   - `list_containers(filters: dict[str, str] | None = None, show_all: bool = True) ->
     list[ManagedContainer]`;
   - `inspect_container(name: str) -> ManagedContainer`;
   - `remove_container(name: str, force: bool = True) -> None`.
3. Extend `OciContainerRuntimeAdapter` in
   src/color_scheme_generator/adapters/oci_container_runtime.py:
   - pass `labels=labels or {}` into `RunConfig`;
   - implement the three methods: `engine.containers.list(show_all=show_all, filters=filters)`,
     `engine.containers.inspect(name)`, `engine.containers.remove(name, force=force)`;
   - map oci_runtime ContainerInfo to ManagedContainer; use `str(info.state)`;
   - if list `labels` is not a Mapping, map to `{}` (Docker list returns a comma-separated string);
   - do not trust `info.id` from Docker list; use `name` for inspect/remove.
4. Extend `ContainerProcessor` in
   src/color_scheme_generator/adapters/container_processor.py:
   - at the start of `process_generate` and `process_show`, generate `session_id = str(uuid.uuid4())`
     and build labels:
       csg.managed = "true"
       csg.session = session_id
       csg.created_at = UTC RFC3339 (e.g. datetime.now(timezone.utc).isoformat().replace("+00:00","Z"))
       csg.timeout_seconds = str(settings.container.timeout_seconds)
       csg.boot_id = read first line of /proc/sys/kernel/random/boot_id, stripped, only if readable
   - call `self._sweep_stale_containers(settings, session_id)` BEFORE `image_exists` in both verbs;
   - pass `labels=labels` to `self._container_runtime.run(...)`.
5. Sweep policy (private helper, best-effort):
   - list with `filters={"label": "csg.managed=true"}, show_all=True`; on any list error log a
     warning and return (the run must proceed);
   - for each candidate: inspect by name; on inspect error log debug/warning and continue;
   - skip if labels.get("csg.managed") != "true"; skip if labels.get("csg.session") == session_id;
   - if current boot id and labels["csg.boot_id"] are both non-empty and differ, remove;
   - else parse `created`; fallback to labels["csg.created_at"]; if neither parses, skip (never
     guess);
   - timeout = int(labels["csg.timeout_seconds"]) if valid else settings.container.timeout_seconds;
   - remove only if now - created > timeout + 60 seconds;
   - remove with force=True; catch and log per-container remove errors; never raise;
   - keep the existing adapter `finally` removal; do not switch to `--rm`.
6. Tests (hermetic, fakes; no network):
   - add tests/unit/adapters/test_stale_container_sweep.py covering: normal run leaves no wrapper;
     stale same-boot removed and run succeeds; previous-boot removed immediately; young same-boot
     kept; unlabelled/foreign untouched; unparseable age skipped; list/inspect failure does not block
     generation; sweep before image preflight (image_exists false still removes stale); show also
     sweeps and labels.
   - add tests/unit/adapters/test_oci_container_runtime_labels.py covering: labels threaded into
     RunConfig; list filter/show_all forwarded; inspect/remove by name; Docker-style string labels
     normalised; force flag forwarded.
   - update the fake runtime in tests/unit/adapters/test_container_processor.py and the
     MockRuntime in tests/unit/ports/test_interfaces.py for the new methods; add port signature
     assertions for `labels` last in tests/unit/ports/test_contracts.py.
   - Keep existing tests green.
7. Manual acceptance on this host (record command/output in the ticket evidence):
   - `ENGINE=podman bash tickets/BUG-001-csg-stale-container-sweep/repro.sh` → stale gone, csg exit 0
     after the fix;
   - create an unlabelled container from the csg image and a foreign-labelled container, run a
     normal generate, assert both are untouched;
   - run a normal generate with no stale container, assert
     `podman ps -a --filter label=csg.managed=true` is empty;
   - repeat with `ENGINE=docker` if docker is reachable.
8. Gates and closeout: `make gates` exit 0; `openspec validate csg-stale-container-sweep --strict`
   valid; update ticket acceptance checkboxes, evidence, status `done`, and tickets/INDEX.md in a
   closeout commit. Merge/push only when green. Do not tag, bump the version, release, or edit
   dotfiles-v3. The release/pin chain is a documented follow-up in the ticket, not part of this
   implementation.

Deliverable in your final report: files changed, exact test/gate commands and results, the
real-engine before/after observations, and the merged commit. If any existing test fake or protocol
implementation cannot be updated without changing unrelated behavior, stop and report the blocker
instead of weakening the test.
````
