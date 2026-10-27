# Tasks

## 1. Runtime port and adapter inventory

- [x] 1.1 Add the frozen `ManagedContainer` domain record (`name`, `state`, `labels`, `created`) and
  the `labels` argument on `ContainerRuntimePort.run`; add
  `list_containers(filters, show_all)`, `inspect_container(name)` and
  `remove_container(name, force)` to the port. Verify: `uv run pytest
  tests/unit/ports/test_contracts.py tests/unit/ports/test_interfaces.py -q` → passes after the
  fakes declare the new methods, and
  `uv run python -c "import inspect; from color_scheme_generator.ports.container_runtime import
  ContainerRuntimePort as P; print(list(inspect.signature(P.run).parameters))"` lists `labels`
  last.
- [x] 1.2 Implement the port methods in `OciContainerRuntimeAdapter`: map list/inspect results to
  `ManagedContainer`, forward `show_all=True` and the label filter, inspect/remove by name, and
  normalise a non-mapping list `labels` value to `{}`. Add a unit test with a fake engine that
  asserts the filter, `show_all`, `-l` label propagation into `RunConfig`, and the Docker-style
  string-label case. Verify: `uv run pytest
  tests/unit/adapters/test_oci_container_runtime_labels.py tests/unit/adapters/test_image_lifecycle.py
  -q` → passes.

## 2. Container processor sweep

- [x] 2.1 In `ContainerProcessor`, generate a `uuid4` session id per `process_generate` and
  `process_show`, build the label map (`csg.managed`, `csg.session`, `csg.created_at`,
  `csg.timeout_seconds`, optional `csg.boot_id`), and pass it to `run`. Verify: `uv run pytest
  tests/unit/adapters/test_stale_container_sweep.py -q` → the label tests for both verbs pass.
- [x] 2.2 Add `_sweep_stale_containers(settings, session_id)` and call it before `image_exists` in
  both verbs. Implement the D3 policy: skip non-`csg.managed` candidates, previous boot removes
  immediately, same boot removes only after the container's own timeout plus 60 s, missing age is
  skipped, and all list/inspect/remove errors are logged and swallowed. Verify: `uv run pytest
  tests/unit/adapters/test_stale_container_sweep.py -q` → the stale, previous-boot, young,
  foreign/unlabelled, missing-age, preflight-order and inventory-failure scenarios pass.
- [x] 2.3 Update every test fake that implements `ContainerRuntimePort` (at least
  `tests/unit/adapters/test_container_processor.py` and
  `tests/unit/ports/test_interfaces.py`) to declare the new methods; keep the existing container
  suite green. Verify: `uv run pytest tests/unit/adapters/test_container_processor.py
  tests/unit/ports -q` → passes.

## 3. Regression and acceptance

- [x] 3.1 Add the regression suite `tests/unit/adapters/test_stale_container_sweep.py` covering:
  normal run leaves no wrapper; stale same-boot wrapper removed and the run succeeds; previous-boot
  wrapper removed immediately; young same-boot wrapper kept; unlabelled/foreign container
  untouched; unparseable age skipped; inventory failure does not block generation; `show` sweeps
  too. Verify: `uv run pytest tests/unit/adapters/test_stale_container_sweep.py -q` → all pass.
- [x] 3.2 Run the real-engine acceptance on this host and record the commands/output in the ticket
  evidence: create a labelled stale container, run a normal container-mode `generate`, observe it
  removed and the generation succeeds; create an unlabelled container and a foreign-labelled
  container, run again, observe both untouched; run a normal generation with no stale container and
  observe no `csg.managed=true` wrapper remains. Verify: the three `podman ps -a --filter ...`
  observations in the ticket are green for both podman and, where available, docker.
- [x] 3.3 Run the full gates on the ticket branch. Verify: `make gates` → exit 0; `openspec validate
  --change csg-stale-container-sweep --strict` → valid.

## Workflow follow-up

- Archive `csg-stale-container-sweep` after the bug fix and evidence are merged; no tag or release
  in the planning ticket.
- Release follow-up (separate repos/commits): csg patch bump and annotated `v0.2.1`; `dotfiles-v3`
  `cli-tools.yaml` csg tag + provisioning image/tag mirror; engine release; v3 pin bump; verify
  `csg --version` and the stale-container behaviour on the pinned engine.
