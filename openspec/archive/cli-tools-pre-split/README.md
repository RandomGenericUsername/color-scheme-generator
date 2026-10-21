# Pre-split OpenSpec archive (from `dotfiles-v3`)

This directory is the **verbatim** copy of the retired nested OpenSpec root
`src/cli-tools/openspec/` of `dotfiles-v3`, carried here by slice S6a of the CLI-repos split
(spine **AD-15**: OpenSpec ownership follows code ownership).

Provenance:

- Source: `dotfiles-v3/src/cli-tools/openspec/` (deleted in the S6 deletion commit of that repo).
- Source ref: `dotfiles-v3` `master` at `6e0633baa2dae28f3193397fa529234074f026c1`
  (the S6a precondition SHA).
- Carried: 2026-10-21, slice S6a, by `cp -a`; verified with
  `diff -r <source> openspec/archive/cli-tools-pre-split` → empty.

What it contains (2 directories, 5 files):

| Path | What it is |
| --- | --- |
| `changes/fix-container-engine-plumbing/proposal.md` | Completed csg-only change: the global `--container-engine` flag was discarded, `install` had its own `--engine`; the fix stores the engine in `ctx.obj` and removes the duplicate flag. |
| `changes/fix-container-engine-plumbing/design.md` | The decision record (D1: store in `ctx.obj`, D2: also feed `cli_overrides`, D3: remove install's `--engine`), risks, and affected files. |
| `changes/fix-container-engine-plumbing/tasks.md` | Nine checked tasks (all `[x]`): the change shipped before the split. |
| `changes/fix-container-engine-plumbing/.openspec.yaml` | The nested root's per-change scaffolding (`schema: spec-driven`, `created: 2026-07-28`). Preserved as history; it is inert here. |
| `specs/no-spec-changes.md` | Placeholder stating the change was pure plumbing with no capability requirement changes. |

This tree is **archive, not an active OpenSpec root**:

- The live root is `openspec/` (`config.yaml`, `specs/`, `changes/`).
- Nothing under `openspec/archive/` is validated as a capability or a change:
  `openspec validate --specs --strict` and `openspec validate repo-birth --strict` ignore it.
- The `.openspec.yaml` here is not a second root marker; the directory lives under `archive/` and
  carries no `openspec` commands.

History is never rewritten (spine AD-15): do not edit these files, do not "fix" the change log.
