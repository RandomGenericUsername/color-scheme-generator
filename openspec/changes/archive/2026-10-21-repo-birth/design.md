# Design — repo birth

## Decisions

### D1. History comes from `git subtree split`, not a fresh root commit

The in-tree package has 90 commits, including the S3 Dockerfile rewrite to package-relative COPY
paths, the S0b hermetic fixture, and the sibling tag pins. A fresh import would lose those "why"
records. `git subtree split -P src/cli-tools/color-scheme-generator` writes a branch whose tree is
the package directory and whose commits are the ones that touched it.

Evidence: `git -C /home/inumaki/Development/dotfiles-v3 rev-list --count
split/color-scheme-generator` → `90`; the split tip is
`b991db0cee293e8e3600484425f04ea2ec9ceb01`.
Verify: `git log --oneline | wc -l` in this repo → `90` before the scaffold commit.

### D2. Harness files are copied, not re-authored

AD-12 requires the same `worktree-guard.sh` and the same `skills-lock.json` hashes as `mu`. The
copy set is exactly: `scripts/worktree-guard.sh`, `skills-lock.json`, `_bmad/`, `.agents/skills/`,
`.opencode/`, `tickets/_template/`, `tickets/_fixtures/`, `tickets/LIFECYCLE.md`.
`tickets/INDEX.md` is repo-specific, and `AGENTS.md` is retargeted but keeps the evidence rule
verbatim.

Evidence: `diff -r` per path against `mu` is empty (ticket evidence table).
Verify: `diff -r /home/inumaki/Development/mu/_bmad _bmad && diff
/home/inumaki/Development/mu/skills-lock.json skills-lock.json`.

### D3. All four images build from this repo root only

`Dockerfile.base` is the only image with a build context; the three backend Dockerfiles derive from
it via `ARG BASE_IMAGE` and add only engine-level packages. The base copies only repo-relative paths
(`pyproject.toml`, `uv.lock`, `README.md`, `LICENSE`, `src/`). The S3 rewrite already removed every
`src/shared`/`src/cli-tools` path; this repo proves it by building with no monorepo present. The
build stage carries `uv==0.9.22`, `git` and CA certificates because the sibling dependencies are
fetched from their tags at build time; determinism comes from the lock + tag, and an unreachable
pin fails the build closed (AD-5).

Evidence: `Dockerfile.base` lines 1–18; `podman build ... .` → exit 0.
Verify: `rg -n "src/shared|src/cli-tools|\.\./" src/color_scheme_generator/adapters/docker/`
→ exit 1; `make image` → four images, `csg --version` prints `0.1.0 contract 0.1.0`.

### D4. The image tag is the pin, supplied through settings

`[container] image_tag` defaults to `latest` in the bundled settings, which is fine for a
developer's local build but wrong for provisioning (AD-7: the pin is the tag). `csg install` reads
the tag from the resolved settings, so provisioning renders `image_tag = v0.1.0` (or sets
`COLORSCHEME__CONTAINER__IMAGE_TAG=v0.1.0`) and `verify` asserts the image exists at that exact
tag. This repo adds no new flag for it: the imported verb already threads the setting through
`engine_qualified_image`, and a second source of truth for the tag would be a regression.

Evidence: `src/color_scheme_generator/cli/install_cmd.py` lines 52–55, 91;
`src/color_scheme_generator/adapters/settings/config_resolver.py` (`container.image_tag` override
rule); `src/color_scheme_generator/cli/_helpers.py` `build_image_name`.
Verify: `COLORSCHEME__CONTAINER__IMAGE_TAG=v0.1.0 csg install --context . --container-engine
podman` → exit 0; `podman images` lists `csg-base-podman:v0.1.0` and the backend images.

### D5. The Makefile's `GATES` is the single gate list; CI is compared to it

The workflow has one job per gate so a failure names the gate, but a hand-maintained job list
drifts. `scripts/ci-gates-parity.py` parses `GATES` from the `Makefile` and the job keys from the
workflow and fails on any unmatched entry in either direction. CI-only jobs (`ci-gates-parity`,
`image`, `release`) are declared with a reason; a stale declaration fails.

Evidence: `make ci-gates-parity` → `PASS gates=[...] jobs=[...] exempt=[...]`.
Verify: `make ci-gates-parity`.

### D6. Hermetic means hermetic, not "green on this host"

AD-8 is implemented in the imported tests (`tests/conftest.py` + `tests/test_hermetic_canary.py`).
The Makefile adds `hermetic`, which runs the suite with `HOME` and all four `XDG_*` roots pointed at
fresh temp dirs; the fixture does the `chdir`. `make gates` includes it.

Evidence: the canary asserts every `XDG_*` root is under the pytest tmp root.
Verify: `make hermetic` → exit 0 with the same count as `make test`.

### D7. `image` is a CI job but not a `make gates` member

A real image build needs an engine and network access to the pinned git tags; making it a gate
would make every local gate run depend on Podman/Docker. It is a first-class verb (`make image`),
runs in CI as a declared CI-only job, and is proven locally in the birth ticket. The parity script
records the exemption, so the gap is explicit rather than silent.

Evidence: `CI_ONLY_EXEMPT` in `scripts/ci-gates-parity.py`; `image` job in the workflow.
Verify: `make ci-gates-parity` → exit 0 with `image` listed as exempt.

### D8. The nested OpenSpec root is carried as archive, not as a second root

`src/cli-tools/openspec/` is a second OpenSpec root that only ever held one csg-only change
(`fix-container-engine-plumbing`, complete) and a placeholder spec. AD-15 assigns it to this repo.
It is carried verbatim under `openspec/archive/cli-tools-pre-split/` with a provenance note: the
change is history, not a live change, and the placeholder spec is preserved rather than dropped so
the record is reconstructable. Nothing under `openspec/archive/` is validated as a capability.

Evidence: `src/cli-tools/openspec/changes/fix-container-engine-plumbing/{proposal,design,tasks}.md`
in `dotfiles-v3`; the carried copy under `openspec/archive/cli-tools-pre-split/`.
Verify: `diff -r /home/inumaki/Development/dotfiles-v3/src/cli-tools/openspec
openspec/archive/cli-tools-pre-split` → empty; `openspec validate repo-birth --strict` → exit 0
(the archive is not a change).

## Verification plan

| Decision | Command | Expected |
| --- | --- | --- |
| D1 | `git log --oneline \| wc -l` | `90` imported commits before the scaffold |
| D2 | `diff -r <mu-path> <path>` for each copied path | empty output, exit 0 |
| D3 | `make image` | four builds exit 0; `0.1.0 contract 0.1.0` from inside the base image |
| D4 | `COLORSCHEME__CONTAINER__IMAGE_TAG=v0.1.0 csg install --context . --container-engine podman` | exit 0; tag-qualified base + backend images |
| D5 | `make ci-gates-parity` | `PASS ...`, exit 0 |
| D6 | `make hermetic` | exit 0, same test count as `make test` |
| D8 | `diff -r <dotfiles-nested-openspec> openspec/archive/cli-tools-pre-split` | empty, exit 0 |
| Packaging | `uv lock --check && uv build` | exit 0; `dist/color_scheme_generator-0.1.0-{whl,tar.gz}` |
| Release | `git ls-remote --tags origin v0.1.0` | exactly one line (tag object) + peeled commit |
