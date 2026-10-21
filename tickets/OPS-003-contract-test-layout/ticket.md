---
id: OPS-003
title: "Move the invocation-contract test to tests/contract/ (path-only)"
kind: ops-task
status: in-progress
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/OPS-003/
branch: ticket/OPS-003-contract-test-layout
---

# Move the invocation-contract test to `tests/contract/` (path-only)

> `ops-task` read as `chore`: test layout. **Path-only, no behaviour change.** No assertion, no
> fixture, no dependency, no public surface and no packaging content changes; the same test file
> lands one directory over because that is the sibling-repo convention for a conformance suite.

## Ceremony choice

**No OpenSpec change, no BMAD.** A file move plus the doc lines that name it introduce no
requirement and resolve no architectural unknown. Git discipline is kept in full: clean-`main`
guard, ticket worktree, planning and implementation in separate commits.

## Facts (verified before the move)

| Claim | Command | Observed |
| --- | --- | --- |
| `main` clean before branching | `bash scripts/worktree-guard.sh check-clean` | exit 0, no output |
| the current location is the only integration conformance test | `ls tests/integration` | `adapters/`, `test_invocation_contract.py` |
| other test dirs in this repo are packages | `ls tests/*/__init__.py` | `tests/unit/__init__.py` — so `tests/contract/` becomes a package too |
| the file is location-independent | `rg -n '__file__\|parent\|chdir\|fixtures\|data/' tests/integration/test_invocation_contract.py` | only `Path(sys.executable).parent` (line 95) and `mkdir(parents=True)` (line 148); no `__file__`, no fixture path, no relative import |
| only the test file and docs name the old path | `rg -n 'integration/test_invocation_contract\|tests/integration' README.md CHANGELOG.md .github docs tickets openspec scripts Makefile pyproject.toml` | `README.md:103`, `CHANGELOG.md:11` (the test specifically); `docs/ARCHITECTURE_PLAN.md:769` and the closed `OPS-002` ticket describe the *directory/record*, not this test |
| the sibling convention is `tests/contract/` | `find /home/inumaki/Development/dotfiles/*/tests -maxdepth 2 -name '__init__.py'` | `wallpaper-effects-generator/tests/contract/__init__.py`, `icon-templates-renderer/tests/contract/` (with its own `test_invocation_contract.py`) |
| baseline is green before the move | `make gates` | exit 0; `640 passed in 33.57s` (test), `640 passed in 31.46s` (hermetic) |

`docs/ARCHITECTURE_PLAN.md:769` keeps describing `tests/integration/` because
`tests/integration/adapters/test_btop_theme_applies.py` stays there; rewriting history in the
closed `OPS-002` ticket is not done.

## Work

1. `git mv tests/integration/test_invocation_contract.py tests/contract/test_invocation_contract.py`.
2. Add `tests/contract/__init__.py` (this repo's `tests/unit/` is a package; the siblings do the
   same) so the new directory matches the package convention.
3. Update the two doc lines that name the test: `README.md:103`, `CHANGELOG.md:11`.
4. Prove: `uv run pytest tests/contract -q -rs` → 1 passed (8 artifacts, no skip), `make gates`
   exit 0 with the same `640` counts, `make ci-gates-parity` PASS, `uv build` exit 0.
5. Commit, ff-merge to `main`, push. No tag, no version bump.

## Done-when

- [ ] `tests/contract/test_invocation_contract.py` is the only path for the conformance test, the
  old path is gone, `git show --stat -M` reports a rename, all gates are green on the ticket
  branch, and the branch is ff-merged and pushed with no tag or version bump.
