# Ticket index

> Counting rule: completeness checks cover item files (`tickets/<id>-<slug>/ticket.md`) only.
> `tickets/_template/` (and any `tickets/_fixtures/`) are excluded from INDEX completeness counting.
> Entry format: link — title | `status` | execution links. Epics add `done/total children done`, done-when, and one nested line per child. Bugs add severity. Spikes add timebox state.

## Active epics

(none)

## Requirements

(none)

## Bugs

- [BUG-002-csg-exit-zero-artifacts](./BUG-002-csg-exit-zero-artifacts/ticket.md) — csg exits 0 without artifacts when CWD templates/ is not a csg catalog | severity: high | `done` | tag v0.2.2

## Ops tasks

(none)

## Spikes

(none)

## Tasks

(none)

## Done (links only, newest last)

- [REQ-001-repo-birth](./REQ-001-repo-birth/ticket.md) — Birth the color-scheme-generator repo (mu-strict, `csg`) and cut v0.1.0 | `done` | openspec: repo-birth (archived 2026-10-21 → `openspec/changes/archive/2026-10-21-repo-birth/`, delta merged into `specs/repo-harness/`)
- [OPS-001-repin-contracts-v020](./OPS-001-repin-contracts-v020/ticket.md) — Re-pin contracts v0.2.0 and release csg v0.2.0 | `done` | openspec: none (recorded: ops-task, no spec delta)
- [OPS-002-invocation-contract-ci](./OPS-002-invocation-contract-ci/ticket.md) — Prove this repo's own side of the csg invocation contract in CI | `done` | openspec: none (recorded: ops-task, no spec delta)
- [OPS-003-contract-test-layout](./OPS-003-contract-test-layout/ticket.md) — Move the invocation-contract test to `tests/contract/` (path-only) | `done` | openspec: none (recorded: ops-task, no spec delta)
- [BUG-001-csg-stale-container-sweep](./BUG-001-csg-stale-container-sweep/ticket.md) — Sweep stale csg containers left by host SIGKILL or power loss | `done` | severity: medium | openspec: csg-stale-container-sweep (archived 2026-10-26 → `openspec/changes/archive/2026-10-26-csg-stale-container-sweep/`, delta merged into `specs/csg-container-mode/`); released `v0.2.1`
