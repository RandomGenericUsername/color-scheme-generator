# Layered Settings Fixes — Design Spec

**Date:** 2026-03-10
**Status:** Approved

## Problem Summary

An audit of the layered settings feature revealed that the advertised five-layer configuration pipeline is only three layers in production. The `COLORSCHEME_*` environment variable layer (layer 4) is parsed by `ConfigResolver` but never called by `load_config()`. Additionally, `ConfigResolver._load_package_defaults()` is a permanent stub returning `{}`, meaning dry-run output cannot show package-default attribution. Several smaller correctness and quality issues were also identified.

## Audit Findings Addressed

| ID | Severity | Description |
|----|----------|-------------|
| CRIT-1 | Critical | Env-var layer not wired into main pipeline |
| CRIT-2 | Critical | `ConfigResolver._load_package_defaults()` is a stub |
| CRIT-3 | Critical | `deep_merge` uses shallow copy — cross-layer mutation risk at 3+ levels |
| IMP-1 | Important | Orchestrator `settings.toml` wraps keys in `[container]` — silently ignored by flat model |
| IMP-2 | Important | `ConfigResolver` swallows TOML errors as warnings instead of raising |
| IMP-4 | Important | `paths.py` reads `XDG_CONFIG_HOME` at import time — breaks test monkeypatching |
| IMP-5 | Important | `SchemaRegistry._entries` accessed directly in tests via private attribute |
| IMP-6 | Important | `apply_overrides` uses implicit `model_dump()` round-trip |
| MIN-1 | Minor | Vacuously-true assertions in `test_resolver.py` |
| MIN-2 | Minor | Dead test in `test_paths.py` with no assertion |
| MIN-4 | Minor | `SettingsValidationError.source_layer` never passed in `build_validated_namespace()` |
| MIN-5 | Minor | `reload_config()` docstring incorrectly says "for testing only" |
| MIN-6 | Minor | `COLOR_SCHEME_TEMPLATES` parsing duplicated in `resolver.py` and `paths.py` |

## Architectural Decision: Shared Utility Extraction

`SettingsLoader` (production pipeline) and `ConfigResolver` (dry-run attribution) serve different responsibilities and must not depend on each other. The right boundary is shared utility functions that both call independently:

```
SettingsLoader        ConfigResolver
      │                     │
      └──── load_toml() ────┘   (already shared in loader.py)
      └── parse_env_vars() ──┘   (newly extracted into transforms.py)
```

`parse_env_vars()` becomes the single source of truth for `COLORSCHEME_*` parsing and the `COLOR_SCHEME_TEMPLATES` special case. Neither class knows about the other. This resolves MIN-6.

`ConfigResolver` importing `SchemaRegistry` in `_load_package_defaults()` is acceptable — `SchemaRegistry` is a shared registry component, not `SettingsLoader`. This does not violate the stated boundary.

## Output Shape of `parse_env_vars()`

`parse_env_vars()` returns **section-keyed** dicts, not namespace-keyed:

```python
# COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom
{"generation": {"default_backend": "custom"}}

# COLOR_SCHEME_TEMPLATES=/foo
{"templates": {"directory": "/foo"}}
```

The top-level keys are section names (matching fields of the namespace Pydantic model), not namespace names. The mapping from section → namespace is performed by the **caller** using `SchemaRegistry`. This keeps `parse_env_vars()` simple, namespace-agnostic, and usable by both `SettingsLoader` and `ConfigResolver` without coupling either to the registry.

## Approach: Layered Phases

Work is ordered so shared foundations exist before consumers use them. TDD throughout: failing test written before every implementation change.

---

## Phase 1 — Foundation Fixes

Isolated, no inter-dependencies. Each fix has a dedicated failing test written first.

### `merger.py` — Fix shallow copy (CRIT-3)

Replace `base.copy()` with `copy.deepcopy(base)` in `deep_merge()`.

**The real mutation risk** occurs across multiple merge calls: when `deep_merge(result_of_first_merge, override)` is called, nested dicts in `result_of_first_merge` that were shallow-copied from the original `base` are mutated by the second call.

**Test first (`test_merger.py`):** Add `test_deep_merge_result_not_mutated_by_second_merge` — perform `result1 = deep_merge(base, override1)`, then `deep_merge(result1, override2)`, assert that `result1`'s nested dict is unchanged by the second call. This is the actual failure scenario produced by shallow copy. Fails with `base.copy()`; passes with `copy.deepcopy(base)`.

### `packages/orchestrator/.../settings.toml` — Fix key mismatch (IMP-1)

Two files need updating; one does not:

- **Fix:** `packages/orchestrator/src/color_scheme_orchestrator/config/settings.toml` — remove the `[container]` wrapper so `engine = "docker"` is at the top level.
- **Fix:** `packages/settings/tests/conftest.py` fixture `orchestrator_defaults_toml` — same change, remove `[container]` wrapper.
- **Do not change:** `packages/settings/tests/test_pipeline.py` fixture `orch_file` — already writes `engine = "docker"` at the top level and is correct.

**Test first (`packages/orchestrator/tests/unit/test_settings_validation.py`):** Add `test_orchestrator_engine_default_comes_from_toml` — temporarily patch `ContainerSettings.model_fields["engine"].default` to `"podman"`, load config from the package TOML only, assert `engine == "docker"`. Fails until the `[container]` wrapper is removed (because the TOML value is currently silently ignored and the Pydantic default is used).

### `paths.py` — Fix import-time constants (IMP-4)

**Scope:** The module-level constants `XDG_CONFIG_HOME`, `USER_CONFIG_DIR`, `USER_SETTINGS_FILE` in `paths.py` are frozen at import time. `loader.py.__init__` reads `os.environ` independently at construction time and is unaffected by this fix. The fix is scoped to `paths.py` constants that are used by tests and any production callers that import them directly.

**Action:** Audit all production callers of `XDG_CONFIG_HOME`, `USER_CONFIG_DIR`, `USER_SETTINGS_FILE` from `paths.py`. For any that exist, update to call functions. Convert the constants to functions:

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

Update all callers found in the audit.

**Test first (`test_paths.py`):** Add `test_xdg_config_home_respects_env_var_after_import` — monkeypatch `os.environ["XDG_CONFIG_HOME"]` after the module is already imported, call `get_xdg_config_home()`, assert returned path reflects the patched value. Fails until constants become functions.

### `overrides.py` — Explicit model_dump mode (IMP-6)

Change `config.model_dump()` to `config.model_dump(mode="python")`.

**Test first (`test_overrides.py`):** Add `test_override_with_custom_validator_field` — use a field with a custom validator that transforms the stored value, assert the round-trip preserves the validated type rather than reverting to the raw input.

### `unified.py` — Pass `source_layer` to `SettingsValidationError` (MIN-4)

In `build_validated_namespace()`, pass `source_layer` when raising so error messages include layer attribution.

**Test first (`test_unified.py`):** Add `test_validation_error_includes_source_layer` — feed invalid data for a known namespace, catch `SettingsValidationError`, assert `source_layer` is not `None`.

### `__init__.py` — Fix `reload_config()` docstring (MIN-5)

Update docstring: `reload_config()` is a public API for runtime config reloading (e.g. config file watchers), not a test utility. Keep `reset()` as test-only. No test needed.

---

## Phase 2 — Extract `parse_env_vars()` Shared Utility

Extract env-var parsing from `ConfigResolver._collect_env_vars()` into `transforms.py`.

### New function: `transforms.parse_env_vars(environ=None) -> dict[str, dict]`

- Accepts `environ: dict | None` — uses `os.environ` if `None` (enables hermetic testing)
- Scans for `COLORSCHEME_*` keys, parses `COLORSCHEME_SECTION__KEY` double-underscore format
- Returns `{section_name: {key: value}}` — section-keyed, not namespace-keyed (see Output Shape above)
- `COLOR_SCHEME_TEMPLATES=/foo` special case → `{"templates": {"directory": "/foo"}}`
- Keys normalized to lowercase
- Unrelated env vars silently ignored

**Test first (`test_transforms.py`) — new class `TestParseEnvVars`:**

- `test_single_key`: `{"COLORSCHEME_GENERATION__DEFAULT_BACKEND": "custom"}` → `{"generation": {"default_backend": "custom"}}`
- `test_nested_double_underscore`: `COLORSCHEME_BACKENDS__PYWAL__ALGORITHM=wal` → `{"backends": {"pywal": {"algorithm": "wal"}}}`
- `test_color_scheme_templates_special_case`: `{"COLOR_SCHEME_TEMPLATES": "/foo"}` → `{"templates": {"directory": "/foo"}}`
- `test_unrelated_vars_ignored`: `{"HOME": "/home/user", "PATH": "/usr/bin"}` → `{}`
- `test_empty_environ`: `{}` → `{}`
- `test_keys_normalized_to_lowercase`: `{"COLORSCHEME_GENERATION__DEFAULT_BACKEND": "custom"}` with uppercase section → same as lowercase

All written and failing before moving any code from `resolver.py`.

---

## Phase 3 — Wire Env-Var Layer into `SettingsLoader` (CRIT-1)

After `discover_layers()` collects file-based layers, call `parse_env_vars()` and map sections to namespaces using `SchemaRegistry`. Create one `LayerSource` per namespace that has env-var overrides:

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

This routes `{"generation": {...}}` to namespace `"core"` because `AppConfig` has a `generation` field. It routes `{"templates": {...}}` to `"core"` because `AppConfig` has a `templates` field. Env vars slot at priority 4 — after user config, before CLI overrides.

**Test first — `test_loader.py`, new class `TestEnvVarLayer`:**

- `test_env_var_layer_present_when_set`: set `COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom`, call `discover_layers()`, assert a `LayerSource` with `layer="env"` and `namespace="core"` appears after all user-layer sources
- `test_env_var_layer_absent_when_no_colorscheme_vars`: clear all `COLORSCHEME_*` from env, assert no env-layer `LayerSource` in results
- `test_env_var_layer_has_no_file_path`: `file_path` is `None` on the env-layer `LayerSource`
- `test_env_var_unknown_section_ignored`: set `COLORSCHEME_UNKNOWN__KEY=value` where `unknown` is not a field on any registered model — assert no env layer created

**Test first — `test_pipeline.py`, new class `TestEnvVarLayerPipeline`:**

- `test_env_var_overrides_user_config`: user TOML sets `default_backend = "pywal"`, env var sets `COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom`, call `get_config()`, assert `default_backend == "custom"`
- `test_env_var_beaten_by_cli_override`: env var sets `custom`, CLI override sets `wallust`, assert `wallust` wins
- `test_env_var_beats_project_config`: project TOML sets `default_backend = "pywal"`, env var overrides, assert env wins

All written and failing before `loader.py` is changed.

---

## Phase 4 — Complete `ConfigResolver` (CRIT-2)

### `_load_package_defaults()` — replace stub

`ConfigResolver` is permitted to import and call `SchemaRegistry` — it is a shared registry, not `SettingsLoader`, so this does not violate the architectural boundary.

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

`ConfigResolver` uses the section-keyed output directly — it applies precedence by walking `section.key` paths, which aligns with the `{section: {key: value}}` shape.

### Error handling (IMP-2)

In `_load_project_config()` and `_load_user_config()`, replace broad `except Exception → Warning` with re-raising `SettingsFileError`, consistent with `loader.py`.

**Test first — `test_resolver.py`:**

- `test_load_package_defaults_returns_real_values`: assert `_load_package_defaults()` returns `{"engine": "docker"}` under the orchestrator namespace key. Fails while stub returns `{}`.
- `test_env_vars_delegate_to_shared_parser`: mock `transforms.parse_env_vars`, call `ConfigResolver._collect_env_vars()`, assert the mock was called. Fails until delegation is implemented.
- `test_malformed_project_config_raises_settings_file_error`: write bad TOML to project config path, assert `SettingsFileError` is raised. Fails while errors are swallowed as warnings.
- Replace `test_apply_precedence_env_overrides_configs` with: set same key in both env and user config, call `_apply_precedence()`, assert winning `ResolvedValue.source == ConfigSource.ENV` exactly — not a disjunction.
- Replace `test_apply_precedence_user_overrides_project` with: set same key in both user and project config, assert winning `source == ConfigSource.USER_CONFIG` exactly.
- Fix `test_load_user_config_with_mock`: patch `os.getenv` or `paths.get_user_settings_file` instead of `Path.home` (current patch target has no effect).
- Fix `test_checks_container_templates_dir` (MIN-2): add an actual assertion after the mock setup — e.g. assert the return value of `is_container_environment()` is `True` when `CONTAINER_TEMPLATES_DIR.exists()` returns `True`.

---

## Phase 5 — Test Quality

- `test_registry.py`: remove direct `SchemaRegistry._entries` access. Replace with public API calls (`get()`, `all_namespaces()`).
- `test_pipeline.py`: add `test_registration_bleed_guard` — call `reset()`, explicitly register both consumer models (`core` and `orchestrator`), call `SchemaRegistry.all_namespaces()`, assert result equals `{"core", "orchestrator"}` exactly. Do not rely on import side effects to drive registration — this test must be hermetic.

---

## Phase 6 — Smoke Test Updates

**`test_settings_precedence`** — replace the current pass-through fallback:

```bash
# Before: passes even when env var is not respected
# (command exits 0, and there's a fallback "test_passed" branch
#  that fires if the output file doesn't appear in the expected dir)
# After:
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

**`test_dry_run_configuration_resolution`** — strengthen Default attribution:

```bash
# Before: asserts the word "Default" appears somewhere in output
# After: assert a specific known default value appears with Default attribution
# e.g., the dry-run output must contain "docker" and "Default" in close proximity
# (exact format depends on the dry-run output structure — verify against
#  actual dry-run output before writing the assertion)
```

---

## Phase 7 — Documentation Updates

### `docs/reference/settings-api.md`

- Update BHV-0019: change "package < project < user < CLI" to "package < project < user < env < CLI"
- Add **BHV-0038**: "Env-var layer (`COLORSCHEME_*`) is processed by `load_config()` as layer 4, between user config and CLI overrides"
- Update `load_config()` function description to explicitly name all four file/env layers it processes
- Remove any phrasing suggesting env-var handling only exists in `ConfigResolver`

### `docs/explanation/architecture.md`

- Update the settings stack ASCII diagram: add env layer between user config and CLI, labelled as active in the live pipeline
- Update caching section: `reload_config()` is a public API for runtime reloading (e.g. config file watchers), not a test utility

### `docs/how-to/configure-settings.md`

- No content changes needed — the five-layer table and `COLORSCHEME_*` examples are already written correctly; they become accurate after the fix
- Verify the example commands in the env-var section work as written after implementation

---

## Success Criteria

- `make test-all` passes with ≥95% coverage on all packages
- `make smoke-test-custom` passes including the strengthened `test_settings_precedence` and `test_dry_run_configuration_resolution`
- `COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom color-scheme-core generate <wallpaper>` uses the `custom` backend
- `color-scheme-core generate --dry-run` shows real package default values with `Default` attribution
- All five layers appear in dry-run source attribution output
- No regressions in XDG_CONFIG_HOME, project/user config, or CLI override behaviour
