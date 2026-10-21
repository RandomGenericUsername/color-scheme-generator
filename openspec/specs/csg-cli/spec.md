# csg-cli Specification

## Purpose
Defines the `csg` command-line surface: palette generation, preview, backend/catalog inspection,
configuration and template dumps, and the version handshake.

## Requirements

### Requirement: `--version` reports both pins
`csg --version` SHALL print `<package version> contract <contracts version>` where the contract
token comes from `cli_invocation_contract.CONTRACT_VERSION`.

Source: spine AD-4/AD-11; `src/color_scheme_generator/cli/main.py` `_version_callback`.

#### Scenario: version handshake
- **WHEN** `csg --version` runs against the installed 0.1.0 wheel
- **THEN** it prints `0.1.0 contract 0.1.0` and exits 0

### Requirement: `generate` writes one artifact per requested format
`csg generate IMAGE --format F ...` SHALL write `colors.<suffix>` for every requested format into
the resolved output directory, overwriting only when `[output] overwrite` or
`--output-dir`/env configuration allows it.

Source: `src/color_scheme_generator/cli/main.py`; `src/color_scheme_generator/adapters/local_processor.py`;
`src/color_scheme_generator/adapters/jinja_template_renderer.py`.

#### Scenario: eight formats in container mode
- **WHEN** `csg generate <image>` runs with `--format yaml --format conf --format gtk.css
  --format adw.css --format sequences --format rasi --format kitty --format btop.theme`
- **THEN** the exit code is 0 and those eight `colors.*` files exist in the output directory

### Requirement: settings discovery is layered and ordered
Settings SHALL resolve in this order (highest priority first): `--config` flag, `COLORSCHEME__*`
environment overrides, `COLORSCHEME_CONFIG_FILE_PATH`, `settings.toml` in the CWD or up to three
parent levels, `$XDG_CONFIG_HOME/color-scheme-generator/settings.toml`, packaged defaults. A bad
explicit config SHALL fail loudly rather than silently fall back.

Source: `src/color_scheme_generator/adapters/settings/config_resolver.py` (`ResolutionPolicy(env_prefix="COLORSCHEME")`);
`src/color_scheme_generator/cli/main.py` app help.

#### Scenario: env override wins over the bundled default
- **WHEN** `COLORSCHEME__OUTPUT__DIRECTORY=<tmp>` is set for a `generate` run
- **THEN** the artifacts land in `<tmp>` and the bundled `/tmp/color-scheme` default is not used

#### Scenario: invalid explicit config fails
- **WHEN** `csg info --config <malformed settings.toml>` runs
- **THEN** the exit code is non-zero and the error is printed on stderr

### Requirement: inspection verbs never mutate state
`info`, `show`, `dump-config`, `dump-templates`, `list-backends` and `version` SHALL report or write
only their documented artifacts; they SHALL NOT build, remove or run container images.

Source: `src/color_scheme_generator/cli/{info_cmd,dump_config_cmd,dump_templates_cmd,list_backends_cmd,show,version_cmd}.py`;
`src/color_scheme_generator/cli/main.py` command registrations.

#### Scenario: dump-config round-trips
- **WHEN** `csg dump-config --output <file>` runs
- **THEN** the exit code is 0 and `<file>` is a TOML document that `csg info --config <file>` accepts
