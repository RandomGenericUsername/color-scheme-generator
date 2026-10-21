---
id: OPS-002
title: "Prove this repo's own side of the csg invocation contract in CI"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/OPS-002/
branch: ticket/OPS-002-invocation-contract-ci
---

# Prove this repo's own side of the csg invocation contract in CI

> `ops-task` read as `chore`: CI/test capability. No product behaviour change, no release.

## Ceremony choice

**No OpenSpec change, no BMAD.** The slice adds a conformance test and the dev-environment
dependency that makes it runnable; it introduces no requirement, changes no public surface and
resolves no architectural unknown. Git discipline is kept in full: clean-`main` guard, ticket
worktree, planning and implementation commits separated.

## Facts (verified before planning)

| Claim | Command | Observed |
| --- | --- | --- |
| the contract already owns every argv/env/artifact literal for `csg` | `python -c 'from cli_invocation_contract import get; print(get("csg"))'` | `argv` = `generate {wallpaper}` + 8 `--format` flags; `env.required` = `COLORSCHEME__OUTPUT__DIRECTORY`, `COLORSCHEME__OUTPUT__OVERWRITE` (`"true"`); `artifacts` = `exact_filename`, 8 filenames, `min_count 8`; `timeout 60` |
| `custom` is the only backend with no external binary | `rg -n "shutil.which" src/color_scheme_generator/adapters/backends/`; `sed -n 20,33p src/color_scheme_generator/adapters/backends/custom_generator.py` | pywal → `wal`; wallust → `wallust`; custom → `import numpy, PIL.Image, sklearn.cluster` only |
| the `custom` extra resolves from the **existing** lock on Python 3.14 | `uv sync --frozen --extra custom`; `.venv/bin/python -c "import PIL, numpy, sklearn; print(...)"` | lock unchanged; `pillow 12.3.0`, `numpy 2.5.1`, `scikit-learn 1.9.0` |
| the record's invocation (no `--backend`) writes all 8 artifacts with env-only settings | `env -i … COLORSCHEME__GENERATION__BACKEND=custom COLORSCHEME__OUTPUT__DIRECTORY=… .venv/bin/csg generate wall.png --format yaml … --format btop.theme` | exit 0; `colors.{yaml,conf,gtk.css,adw.css,sequences,rasi,kitty,btop.theme}` present, 8 files |
| `main` was clean before branching | `bash scripts/worktree-guard.sh check-clean` | exit 0, no output |

## Backend choice

`custom` — the record's argv carries no `--backend`, so the backend is chosen by the documented
settings mechanism (`COLORSCHEME__GENERATION__BACKEND`, precedence rule 2 in the README). It is
the only backend that needs no `wal`/`wallust` binary, so it works on a bare CI runner. The record
argv, env keys and artifact list stay untouched; the test injects only the record's env values plus
`COLORSCHEME__GENERATION__BACKEND=custom` and `COLORSCHEME__RUNTIME__MODE=local` (both documented
`COLORSCHEME__SECTION__KEY` overrides), so a stray host `settings.toml` cannot move extraction into
container mode.

## CI wiring

The `custom` extra becomes part of the `dev` dependency group
(`"color-scheme-generator[custom]"`), so `make sync` — the step every existing CI job already runs
— installs it and the ordinary `test` and `hermetic` jobs execute the conformance test with no new
job, no new gate and no `scripts/ci-gates-parity.py` change. The test therefore **runs**, it is
never skipped; a missing backend dependency fails collection loudly instead of silently passing.

## Work

1. `pyproject.toml` + `uv.lock`: `dev` group includes `color-scheme-generator[custom]` (2-line lock
   diff; no new packages, no pin change).
2. `tests/integration/test_invocation_contract.py`: build a deterministic 16×16 PNG, run the
   installed `csg` console script with `record["argv"]` (only `{wallpaper}` substituted) in a
   scrubbed env and a tmp output dir, then call
   `assert_cli_writes_artifacts(record, "csg", run, cwd)` from `cli_invocation_contract.testkit`.
   Assert the returned artifact count equals the record's `min_count` (8) and that the files are
   non-empty.
3. `README.md`: note that the dev env carries the `custom` extra because the conformance test runs
   the real binary.
4. `CHANGELOG.md` `[Unreleased]`: tests/CI only, explicitly no version bump.
5. Gates: `make gates`, `make ci-gates-parity`, `uv build`; prove the test under a CI-like env
   (`GITHUB_ACTIONS=true CI=true`, empty HOME/XDG, foreign cwd).

## Done-when

- [x] `tests/integration/test_invocation_contract.py` runs in the existing CI `test` job (no skip,
  no new job), `assert_cli_writes_artifacts` returns 8 artifacts from a real `csg` run, all gates
  are green on the ticket branch, and the branch is ff-merged and pushed with no version bump or
  tag (tests/CI only; wheel content unchanged).

## Evidence

| Claim | Command | Observed |
| --- | --- | --- |
| `main` clean before branching | `bash scripts/worktree-guard.sh check-clean` | exit 0, no output |
| `custom` is the only binary-free backend | `rg -n "shutil.which" src/color_scheme_generator/adapters/backends/` | `pywal_generator.py: return shutil.which("wal")`; `wallust_generator.py: return shutil.which("wallust")`; custom has no `which` |
| the `custom` extra resolves from the existing lock on Python 3.14 | `uv sync --frozen --extra custom`; `.venv/bin/python -c "import PIL, numpy, sklearn; print(...)"` | lock unchanged; `12.3.0 2.5.1 1.9.0` |
| a plain `make sync` now provides the backend (no new CI step) | `uv sync --frozen`; `.venv/bin/python -c "import sklearn"` | `sklearn present after plain sync` |
| the test runs, not skips, under a CI-like env | `GITHUB_ACTIONS=true CI=true HOME=<tmp> XDG_*=… .venv/bin/python -m pytest tests/integration/test_invocation_contract.py -v -rs` | `1 passed in 3.09s` |
| the run through `assert_cli_writes_artifacts` returns the record's 8 artifacts | same helper script as the test, printing the result | `artifact_count=8`; `colors.{adw.css,btop.theme,conf,gtk.css,kitty,rasi,sequences,yaml}`, 306–5280 bytes each |
| `make gates` green | `make gates` | exit 0; `640 passed in 30.89s` (test), `All checks passed!` (lint), `640 passed in 30.90s` (hermetic), `Resolved 35 packages` (lock-check), docs-check silent |
| CI job set unchanged (existing `test`/`hermetic` jobs, no new job) | `make ci-gates-parity` | `PASS gates=[…] jobs=[…] exempt=[ci-gates-parity, image, release]`; `.github/workflows/gates.yml` not modified |
| build green, no version change | `uv build` | `color_scheme_generator-0.2.0.tar.gz` + `...-py3-none-any.whl` |
| wheel code content unchanged; only metadata differs (README note) | build from `main` and from the branch, `diff -r` extracted wheels | 83 entries; only `METADATA`/`RECORD` differ by the README paragraph; no source file differs |

## Findings / deviations

- **Host `csg` shadowing.** The first draft preferred `shutil.which("csg")`; on this host that is
  `/home/inumaki/.local/bin/csg`, an older install without the `custom` extra, and the test failed
  with `BackendNotAvailableError` (`No backends available: custom, pywal, wallust`). The test now
  prefers `<sys.executable>/../csg` and only then PATH, so it proves *this* checkout's CLI. Observed
  fix: `1 passed`.
- **No new CI job, so no `scripts/ci-gates-parity.py` change.** The extra rides the existing `dev`
  group that every job's `make sync` already installs; a `contract` job would have needed a
  CI-only exemption for zero additional coverage.
- **No version bump, no tag.** Runtime code, CLI surface, contract record and dependencies are
  unchanged; only tests, the dev group, README and CHANGELOG moved. The wheel keeps version
  `0.2.0` and identical package sources (the `METADATA` long description gained the README note).
  A tag would claim a product change that did not happen.
