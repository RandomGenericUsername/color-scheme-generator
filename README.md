# color-scheme-generator (`csg`)

Color scheme generator for the dotfiles CLI toolchain: extracts a color palette from a wallpaper
image — locally or inside a container backend (`custom`, `pywal`, `wallust`) — and renders it
through a bundled Jinja2 template catalog (GTK/Adwaita CSS, kitty, rasi, btop, hyprland, YAML,
JSON, shell, …).

This repo **owns its four container images and its build verb** (spine AD-5/AD-7): the Dockerfiles
live at `src/color_scheme_generator/adapters/docker/`, their build context is this repo root, and
the image tag is the pin (`vX.Y.Z`), never `latest`.

## Public surface

```console
csg generate IMAGE [--format F ...] [--backend NAME] [--param K=V ...] \
                   [--output-dir DIR] [--config FILE] [--templates-dir DIR] \
                   [--runtime {local,container}] [--container-engine {docker,podman}]
csg show [--config FILE] [--templates-dir DIR] ...
csg info [--config FILE] [--templates-dir DIR]
csg install [--config FILE] [--container-engine {docker,podman}] \
            [--context DIR | --source-root DIR] [--backend NAME ...] [--dry-run]
csg uninstall [--config FILE] [--container-engine {docker,podman}]
csg dump-config [--output FILE]
csg dump-templates [--output DIR]
csg list-backends [--config FILE]
csg version
csg --version
```

- `--version` prints `<package version> contract <contracts version>`, e.g.
  `0.2.0 contract 0.2.0`. The contract token comes from
  `cli_invocation_contract.CONTRACT_VERSION`, not from `cli-output`.
- Global flags: `--output-format {json,plain,rich}`, `-v/-vv/-vvv`, `-q`.
- Exit codes: `0` success, non-zero a domain/config error with the message on the output stream.

## Container mode

`csg install` builds `Dockerfile.base` against a **single-package repo root** resolved by
`oci_runtime.resolve_build_context` (override `--context`, env `CSG_SOURCE_ROOT`, PEP 610, package
walk), then builds each requested backend Dockerfile with `--build-arg BASE_IMAGE=<base>`.

`Dockerfile.base` copies only repo-relative paths (`pyproject.toml`, `uv.lock`, `README.md`,
`LICENSE`, `src/`); the pinned sibling dependencies are fetched from their git tags at build time
(the stage carries `uv==0.9.22`, `git` and CA certificates), so an unreachable pin fails closed. No
path outside this repo is referenced. The per-backend Dockerfiles keep their `ARG BASE_IMAGE`:

| Dockerfile | Adds |
| --- | --- |
| `Dockerfile.base` | `python:3.14-slim` + `uv sync --frozen --no-dev --no-editable` |
| `Dockerfile.custom` | `pillow`, `numpy`, `scikit-learn` |
| `Dockerfile.pywal` | `imagemagick` + `pywal` |
| `Dockerfile.wallust` | the pinned `wallust` 3.5.2 release binary |

```bash
make image                                   # all four, at v0.2.0, then csg --version
COLORSCHEME__CONTAINER__IMAGE_TAG=v0.2.0 \
  csg install --context . --container-engine podman
podman run --rm csg-base-podman:v0.2.0 csg --version   # 0.2.0 contract 0.2.0
```

The image names are the CLI's own scheme, `<prefix>-<suffix>-<engine>:<tag>`:
`csg-base-podman:v0.2.0`, `csg-custom-podman:v0.2.0`, `csg-pywal-podman:v0.2.0`,
`csg-wallust-podman:v0.2.0`. The tag comes from `[container] image_tag` (override
`COLORSCHEME__CONTAINER__IMAGE_TAG`); there is no separate `--image-tag` flag because the setting is
the single source of truth.

## Configuration

Settings are resolved with this precedence (highest first):

1. CLI flag
2. env `COLORSCHEME__SECTION__KEY` (double underscore = nesting)
3. `COLORSCHEME_CONFIG_FILE_PATH`
4. `settings.toml` in the CWD or up to three parent levels
5. `$XDG_CONFIG_HOME/color-scheme-generator/settings.toml`
6. packaged defaults (`src/color_scheme_generator/defaults/settings.toml`)

Templates resolve the same way with `--templates-dir`, `COLORSCHEME_TEMPLATES_TEMPLATES_DIR`,
`templates/` in the CWD or up to three parent levels, the XDG directory, then the packaged
catalog. `[runtime] mode` chooses **where** extraction runs (`local`/`container`) and
`[container] engine` chooses **which** OCI runtime (`docker`/`podman`).

## Template catalog

`src/color_scheme_generator/defaults/templates/` holds the 12 `<artifact>.<format>.j2` templates
(`json`, `sh`, `yaml`, `conf`, `css`, `gtk.css`, `adw.css`, `sequences`, `rasi`, `scss`, `kitty`,
`btop.theme`). They ship inside the wheel and are also a consumer asset: `dotfiles-v3` provisioning
copies them from the pinned checkout (spine AD-10). `csg dump-templates --output DIR` materializes
the resolved catalog.

## Install

From a checkout (development):

```bash
make sync          # uv sync --frozen
make gates         # test + lint + hermetic + lock-check + docs-check
make build         # sdist + wheel in dist/
make image         # build the four container images from this repo root
```

The `dev` dependency group carries `color-scheme-generator[custom]`, so `make sync` installs
Pillow/numpy/scikit-learn. That is what lets `tests/integration/test_invocation_contract.py` run the
real `csg` binary against the pinned `cli_invocation_contract` record (8 `--format` flags, the two
`COLORSCHEME__OUTPUT__*` env keys, 8 artifacts) in every CI job without a `wal`/`wallust` binary.

As a consumer, pin an immutable tag — never a path and never a branch:

```toml
# pyproject.toml
dependencies = ["color-scheme-generator>=0.2.0"]

[tool.uv.sources]
color-scheme-generator = { git = "https://github.com/RandomGenericUsername/color-scheme-generator", tag = "v0.2.0" }
```

```bash
uv tool install "git+https://github.com/RandomGenericUsername/color-scheme-generator@v0.2.0"
csg --version    # 0.2.0 contract 0.2.0
```

A published tag is never moved or deleted; a fix ships as a new tag.

## What `dotfiles-v3` pins

`dotfiles-v3` addresses this repo as `{name: csg, repo: <this repo>, tag: v0.1.0}` in
`provisioning/cli-tools.yaml`; the `cli_tools` role shallow-clones that tag, installs `csg` from the
checkout, builds with `--context <checkout>`, and `verify` asserts the images exist at that exact
tag. `provisioning/assets.yaml` copies the template catalog from the same checkout (spine
AD-7/AD-10). Provisioning owns the pin, clone, install and image tag; it never writes or patches
this repo's Dockerfiles.

## Sibling pins

This repo consumes four sibling repos by immutable tag (spine AD-3):

| Distribution | Tag | Source |
| --- | --- | --- |
| `cli-output` | `v0.1.0` | `https://github.com/RandomGenericUsername/cli-output` |
| `config-assembler-engine` | `v0.1.0` | `https://github.com/RandomGenericUsername/config-assembler-engine` |
| `oci-runtime` | `v0.5.0` | `https://github.com/RandomGenericUsername/oci-runtime` |
| `cli-invocation-contract` | `v0.2.0` | `https://github.com/RandomGenericUsername/contracts` |

## Release

Version in `pyproject.toml` + `CHANGELOG.md` entry → annotated tag `vX.Y.Z` → GitHub Actions runs
the gates and the image builds, then attaches the sdist and wheel to the GitHub Release. PyPI is not
used.

## Repo harness

- `AGENTS.md` (with `CLAUDE.md` symlinked to it) is the operating contract: evidence rule,
  worktree discipline, planning-vs-implementation commits.
- `tickets/` is the work ledger (`INDEX.md`, `LIFECYCLE.md`, `_template/`).
- `openspec/` holds the specs and the change log (`config.yaml`, `specs/`, `changes/`);
  `openspec/archive/cli-tools-pre-split/` preserves the pre-split nested OpenSpec tree.
- `scripts/worktree-guard.sh create <id> <slug>` makes `.worktrees/<id>/` on
  `ticket/<id>-<slug>`; never work on `main`.
- `.agents/skills/` + `skills-lock.json` and `_bmad/` are hash-pinned copies of the `mu` harness.

## License

MIT — see `LICENSE`.
