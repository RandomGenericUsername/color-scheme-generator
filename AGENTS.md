# AGENTS.md — color-scheme-generator operating contract

Canonical agent instructions for this repo. Claude (`CLAUDE.md` symlinks here), OpenCode, and all
BMAD/OpenSpec skills must follow this.

## 1. Evidence rule (hard requirement)

No suggestion "in the air". Every technical claim, recommendation, or design decision must carry testable evidence — at least one of:

- **Doc evidence:** file path + line range, or commit SHA, or URL + quoted section.
- **Prototype evidence:** a script/command in-repo that runs and prints the validating output. State the exact command and observed result.
- **Test evidence:** `command run → result` (exit code + key output). Failing-as-expected counts if it validates the claim.

Format: any non-trivial claim gets an `Evidence:` line and a `Verify:` line (how to reproduce in one command). If evidence doesn't exist yet, say `Evidence: MISSING — run <X> to produce it` and do not present the claim as fact.

## 2. Charter — `csg`, the color scheme generator

- This repo owns one package: `color-scheme-generator` (import package
  `color_scheme_generator`, console script `csg`). It extracts color palettes from wallpaper images
  locally or inside a container, renders them through a bundled Jinja2 template catalog, and reads
  layered settings plus a backend catalog.
- Public surface: `generate`, `show`, `info`, `install`, `uninstall`, `dump-config`,
  `dump-templates`, `list-backends`, `version`, and `--version`; the Python entry point is
  `color_scheme_generator.cli.main:app`.
  Evidence: `pyproject.toml` `[project.scripts]`; `src/color_scheme_generator/cli/main.py`
  (command registrations at lines 290–297); `src/color_scheme_generator/cli/install_cmd.py`.
- **This repo owns its four container images and its build verb** (spine AD-5/AD-7). The
  Dockerfiles are `src/color_scheme_generator/adapters/docker/Dockerfile.{base,custom,pywal,wallust}`;
  the build context is **this repo root** and `Dockerfile.base` copies only repo-relative paths
  (`pyproject.toml`, `uv.lock`, `README.md`, `LICENSE`, `src/`). The three backend Dockerfiles keep
  their `ARG BASE_IMAGE` and add engine-level packages only. No Dockerfile path may reference a
  sibling repo or a parent directory. `csg install --context <checkout> --container-engine <engine>`
  builds them; the **image tag is the pin, never `latest`** (it comes from
  `[container] image_tag`, overridable with `COLORSCHEME__CONTAINER__IMAGE_TAG`).
  Evidence: `src/color_scheme_generator/adapters/docker/Dockerfile.*`;
  `src/color_scheme_generator/cli/install_cmd.py`; `Makefile` `image` target.
- The bundled template catalog at `src/color_scheme_generator/defaults/templates/` is a **public
  asset surface**: `dotfiles-v3` provisioning copies it from the pinned checkout (spine AD-10). Do
  not rename or relocate a template without a consumer pin bump; `dump-templates` is the supported
  materialization verb.
- Dependencies are `typer`, `pydantic`, `jinja2`, `rich`, plus the pinned sibling packages
  `cli-output`, `config-assembler-engine`, `oci-runtime` and `cli-invocation-contract`.
  `oci-runtime` supplies the repo-root build-context locator; it is not a runtime path dependency.
- `cli-output` is presentation only; this repo does not own the runtime↔CLI invocation contract
  (it lives in the `contracts` repo as `cli-invocation-contract`, spine AD-4). The contract's
  conformance kit (`cli_invocation_contract.testkit`) is the source of invocation assertions; do
  not duplicate argv/env/artifact literals in tests.
- Siblings are consumed as immutable git tags, never a path and never `editable = true`
  (spine AD-3). The four git sources are declared in `[tool.uv.sources]` and locked in `uv.lock`.
- Settings discovery order is CLI flag → `COLORSCHEME__…` env → `COLORSCHEME_CONFIG_FILE_PATH` →
  `settings.toml` in CWD/parents → `$XDG_CONFIG_HOME/color-scheme-generator/settings.toml` →
  bundled defaults; template discovery mirrors it with `COLORSCHEME_TEMPLATES_TEMPLATES_DIR` and
  `templates/`.

## 3. How we work here

- Read files, run commands (`rg`, `git log`, `uv`, `pytest`, `podman`/`docker`, `openspec
  validate`), paste results. Prefer executed output over recalled text.
- When findings contradict an earlier claim, state the discrepancy and trust the evidence.
- Keep changes small, verifiable, committable. A suite that is green only on the author's host is
  not green: tests are hermetic (empty `HOME` / `XDG_*`, foreign cwd), enforced by
  `tests/conftest.py` plus the canary in `tests/test_hermetic_canary.py`.
  Verify: `make hermetic` → exit 0.
- Container-engine tests and the image build skip/fail honestly when no engine is reachable; they
  are never silently deleted. `make image` is a real build against this repo root.

## 4. OpenSpec + BMAD routing (via tickets)

- All work starts as a ticket in `tickets/` (`_template/`, vocab + rollup in `INDEX.md`, flow in
  `LIFECYCLE.md`). Triage with `/triage` (lanes in `tickets/_fixtures/router-lanes.md`).
- Broad scope (package charter, public API evolution, dependency policy) → BMAD. Installed
  skills are exactly the seven in `skills-lock.json`: `bmad`, `bmad-architecture`, `bmad-build`,
  `bmad-product-brief`, `bmad-spec`, `bmod-core-tools`, `bmod-method` — say so when a step needs a
  missing skill instead of improvising.
- Bounded slices (one proposal + spec + design + tasks) → OpenSpec
  (`/opsx-propose`, `/opsx-apply`, `/opsx-archive`). Artifact rules in
  `openspec/config.yaml` restate this evidence rule per artifact.
- `openspec/archive/cli-tools-pre-split/` is preserved history from the pre-split monorepo
  (spine AD-15). It is not an active root and is never edited or re-validated.
- Never work on main: `scripts/worktree-guard.sh create <id> <slug>` scaffolds
  `ticket/<id>-<slug>` + `.worktrees/<id>/`, and aborts when the tree is dirty. Record
  worktree/branch in the ticket.

## 5. Planning vs implementation

- Planning edits (tickets, `openspec/` changes, docs) and implementation changes (code, packaging,
  harness) land in **separate commits**.
- Never mix planning edits with implementation in one commit or one turn.

## 6. Release ritual

- Green gates on the ticket branch → version bumped in `pyproject.toml` + `CHANGELOG.md` →
  annotated tag `vMAJOR.MINOR.PATCH` → CI builds sdist + wheel and attaches them to the GitHub
  Release → consumer pin bump in its own commit.
- A published tag is never moved or deleted; a fix is a new tag. PyPI is not a channel.
- The first tag is `v0.1.0`, continuing the imported package's in-tree `0.1.0` version (spine
  AD-9: version continuity; versions never move backwards).
  Evidence: `CHANGELOG.md` `0.1.0`; `git tag -l`.

## 7. Gates

- `make gates` = `test lint hermetic lock-check docs-check`; `make build` produces the sdist and
  wheel; `make image` builds `Dockerfile.base` plus the three backend Dockerfiles from this repo
  root at `v<version>` and runs `csg --version` in the base image (spine AD-5).
  CI (`.github/workflows/gates.yml`) runs one job per gate target plus `ci-gates-parity`, which
  compares the workflow's job set against `GATES` in the `Makefile`, and an `image` job that
  builds and runs the containers.
  Verify: `make gates && make build && make image` → exit 0; `make ci-gates-parity` → exit 0.
