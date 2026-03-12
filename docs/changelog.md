# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Settings: `COLORSCHEME_*` environment variable layer now active in `load_config()` (CRIT-01)
- Settings: deep merge no longer mutates earlier layers when 3+ layers are present (CRIT-03)
- Settings: orchestrator `settings.toml` `[container]` key wrapper removed — `engine` field now correctly loaded from package defaults (MAJ-02)
- Core: saturation adjustment no longer applied twice when using `--saturation` (CRIT-04)

### Added

- Settings: `get_xdg_config_home()` and `get_user_settings_file()` functions in `paths.py` that read `XDG_CONFIG_HOME` at call time rather than import time (MIN-01)

### Changed

- Docs: `show` command correctly documented as container-based (MAJ-01)
- Docs: settings layer order updated to include env-var layer (MIN-03)
- Docs: `docs/archive/`, `docs/plans/`, and `docs/superpowers/` removed

### Changed (Dev Setup)

- Smoke test `print_summary` now prints test output directory before final banner, matching wallpaper-effects-generator convention
- Smoke workflow (`smoke-tests.yml`) now runs in verbose mode by default on `push` events for easier CI debugging
- `make smoke-test` targets now support `WALLPAPER=/path/to/image.jpg` override; default fixture path unchanged
