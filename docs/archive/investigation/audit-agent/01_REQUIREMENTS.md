# Investigation Requirements

## Repository
- Repo root: /home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/color-scheme-generator
- Primary language/ecosystem: Python (uv monorepo, 4 packages: core, orchestrator, settings, templates)
- Project type: CLI / monorepo

## Scope
- Documentation roots: docs/
- Interfaces of interest:
  - color-scheme-core CLI (packages/core)
  - color-scheme CLI / orchestrator (packages/orchestrator)
  - Python public API: types, exceptions (packages/core)
  - Settings API: SchemaRegistry, config layers, env vars (packages/settings)
  - Template system (packages/templates)

## Tests
- Preferred test command(s): uv run pytest packages/ -v
- Test categories: unit (packages/*/tests/unit/), integration (packages/*/tests/integration/)
- Environment notes:
  - Smoke tests at tests/smoke/ require Docker/Podman containers — EXCLUDE from investigation scope
  - Unit + integration tests run locally with no external dependencies (external backends are mocked)

## Contracts (optional)
- No OpenAPI/JSON schema/proto files. Pydantic models in packages/settings/ serve as schema.

## Acceptance thresholds (defaults)
- S0 must be: 0
- S1 must be: <= 3
- Open Unknowns must be: <= 5
