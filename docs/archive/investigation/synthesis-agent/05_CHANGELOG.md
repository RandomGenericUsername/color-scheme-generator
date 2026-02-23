# Documentation Change Log

## Iteration 0002 (2026-02-23)

Initial documentation set written under docs/ using the Diataxis profile.

### Added

- `docs/tutorials/getting-started.md` — Step-by-step tutorial covering generate, show,
  backend selection, saturation, dry-run, and format filtering (BHV-0001..0009).

- `docs/how-to/use-dry-run.md` — How-to for dry-run mode on all commands: core
  generate, core show, orchestrator generate, orchestrator install, orchestrator
  uninstall (BHV-0004..0008, 0029, 0030).

- `docs/how-to/configure-settings.md` — How-to for configuration: file locations and
  format, COLORSCHEME_* env vars, COLOR_SCHEME_TEMPLATES, get_config overrides, list
  replacement semantics, caching (BHV-0019..0022, 0031, 0032).

- `docs/how-to/install-backends.md` — How-to for building and removing backend
  container images, engine selection, dry-run, image naming, build output messages
  (BHV-0025..0030, 0034, 0035, 0036).

- `docs/reference/cli-core.md` — Full reference for color-scheme-core CLI: version,
  generate, show commands with all options including --dry-run/-n (BHV-0001..0010).
  Corrects S1-0001 (wallust > pywal > custom).

- `docs/reference/cli-orchestrator.md` — Full reference for color-scheme CLI: version,
  generate, show, install, uninstall commands with --dry-run/-n for install and
  uninstall (BHV-0023..0030, 0034..0036). Fixes S1-0003.

- `docs/reference/settings-api.md` — Full reference for settings API:
  configure/load_config/reload_config/get_config (with correct dict signature),
  apply_overrides, SchemaRegistry, config file format, env vars, precedence, list
  replacement (BHV-0017..0022, 0031, 0032). Fixes S1-0002.

- `docs/reference/types.md` — Reference for Color, ColorScheme, GeneratorConfig types:
  attributes, validation rules, adjust_saturation, from_settings
  (BHV-0012..0016).

- `docs/reference/exceptions.md` — Reference for all 11 public exception types from
  core and settings packages, plus TemplateRegistryError (BHV-0010, 0017, 0018, 0033).

- `docs/explanation/architecture.md` — Conceptual explanation of the two-CLI design,
  backend auto-detection order (wallust > pywal > custom), the 16-color constraint,
  settings layer stack, config caching, container image naming, and design rationale.

### Corrections (vs. archive docs)

- Auto-detection order corrected to wallust > pywal > custom (was pywal > wallust in
  archive; see S1-0001).
- get_config signature corrected to `get_config(overrides: dict[str, Any] | None = None)`
  (was `get_config(**overrides)` in archive; see S1-0002).
- --dry-run / -n added to install and uninstall command references (was absent; see
  S1-0003).
