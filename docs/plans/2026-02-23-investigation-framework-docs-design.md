# Design: Investigation + Synthesis Framework for Documentation

**Date:** 2026-02-23
**Status:** Approved

---

## Context

The project has a Diátaxis-structured `docs/` directory but it contains significant content errors
(7 critical, 9 additional discrepancies) catalogued in `docs/audit-2026-02-20.md`. Rather than
patching files in place, we run the full investigation+synthesis framework to produce clean,
test-grounded documentation from scratch.

---

## Decision

**Option B: Run the full investigation framework.**

Patch-in-place (Option A) would preserve existing errors and introduce new ones. Running the
framework produces docs where every claim traces directly to a test assertion, with no invented
behavior. The existing audit already confirms the test suite is comprehensive enough to serve as
ground truth.

---

## Repository Layout

```
color-scheme-generator/
└── docs/
    ├── investigation/           ← framework state (committed to repo)
    │   ├── audit-agent/         ← copied from framework template, configured
    │   └── synthesis-agent/     ← copied from framework template, configured
    ├── archive/                 ← old docs moved here before synthesis runs
    │   ├── tutorials/
    │   ├── how-to/
    │   ├── reference/
    │   ├── explanations/
    │   ├── README.md
    │   └── audit-2026-02-20.md
    ├── plans/                   ← this file lives here
    ├── tutorials/               ← synthesized output
    ├── how-to/
    ├── reference/
    └── explanation/
```

---

## Configuration

### `docs/investigation/audit-agent/01_REQUIREMENTS.md`

```
Repo root: <project root>
Primary language/ecosystem: Python (uv monorepo, 4 packages)
Project type: CLI / monorepo

Documentation roots: docs/
Interfaces of interest:
  - color-scheme-core CLI
  - color-scheme CLI (orchestrator)
  - Python public API: types, exceptions, settings SchemaRegistry

Test command: uv run pytest packages/
Test categories: unit, integration
Environment notes: smoke tests require Docker/Podman containers — exclude from investigation scope

Acceptance thresholds:
  S0 must be: 0
  S1 must be: <= 3
  Open Unknowns must be: <= 5
```

### `docs/investigation/synthesis-agent/01_OUTPUT_TARGET.md`

```
OUTPUT_PROFILE = synthesis-agent/profiles/diataxis
VERIFICATION_POLICY = verified-only
PRIMARY_AUDIENCE = end-users
OUTPUT_DIR = ../../   (resolves to docs/)

Interfaces:
  - color-scheme-core CLI
  - color-scheme CLI
  - Settings API (SchemaRegistry, config layers, env vars)
  - Template system
Exclusions:
  - Smoke test infrastructure
  - Internal container management implementation
  - CI/GitHub Actions configuration

Formatting:
  Language: English
  Tone: technical, direct
  Examples runnable: yes
  Include BHV IDs near examples: no
```

---

## Synthesis Profile

**Diátaxis** — produces `tutorials/`, `how-to/`, `reference/`, `explanation/` under `docs/`.
Matches the existing structural intent without adding build tooling (mkdocs profile excluded).

**Verification policy:** `verified-only` — behaviors not confirmed by tests are silently omitted.
Result is lean and accurate, not exhaustive.

---

## Execution Plan

1. **Setup** — Copy framework template files into `docs/investigation/`, write config files, commit.
2. **Audit phase** — Dispatch autonomous agent. Runs 8-phase state machine
   (`PHASE_1_INVENTORY` → `PHASE_8_FINALIZE_INVESTIGATION`), producing structured artifacts
   (`03_INVENTORY.md` through `11_NEXT_ACTIONS.md`) and a checkpoint per iteration.
   Terminates when `INVESTIGATION_STATUS = PASS`.
3. **Review point** — Inspect `08_FINDINGS.md` and `10_METRICS.md` before proceeding.
4. **Archive** — Move old docs to `docs/archive/`, commit.
5. **Synthesis phase** — Dispatch autonomous agent. Reads Diátaxis profile + investigation
   artifacts, writes `tutorials/`, `how-to/`, `reference/`, `explanation/` under `docs/`.
   Terminates when conformance checks pass.
6. **Final commit** — New docs + framework state committed together.

---

## Approach Considered and Rejected

| Approach | Rejected Because |
|---|---|
| Patch in place (Option A) | Perpetuates patching cycle; no traceability to test evidence |
| Single combined agent (Approach C) | No review point between audit and synthesis |
| Manual per-iteration invocation (Approach B) | High overhead; framework is designed for autonomous operation |
