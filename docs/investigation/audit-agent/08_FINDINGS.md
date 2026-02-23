# Findings (Prioritized)

## S0 Critical
(none)

---

## S1 Major

- S1-0001:
  - Summary: Backend auto-detection order is documented as "pywal > wallust > custom" but code/tests implement "wallust > pywal > custom"
  - Location: docs/reference/cli/core-commands.md lines 66, 107-110; docs/reference/cli/orchestrator-commands.md lines 277-279
  - Evidence: packages/core/src/color_scheme/factory.py line 130: `for backend in [Backend.WALLUST, Backend.PYWAL, Backend.CUSTOM]`; packages/core/tests/unit/test_factory.py line 71: `assert backend == Backend.WALLUST` when all available. Docs say pywal is checked first.
  - Proposed fix: Update docs/reference/cli/core-commands.md lines 66 and 107-111 to read "wallust, pywal, custom" (in that order). Update orchestrator-commands.md auto-detection description similarly.

- S1-0002:
  - Summary: `get_config()` signature in settings-api.md is documented as `get_config(**overrides)` (kwargs) but actual implementation signature is `get_config(overrides: dict[str, Any] | None = None)` (positional dict argument)
  - Location: docs/reference/api/settings-api.md lines 147-175 (signature and example)
  - Evidence: packages/settings/src/color_scheme_settings/__init__.py line 84: `def get_config(overrides: dict[str, Any] | None = None) -> BaseModel:`; packages/settings/tests/test_pipeline.py line 170: called as `get_config({"core.generation.saturation_adjustment": 0.5, ...})` not with kwargs
  - Proposed fix: Update settings-api.md to show correct signature `get_config(overrides: dict[str, Any] | None = None)` and update the example to pass a dict rather than keyword arguments.

- S1-0003:
  - Summary: `--dry-run` / `-n` flags for `install` and `uninstall` orchestrator commands are completely absent from docs/reference/cli/orchestrator-commands.md
  - Location: docs/reference/cli/orchestrator-commands.md — install section (lines 320-530), uninstall section (lines 533-739) — no mention of --dry-run
  - Evidence: packages/orchestrator/src/color_scheme_orchestrator/cli/commands/install.py lines 34-39 (dry_run param declared); packages/orchestrator/tests/integration/test_cli_dry_run.py lines 17-79 (tests for install/uninstall --dry-run); packages/orchestrator/tests/unit/test_install_uninstall_dryrun.py
  - Proposed fix: Add `--dry-run`, `-n` option entry to the install and uninstall options tables in orchestrator-commands.md; add dry-run behavior description and examples for both commands.

---

## S2 Moderate

- S2-0001:
  - Summary: `--dry-run` / `-n` flag is also not listed in the options table for `generate` and `show` commands in docs/reference/cli/core-commands.md, even though the behavior is implemented and tested
  - Location: docs/reference/cli/core-commands.md — generate options table (lines 63-68); show options table (lines 191-195)
  - Evidence: cli/main.py lines 96-101 (--dry-run declared as Option); tests/integration/test_cli_dry_run.py (comprehensive tests for both generate and show)
  - Proposed fix: Add `--dry-run`, `-n` row to options tables for generate and show commands.

- S2-0002:
  - Summary: The `deep_merge` behavior for lists (lists are replaced entirely, not element-merged) is not documented in the settings API docs
  - Location: docs/reference/api/settings-api.md — merge behavior section (lines 363-403)
  - Evidence: packages/settings/tests/test_merger.py lines 46-56: `deep_merge({"formats": ["json","css","yaml"]}, {"formats": ["json"]}) == {"formats": ["json"]}`
  - Proposed fix: Add a note in the merge behavior section clarifying that list values are replaced entirely rather than merged.

- S2-0003:
  - Summary: `COLOR_SCHEME_TEMPLATES` env var (single underscore, not COLORSCHEME_ prefix) is a special case that is not clearly differentiated from the `COLORSCHEME_*` pattern in the docs
  - Location: docs/reference/cli/core-commands.md lines 352-358; docs/reference/api/settings-api.md (env vars section)
  - Evidence: resolver.py lines 185-189: special handling for COLOR_SCHEME_TEMPLATES; defaults.py lines 44-51: also checked in defaults
  - Proposed fix: Clearly document COLOR_SCHEME_TEMPLATES as a special-case env var distinct from COLORSCHEME_ prefix pattern, with its specific effect on template directory.

---

## S3 Minor

- S3-0001:
  - Summary: settings-api.md example for SchemaRegistry.all_namespaces() shows comment `# ["core", "orchestrator", "settings"]` but the settings package namespace is not "settings"; it registers as part of other packages
  - Location: docs/reference/api/settings-api.md lines 263-265
  - Evidence: test_registry.py shows only "core" and "orchestrator" as example namespaces
  - Proposed fix: Update the example comment to use accurate namespace names.

- S3-0002:
  - Summary: orchestrator-commands.md generate --dry-run flag is also absent (mirrors S1-0003 for generate/show in orchestrator)
  - Location: docs/reference/cli/orchestrator-commands.md lines 41-78 (generate options table)
  - Evidence: orchestrator/cli/main.py lines 72-77 (dry_run parameter declared); test_cli_dry_run.py orchestrator generate tests
  - Proposed fix: Add --dry-run, -n option to orchestrator generate and show options tables.
