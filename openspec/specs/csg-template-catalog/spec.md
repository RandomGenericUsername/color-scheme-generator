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

### Requirement: template discovery is layered and ordered
The templates directory SHALL resolve in this order: `--templates-dir`, the
`COLORSCHEME_TEMPLATES_TEMPLATES_DIR` env var, `templates/` in the CWD or up to three parent
levels, `$XDG_CONFIG_HOME/color-scheme-generator/templates/`, then the packaged defaults.

Source: `src/color_scheme_generator/adapters/template_dir_resolver.py`.

#### Scenario: user templates win, packaged defaults still resolve
- **WHEN** a `templates/` directory exists in the CWD
- **THEN** `csg generate` renders from it, and with no such directory it renders from the packaged
  defaults (the fallback is exercised by `tests/unit/adapters/test_template_dir_resolver.py`)

### Requirement: the catalog can be materialized for provisioning
`csg dump-templates --output DIR` SHALL copy the resolved catalog to `DIR` without modifying the
source.

Source: `src/color_scheme_generator/cli/dump_templates_cmd.py`.

#### Scenario: dump is a faithful copy
- **WHEN** `csg dump-templates --output <tmp>` runs
- **THEN** the exit code is 0 and every `*.j2` under the packaged catalog also exists under `<tmp>`
