# csg-container-mode Specification

## Purpose
Defines the container backends this repo owns: the four Dockerfiles, their build context, the tag
pin, and the `install`/`uninstall` verbs.

## Requirements

### Requirement: every image builds from this repo root
The four images SHALL be built with the repository root as context, and
`src/color_scheme_generator/adapters/docker/Dockerfile.base` SHALL copy only repo-relative paths
(`pyproject.toml`, `uv.lock`, `README.md`, `LICENSE`, `src/`). The per-backend Dockerfiles
(`custom`, `pywal`, `wallust`) SHALL keep their `ARG BASE_IMAGE` and add only engine-level
packages. No Dockerfile path may name a sibling repo or a parent directory.

Source: spine AD-5/AD-7; `Dockerfile.base` lines 1–18; `Dockerfile.{custom,pywal,wallust}`.

#### Scenario: build with no monorepo present
- **WHEN** `podman build -t color-scheme-generator-base:v0.1.0 -f
  src/color_scheme_generator/adapters/docker/Dockerfile.base .` runs in a standalone checkout
- **THEN** the build exits 0

#### Scenario: backend images derive from the pinned base
- **WHEN** each `Dockerfile.{custom,pywal,wallust}` is built with
  `--build-arg BASE_IMAGE=<base>:v0.1.0`
- **THEN** every build exits 0 and no Dockerfile needs a sibling checkout

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
