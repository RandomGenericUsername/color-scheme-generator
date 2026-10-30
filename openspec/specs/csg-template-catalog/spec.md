# csg-template-catalog Specification

## Purpose
Defines the bundled Jinja2 template catalog. It is a public asset surface: `dotfiles-v3`
provisioning copies these files from the pinned checkout (spine AD-10), so their paths and names
are a compatibility contract.

## Requirements

### Requirement: the catalog ships inside the package
The 12 `<artifact>.<format>.j2` templates SHALL live at
`src/color_scheme_generator/defaults/templates/` and SHALL be included in the wheel, so an
installed `csg` renders without a checkout.

Source: `pyproject.toml` `[tool.hatch.build] include`; `src/color_scheme_generator/defaults/templates/`.

#### Scenario: installed render
- **WHEN** `csg generate <image> --format kitty` runs from a wheel install with no templates
  directory configured
- **THEN** the exit code is 0 and `colors.kitty` is written from the packaged template

### Requirement: template discovery is layered, ordered, and content-validated
The templates directory SHALL resolve in this order: `--templates-dir`, the
`COLORSCHEME_TEMPLATES_TEMPLATES_DIR` env var, `templates/` in the CWD or up to three parent
levels, `$XDG_CONFIG_HOME/color-scheme-generator/templates/`, then the packaged defaults.

A discovered candidate (CWD/parent/XDG) SHALL be accepted only when it contains at least one csg
`colors.*.j2` template; otherwise resolution SHALL continue to the next source. An explicitly
requested `--templates-dir` or `COLORSCHEME_TEMPLATES_TEMPLATES_DIR` SHALL either resolve to a csg
catalog or fail with `ConfigResolutionError`; it SHALL NOT silently fall back.

Source: `src/color_scheme_generator/adapters/template_dir_resolver.py`; ticket `BUG-002`.

#### Scenario: user templates win, packaged defaults still resolve
- **WHEN** a `templates/` directory exists in the CWD and contains `colors.*.j2`
- **THEN** `csg generate` renders from it, and with no such directory it renders from the packaged
  defaults (the fallback is exercised by `tests/unit/adapters/test_template_dir_resolver.py`)

#### Scenario: a decoy CWD templates/ is not selected
- **WHEN** the CWD contains only an unrelated `templates/ags-app/` tree with no `colors.*.j2`
  template (the AGS wallpaper-selector app)
- **THEN** the resolver falls through to the XDG/packaged catalog and `csg generate` writes the
  requested artifacts instead of exiting 0 with none

#### Scenario: an explicit decoy fails loudly
- **WHEN** `--templates-dir` or `COLORSCHEME_TEMPLATES_TEMPLATES_DIR` names a directory without a
  `colors.*.j2` catalog
- **THEN** resolution raises `ConfigResolutionError` naming the source and path, and the CLI exits
  non-zero

### Requirement: the catalog can be materialized for provisioning
`csg dump-templates --output DIR` SHALL copy the resolved catalog to `DIR` without modifying the
source.

Source: `src/color_scheme_generator/cli/dump_templates_cmd.py`.

#### Scenario: dump is a faithful copy
- **WHEN** `csg dump-templates --output <tmp>` runs
- **THEN** the exit code is 0 and every `*.j2` under the packaged catalog also exists under `<tmp>`
