# Docs Cleanup — Design Spec

**Date:** 2026-03-11
**Status:** Approved

## Problem Summary

The `docs/` directory contains accumulated noise from earlier development phases:
investigation artifacts, completed implementation plans, superseded archive docs, and
old audit reports. This makes the docs directory hard to navigate and causes
`make docs-build` to rely on `exclude_docs` hacks to avoid rendering stale content.

The project changelog also lives at the repository root rather than inside `docs/`,
breaking the "all documentation lives in `docs/`" convention and missing from the
MkDocs nav.

## Scope

**Delete entirely:**

| Path | Reason |
|------|--------|
| `docs/archive/` | Superseded content and investigation artifacts (~70 files) |
| `docs/plans/` | Completed implementation plans (mkdocs migration, show-containerization both merged) |
| `docs/superpowers/` | Internal AI spec files — superseded by the plans produced from them |
| `docs/audit-2026-02-23.md` | Superseded by 2026-03-11 audit |

**Migrate:**

| From | To | Notes |
|------|----|-------|
| `CHANGELOG.md` (root) | `docs/changelog.md` | Content unchanged; Keep a Changelog format preserved |
| Root `CHANGELOG.md` | One-liner redirect | `See [docs/changelog.md](docs/changelog.md) for the full changelog.` |

**Update `mkdocs.yml`:**

- Remove the `exclude_docs` block entirely (nothing left to exclude after cleanup)
- Add `Changelog: changelog.md` to the nav between Home and Tutorial:

```yaml
nav:
  - Home: index.md
  - Changelog: changelog.md
  - Tutorial:
      - Getting Started: tutorials/getting-started.md
  ...
```

**Update `docs/index.md`:**

- Add a link to `docs/changelog.md` in the navigation / quick-links section

## Final `docs/` Structure

```
docs/
  index.md
  changelog.md
  explanation/
    architecture.md
  tutorials/
    getting-started.md
  how-to/
    configure-settings.md
    install-backends.md
    use-dry-run.md
    integrate-shell.md
    create-templates.md
    troubleshoot-errors.md
  reference/
    cli-core.md
    cli-orchestrator.md
    settings-api.md
    exceptions.md
    types.md
```

## Makefile

No changes required. `docs-serve` and `docs-build` targets call `mkdocs` directly
and are unaffected by the file moves.

## Success Criteria

- `make docs-build` passes with `--strict` (no broken links, no excluded paths)
- `docs/` contains only the files listed in the Final Structure above
- `CHANGELOG.md` at the root exists as a redirect one-liner
- `docs/changelog.md` contains the full migrated content
- `mkdocs.yml` nav includes Changelog and has no `exclude_docs` block
