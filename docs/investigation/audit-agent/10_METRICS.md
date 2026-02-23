# Investigation Metrics

## Counts (current)
- S0: 0
- S1: 3
- S2: 3
- S3: 2
- Unknowns open: 1

## Thresholds
- S0 must be 0: PASS (0 = 0)
- S1 must be <= 3: PASS (3 <= 3)
- Open Unknowns must be <= 5: PASS (1 <= 5)

## Investigation status
- INVESTIGATION_STATUS = PASS  # PASS | FAIL | BLOCKED

## BHV entries
- Total BHV entries in 07_TRACEABILITY.md: 36

## Findings summary
- S0: none
- S1-0001: Auto-detection order wrong in docs (wallust>pywal>custom, not pywal>wallust>custom)
- S1-0002: get_config() documented with wrong signature (**kwargs vs positional dict)
- S1-0003: install/uninstall --dry-run/-n flags completely absent from orchestrator-commands.md
- S2-0001: --dry-run flag missing from core-commands.md options tables
- S2-0002: List replacement behavior in deep_merge undocumented
- S2-0003: COLOR_SCHEME_TEMPLATES special-case env var not clearly differentiated
- S3-0001: Wrong namespace names in settings-api.md example
- S3-0002: orchestrator generate/show --dry-run also absent from options tables
