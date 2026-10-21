# repo-harness (delta)

## ADDED Requirements

### Requirement: the mu harness is present and byte-identical

The repo SHALL contain `scripts/worktree-guard.sh` (executable), `skills-lock.json`, `_bmad/`,
`.agents/skills/`, `.opencode/`, `tickets/_template/`, `tickets/_fixtures/` and
`tickets/LIFECYCLE.md`, each byte-identical to `/home/inumaki/Development/mu`.

Source: spine AD-12; `mu/AGENTS.md` §2; `ARCHITECTURE-SPINE.md` § Repo Birth Checklist items 3–6.

#### Scenario: guard is executable and clean-tree safe

- **WHEN** `bash scripts/worktree-guard.sh check-clean` runs on a clean tree
- **THEN** it exits 0

#### Scenario: a dirty tree is refused

- **WHEN** any tracked file is modified and `check-clean` runs
- **THEN** it exits 1 and prints `main is dirty, address it first`

#### Scenario: copied trees match their source

- **WHEN** `diff -r /home/inumaki/Development/mu/_bmad _bmad` runs
- **THEN** the output is empty and the exit code is 0

### Requirement: work routes through tickets and never lands on main

Every change SHALL have a ticket under `tickets/<id>-<slug>/ticket.md` whose status matches
`tickets/INDEX.md`, and item work SHALL happen on `ticket/<id>-<slug>` created by
`scripts/worktree-guard.sh create <id> <slug>`.

Source: `mu/AGENTS.md` §3; `mu/tickets/LIFECYCLE.md`; spine Consistency Conventions (Branch /
worktree).

#### Scenario: ticket and INDEX agree

- **WHEN** `rg -n "<id>" tickets/INDEX.md tickets/<id>-<slug>/ticket.md` runs
- **THEN** both files match, and the status token in each is the same

### Requirement: a fresh clone passes the gate set

`make sync && make gates && make build` SHALL exit 0 on a fresh clone, where
`GATES = test lint hermetic lock-check docs-check`, and `hermetic` SHALL pass with `HOME` and all
four `XDG_*` variables pointed at empty temp dirs.

Source: spine AD-8, AD-12, AD-14; birth checklist items 9–11.

#### Scenario: gates on a fresh clone

- **WHEN** `git clone <repo> /tmp/x && cd /tmp/x && make sync && make gates` runs
- **THEN** every gate exits 0 and `make hermetic` reports the same test count as `make test`

#### Scenario: build produces both artifacts

- **WHEN** `make build` runs
- **THEN** `dist/color_scheme_generator-0.1.0-*.whl` and `dist/color_scheme_generator-0.1.0.tar.gz`
  exist

#### Scenario: workflow and Makefile agree

- **WHEN** `make ci-gates-parity` runs
- **THEN** it prints `PASS ...` and exits 0; adding a gate without a job (or the reverse) exits 1

### Requirement: the container images build from the repo root

`make image` SHALL build `src/color_scheme_generator/adapters/docker/Dockerfile.base` and the three
backend Dockerfiles with the repository root as context, at tag `v<version>`, run `csg --version` in
the base image, and no Dockerfile SHALL reference a sibling repo or a parent directory.

Source: spine AD-5, AD-7; `SLICES.md` § S6 acceptance gates.

#### Scenario: image reports both versions

- **WHEN** `make image` runs
- **THEN** every build exits 0 and the base-image run prints `0.1.0 contract 0.1.0`

#### Scenario: no monorepo paths

- **WHEN** `rg -n "src/shared|src/cli-tools|\.\./" src/color_scheme_generator/adapters/docker/`
  runs
- **THEN** it exits 1 with no matches

### Requirement: the nested pre-split OpenSpec tree is preserved as archive

`openspec/archive/cli-tools-pre-split/` SHALL be byte-identical to the retired
`dotfiles-v3/src/cli-tools/openspec/` tree and SHALL carry a provenance note; it SHALL NOT be
validated as an active change or capability.

Source: spine AD-15; `SLICES.md` § S6 step 3.

#### Scenario: archive matches its source

- **WHEN** `diff -r <dotfiles>/src/cli-tools/openspec openspec/archive/cli-tools-pre-split` runs
- **THEN** the output is empty and the exit code is 0

### Requirement: a release is a tag with reproducible artifacts

An annotated `vMAJOR.MINOR.PATCH` tag SHALL be created only after the gates, image proof and CI
are green, `CHANGELOG.md` SHALL describe the release, and CI SHALL attach the sdist and wheel built
from that commit to the GitHub Release. A published tag is never moved or deleted.

Source: spine AD-9, AD-16; OPEN-5 (MIT `LICENSE` before the first tag).

#### Scenario: the first tag resolves to one commit

- **WHEN** `git ls-remote --tags origin v0.1.0` runs with credentials disabled
- **THEN** it prints exactly one line ending in `refs/tags/v0.1.0`, and
  `git rev-parse v0.1.0^{commit}` names the released commit

#### Scenario: the release carries both artifacts

- **WHEN** `gh release view v0.1.0 --json assets --jq '.assets[].name'` runs
- **THEN** it lists `color_scheme_generator-0.1.0-py3-none-any.whl` and
  `color_scheme_generator-0.1.0.tar.gz`
