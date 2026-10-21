# repo-birth

## Why

`color-scheme-generator` is the last CLI extracted from `dotfiles-v3` in the CLI/split programme
(spine `SLICES.md` § S6). The package is green in-tree and its Dockerfiles were already rewritten in
S3 to copy only package-relative paths, but a repository is not a valid extraction target until it
is mu-strict from its first commit (spine **AD-12**) and all four images are proven to build from
**its own repo root** (AD-5).

Evidence: the package has 49 tracked `test_*.py` files and no sibling path inside its Dockerfiles.
Verify: `git -C /home/inumaki/Development/dotfiles-v3 ls-tree -r --name-only master --
src/cli-tools/color-scheme-generator | grep -c '^tests/.*test_.*\.py$'` → `49`;
`rg -n "src/shared|src/cli-tools|\.\./" src/color_scheme_generator/adapters/docker/` → exit 1.

Evidence: the split must preserve history with `git subtree split`, not a fresh-root import
(spine OPEN-8, `SLICES.md` § Slice template step 2).
Verify: `git -C /home/inumaki/Development/dotfiles-v3 subtree split -P
src/cli-tools/color-scheme-generator -b split/color-scheme-generator` → exit 0, branch tip
`b991db0c`, 90 commits.

Evidence: the harness must be copied from `mu`, not re-authored (AD-12).
Verify: `diff -r /home/inumaki/Development/mu/_bmad _bmad` → empty; same for
`scripts/worktree-guard.sh`, `skills-lock.json`, `.agents/skills`, `.opencode`, `tickets/_template`,
`tickets/_fixtures`, `tickets/LIFECYCLE.md`.

## What Changes

- Create the public repo `RandomGenericUsername/color-scheme-generator`, default branch `main`, from
  the `git subtree split` result of `src/cli-tools/color-scheme-generator` (90 commits preserved).
- Carry the nested `src/cli-tools/openspec/` tree into this repo as
  `openspec/archive/cli-tools-pre-split/` (AD-15): one completed csg-only change
  (`fix-container-engine-plumbing`) plus its placeholder spec, preserved verbatim with a provenance
  note. It is archive, not an active OpenSpec root.
- Install the mu-strict harness **byte-for-byte**: `scripts/worktree-guard.sh`, `skills-lock.json`,
  `_bmad/`, `.agents/skills/`, `.opencode/`, `tickets/_template/`, `tickets/_fixtures/`,
  `tickets/LIFECYCLE.md`.
- Add the repo contract: `AGENTS.md` (evidence rule verbatim, charter = `csg` with four container
  backends and the template catalog, ticket routing, never work on main, planning vs implementation,
  release ritual), `CLAUDE.md` → `AGENTS.md`.
- Add the work ledger: `tickets/INDEX.md` (counting rule header), `tickets/REQ-001-repo-birth/`.
- Add the OpenSpec root: `openspec/config.yaml`, `openspec/specs/{csg-cli,csg-container-mode,
  csg-template-catalog}/` and this change.
- Add a fresh-clone Makefile (`sync`, `test`, `lint`, `format`, `check`, `hermetic`, `lock-check`,
  `docs-check`, `gates`, `gates-ci`, `build`, `install`, `image`, `clean`, `ci-gates-parity`),
  `.github/workflows/gates.yml` (one job per gate + `ci-gates-parity` + `image` + tag release),
  `scripts/ci-gates-parity.py`, MIT `LICENSE`, `README.md`, `CHANGELOG.md`, `.gitignore`,
  `.dockerignore`.
- Keep packaging honest: the four sibling dependencies stay git-tag sources with compatibility
  ranges and a current committed `uv.lock`; `uv build` produces
  `color_scheme_generator-0.1.0` sdist + wheel.
- `Dockerfile.base` copies `README.md` and `LICENSE` because hatchling reads release metadata while
  building the wheel in the image; every copied path is repo-relative.

## Out of scope

- Rewiring `dotfiles-v3` (`provisioning/cli-tools.yaml`, `provisioning/assets.yaml`,
  `roles/cli_tools`, `roles/assets`, `roles/verify`, `deploy-coverage`) to the `{name, repo, tag}`
  pin, and deleting `src/cli-tools/` — those are the remaining S6 steps in that repo.
- Any palette/backend/template behaviour change.
- Changes to the invocation-contract record.
- PyPI publication.
