---
id: OPS-001
title: "Re-pin contracts v0.2.0 and release csg v0.2.0"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/OPS-001/
branch: ticket/OPS-001-repin-contracts-v020
---

# Re-pin contracts v0.2.0 and release csg v0.2.0

> `ops-task` read as `chore`: dependency re-pin + release ritual. No product behaviour change.

## Ceremony choice

**No OpenSpec change, no BMAD.** This ticket moves a pin and cuts a release; it adds no
requirement, changes no public surface and introduces no architectural unknown, so there is no
delta to propose or archive. The bounded-slice route (`/opsx-propose`) would produce an empty
spec delta. Git discipline is kept in full: clean-`main` guard, ticket worktree, planning and
implementation commits separated.

## Facts (verified before planning)

| Claim | Command | Observed |
| --- | --- | --- |
| `contracts` `v0.2.0` is an annotated tag on `442fb9ab…` peeling to `c6c3ab5d…` | `git -C /tmp/opencode/contracts-check cat-file -t v0.2.0`; `rev-parse v0.2.0`; `rev-parse 'v0.2.0^{commit}'` | `tag`; `442fb9abdc73fa109115ba804911a10af9f4cad1`; `c6c3ab5d523d06210f8e87535c464d3190d005c0` |
| the pinned contract source reports `CONTRACT_VERSION = "0.2.0"` and `DATA_VERSION = 2` | `grep -rn "CONTRACT_VERSION\|DATA_VERSION" src` at `v0.2.0` | `src/cli_invocation_contract/__init__.py:34: CONTRACT_VERSION = "0.2.0"`; `:38: DATA_VERSION = 2` |
| the data-v2 change is the itr-only `ICON_RENDERER__TEMPLATES__DIR` env key, so `csg`'s record shape is unchanged | `git log --oneline -1 v0.2.0` | `c6c3ab5 feat(REQ-008): record ICON_RENDERER__TEMPLATES__DIR for itr (contract 0.2.0, data v2)` |
| current pin is `v0.1.0` at `48cf3cfe…` | `grep -n contracts uv.lock` | `source = { git = ".../contracts?tag=v0.1.0#48cf3cfed4b192b241505789409c4f282921c896" }` |
| `main` was clean before branching | `bash scripts/worktree-guard.sh check-clean` | exit 0, no output |

## Work

1. `pyproject.toml`: `[tool.uv.sources]` contracts tag `v0.1.0` → `v0.2.0`; package
   `version` `0.1.0` → `0.2.0`.
2. `uv lock` and prove the lock records the peeled commit `c6c3ab5d…`.
3. `tests/unit/cli/test_version_flag.py`: keep deriving the contract token from
   `cli_invocation_contract.CONTRACT_VERSION` and add an explicit `0.2.0` assertion, so a silent
   pin regression fails loudly.
4. `CHANGELOG.md`: `0.2.0` entry (re-pin, version bump, no behaviour change).
5. Gates: `make gates`, `uv build`, `make image IMAGE_ENGINE=podman IMAGE_TAG=v0.2.0` plus
   `csg --version` in the base image.
6. Release: commit, ff-merge to `main`, push, annotated tag `v0.2.0`, GitHub Release with the
   wheel + sdist built from the tag, isolated tag install, anonymous `ls-remote`, CI green.

## Done-when

- [x] `csg --version` prints `0.2.0 contract 0.2.0` from the released `v0.2.0` tag (isolated install
  and base image), the lock pins contracts `c6c3ab5d…`, all gates are green, and the GitHub Release
  carries both artifacts.

## Evidence

| Claim | Command | Observed |
| --- | --- | --- |
| `main` clean before branching | `bash scripts/worktree-guard.sh check-clean` | exit 0, no output |
| worktree + branch | `bash scripts/worktree-guard.sh create OPS-001 repin-contracts-v020` | `worktree=.worktrees/OPS-001/`; `branch=ticket/OPS-001-repin-contracts-v020` |
| tag facts re-verified in a fresh clone | `git cat-file -t v0.2.0`; `git rev-parse v0.2.0`; `git rev-parse 'v0.2.0^{commit}'` in `/tmp/opencode/contracts-check` | `tag`; `442fb9abdc73fa109115ba804911a10af9f4cad1`; `c6c3ab5d523d06210f8e87535c464d3190d005c0` |
| installed contract reports 0.2.0 / data v2 | `uv run python -c "import cli_invocation_contract as c; print(c.CONTRACT_VERSION, c.DATA_VERSION)"` | `0.2.0 2` |
| pin + version bumped | `git show a0f56ad -- pyproject.toml` | `version = "0.2.0"`; contracts `tag = "v0.2.0"` |
| lock records the peeled commit | `uv lock`; `grep -n contracts uv.lock` | `Updated cli-invocation-contract v0.1.0 (48cf3cfe) -> v0.2.0 (c6c3ab5d)`; `.../contracts?tag=v0.2.0#c6c3ab5d523d06210f8e87535c464d3190d005c0` |
| version test derives the token and trips on a stale pin | `uv run pytest tests/unit/cli/test_version_flag.py -q` | `1 passed` |
| suite | `uv run pytest -q` | `639 passed in 29.37s` |
| gates | `make gates` | exit 0; `639 passed` ×2, `All checks passed!`, `Resolved 35 packages in 1ms` |
| packaging | `uv build` | exit 0; `color_scheme_generator-0.2.0-py3-none-any.whl` (77 850 B) + `.tar.gz` (126 708 B) |
| images at the pin | `make image IMAGE_ENGINE=podman IMAGE_TAG=v0.2.0` | exit 0; `csg-{base,custom,pywal,wallust}-podman:v0.2.0` tagged; `0.2.0 contract 0.2.0` |
| CI tag derives from pyproject | `make -n image IMAGE_ENGINE=docker` | `docker build -t "csg-base-docker:v0.2.0" …` |
| workflow/GATES parity | `make ci-gates-parity` | `PASS gates=[…5] jobs=[…8] exempt=[ci-gates-parity, image, release]` |
| ff-merge to `main` | `git merge --ff-only ticket/OPS-001-repin-contracts-v020` | `Updating 1b235b5..9e23232`; `Fast-forward` |
| annotated tag on the released commit | `git cat-file -t v0.2.0`; `git rev-parse v0.2.0`; `git rev-parse 'v0.2.0^{commit}'` | `tag`; `0168c1bdad71876c11156aa3eaf19e2d4c80968e`; `9e23232d59480eaa0f4b65dedd7d8a4c194ab103` |
| anonymous fetch, one line | `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote … 'refs/tags/v0.2.0'` | `0168c1bdad71876c11156aa3eaf19e2d4c80968e	refs/tags/v0.2.0` |
| isolated tag install | `UV_TOOL_DIR=… UV_TOOL_BIN_DIR=… uv tool install --python 3.14 git+…@v0.2.0`; `csg --version` | `Installed 1 executable: csg`; `0.2.0 contract 0.2.0`; contract `direct_url.json` → `commit_id c6c3ab5d…`, `requested_revision v0.2.0` |
| release carries both artifacts | `gh release view v0.2.0 --json …` | `draft:false`, `pre:false`, tag `v0.2.0`; wheel 77 854 B + sdist 126 709 B, both `uploaded` |
| tag CI green, `image` at the new tag | `gh run view 39656868029` | success: test, lint, hermetic, lock-check, docs-check, ci-gates-parity, image, release; image log `docker build -t "csg-base-docker:v0.2.0"` → `0.2.0 contract 0.2.0` |
| `main` CI green | `gh run view 39656853378` | success |

## Deviations

1. **Two commits before the tag, plus this closeout.** Planning (`9b15748`), implementation
   (`a0f56ad`), README docs (`9e23232`). AGENTS §5 keeps docs out of the implementation commit, so
   the README version/tag examples were their own commit; the tag points at `9e23232`, the last
   content commit. This closeout commit follows the tag and carries no product change (the REQ-001
   pattern).
2. **`.github/workflows/gates.yml` `image` job no longer hardcodes `IMAGE_TAG=v0.1.0`.** It ran
   `make image IMAGE_ENGINE=docker IMAGE_TAG=v0.1.0`, which would have built a v0.2.0 package at a
   stale tag label on this release. It now calls `make image IMAGE_ENGINE=docker`, so the tag comes
   from `IMAGE_TAG ?= v$(VERSION)`. Job names are unchanged, so `ci-gates-parity` still passes.
3. **`README.md` "What `dotfiles-v3` pins" still says `v0.1.0`.** That is the consumer's actual pin
   (`dotfiles-v3/dotfiles/provisioning/cli-tools.yaml`, `tag: v0.1.0`), and the consumer bump is a
   separate repo's commit, out of scope here. Everything else in README names `0.2.0`.

## Closeout

Released 2026-10-21 at `9e23232` (annotated tag `v0.2.0` → tag object `0168c1bd`). The tag CI run
`39656868029` is green including `image` (built at `csg-*-docker:v0.2.0`) and `release` (both
artifacts attached), and `main` run `39656853378` is green. An isolated install of the tag and the
base image both print `0.2.0 contract 0.2.0`.

## MISSING / not done here

- `dotfiles-v3` consumer pin bump (`csg` `v0.1.0` → `v0.2.0`) — another repo, own commit, per
  AGENTS §6.
- No real generation run through the `v0.2.0` backend image this time: the record shape is
  unchanged (data v2 adds only an itr key) and the suite covers generation, but no `csg generate
  --runtime container` was executed against `csg-wallust-podman:v0.2.0`.
