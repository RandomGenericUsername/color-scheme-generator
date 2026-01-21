## Description

<!-- Brief description of changes (2-3 sentences) -->

## Type of Change

- [ ] Feature (new functionality)
- [ ] Bug fix (fixes an issue)
- [ ] Documentation (docs only)
- [ ] Refactor (code improvement, no behavior change)
- [ ] Performance improvement
- [ ] Hotfix (critical production issue)
- [ ] Infrastructure/tooling

## Related Issues

Closes #
Related to #

---

## Design Compliance Checklist

> Reference: `docs/plans/2026-01-18-monorepo-architecture-design.md`

### Architecture (Section 1)

- [ ] Changes respect separation of concerns (core vs orchestrator)
- [ ] No circular dependencies introduced
- [ ] Core has zero knowledge of containers (if applicable)
- [ ] Dependencies flow: Orchestrator → Core → Libraries

### Testing (Section 5)

- [ ] Tests written before/alongside implementation code
- [ ] Coverage ≥ 95% (verify: `cd packages/<pkg> && uv run pytest --cov`)
- [ ] Unit tests for new/modified code
- [ ] Integration tests for end-to-end flows (if applicable)
- [ ] All tests pass locally
- [ ] No flaky tests introduced

### Documentation (Section 5)

- [ ] CHANGELOG.md updated with user-facing changes
- [ ] Public APIs have docstrings
- [ ] User documentation updated (if user-facing change):
  - [ ] CLI reference (if CLI changed)
  - [ ] Backend docs (if backend added/modified)
  - [ ] Configuration docs (if settings changed)
  - [ ] Containerization docs (if containers changed)
- [ ] Development docs updated (if process changed)
- [ ] Error database updated (if bug fix)
- [ ] ADR created (if architectural decision made)

### Git Workflow (Section 6)

- [ ] Branch name follows convention (feature/*, bugfix/*, docs/*, etc.)
- [ ] Commits follow Conventional Commits format
- [ ] Commit messages are descriptive
- [ ] PR title follows conventional format
- [ ] No merge commits (rebased on target branch)

### Code Quality

- [ ] Code follows existing patterns and conventions
- [ ] No commented-out code or debug statements
- [ ] No TODO comments (convert to issues instead)
- [ ] Error messages are clear and actionable
- [ ] Edge cases handled appropriately
- [ ] No over-engineering (YAGNI principle)

### CI/CD (Section 7)

- [ ] All CI checks passing
- [ ] Linting passes: `ruff check && black --check && isort --check`
- [ ] Type checking passes: `mypy src/`
- [ ] Security scan clean: `bandit -r src/`
- [ ] No warnings in CI output

### Manual Testing

- [ ] Ran the feature/fix manually
- [ ] Tested on clean environment
- [ ] Tested both core and orchestrator (if applicable)
- [ ] Verified error messages are user-friendly
- [ ] Tested edge cases

### Performance

- [ ] No obvious performance regressions
- [ ] Benchmarks updated (if performance-critical change)
- [ ] Resource usage is reasonable

### Security

- [ ] No hardcoded secrets or credentials
- [ ] Input validation for user-provided data
- [ ] No SQL injection vulnerabilities
- [ ] No command injection vulnerabilities
- [ ] External dependencies reviewed

---

## Verification Commands

<!-- Show the exact commands you ran to verify this works -->

```bash
# Example:
cd packages/core
uv run pytest -v
uv run pytest --cov=src --cov-report=term
uv run ruff check .
uv run mypy src/
./scripts/verify-design-compliance.sh
```

## Breaking Changes

<!-- List any breaking changes and migration path -->

- [ ] No breaking changes
- [ ] Breaking changes documented with migration guide

If breaking changes:
- What breaks:
- Migration path:
- Version bump required: MAJOR / MINOR / PATCH

---

## Screenshots / Logs

<!-- If applicable, add screenshots or relevant log output -->

---

## Reviewer Notes

<!-- Any specific areas you want reviewers to focus on -->

---

## Self-Review Checklist

- [ ] I have reviewed my own code
- [ ] I have tested this thoroughly
- [ ] I have updated all relevant documentation
- [ ] I have run all verification scripts
- [ ] This PR is ready for review

---

## Post-Merge Actions

- [ ] Update implementation progress doc (if phase milestone)
- [ ] Update error database (if bug fix)
- [ ] Notify users (if significant change)
- [ ] None required
