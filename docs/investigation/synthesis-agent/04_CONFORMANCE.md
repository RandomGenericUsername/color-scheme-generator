# Documentation Conformance (Profile-driven)

- OUTPUT_PROFILE: synthesis-agent/profiles/diataxis
- Structure conformance: PASS
- Coverage conformance (public BHVs): 35/36
- Policy conformance: PASS
- Safety (no S0/S1 reproduction): PASS

SYNTHESIS_STATUS = PASS  # PASS | FAIL | BLOCKED

Blocking reasons (if BLOCKED):
- (none)

---

## Structure check

| Directory | Files | Status |
|-----------|-------|--------|
| `docs/tutorials/` | `getting-started.md` | PASS |
| `docs/how-to/` | `use-dry-run.md`, `configure-settings.md`, `install-backends.md` | PASS |
| `docs/reference/` | `cli-core.md`, `cli-orchestrator.md`, `settings-api.md`, `types.md`, `exceptions.md` | PASS |
| `docs/explanation/` | `architecture.md` | PASS |

All four required directories exist and contain at least one `.md` file.

---

## BHV coverage

### Covered (35 / 36)

| BHV | Covered in |
|-----|-----------|
| BHV-0001 | tutorials/getting-started.md, reference/cli-core.md |
| BHV-0002 | tutorials/getting-started.md, reference/cli-core.md |
| BHV-0003 | reference/cli-core.md |
| BHV-0004 | tutorials/getting-started.md, how-to/use-dry-run.md, reference/cli-core.md |
| BHV-0005 | how-to/use-dry-run.md, reference/cli-core.md |
| BHV-0006 | how-to/use-dry-run.md, reference/cli-core.md |
| BHV-0007 | tutorials/getting-started.md, reference/cli-core.md |
| BHV-0008 | how-to/use-dry-run.md, reference/cli-core.md |
| BHV-0009 | tutorials/getting-started.md, reference/cli-core.md, explanation/architecture.md |
| BHV-0010 | reference/cli-core.md, reference/exceptions.md |
| BHV-0012 | reference/types.md |
| BHV-0013 | reference/types.md |
| BHV-0014 | reference/types.md |
| BHV-0015 | reference/types.md, explanation/architecture.md |
| BHV-0016 | reference/types.md |
| BHV-0017 | reference/settings-api.md, reference/exceptions.md |
| BHV-0018 | reference/settings-api.md, reference/exceptions.md |
| BHV-0019 | how-to/configure-settings.md, reference/settings-api.md |
| BHV-0020 | how-to/configure-settings.md, reference/settings-api.md |
| BHV-0021 | how-to/configure-settings.md, reference/settings-api.md |
| BHV-0022 | how-to/configure-settings.md, reference/settings-api.md |
| BHV-0023 | reference/cli-orchestrator.md |
| BHV-0024 | reference/cli-orchestrator.md, how-to/install-backends.md |
| BHV-0025 | how-to/install-backends.md, reference/cli-orchestrator.md |
| BHV-0026 | how-to/install-backends.md, reference/cli-orchestrator.md |
| BHV-0027 | how-to/install-backends.md, reference/cli-orchestrator.md |
| BHV-0028 | how-to/install-backends.md, reference/cli-orchestrator.md |
| BHV-0029 | how-to/use-dry-run.md, how-to/install-backends.md, reference/cli-orchestrator.md |
| BHV-0030 | how-to/use-dry-run.md, how-to/install-backends.md, reference/cli-orchestrator.md |
| BHV-0031 | how-to/configure-settings.md, reference/settings-api.md |
| BHV-0032 | how-to/configure-settings.md, reference/settings-api.md |
| BHV-0033 | reference/exceptions.md |
| BHV-0034 | how-to/install-backends.md, reference/cli-orchestrator.md |
| BHV-0035 | how-to/install-backends.md, reference/cli-orchestrator.md |
| BHV-0036 | reference/cli-orchestrator.md |

### Omitted (1 / 36)

| BHV | Reason |
|-----|--------|
| BHV-0011 | Marked `internal` in 05_TEST_SPEC.md (detect_available exception handling). Not part of public interface. |

Coverage: 35/36 = 97.2% — exceeds the >=90% target.

---

## Policy check (verified-only)

All documented behaviors are grounded in BHV entries from 07_TRACEABILITY.md that have
test evidence listed. No unverified or speculative claims were introduced.

BHV-0011 (internal) is omitted rather than documented without evidence.

Status: PASS

---

## Safety check (S0/S1 not reproduced)

| Finding | Check |
|---------|-------|
| S1-0001: Old docs said auto-detect order is "pywal > wallust > custom" | NOT reproduced. All docs correctly state "wallust > pywal > custom". |
| S1-0002: Old docs showed `get_config(**overrides)` signature | NOT reproduced. reference/settings-api.md shows correct signature `get_config(overrides: dict[str, Any] \| None = None)`. |
| S1-0003: `--dry-run` / `-n` absent from install/uninstall docs | FIXED. Both flags are documented in reference/cli-orchestrator.md and how-to/install-backends.md. |

Status: PASS
