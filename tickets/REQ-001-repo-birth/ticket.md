---
id: REQ-001
title: "Birth the color-scheme-generator repo (mu-strict, csg) and cut v0.1.0"
kind: requirement
status: done
lane: 3
links:
  openspec: repo-birth
  bmad: none
worktree: none
branch: main
---

# Birth the color-scheme-generator repo (mu-strict, csg) and cut v0.1.0

## Requirement

Slice **S6a** of the CLI-repos split SHALL create
`RandomGenericUsername/color-scheme-generator` as a public repo whose root is the imported
`src/cli-tools/color-scheme-generator` package, preserve that package's history with
`git subtree split`, carry the retired nested OpenSpec tree as archive (spine AD-15), install the
`mu` harness byte-for-byte, prove all four container images build from the repo root
(spine AD-5/AD-7), and cut the repo's first tag (`v0.1.0`) only after the gates, packaging, image
proof and CI exist.

The package owns its four Dockerfiles and its `install` build verb. The image build context is this
repo root and the image tag is the pin (`v0.1.0`), never `latest`. The bundled template catalog stays
at `src/color_scheme_generator/defaults/templates/` because `dotfiles-v3` provisioning copies it
(AD-10). `dotfiles-v3` is not modified — the consumer rewire and the in-tree deletion are the
remaining S6 steps in that repo.

## Acceptance

- [x] The repo exists, is **public**, and its `main` carries the imported subtree commits.
  Verify: `gh api repos/RandomGenericUsername/color-scheme-generator --jq .private` → `false`;
  `git log --oneline | wc -l` → 90 imported commits before the scaffold.
- [x] The harness is byte-identical to `mu` at every copied path.
  Verify: `diff -r` per path (see the evidence table) → empty, exit 0.
- [x] `AGENTS.md` carries the evidence rule and this repo's charter; `CLAUDE.md` is a symlink.
  Verify: `rg -c "Evidence:|Verify:" AGENTS.md` → `6`; `test -L CLAUDE.md` → exit 0.
- [x] `tickets/INDEX.md` lists this ticket with the same status as the frontmatter, the OpenSpec
  change validates strictly, and the carried archive matches its source.
  Verify: `openspec validate --specs --strict` → 3 passed; `openspec validate repo-birth --strict`
  → valid; `diff -r -x README.md <dotfiles>/src/cli-tools/openspec
  openspec/archive/cli-tools-pre-split` → empty.
- [x] A fresh clone passes `make sync && make gates && make build` and the suite count is 639.
  Verify (fresh clone at `v0.1.0`): `make sync && make gates && make build && make hermetic` →
  exit 0; `uv run pytest -q` → `639 passed`; `ls dist/color_scheme_generator-0.1.0-*` → wheel +
  sdist.
- [x] All four images build from the repo root at the pin tag, and the base image reports the
  contract version.
  Verify: `make image IMAGE_TAG=v0.1.0` → exit 0; `podman run --rm csg-base-podman:v0.1.0 csg
  --version` → `0.1.0 contract 0.1.0`.
- [x] `csg install --context .` builds the tag-qualified images from this checkout, and a real
  generation run through the pinned backend image writes all requested artifacts.
  Verify: `COLORSCHEME__CONTAINER__IMAGE_TAG=v0.1.0 csg install --context . --container-engine
  podman` → base + three backends at `:v0.1.0`; `csg generate … --runtime container` → eight
  `colors.*` files.
- [x] `.github/workflows/gates.yml` exists and its job set equals `GATES` (plus declared CI-only
  jobs); the first run on `main` is green.
  Verify: `make ci-gates-parity` → `PASS ...`; `gh run view 39605204861` → success (all seven gate
  jobs + image).
- [x] Annotated tag `v0.1.0` exists on the released commit, is anonymously fetchable, and its
  GitHub Release carries the wheel + sdist.
  Verify: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote
  https://github.com/RandomGenericUsername/color-scheme-generator 'refs/tags/v0.1.0'` → exactly one
  line; `gh release view v0.1.0 --json assets` → both artifacts `uploaded`.
- [x] `git status --porcelain` is empty in both repos; `dotfiles-v3` `master` is at the same SHA
  as before the slice.
  Verify: `git status --porcelain` → empty; `git -C /home/inumaki/Development/dotfiles-v3 rev-parse
  master` → `6e0633baa2dae28f3193397fa529234074f026c1`.

## Out of scope

- Rewiring `dotfiles-v3` (`provisioning/cli-tools.yaml`, `provisioning/assets.yaml`,
  `roles/cli_tools`, `roles/assets`, `roles/verify`, `deploy-coverage`) to the `{name, repo, tag}`
  pin and deleting `src/cli-tools/` — those are the remaining S6 steps in that repo.
- Any package behaviour change; the extraction adds harness, packaging metadata and docs only.
- Changes to the invocation-contract content.
- PyPI publication; the channel is the git tag plus GitHub Release artifacts.

## Evidence

| Claim | Command | Observed |
| --- | --- | --- |
| name free, repo created public | `gh repo create RandomGenericUsername/color-scheme-generator --public --description …`; `gh api repos/... --jq .private` | `https://github.com/RandomGenericUsername/color-scheme-generator`; `false` |
| legacy untouched | `gh repo view RandomGenericUsername/color-scheme-generator-legacy --json name,isPrivate` | `{"isPrivate":true,"name":"color-scheme-generator-legacy"}` |
| history preserved | `git subtree split -P src/cli-tools/color-scheme-generator -b split/color-scheme-generator`; `git rev-list --count split/color-scheme-generator` | branch created; tip `b991db0cee293e8e3600484425f04ea2ec9ceb01`; `90` commits |
| imported tree pushed | `git push <repo> refs/heads/split/color-scheme-generator:refs/heads/main` | `* [new branch] split/color-scheme-generator -> main`; clone HEAD `b991db0` |
| harness byte-identical | `diff -r mu/<path> <path>` for `_bmad`, `.agents/skills`, `.opencode`, `scripts/worktree-guard.sh`, `skills-lock.json`, `tickets/_template`, `tickets/_fixtures`, `tickets/LIFECYCLE.md` | `IDENTICAL` × 8, exit 0; `test -x scripts/worktree-guard.sh` → exit 0 |
| evidence rule present | `rg -c "Evidence:\|Verify:" AGENTS.md`; `test -L CLAUDE.md` | `6`; exit 0 |
| specs/change valid | `openspec validate --specs --strict`; `openspec validate repo-birth --strict` | `3 passed, 0 failed`; `Change 'repo-birth' is valid` |
| nested openspec carried | `diff -r -x README.md dotfiles-v3/src/cli-tools/openspec openspec/archive/cli-tools-pre-split` | empty, exit 0 (5 files + provenance `README.md`) |
| suite | `uv run pytest -q` | `639 passed` (ambient and hermetic) |
| gates | `make gates` | exit 0; `639 passed` ×2, `All checks passed!`, lock current, docs-check silent |
| packaging | `make build` | exit 0; `color_scheme_generator-0.1.0-py3-none-any.whl` + `.tar.gz` |
| images at the pin | `make image IMAGE_ENGINE=podman IMAGE_TAG=v0.1.0`; `podman run --rm csg-base-podman:v0.1.0 csg --version` | four builds exit 0; base `a7f2c212eecb`, custom `1d45288281ca`, pywal `e1836d276d46`, wallust `b03c347c526b`; `0.1.0 contract 0.1.0` |
| install verb | `COLORSCHEME__CONTAINER__IMAGE_TAG=v0.1.0 .venv/bin/csg install --context . --container-engine podman` | exit 0; `backend: base/custom/pywal/wallust`, all `status: built` at `csg-*-podman:v0.1.0` |
| pin path never tags `latest` | `podman images --format '{{.Repository}}:{{.Tag}} {{.CreatedAt}}'` | all `:v0.1.0` images created 12:48–12:49; the only `:latest` images predate this slice (00:43–00:45, from S3/S5 work) |
| real generation | tag-installed `csg generate … --runtime container --backend wallust` with eight `--format` flags | exit 0; `colors.{yaml,conf,gtk.css,adw.css,sequences,rasi,kitty,btop.theme}` |
| fresh clone at the tag | `git clone --branch v0.1.0 …`; `make sync && make gates && make build && make hermetic && uv lock --check` | HEAD `14f2faf`; `639 passed` ×2; wheel + sdist; lock current |
| tag install | `UV_TOOL_DIR=… uv tool install --force git+…@v0.1.0`; `csg --version` | `Installed 1 executable: csg`; `0.1.0 contract 0.1.0` |
| CI parity | `make ci-gates-parity` | `PASS gates=[…5] jobs=[…8] exempt=[ci-gates-parity, image, release]` |
| CI run 1 (`9c32283`) | `gh run view 39603307663` | **failure**: `test`/`hermetic` — Typer forced a terminal under `GITHUB_ACTIONS` and Rich interleaved ANSI into option names |
| CI run 2 (`bfd96a7`) | `gh run view 39604658605` | **failure**: same class; the fix had to land before Typer is imported |
| green main run (`14f2faf`) | `gh run view 39605204861` | **success** (test, lint, hermetic, lock-check, docs-check, ci-gates-parity, image) |
| tag CI run | `gh run view 39605345653` | **success**, all 8 jobs incl. `release` |
| annotated tag | `git cat-file -t v0.1.0`; `git rev-parse v0.1.0`; `git rev-parse 'v0.1.0^{commit}'` | `tag`; `47afbbdf4b3d1d7a2ac6dbc9cfea3d6d4487b335`; `14f2faf590f503cc60baf0da81955076e9e42214` |
| anonymous fetch | `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote … 'refs/tags/v0.1.0'` | exactly one line: `47afbbdf… refs/tags/v0.1.0` |
| release artifacts | `gh release view v0.1.0 --json assets` | `color_scheme_generator-0.1.0-py3-none-any.whl` (77 847 B) + `.tar.gz` (125 873 B), both `uploaded` |
| dotfiles untouched | `git -C dotfiles-v3 rev-parse master`; `git status --porcelain`; `git branch --list 'split/color-scheme-generator'` | `6e0633baa2dae28f3193397fa529234074f026c1`; empty; the local split ref only |

## Deviations from the slice text

1. **The nested OpenSpec tree is carried verbatim, including the placeholder spec and
   `.openspec.yaml`.** `SLICES.md` § S6 step 3 said to drop `specs/no-spec-changes.md` and the
   nested `.openspec.yaml`; this slice's instruction was to preserve content. Preserving won: all
   five files are byte-identical under `openspec/archive/cli-tools-pre-split/`, plus a provenance
   `README.md`. It is inert archive under `archive/`, not a second root, and the change validates
   as a single active root. The path is also the instructed `openspec/archive/cli-tools-pre-split/`
   rather than SLICES' `openspec/changes/archive/…`.
2. **`csg install` has no `--image-tag` flag.** The imported verb reads the tag from
   `[container] image_tag`; S5 added `--image-tag` to `weg` only. The tag was supplied with
   `COLORSCHEME__CONTAINER__IMAGE_TAG=v0.1.0`, which is a documented override rule in
   `config_resolver.py`. No flag was added: a second source of truth for the tag is a regression,
   and provisioning already renders the setting.
3. **`Dockerfile.base` copies `README.md` and `LICENSE`** in addition to `pyproject.toml`,
   `uv.lock` and `src/`: hatchling reads the release metadata while building the wheel in the image
   (same deviation the `weg` birth recorded). Every copied path is repo-relative.
4. **`make lint` scopes to `src/`.** The imported `tests/` tree has ~30 pre-existing style findings
   (long fixture lines, `B008` in test doubles) that in-tree had no ruff gate; rewriting them is out
   of slice scope. `src/` had 24 findings: `B008` is ignored (Typer's declaration idiom, as in
   `weg`) and the 17 `E501`/`E701`/`E741` findings were fixed without behaviour change.
5. **Two CI-driven test-harness fixes, no product change.** Typer sets `FORCE_TERMINAL` when it
   sees `GITHUB_ACTIONS` or `FORCE_COLOR` **at import time**, so Rich wrapped help text and split
   `--install-completion` with ANSI escapes. `tests/conftest.py` now pins
   `_TYPER_FORCE_DISABLE_TERMINAL`, `NO_COLOR`, `COLUMNS` and `TERMINAL_WIDTH` before importing the
   CLI, and the autouse hermetic fixture re-asserts them per test. Verified locally with
   `GITHUB_ACTIONS=true FORCE_COLOR=1 COLUMNS=40 uv run pytest -q` → `639 passed`.
6. **Suite count is 639**, matching the in-tree baseline (the slice note said 638–639).
7. **Host-local `:latest` csg images remain.** Four `csg-*-podman:latest` images exist from earlier
   S3/S5 container work (timestamps 00:43–00:45); this slice's pin path produced only `:v0.1.0`
   (12:48–12:49). Nothing from the pin path tagged `latest`.

## Closeout

Closed 2026-10-21. The public repo was created, `main` was pushed at six commits (90 imported +
planning `00ff44b`, implementation `d8e50a1`, spec tightening `9c32283`, and the two test-harness
fixes `bfd96a7`/`14f2faf`), and CI on `14f2faf` is green. The annotated tag `v0.1.0` points at that
tested commit (tag object `47afbbdf`); the tag-triggered run `39605345653` built and attached both
artifacts to the GitHub Release. A fresh clone of the public repo at `v0.1.0` passes the full gate
set, the tagged tool installs and prints `0.1.0 contract 0.1.0`, and a real eight-format generation
runs through the `csg-wallust-podman:v0.1.0` image. This closeout commit follows the tag and carries
no product change.

`dotfiles-v3` remains at `6e0633baa2dae28f3193397fa529234074f026c1` with a clean tree; the only
change there is the local `split/color-scheme-generator` branch. The remaining S6 work lives in
`dotfiles-v3` (manifest/assets/role/verify pin, `deploy-coverage` shape assertions, in-tree
deletion).

### Birth-worktree exception

The scaffold commits were made on `main` in the fresh repo (the slice instruction), as in the
sibling births: `scripts/worktree-guard.sh create` needs a clean `main` to branch from, and the repo
had no scaffold commit yet. Every later item uses a ticket worktree.
