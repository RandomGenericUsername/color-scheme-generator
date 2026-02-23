# Investigation Agent Rules (Fixed Framework)

This directory defines a **fixed investigation state machine**. The structure and file names are **not user-modifiable**.
The purpose is to investigate a repository, using a test-oriented approach, and to produce **investigation artifacts** that
can later be consumed by a separate synthesis loop.

## Non-negotiable principles

1. **No invention**: Do not fabricate commands, flags, endpoints, behaviors, return fields, env vars, or file paths.
2. **Full repo awareness**: Inventory covers docs + code + tests + configs + examples + contracts.
3. **Deterministic completeness**: Every file in scope must be accounted for in `03_INVENTORY.md` unless ignored by `.auditignore`.
4. **Evidence hierarchy** (highest to lowest):
   - Tests (executed assertions)
   - Contracts/specs (OpenAPI/JSON schema/etc.)
   - Code references (implementation)
   - Existing docs (claims)
5. **Traceability required**: Every behavior/claim/finding must point to evidence and location (file + line range when applicable).
6. **Iteration is mandatory**: Work proceeds only through iterations that read state, perform bounded work, write updates, and checkpoint.

## Severity levels

- **S0 Critical**: Incorrect docs/behavior causing failure, data loss, security issues, or non-working instructions.
- **S1 Major**: Core public behavior undocumented or contradicts evidence.
- **S2 Moderate**: Ambiguity, missing edge cases, partial instructions, unclear prerequisites.
- **S3 Minor**: Typos, formatting, style, low-impact clarity.

## Mandatory read order (every iteration)

1. `00_RULES.md`
2. `01_REQUIREMENTS.md`
3. `02_STATE.md`
4. Latest `iterations/####_CHECKPOINT.md` (if none, treat as iteration 0000)
5. Then perform the current phase actions as defined in `02_STATE.md`.

## Mandatory write set (every iteration)

Update living artifacts:
- `02_STATE.md`
- `03_INVENTORY.md`
- `04_TOPIC_MAP.md`
- `05_TEST_SPEC.md`
- `06_DOC_CLAIMS.md`
- `07_TRACEABILITY.md`
- `08_FINDINGS.md`
- `09_UNKNOWNS.md`
- `10_METRICS.md`
- `11_NEXT_ACTIONS.md`

Append a new checkpoint:
- `iterations/####_CHECKPOINT.md`

## Phases (finite state machine)

`02_STATE.md` Phase must be one of:
1. `PHASE_1_INVENTORY`
2. `PHASE_2_TOPIC_MAP`
3. `PHASE_3_TEST_SPEC`
4. `PHASE_4_BEHAVIOR_CATALOG`
5. `PHASE_5_DOC_CLAIMS`
6. `PHASE_6_TRACEABILITY`
7. `PHASE_7_REVIEW_FINDINGS`
8. `PHASE_8_FINALIZE_INVESTIGATION`

## Stall rule

If **two consecutive iterations** do not reduce **any** of:
- S0 count
- S1 count
- Open unknowns count

Terminate investigation as **BLOCKED** and list blockers in `11_NEXT_ACTIONS.md`.

## Termination condition (investigation loop)

Investigation terminates when `10_METRICS.md` declares:
- `INVESTIGATION_STATUS = PASS`
