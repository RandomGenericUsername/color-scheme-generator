---
id: OPS-001
title: "Re-pin contracts v0.2.0 and release csg v0.2.0"
kind: ops-task
status: in-progress
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

`csg --version` prints `0.2.0 contract 0.2.0` from the released `v0.2.0` tag (isolated install and
base image), the lock pins contracts `c6c3ab5d…`, all gates are green, and the GitHub Release
carries both artifacts.
