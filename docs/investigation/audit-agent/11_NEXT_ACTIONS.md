# Next Actions (Investigation)

## Status
Investigation complete. INVESTIGATION_STATUS = PASS.

## Remaining open unknowns

- U-0004 (open): Additional test files not fully read (test_output_manager.py, test_pywal_backend.py, test_wallust_backend.py, test_custom_backend.py, test_container_execution.py). These are unlikely to change finding counts given the current thresholds are met. A synthesis agent may choose to read them for completeness.

## Recommended actions for synthesis agent

1. **Fix S1-0001** (highest impact): Update `docs/reference/cli/core-commands.md` lines 66 and 107-111 to correctly state backend auto-detection order as wallust > pywal > custom. Update `docs/reference/cli/orchestrator-commands.md` backend selection description similarly.

2. **Fix S1-0002** (API correctness): Update `docs/reference/api/settings-api.md` — change `get_config(**overrides)` to `get_config(overrides: dict[str, Any] | None = None)` and update the example code accordingly (line 165: use positional dict, not keyword expansion).

3. **Fix S1-0003** (missing doc): Add `--dry-run` / `-n` flag documentation to `install` and `uninstall` commands in `docs/reference/cli/orchestrator-commands.md`.

4. **Fix S2-0001**: Add `--dry-run` / `-n` to the options tables in core-commands.md for both `generate` and `show` commands.

5. **Fix S2-0002**: Add a note in settings-api.md merge behavior section explaining that list values are replaced entirely (not appended).

6. **Fix S2-0003**: Clearly distinguish `COLOR_SCHEME_TEMPLATES` (special-case) from `COLORSCHEME_*` (general pattern) in env var documentation.

## Blockers
None. Investigation completed within threshold.
