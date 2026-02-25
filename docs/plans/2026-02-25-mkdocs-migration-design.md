# Design: MkDocs Material Migration

**Date:** 2026-02-25
**Status:** Approved

## Goal

Add MkDocs Material as a local documentation site generator on top of the existing
Diataxis-structured docs. Zero content changes to existing Markdown files.

## Approach

Approach B — Material with Diataxis navigation tabs. Each Diataxis quadrant
(Tutorial, How-To, Reference, Explanation) maps to a top-level navigation tab
in the Material theme, making the documentation philosophy visible at a glance.

## Constraints

- Local only — no CI, no GitHub Pages, no hosted deployment
- Hand-written docs only — no mkdocstrings or auto-generated API reference
- `docs/archive/` and `docs/audit-*.md` excluded from rendered site
- Zero content changes to existing `.md` files

## Changeset

| Action | File | Detail |
|--------|------|--------|
| Rename | `docs/README.md` → `docs/index.md` | MkDocs home page convention |
| Create | `mkdocs.yml` | Site config with Material theme and nav |
| Update | `pyproject.toml` | Add `mkdocs-material` to dev dependency group |
| Update | `Makefile` | Add `docs-serve` and `docs-build` targets |
| Update | `.gitignore` | Add `site/` |

## mkdocs.yml

```yaml
site_name: Color Scheme Generator
docs_dir: docs
theme:
  name: material
  palette:
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.top
    - search.highlight

exclude_docs: |
  archive/
  audit-*.md

nav:
  - Tutorial:
    - Getting Started: tutorials/getting-started.md
  - How-To:
    - Configure Settings: how-to/configure-settings.md
    - Install Backends: how-to/install-backends.md
    - Use Dry Run: how-to/use-dry-run.md
    - Integrate with Shell: how-to/integrate-shell.md
    - Create Templates: how-to/create-templates.md
    - Troubleshoot Errors: how-to/troubleshoot-errors.md
  - Reference:
    - CLI (color-scheme-core): reference/cli-core.md
    - CLI (color-scheme): reference/cli-orchestrator.md
    - Settings API: reference/settings-api.md
    - Exceptions: reference/exceptions.md
    - Types: reference/types.md
  - Explanation:
    - Architecture: explanation/architecture.md
```

## Makefile targets

```makefile
docs-serve: ## Serve docs locally with live reload
	uv run mkdocs serve

docs-build: ## Build static docs site to site/
	uv run mkdocs build --strict
```

## Notes

- `navigation.tabs` makes quadrant names appear as header tabs
- `--strict` on build treats broken internal links as errors
- `site/` is generated output — added to `.gitignore`
- `exclude_docs: audit-*.md` glob covers all future audit files automatically
- `docs/index.md` (renamed from README.md) becomes the landing page, not assigned
  to any quadrant tab — accessible via the site name link
