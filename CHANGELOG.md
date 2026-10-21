# Changelog

Notable changes to the `color-scheme-generator` repo. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow the git tags
(`vMAJOR.MINOR.PATCH`, annotated, never moved).

## [Unreleased]

## [0.1.0] - 2026-10-21

First release. The package content is the in-tree `src/cli-tools/color-scheme-generator` package
(version `0.1.0` there) imported with `git subtree split`, history preserved; the version continues
at `0.1.0` (spine AD-9: versions never move backwards).

### Added

- Repo harness copied byte-for-byte from `mu`: `scripts/worktree-guard.sh`, `skills-lock.json`,
  `_bmad/`, `.agents/skills/`, `.opencode/`, `tickets/_template/`, `tickets/_fixtures/`,
  `tickets/LIFECYCLE.md`.
- `Makefile` fresh-clone verbs (`sync`, `test`, `lint`, `format`, `check`, `hermetic`,
  `lock-check`, `docs-check`, `gates`, `gates-ci`, `image`, `build`, `install`, `clean`,
  `ci-gates-parity`), `.github/workflows/gates.yml`, `scripts/ci-gates-parity.py`.
- `make image` builds all four Dockerfiles (`base`, `custom`, `pywal`, `wallust`) from this repo
  root at the `v<version>` tag and runs `csg --version` inside the base image (AD-5/AD-7).
- MIT `LICENSE`, `README.md`, `AGENTS.md`, `CLAUDE.md` symlink, ticket `REQ-001-repo-birth`, the
  OpenSpec change `repo-birth`, and the imported capability specs `csg-cli`, `csg-container-mode`
  and `csg-template-catalog`.
- `openspec/archive/cli-tools-pre-split/`: the retired nested `dotfiles-v3` OpenSpec root carried
  verbatim (the completed `fix-container-engine-plumbing` change and its placeholder spec) with a
  provenance note (AD-15).

### Changed

- `pyproject.toml`: release metadata (`readme`, `license`, `license-files`, classifiers),
  `hatchling>=1.27`, an sdist `only-include` list so the harness trees stay out of the artifact,
  explicit compatibility ranges for the four sibling dependencies, and a dev group carrying
  `pytest`, `pytest-cov` and `ruff`.
- Sibling dependencies are consumed as immutable git tags (spine AD-3): `cli-output` `v0.1.0`,
  `config-assembler-engine` `v0.1.0`, `oci-runtime` `v0.5.0`, and `cli-invocation-contract`
  (`contracts`) `v0.1.0`. `uv.lock` records the resolved commits.
- `Dockerfile.base` copies `README.md` and `LICENSE` in addition to `pyproject.toml`, `uv.lock` and
  `src/`: hatchling reads the release metadata while building the wheel in the image. Every copied
  path is repo-relative.

### Notes

- The image tag is the pin, not `latest` (spine AD-7). The effective tag comes from
  `[container] image_tag` (`COLORSCHEME__CONTAINER__IMAGE_TAG`), which provisioning renders as
  `v0.1.0`.
- Suite: 639 tests, green in the ambient and hermetic environments, and independent of a host
  `podman`/`docker` (engine-dependent tests skip with a reason).
- `tests/conftest.py` pins `_TYPER_FORCE_DISABLE_TERMINAL`, `NO_COLOR`, `COLUMNS` and
  `TERMINAL_WIDTH` before the CLI modules are imported. Typer forces a terminal when it sees
  `GITHUB_ACTIONS`, which made Rich wrap and interleave ANSI between the characters of an option
  name, so `--help` substring assertions failed on CI but not on a developer terminal. The fix is
  in the test harness; no product code changed.
