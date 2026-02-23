# Unknowns Register

Unknown IDs: `U-0001`, `U-0002`, ...

- U-0001:
  - Question: What is the exact behavior of `OutputManager` when writing output files — does it create parent directories automatically?
  - Status: resolved
  - Opened in iteration: 0002
  - Attempts: Reviewed cli/main.py and output/manager.py; orchestrator/cli/main.py line 152 calls `output_dir.mkdir(parents=True, exist_ok=True)` before container execution; core CLI does not explicitly mkdir in the generate path but docs claim "Created if it does not exist"
  - Resolution evidence: docs/reference/cli/core-commands.md line 65; orchestrator/cli/main.py line 152. The orchestrator creates the dir; core OutputManager behavior not independently confirmed from static analysis — treated as partially resolved.

- U-0002:
  - Question: Does the `pywal` backend check for `wal` binary or `pywal` binary in PATH?
  - Status: resolved
  - Opened in iteration: 0002
  - Attempts: Reviewed docs/reference/cli/core-commands.md line 107: "Checks if wal binary is in PATH"
  - Resolution evidence: docs claim "wal" binary (pywal CLI is `wal`); test_factory.py line 32: mock_which returns "/usr/bin/wal". Confirmed: pywal backend checks for `wal`.

- U-0003:
  - Question: What is the exact precedence when COLORSCHEME_ env var and user config both define the same key?
  - Status: resolved
  - Opened in iteration: 0002
  - Attempts: Reviewed resolver.py lines 328-361
  - Resolution evidence: resolver.py lines 347-362: ENV checked before USER_CONFIG in _resolve_setting; ENV wins over user config.

- U-0004:
  - Question: Are there additional test files not yet read that might reveal undocumented behaviors (test_output_manager.py, test_pywal_backend.py, test_wallust_backend.py, test_custom_backend.py, test_container_execution.py)?
  - Status: open
  - Opened in iteration: 0002
  - Attempts: Files inventoried but not fully read; no evidence of critical new behaviors from file names
  - Resolution evidence: (none — static analysis only)

- U-0005:
  - Question: Does the orchestrator generate command also support `--dry-run`? (separate from install/uninstall)
  - Status: resolved
  - Opened in iteration: 0002
  - Attempts: Reviewed orchestrator/cli/main.py lines 72-132
  - Resolution evidence: orchestrator/cli/main.py lines 72-77 declares dry_run parameter; lines 99-132 implement dry-run mode for orchestrator generate. Confirmed: orchestrator generate also supports --dry-run.
