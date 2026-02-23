# Traceability Matrix

## BHV → Documentation coverage

| Behavior | Covered by DOC claims | Coverage status | Notes |
|----------|-----------------------|----------------|-------|
| BHV-0001 (generate produces files) | DOC-0002, DOC-0003 | covered | |
| BHV-0002 (generate only requested formats) | DOC-0002 | covered | |
| BHV-0003 (generate invalid image → exit 1) | DOC-0007 | covered | |
| BHV-0004 (generate --dry-run shows plan) | DOC-0005 | partial — dry-run not in core-commands.md options table | --dry-run option absent from options table |
| BHV-0005 (-n alias for --dry-run) | DOC-0005 | partial — not in options table | |
| BHV-0006 (dry-run creates no files) | DOC-0005 | partial | |
| BHV-0007 (show displays colors) | none explicit | uncovered | show behavior described in prose but no BHV link |
| BHV-0008 (show --dry-run no color tables) | DOC-0005 | partial | |
| BHV-0009 (auto_detect: wallust>pywal>custom) | DOC-0001 | contradicted — doc says pywal>wallust>custom | FINDING: F-001 |
| BHV-0010 (create raises BackendNotAvailableError) | DOC-0008 | covered | |
| BHV-0011 (detect_available handles exceptions) | none | uncovered | internal behavior |
| BHV-0012 (Color hex/RGB validation) | DOC-0022, DOC-0023 | covered | |
| BHV-0013 (Color hex/RGB consistency) | DOC-0022 | covered | |
| BHV-0014 (adjust_saturation) | docs/reference/api/types.md | covered | |
| BHV-0015 (ColorScheme exactly 16 colors) | DOC-0024 | covered | |
| BHV-0016 (GeneratorConfig.from_settings) | DOC-0025 | covered | |
| BHV-0017 (SchemaRegistry duplicate raises) | DOC-0018 | covered | |
| BHV-0018 (SchemaRegistry get unregistered) | DOC-0018 | covered | |
| BHV-0019 (SettingsLoader layer order) | DOC-0019 | covered | |
| BHV-0020 (deep_merge lists replaced) | none explicit | uncovered | important merge behavior undocumented |
| BHV-0021 (CLI overrides everything via get_config) | DOC-0019, DOC-0016 | partial — DOC-0016 signature is wrong | FINDING: F-002 |
| BHV-0022 (load_config caches) | DOC-0017 | covered | |
| BHV-0023 (ContainerSettings engine validation) | DOC-0012 | covered | |
| BHV-0024 (ContainerManager image name) | DOC-0010 | covered | |
| BHV-0025 (install default engine=docker) | DOC-0012 | covered | |
| BHV-0026 (install invalid engine → exit 1) | DOC-0012 | covered | |
| BHV-0027 (install no backend → all three) | orchestrator-commands.md install section | covered | |
| BHV-0028 (install build command structure) | DOC-0012 | covered | |
| BHV-0029 (install --dry-run) | DOC-0015 | contradicted — undocumented | FINDING: F-003 |
| BHV-0030 (uninstall --dry-run bypasses confirmation) | DOC-0015 | contradicted — undocumented | FINDING: F-003 |
| BHV-0031 (COLORSCHEME_ env vars) | DOC-0020 | covered | |
| BHV-0032 (COLOR_SCHEME_TEMPLATES env var) | DOC-0020 | covered | |
| BHV-0033 (TemplateRegistry duplicate raises) | none explicit | uncovered | |
| BHV-0034 (install build success message) | orchestrator-commands.md lines 382-389 | covered | |
| BHV-0035 (install build failure) | orchestrator-commands.md error handling | covered | |
| BHV-0036 (ContainerSettings registry trailing slash) | none | uncovered | |

---

## DOC → Evidence

| Doc claim | Evidence (test/contract/code) | Evidence status | Notes |
|-----------|-------------------------------|----------------|-------|
| DOC-0001: auto-detect order pywal>wallust>custom | factory.py:130 [WALLUST, PYWAL, CUSTOM]; test_factory.py:71 WALLUST wins | CONTRADICTED | Doc says pywal first; code/tests show wallust first |
| DOC-0002: 8 output formats by default | defaults.py:13-22; test_cli_generate.py:24-67 | VERIFIED | |
| DOC-0003: all 8 formats if not specified | defaults.py:13-22 | VERIFIED | |
| DOC-0004: default output ~/.config/color-scheme/output | defaults.py:12 | VERIFIED | |
| DOC-0005: --dry-run supported | cli/main.py:96-154; test_cli_dry_run.py | VERIFIED (behavior exists) | But not in options table of core-commands.md |
| DOC-0006: saturation range 0.0-2.0, default 1.0 | cli/main.py:88-95; defaults.py:26 | VERIFIED | |
| DOC-0007: exit 0 success, exit 1 error | test_cli_generate.py:40,111; cli/main.py | VERIFIED | |
| DOC-0008: backend availability mechanism | backends/pywal.py, wallust.py, custom.py | VERIFIED (mechanism); order wrong — see DOC-0001 | |
| DOC-0009: output files named colors.<format> | cli/main.py:236; test_cli_generate.py:92-96 | VERIFIED | |
| DOC-0010: container image names | test_image_names.py:14-48 | VERIFIED | |
| DOC-0011: volume mounts | test_container_manager_mounts.py, test_volume_mounts.py (unit tests only) | PARTIALLY VERIFIED | Full verification requires smoke test (out of scope) |
| DOC-0012: install --engine docker/podman | test_install_unit.py:17-39; test_settings_validation.py:19-25 | VERIFIED | |
| DOC-0013: uninstall --yes skips confirmation | test_uninstall_unit.py | VERIFIED | |
| DOC-0014: show delegates to core | orchestrator/cli/main.py:270-292 | VERIFIED | |
| DOC-0015: install/uninstall --dry-run (absent from doc) | install.py:34-87; test_cli_dry_run.py:17-79 | CONTRADICTED (undocumented) | |
| DOC-0016: get_config(**overrides) signature | settings/__init__.py:84; test_pipeline.py:170 | CONTRADICTED | Actual signature: get_config(overrides: dict | None = None) |
| DOC-0017: load_config caches | test_pipeline.py:183-191 | VERIFIED | |
| DOC-0018: SchemaRegistry.register raises on duplicate | test_registry.py:67-70; registry.py:44-48 | VERIFIED | |
| DOC-0019: layer ordering package<project<user<CLI | test_pipeline.py:98-181; test_loader.py:127-143 | VERIFIED | |
| DOC-0020: COLORSCHEME_* and COLOR_SCHEME_TEMPLATES env vars | resolver.py:154-191; test_resolver.py:169-196 | VERIFIED | |
| DOC-0021: reload_config forces fresh load | test_pipeline.py:193-201 | VERIFIED | |
| DOC-0022: Color.hex pattern | types.py:23 | VERIFIED | |
| DOC-0023: Color.rgb range 0-255 | types.py:27-33; test_types.py:37-57 | VERIFIED | |
| DOC-0024: ColorScheme.colors exactly 16 | types.py:100; test_types.py:135-147 | VERIFIED | |
| DOC-0025: color_count hardcoded 16 | types.py:125 | VERIFIED | |
