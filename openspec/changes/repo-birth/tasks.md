# Tasks

## 1. Import and scaffold (≤2h)

- [ ] 1.1 Create the public repo and push the subtree-split branch as `main`; verify the 90
  imported commits are present.
  Verify: `git log --oneline | wc -l` → `90` before the scaffold commit; `gh repo view
  RandomGenericUsername/color-scheme-generator --json visibility --jq .visibility` → `PUBLIC`.
- [ ] 1.2 Copy the mu harness byte-for-byte (`scripts/worktree-guard.sh`, `skills-lock.json`,
  `_bmad/`, `.agents/skills/`, `.opencode/`, `tickets/_template/`, `tickets/_fixtures/`,
  `tickets/LIFECYCLE.md`).
  Verify: `diff` against `/home/inumaki/Development/mu/<path>` for each → empty, exit 0; `test -x
  scripts/worktree-guard.sh` → exit 0.
- [ ] 1.3 Write `AGENTS.md` (evidence rule verbatim, `csg` charter with four container backends and
  the template catalog, ticket routing, worktree discipline, planning-vs-implementation, release
  ritual) and `CLAUDE.md` → `AGENTS.md`.
  Verify: `test -L CLAUDE.md` → exit 0; `rg -c "Evidence:|Verify:" AGENTS.md` → ≥ 2.

## 2. Ledger and specs (≤2h)

- [ ] 2.1 Add `tickets/INDEX.md` with the counting-rule header and
  `tickets/REQ-001-repo-birth/`.
  Verify: `rg -n "REQ-001" tickets/INDEX.md tickets/REQ-001-repo-birth/ticket.md` → both hit.
- [ ] 2.2 Add `openspec/config.yaml`, the three imported capability specs, and the `repo-birth`
  change (proposal, design, tasks, spec delta).
  Verify: `openspec validate --specs --strict` and `openspec validate repo-birth --strict` →
  exit 0.
- [ ] 2.3 Carry the nested `dotfiles-v3` `src/cli-tools/openspec/` tree verbatim into
  `openspec/archive/cli-tools-pre-split/` with a provenance note.
  Verify: `diff -r <dotfiles>/src/cli-tools/openspec openspec/archive/cli-tools-pre-split` →
  empty, exit 0.

## 3. Gates and release (≤2h)

- [ ] 3.1 Add the fresh-clone `Makefile` and `scripts/ci-gates-parity.py`; make every verb run
  from `$(CURDIR)`.
  Verify: `make gates` → exit 0; `make ci-gates-parity` → `PASS ...`.
- [ ] 3.2 Add `.github/workflows/gates.yml` with one job per gate, `ci-gates-parity`, an `image`
  job, and a tag-only `release` job.
  Verify: `make ci-gates-parity` → exit 0 (the workflow is parsed, not grepped).
- [ ] 3.3 Prove the image story from the repo root: build all four Dockerfiles at `v0.1.0` and run
  `csg --version` in the base image.
  Verify: `make image IMAGE_TAG=v0.1.0` → exit 0 and `0.1.0 contract 0.1.0`; `podman images`
  lists `csg-base-podman:v0.1.0`, `csg-custom-podman:v0.1.0`, `csg-pywal-podman:v0.1.0`,
  `csg-wallust-podman:v0.1.0`.
- [ ] 3.4 Prove the install verb builds the same tag-qualified images from `--context .`.
  Verify: `COLORSCHEME__CONTAINER__IMAGE_TAG=v0.1.0 csg install --context . --container-engine
  podman` → exit 0 (base + three backends).
- [ ] 3.5 Prove packaging on a fresh clone: `uv sync --frozen`, `uv run pytest -q`, `make gates`,
  `uv build`.
  Verify: exit 0; `uv run pytest -q` → `639 passed`; `ls dist/color_scheme_generator-0.1.0-*`
  lists a wheel and an sdist.
- [ ] 3.6 Tag annotated `v0.1.0` after the gates and CI exist; push the tag; confirm the Release
  carries both artifacts.
  Verify: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote
  https://github.com/RandomGenericUsername/color-scheme-generator 'refs/tags/v0.1.0'` →
  exactly one line; `gh release view v0.1.0 --json assets --jq '.assets[].name'` → wheel + sdist.

## 4. Closeout (≤0.5h)

- [ ] 4.1 Tick acceptance, record commands + results in the ticket, move the INDEX entry to Done.
  Verify: `git status --porcelain` → empty; `rg -n "REQ-001" tickets/INDEX.md` → the Done
  section lists it.
