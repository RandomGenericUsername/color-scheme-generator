---
id: REQ-001
title: "Birth the color-scheme-generator repo (mu-strict, csg) and cut v0.1.0"
kind: requirement
status: in-progress
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

- [ ] The repo exists, is **public**, and its `main` carries the imported subtree commits.
  Verify: `gh api repos/RandomGenericUsername/color-scheme-generator --jq .private` → `false`;
  `git log --oneline | wc -l` → 90 imported commits before the scaffold.
- [ ] The harness is byte-identical to `mu` at every copied path.
  Verify: `diff -r` per path (see the evidence table) → empty, exit 0.
- [ ] `AGENTS.md` carries the evidence rule and this repo's charter; `CLAUDE.md` is a symlink.
  Verify: `rg -c "Evidence:|Verify:" AGENTS.md` → ≥ 2; `test -L CLAUDE.md` → exit 0.
- [ ] `tickets/INDEX.md` lists this ticket with the same status as the frontmatter, the OpenSpec
  change validates strictly, and the carried archive matches its source.
  Verify: `openspec validate --specs --strict` → exit 0; `openspec validate repo-birth --strict`
  → exit 0; `diff -r <dotfiles>/src/cli-tools/openspec openspec/archive/cli-tools-pre-split` → empty.
- [ ] A fresh clone passes `make sync && make gates && make build` and the suite count is 639.
  Verify: `uv sync --frozen && uv run pytest -q` → `639 passed`; `make gates` → exit 0;
  `ls dist/color_scheme_generator-0.1.0-*` → wheel + sdist.
- [ ] All four images build from the repo root at the pin tag, and the base image reports the
  contract version.
  Verify: `make image IMAGE_TAG=v0.1.0` → exit 0; `podman run --rm csg-base-podman:v0.1.0 csg
  --version` → `0.1.0 contract 0.1.0`.
- [ ] `csg install --context .` builds the tag-qualified images from this checkout.
  Verify: `COLORSCHEME__CONTAINER__IMAGE_TAG=v0.1.0 csg install --context . --container-engine
  podman` → base + three backend images at `:v0.1.0`.
- [ ] `.github/workflows/gates.yml` exists and its job set equals `GATES` (plus declared CI-only
  jobs); the first run on `main` is green.
  Verify: `make ci-gates-parity` → `PASS ...`; `gh run list -R RandomGenericUsername/color-scheme-generator
  --limit 1 --json status,conclusion` → `completed` / `success`.
- [ ] Annotated tag `v0.1.0` exists on the released commit, is anonymously fetchable, and its
  GitHub Release carries the wheel + sdist.
  Verify: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote
  https://github.com/RandomGenericUsername/color-scheme-generator 'refs/tags/v0.1.0'` →
  exactly one line; `gh release view v0.1.0 --json assets --jq '.assets[].name'` → both artifacts.
- [ ] `git status --porcelain` is empty in both repos; `dotfiles-v3` `master` is at the same SHA
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

Evidence is recorded at closeout.

## Deviations from the slice text

Evidence is recorded at closeout.
