# Audit Fixes — Design Spec

**Date:** 2026-03-11
**Status:** Approved

## Problem Summary

A 2026-03-11 audit of the project identified four critical issues and several major/minor
issues across the settings pipeline, core CLI, and documentation:

- **CRIT-01:** `COLORSCHEME_*` env-var layer documented as layer 4 but never wired into
  `load_config()` — only parsed in the dry-run `ConfigResolver`
- **CRIT-02:** `ConfigResolver._load_package_defaults()` is a permanent stub returning
  `{}` — dry-run "Package default" attribution is always empty
- **CRIT-03:** `deep_merge` uses `base.copy()` (shallow) — cross-layer mutation risk at
  3+ levels
- **CRIT-04:** Saturation applied twice: once in each backend's `generate()`, once again
  in `cli/main.py` — TTY and non-TTY `show` paths also produce different results
- **MAJ-01:** `show` command documented as "no container / delegates to host" since the
  show-containerization merge; it now runs in a container
- **MAJ-02:** `packages/orchestrator/config/settings.toml` wraps keys in `[container]`,
  which is silently ignored by the flat `ContainerSettings` model
- **MIN-01:** `paths.py` `XDG_CONFIG_HOME`/`USER_SETTINGS_FILE` frozen at import time
- **MIN-03:** `settings-api.md` BHV-0019 will need updating once CRIT-01 is fixed

This spec also incorporates all items from the previously approved
`2026-03-10-layered-settings-fixes-design.md` which is superseded by this document.

## TDD Rule

A failing test is written before every implementation change. No exceptions.

---

## Phase 1 — Foundation Fixes (isolated, no interdependencies)

### `merger.py` — Fix shallow copy (CRIT-03)

Replace `base.copy()` with `copy.deepcopy(base)` in `deep_merge()`.

**Test first (`test_merger.py`):** `test_deep_merge_result_not_mutated_by_second_merge` —
call `result1 = deep_merge(base, override1)`, then `deep_merge(result1, override2)`,
assert `result1`'s nested dict is unchanged.

### `orchestrator/config/settings.toml` — Fix key mismatch (MAJ-02)

Remove the `[container]` wrapper so `engine = "docker"` is at the top level.
Same fix in `packages/settings/tests/conftest.py` fixture `orchestrator_defaults_toml`.
Do not change `packages/settings/tests/test_pipeline.py` fixture `orch_file` — already
correct.

**Test first (`test_settings_validation.py`):**
`test_orchestrator_engine_default_comes_from_toml` — temporarily patch
`ContainerSettings.model_fields["engine"].default` to `"podman"`, load config from
package TOML only, assert `engine == "docker"`. Fails until `[container]` wrapper
is removed.

### `paths.py` — Fix import-time constants (MIN-01)

Convert module-level constants to functions:

```python
# Before
XDG_CONFIG_HOME: Path = Path(os.getenv("XDG_CONFIG_HOME", _xdg_default))
USER_SETTINGS_FILE: Path = XDG_CONFIG_HOME / APP_NAME / SETTINGS_FILENAME

# After
def get_xdg_config_home() -> Path:
    return Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))

def get_user_settings_file() -> Path:
    return get_xdg_config_home() / APP_NAME / SETTINGS_FILENAME
```

Audit all production callers before changing; update any that import the constants
directly.

**Test first (`test_paths.py`):** `test_xdg_config_home_respects_env_var_after_import` —
monkeypatch `os.environ["XDG_CONFIG_HOME"]` after import, call `get_xdg_config_home()`,
assert returned path reflects patched value.

### `overrides.py` — Explicit model_dump mode (IMP-6)

Change `config.model_dump()` to `config.model_dump(mode="python")`.

**Test first (`test_overrides.py`):** `test_override_with_custom_validator_field` — use a
field with a custom validator, assert round-trip preserves the validated type.

### `unified.py` — Pass `source_layer` to `SettingsValidationError` (MIN-4)

Pass `source_layer` when raising `SettingsValidationError` in
`build_validated_namespace()`.

**Test first (`test_unified.py`):** `test_validation_error_includes_source_layer` — feed
invalid data, catch `SettingsValidationError`, assert `source_layer` is not `None`.

### `__init__.py` — Fix `reload_config()` docstring (MIN-5)

`reload_config()` is a public API for runtime config reloading, not a test utility.
Update docstring accordingly. No test needed.

---

## Phase 2 — Extract `parse_env_vars()` Shared Utility

Add to `transforms.py`:

```python
def parse_env_vars(environ: dict | None = None) -> dict[str, dict]:
    ...
```

- Uses `os.environ` if `environ` is `None`
- Parses `COLORSCHEME_SECTION__KEY` → `{section: {key: value}}`
- `COLOR_SCHEME_TEMPLATES=/foo` → `{"templates": {"directory": "/foo"}}`
- Keys normalised to lowercase
- Returns section-keyed dict (not namespace-keyed)

**Test first (`test_transforms.py`) — new class `TestParseEnvVars`:**

- `test_single_key`
- `test_nested_double_underscore`
- `test_color_scheme_templates_special_case`
- `test_unrelated_vars_ignored`
- `test_empty_environ`
- `test_keys_normalised_to_lowercase`

All written and failing before moving any code.

---

## Phase 3 — Wire Env-Var Layer into `SettingsLoader` (CRIT-01)

After user-config layer in `discover_layers()`:

```python
raw_env = parse_env_vars()
for entry in SchemaRegistry.all_entries():
    model_sections = set(entry.model.model_fields.keys())
    namespace_data = {k: v for k, v in raw_env.items() if k in model_sections}
    if namespace_data:
        layers.append(LayerSource(
            layer="env",
            namespace=entry.namespace,
            file_path=None,
            data=namespace_data,
        ))
```

**Test first — `test_loader.py`, new class `TestEnvVarLayer`:**

- `test_env_var_layer_present_when_set`
- `test_env_var_layer_absent_when_no_colorscheme_vars`
- `test_env_var_layer_has_no_file_path`
- `test_env_var_unknown_section_ignored`

**Test first — `test_pipeline.py`, new class `TestEnvVarLayerPipeline`:**

- `test_env_var_overrides_user_config`
- `test_env_var_beaten_by_cli_override`
- `test_env_var_beats_project_config`

---

## Phase 4 — Complete `ConfigResolver` (CRIT-02)

### `_load_package_defaults()` — replace stub

```python
def _load_package_defaults(self) -> dict[str, dict]:
    result = {}
    for entry in SchemaRegistry.all_entries():
        try:
            data = load_toml(entry.defaults_file)
            result[entry.namespace] = data
        except SettingsFileError as e:
            self.warnings.append(Warning(
                message=f"Could not load package defaults for {entry.namespace}: {e}",
                level=WarningLevel.INFO,
            ))
    return result
```

### `_collect_env_vars()` — delegate to shared utility

```python
def _collect_env_vars(self) -> dict[str, dict]:
    return parse_env_vars()
```

### Error handling (IMP-2)

In `_load_project_config()` and `_load_user_config()`, replace broad
`except Exception → Warning` with re-raising `SettingsFileError`.

**Test first — `test_resolver.py`:**

- `test_load_package_defaults_returns_real_values`
- `test_env_vars_delegate_to_shared_parser`
- `test_malformed_project_config_raises_settings_file_error`
- Replace vacuously-true assertions with exact `source` checks (MIN-1 from spec)
- Fix `test_load_user_config_with_mock`: patch correct target
- Fix `test_checks_container_templates_dir` (MIN-2 from spec): add actual assertion

---

## Phase 5 — Test Quality

- `test_registry.py`: remove `SchemaRegistry._entries` direct access; use public API
- `test_pipeline.py`: add `test_registration_bleed_guard` hermetic test

---

## Phase 6 — Smoke Test Updates

**`test_settings_precedence`:**

```bash
env_test_dir="$TEST_OUTPUT_DIR/env-override-test"
COLORSCHEME_OUTPUT__DIRECTORY="$env_test_dir" \
  run_cmd color-scheme-core generate "$WALLPAPER"
if [ -f "$env_test_dir/colors.json" ]; then
    test_passed "env var COLORSCHEME_OUTPUT__DIRECTORY overrides output directory"
else
    test_failed "env var COLORSCHEME_OUTPUT__DIRECTORY had no effect"
fi
# No fallback pass branch
```

**`test_dry_run_configuration_resolution`:** Assert a specific known default value
(e.g. `"docker"`) appears with `Default` attribution. Remove the generic word-match.

---

## Phase 7 — Core Bug Fix: Double Saturation (CRIT-04)

### Root cause

All three backends apply `config.saturation_adjustment` during `generate()`. Then
`cli/main.py` applies it a second time after receiving the scheme back. Result: with
`--saturation 1.5`, saturation is applied as 1.5² ≈ 2.25 (clamped). TTY and non-TTY
`show` paths also differ: TTY double-applies, non-TTY does not.

### Fix

Remove the redundant saturation blocks from `cli/main.py`:
- `generate` command: remove lines 215–229
- `show` command TTY branch: remove lines 419–430

Backends remain the single authoritative place saturation is applied. No changes to
`pywal.py`, `wallust.py`, or `custom.py`.

### Tests

**Test first — `test_cli_main.py`:**

Add to `TestGenerateSaturation`:
- `test_saturation_applied_exactly_once_in_generate` — mock backend's `generate()` to
  return a scheme with a known `Color`; assert `Color.adjust_saturation` call count
  equals 1 (not 2) when `--saturation 1.5` is passed

Add to `TestShowSaturation`:
- `test_saturation_applied_exactly_once_in_show_tty` — same pattern for TTY show path
- `test_saturation_consistent_between_tty_and_nontty` — assert both paths call
  `adjust_saturation` the same number of times

---

## Phase 8 — Documentation Corrections

### MAJ-01 — Fix stale `show` command docs

**`docs/reference/cli-orchestrator.md`:**
- Command summary table: `show | No | Display colors (delegates to core CLI on host)`
  → `show | Yes | Display colors via container`

**`docs/explanation/architecture.md`:**
- Remove "The show command is an exception..." paragraph
- Replace with accurate description: `show` runs in a container with TTY detection so
  Rich renders colour tables interactively when the host terminal supports it

### MIN-03 — Update settings layer documentation

**`docs/reference/settings-api.md`:**
- BHV-0019: `package < project < user < CLI` → `package < project < user < env < CLI`
- Add BHV-0038: "Env-var layer (`COLORSCHEME_*`) is processed by `load_config()` as
  layer 4, between user config and CLI overrides"
- Update `load_config()` description to list all five layers

**`docs/how-to/configure-settings.md`:**
- Add BHV-0038 row to verification table

---

## Phase 9 — Changelog

Add to `docs/changelog.md` under `## [Unreleased]`:

- Settings: `COLORSCHEME_*` environment variable layer now active in `load_config()`
- Settings: deep merge no longer mutates earlier layers when 3+ layers are present
- Settings: orchestrator `settings.toml` `[container]` key wrapper removed — `engine`
  field now correctly loaded from file
- Settings: `XDG_CONFIG_HOME` and `USER_SETTINGS_FILE` in `paths.py` now read
  environment at call time, not import time
- Core: saturation adjustment no longer applied twice when using `--saturation`
- Docs: `show` command correctly documented as container-based
- Docs: `docs/archive/`, `docs/plans/`, and investigation artifacts removed

---

## Success Criteria

- `make test-all` passes with >= 95% coverage on all packages
- `make smoke-test-custom` passes including strengthened `test_settings_precedence`
  and `test_dry_run_configuration_resolution`
- `COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom color-scheme-core generate <img>`
  uses the `custom` backend
- `color-scheme-core generate --dry-run` shows real package default values with
  `Default` attribution
- `color-scheme-core generate image.jpg --saturation 1.5` applies saturation exactly
  once; color values match a single application of 1.5x
- TTY and non-TTY `show` produce identical color values for the same inputs
- All documentation claims verified against source code
