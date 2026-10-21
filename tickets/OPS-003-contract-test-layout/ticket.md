---
id: OPS-003
title: "Move the invocation-contract test to tests/contract/ (path-only)"
kind: ops-task
status: done
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

- [x] `tests/contract/test_invocation_contract.py` is the only path for the conformance test, the
  old path is gone, `git show --stat -M` reports a rename, all gates are green on the ticket
  branch, and the branch is ff-merged and pushed with no tag or version bump.

## Evidence

| Claim | Command | Observed |
| --- | --- | --- |
| `main` clean before branching | `bash scripts/worktree-guard.sh check-clean` | exit 0, no output |
| baseline before the move | `make gates` | exit 0; `640 passed in 33.57s` (test), `640 passed in 31.46s` (hermetic) |
| the file carries no location dependency | `rg -n '__file__\|parent\|chdir\|fixtures\|data/' tests/integration/test_invocation_contract.py` (pre-move) | only `Path(sys.executable).parent` and `mkdir(parents=True)`; no `__file__`, no fixture path, no relative import — so nothing to fix after the move |
| the move is a rename, not a rewrite | `git show --stat -M 274ed5a` | `tests/{integration => contract}/test_invocation_contract.py \| 0`; `tests/contract/__init__.py \| 0`; only `README.md`/`CHANGELOG.md` change a line |
| the old path is gone | `ls tests/integration`; `test -e tests/integration/test_invocation_contract.py` | `adapters/`, `__pycache__`; old path test exit 1 (absent) |
| the moved test runs, not skips | `uv run pytest tests/contract -q -rs` | exit 0; `1 passed in 3.26s`; no skip line printed |
| the run still produces the record's 8 artifacts | moved test's own helpers + `assert_cli_writes_artifacts`, printing the result (same script shape as OPS-002) | `artifact_count=8`, `min_count=8`; `colors.{adw.css,btop.theme,conf,gtk.css,kitty,rasi,sequences,yaml}`, 306–5280 bytes |
| `make gates` green with unchanged counts | `make gates` | exit 0; `640 passed in 31.59s` (test), `All checks passed!` (lint), `640 passed in 31.54s` (hermetic), `Resolved 35 packages` (lock-check), docs-check silent |
| CI job set unchanged | `make ci-gates-parity` | `PASS gates=['docs-check','hermetic','lint','lock-check','test'] jobs=[…] exempt=['ci-gates-parity','image','release']` |
| build green, no version change | `uv build` | exit 0; `color_scheme_generator-0.2.0.tar.gz` + `...-py3-none-any.whl` |
| no stale reference to the old test path | `rg -n 'tests/integration\|integration/test_invocation_contract' README.md CHANGELOG.md .github docs scripts Makefile pyproject.toml tests` | only `docs/ARCHITECTURE_PLAN.md:769` (describes the still-existing `tests/integration/` dir) and `tests/integration/adapters/test_btop_theme_applies.py:126` (a comment about its own path) |

## Findings / deviations

- **Nothing to fix inside the file.** It builds its own PNG and output dir under `tmp_path` and
  imports only absolute modules, so the move needed no import or fixture rewrite — confirmed by the
  zero-line rename diff and by the green test run.
- **`docs/ARCHITECTURE_PLAN.md:769` left as is.** It describes the `tests/integration/` directory,
  which still exists for the btop test; it does not name the moved file.
- **Closed `OPS-002` left as is.** Its ticket text records the state at that time; history is not
  rewritten.
- **No tag, no version bump.** The wheel/sdist version stays `0.2.0`; only test layout and the two
  doc lines naming the test changed. A path-only move is not a product change.
