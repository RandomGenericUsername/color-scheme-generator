# csg-container-mode Specification

## Purpose
Defines the container backends this repo owns: the four Dockerfiles, their build context, the tag
pin, and the `install`/`uninstall` verbs.

## Requirements

### Requirement: every image builds from this repo root
All four images SHALL be built with the repository root as context.
`src/color_scheme_generator/adapters/docker/Dockerfile.base` SHALL copy only repo-relative paths
(`pyproject.toml`, `uv.lock`, `README.md`, `LICENSE`, `src/`). The per-backend Dockerfiles
(`custom`, `pywal`, `wallust`) SHALL keep their `ARG BASE_IMAGE` and add only engine-level
packages.

Source: spine AD-5/AD-7; `Dockerfile.base` lines 1–18; `Dockerfile.{custom,pywal,wallust}`.

#### Scenario: no sibling or parent references
- **WHEN** `rg -n "src/shared|src/cli-tools|\.\./" src/color_scheme_generator/adapters/docker/`
  runs
- **THEN** it exits 1 with no matches

### Requirement: git dependencies are fetched at build time, fail-closed
The build stage SHALL carry `uv` at the pinned version plus `git` and CA certificates, and SHALL
install from the committed lock (`uv sync --frozen --no-dev --no-editable`) so an unreachable pin
fails the build instead of resolving a newer commit.

Source: spine AD-3/AD-5; `Dockerfile.base` lines 8–16.

#### Scenario: locked install
- **WHEN** the image builds with the committed `uv.lock`
- **THEN** the same sibling tags recorded in the lock are the ones installed

### Requirement: the image tag is the pin
The effective image tag SHALL equal the repo tag (`vX.Y.Z`) rather than `latest`, and `csg install`
SHALL accept the build context explicitly (`--context`, alias `--source-root`) so provisioning can
build from the pinned checkout at that tag.

Source: spine AD-7; `src/color_scheme_generator/cli/install_cmd.py`;
`src/color_scheme_generator/cli/options.py` (`CONTEXT_OPT`).

#### Scenario: tag-qualified image exists
- **WHEN** `podman images --format '{{.Repository}}:{{.Tag}}'` runs after an install at `v0.1.0`
- **THEN** `csg-base-podman:v0.1.0` and each requested `csg-<backend>-podman:v0.1.0` exist, and no
  image produced by the pin path carries `:latest`

### Requirement: the base image runs the pinned CLI
The base image SHALL expose `csg` on `PATH` and report the package and contract versions when run
without a checkout mounted.

Source: `Dockerfile.base` (`ENV UV_PROJECT_ENVIRONMENT`, `ENV PATH`, `CMD`); spine AD-5.

#### Scenario: version inside the image
- **WHEN** `podman run --rm color-scheme-generator-base:v0.1.0 csg --version` runs
- **THEN** it prints `0.1.0 contract 0.1.0` and exits 0

### Requirement: `uninstall` removes tag-qualified images
`csg uninstall` SHALL remove the engine-qualified images named by the effective settings and SHALL
report a no-op when an image is absent.

Source: `src/color_scheme_generator/cli/uninstall_cmd.py`.

#### Scenario: removal is idempotent
- **WHEN** `csg uninstall --container-engine podman` runs twice
- **THEN** both runs exit 0 and the second reports the absent image rather than failing

### Requirement: container-mode wrappers are labelled as csg-owned

Every container-mode `generate` and `show` wrapper SHALL carry the labels `csg.managed=true`,
`csg.session=<uuid>`, `csg.created_at=<RFC3339 UTC>` and `csg.timeout_seconds=<integer>`. When the
host exposes `/proc/sys/kernel/random/boot_id`, the wrapper SHALL also carry
`csg.boot_id=<value>`.

Source: ticket `BUG-001`; the SIGKILL repro leaves an unlabelled wrapper.
Verify: `uv run pytest tests/unit/adapters/test_stale_container_sweep.py -q`.

#### Scenario: wrapper carries the ownership and run metadata

- **WHEN** a container-mode `csg generate` creates its wrapper
- **THEN** the wrapper has `csg.managed=true`, a non-empty `csg.session`, a parseable
  `csg.created_at`, and an integer `csg.timeout_seconds`; `csg.boot_id` is present when the host
  boot id is readable

#### Scenario: show is labelled the same way as generate

- **WHEN** a container-mode `csg show` creates its wrapper
- **THEN** the wrapper carries the same ownership labels as a `generate` wrapper

### Requirement: stale csg-owned wrappers are swept before a new run

Before creating a wrapper, csg SHALL list containers filtered by `label=csg.managed=true` and
remove only labelled wrappers that are stale: different `csg.boot_id`, or age beyond the wrapper's
own timeout plus 60 s. Young same-boot, unlabelled and unknown-age containers SHALL NOT be removed.

Source: ticket `BUG-001`; design option A.
Verify: `uv run pytest tests/unit/adapters/test_stale_container_sweep.py -q`.

#### Scenario: stale same-boot wrapper is removed

- **WHEN** a labelled wrapper is older than its `csg.timeout_seconds` plus 60 s and carries the
  current boot id
- **THEN** the next container-mode `generate` or `show` removes it with a forced removal before
  creating its own wrapper, and the requested run still succeeds

#### Scenario: previous-boot wrapper is removed immediately

- **WHEN** a labelled wrapper carries a `csg.boot_id` different from the current host boot id
- **THEN** the next container-mode `generate` or `show` removes it even if its age is below the
  timeout-plus-grace threshold

#### Scenario: young same-boot wrapper is kept

- **WHEN** a labelled wrapper is younger than its `csg.timeout_seconds` plus 60 s and carries the
  current boot id
- **THEN** the sweep does not remove it, because another `csg` run may still own it

#### Scenario: unlabelled and foreign containers are untouched

- **WHEN** the inventory contains an unlabelled container, a container labelled by another tool,
  or a manually started container from a csg image without `csg.managed=true`
- **THEN** the sweep does not remove it

#### Scenario: missing age is not guessed

- **WHEN** a labelled wrapper has neither a parseable engine `created` value nor a parseable
  `csg.created_at` label
- **THEN** the sweep leaves it in place rather than guessing that it is stale

#### Scenario: normal run leaves no wrapper behind

- **WHEN** a container-mode `generate` completes normally and no pre-existing stale wrapper exists
- **THEN** the wrapper is removed by the existing `finally` and a query for
  `label=csg.managed=true` returns no container from that run

### Requirement: the sweep is best-effort and never blocks generation

List, inspect or remove failures during the sweep SHALL be logged and SHALL NOT fail `generate` or
`show`; the requested container run SHALL proceed. The sweep SHALL run before image preflight so a
missing image does not prevent cleanup.

Source: ticket `BUG-001`; recovery must not become a new failure mode.
Verify: `uv run pytest tests/unit/adapters/test_stale_container_sweep.py -q`.

#### Scenario: inventory failure does not block the run

- **WHEN** the container engine cannot list or inspect containers during the sweep
- **THEN** `generate` or `show` logs the sweep failure and still performs the requested container
  run

#### Scenario: sweep runs before image preflight

- **WHEN** the requested backend image is absent but a stale labelled wrapper exists
- **THEN** the stale wrapper is removed before the image-not-found error is raised
