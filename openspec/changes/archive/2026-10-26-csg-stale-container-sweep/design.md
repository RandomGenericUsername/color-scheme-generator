# Design — stale csg container sweep

## Context

`ContainerProcessor` is the only place that knows both the resolved `AppSettings` and the selected
container engine. Its container-mode branch builds mounts, calls
`ContainerRuntimePort.run(...)`, and relies on `OciContainerRuntimeAdapter.run` to remove the
wrapper in a `finally` (`src/color_scheme_generator/adapters/oci_container_runtime.py:43-70`). The
adapter creates the wrapper detached with `remove=False`, then execs the inner `csg`. The port has
no label, list, inspect or remove operation
(`src/color_scheme_generator/ports/container_runtime.py:14-42`).

A host `SIGKILL` or power loss skips the `finally`; the wrapper remains, and the next `csg` run has
no ownership marker to find it. The observed repro is in `tickets/BUG-001-csg-stale-container-sweep/`.

`oci-runtime` v0.5.0 (pinned in `uv.lock`) already supports everything the sweep needs:
`RunConfig.labels` (`domain/types.py:119-147`), `-l` emission
(`adapters/managers/container.py:155-156`), `ContainerManager.list(show_all, filters)` and
`inspect`/`remove` (`ports/managers.py:49-94`), and `--filter key=value`
(`domain/list_command.py:12-14`). Two Docker-list parser limits matter:

- Docker `ps --format '{{json .}}'` reports the id as `ID`, but the v0.5.0 parser reads `Id`, so
  `ContainerInfo.id` is `""` for Docker list results.
- Docker list `Labels` is a comma-separated string, while the parser stores it unchanged; only
  Docker inspect yields a mapping.

The sweep therefore lists by server-side label filter and then inspects each candidate **by name**.
This is a csg-side workaround; fixing the sibling parser is a separate repo's change.

## Goals / Non-Goals

**Goals:**

- Recover stale csg-owned wrappers on the next container-mode `generate`/`show`, including wrappers
  left by a previous boot.
- Distinguish stale wrappers from live concurrent runs and from containers csg does not own.
- Keep the recovery best-effort: a broken inventory must not break palette generation.
- Add no timer, daemon, host provisioning, or runtime change.

**Non-Goals:**

- Removing unlabelled containers, including manual containers started from a csg image.
- A `csg clean`/`reconcile` public verb, a lease registry, or systemd/cron integration.
- Changing the image tag pin, Dockerfiles, the invocation contract, or the sibling `oci-runtime`
  source.
- The csg release, the `dotfiles-v3` pin, and the engine release (documented follow-up only).

## Decisions

### D1. Labels are the ownership boundary, with per-run metadata

Each wrapper gets:

| Label | Value | Purpose |
| --- | --- | --- |
| `csg.managed` | `true` | The only list filter; explicit csg ownership |
| `csg.session` | `uuid4()` | Run correlation and future lease/reconcile work |
| `csg.created_at` | RFC3339 UTC | Human diagnosis; fallback age source |
| `csg.timeout_seconds` | settings timeout at creation | Per-container staleness budget |
| `csg.boot_id` | host boot id when readable | Previous-boot (power-loss) fast path |

Rationale: a label filter is safe and cheap, and the metadata lets the sweep decide staleness
without trusting a single engine timestamp. A container without `csg.managed=true` is never a
candidate even if its image name starts with `csg-`.

Alternatives considered:

- **Match by image name and age only.** Rejected: a user may legitimately run
  `csg-base-podman:v0.2.0` manually, and an old unlabelled container is indistinguishable from a
  foreign one. It violates the "foreign containers untouched" acceptance.
- **Use container names (`csg-<uuid>`).** Useful for readability but not an ownership proof; names
  can be chosen by anyone. Labels remain the contract.

### D2. Sweep at the start of a container-mode run, before image preflight

`ContainerProcessor.process_generate` and `process_show` call a private
`_sweep_stale_containers(settings, current_session)` after settings are resolved and before
`image_exists`. The sweep is not in the Typer callback: `--version`, `info`, `dump-config`,
`list-backends` and `install` must not touch the container engine, and the callback has no resolved
`[container]` settings.

Running before image preflight is deliberate: a missing backend image (or a host that only has the
base image) must not block cleanup. If the engine is unreachable, the subsequent `run` will report
the real error; the sweep is best-effort and does not mask it.

Alternatives considered:

- **CLI startup search.** Rejected: it would make every command engine-dependent and slower, and
  would need a settings resolution the callback does not own.
- **Sweep inside `csg install`/`uninstall`.** Rejected: those manage images, not run wrappers; a
  user may never call them after a crash.
- **Background timer/systemd unit.** Rejected for the first slice by the ticket scope; it adds host
  provisioning and is unnecessary when every run can reconcile.

### D3. Staleness: previous boot immediate, same boot timeout + grace

For each candidate inspected by name:

1. Confirm `labels.get("csg.managed") == "true"`; otherwise skip.
2. Skip if `csg.session` equals the current session (defensive; the current wrapper does not exist
   yet at sweep time).
3. If `csg.boot_id` and the current boot id are both non-empty and differ, remove.
4. Otherwise parse `created` from inspect; if that fails, parse `csg.created_at`; if both fail,
   skip and log at debug.
5. `timeout = int(csg.timeout_seconds)`; if missing or invalid, use the current settings timeout.
6. Remove only if `now - created > timeout + 60 s`.

The 60 s grace covers engine clock granularity, the gap between label creation and the engine
timestamp, and a host that is a little slow to start another run. Using the container's own
`timeout_seconds` avoids a second run with a shorter timeout killing a legitimately long run.
Previous-boot removal is immediate because a wrapper from another boot cannot be live.

Alternatives considered:

- **Fixed age threshold (for example 5 minutes).** Rejected: a configured 1-hour run would be
  killed by a later 5-minute run.
- **Lease/registry under `XDG_RUNTIME_DIR`.** More precise for same-boot orphans, but adds file
  lifecycle, permissions, PID-reuse and cross-boot cleanup. The boot-id label gets the important
  power-loss case without state; a lease can be added later without changing the label contract.
- **`--rm` on the wrapper.** Rejected as the primary fix: the adapter needs a detached container it
  can `exec` into, and changing engine-side auto-removal semantics is a larger behavioural change.
  It also would not give a sweep anything to find if the engine misses the removal.

### D4. Inventory by filtered list, metadata by inspect-by-name

The port gains `list_containers(filters=..., show_all=True)`,
`inspect_container(name)` and `remove_container(name, force=True)`. The adapter:

- calls `engine.containers.list(show_all=True, filters={"label": "csg.managed=true"})`;
- maps each result to a domain `ManagedContainer(name, state, labels, created)`, normalising a
  non-mapping `labels` value to `{}` (Docker list);
- for each candidate, calls `engine.containers.inspect(name)` and uses that mapping;
- calls `engine.containers.remove(name, force=True)`.

Using `name` is required, not stylistic: Docker list gives an empty `id` in oci-runtime v0.5.0.
The server-side filter is still the safety boundary; inspect is the metadata source.

Alternatives considered:

- **Trust list labels and ids.** Rejected: Docker list ids are empty and labels are a string.
- **Shell out to `podman ps`/`docker ps`.** Rejected: bypasses the existing engine abstraction and
  duplicates docker/podman parsing this repo already pays for in `oci-runtime`.

### D5. Extend the existing runtime port; keep policy in `ContainerProcessor`

The port gets `labels: dict[str, str] | None = None` on `run` and the three inventory/removal
methods. A small frozen `ManagedContainer` domain record keeps `oci_runtime` types out of the
processor. `ContainerProcessor` owns the policy (what is stale) and the adapter owns the mapping
(what the engine reports).

Alternatives considered:

- **One high-level `sweep_stale_containers` port method.** Fewer methods, but puts boot-id reading,
  age parsing and policy in the adapter, making the policy harder to unit-test through a fake
  runtime.
- **A new `ContainerSweeper` service plus a second port.** Cleanest on paper, but three extra
  abstractions for one loop; overkill for this bounded fix.

### D6. Best-effort, idempotent, and non-fatal

The sweep catches `Exception` around list/inspect/remove, logs a warning (debug for expected
not-found races), and continues. It never raises a new domain error and never changes the
generation result. Removal is forced but idempotent: a candidate may disappear between list and
inspect, which is logged and skipped.

Alternatives considered:

- **Fail the run if cleanup fails.** Rejected: a cleanup failure would turn a working palette run
  into an outage; the next run retries anyway.
- **Retry with backoff.** Rejected for the first slice; a single pass keeps the latency predictable
  and the next invocation is the retry.

## Risks / Trade-offs

- **A live wrapper could be removed if its clock or timeout label is wrong.** → Use the container's
  own timeout label, a 60 s grace, and a previous-boot-only fast path; never remove when the age is
  unknown. A malformed timeout falls back to the current settings, never to "immediately stale".
- **The sweep adds a list plus N inspects to every container run.** → Normally N is zero or one;
  the list is filtered server-side and the cost is small compared with image inspection/exec.
- **A crash during the sweep leaves some candidates.** → The sweep is idempotent; the next run
  lists again. Removal happens only after a successful inspect.
- **Docker and Podman differ in their list payload.** → Use only the name from the list and inspect
  for labels/created; tests cover both engine shapes with fakes, and the manual evidence covers
  both real engines.
- **A user or another tool labels a container `csg.managed=true`.** → Explicit opt-in to csg
  ownership; the label is documented as reserved.
- **A wrapper is restarted by an engine restart policy.** → csg sets `RestartPolicy.NO`; the boot
  id check removes a previous-boot wrapper even if an operator changed that.
- **Labels expose a uuid and a boot id.** → No secrets or user data; both are local diagnostics.

## Verification plan

| Decision | Command | Expected |
| --- | --- | --- |
| D1 labels | `uv run pytest tests/unit/adapters/test_stale_container_sweep.py -q` | label assertions pass for `generate` and `show` |
| D2 placement | same suite, `test_sweep_runs_before_image_preflight` | stale container removed when `image_exists` is false; the image error still surfaces |
| D3 staleness | same suite, `test_stale_same_boot_removed`, `test_previous_boot_removed`, `test_young_same_boot_kept`, `test_missing_age_skipped` | each scenario passes |
| D4 inventory | `uv run pytest tests/unit/adapters/test_oci_container_runtime_labels.py -q` | list filter/show_all forwarded; inspect by name; Docker string labels normalised to `{}` |
| D5 port | `uv run pytest tests/unit/ports/test_contracts.py tests/unit/ports/test_interfaces.py -q` | contract signatures and fake protocol instances pass |
| D6 best-effort | same suite, `test_inventory_failure_does_not_block_generation` | run is attempted and the result is returned |
| Real engine | manual, in the ticket | stale labelled container removed; unlabelled/foreign untouched; normal run leaves none |
| Gates | `make gates` | exit 0 |

Manual real-engine probes recorded in the ticket use both engines:
`podman ps -a --filter label=csg.managed=true` and the equivalent `docker` filter; the oci-runtime
probe showed `count 1`, the labels, and `removed` for both, with Docker list labels a string and
Docker inspect labels a mapping.

## Migration Plan

No schema, config, image, or contract migration. Existing unlabelled containers from earlier csg
versions are deliberately not removed by this change; operators may remove them manually. New
labels are additive and ignored by older csg versions. Rolling back the code stops new labels and
sweeps; old labelled containers are inert.

## Open Questions

None that change the spec, the approach, or the task breakdown. The lease/registry option and a
`csg clean` verb are documented follow-ups, not prerequisites.
