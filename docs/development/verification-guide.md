# Verification Infrastructure Quick Reference

Guide to using verification scripts and compliance checking tools.

## Daily Development Workflow

### Before Starting Work

1. Check design compliance:
   ```bash
   ./scripts/verify-design-compliance.sh
   ```

2. Review current phase goals:
   ```bash
   cat docs/implementation-progress.md
   ```

### During Development

3. Run tests frequently:
   ```bash
   cd packages/core  # or packages/orchestrator
   uv run pytest -v
   ```

4. Check coverage:
   ```bash
   uv run pytest --cov=src --cov-report=term
   ```

5. Lint and format:
   ```bash
   uv run ruff check .
   uv run black .
   uv run isort .
   ```

### Before Creating PR

6. Update CHANGELOG.md:
   ```markdown
   ## [Unreleased]

   ### Added
   - Your feature description
   ```

7. Run all verifications:
   ```bash
   ./scripts/verify-design-compliance.sh
   ./scripts/verify-documentation.sh
   ```

8. Ensure all tests pass:
   ```bash
   cd packages/core && uv run pytest
   cd packages/orchestrator && uv run pytest
   ```

### After Completing Phase

9. Run phase gate check:
   ```bash
   ./scripts/phase-gate-check.sh <N>
   ```

10. Update progress document:
    ```bash
    # Edit docs/implementation-progress.md
    # Mark phase as complete
    # Update next phase status
    ```

## Verification Scripts Reference

### verify-design-compliance.sh

Checks:
- Monorepo structure matches design
- Package structure correct
- Test coverage ≥ 95%
- Documentation structure
- Git workflow compliance

Usage:
```bash
./scripts/verify-design-compliance.sh
```

Exit codes:
- 0: All checks passed
- 1: Violations found

### verify-documentation.sh

Checks:
- CHANGELOG.md exists and has correct format
- README.md has required sections
- User documentation present
- Development documentation present
- Error database exists
- ADRs directory exists

Usage:
```bash
./scripts/verify-documentation.sh
```

### phase-gate-check.sh

Comprehensive verification for phase completion.

Runs:
- Common checks (design compliance, docs, git status)
- Phase-specific checks

Usage:
```bash
./scripts/phase-gate-check.sh <phase-number>

# Examples:
./scripts/phase-gate-check.sh 0  # Verification infrastructure
./scripts/phase-gate-check.sh 1  # Foundation
./scripts/phase-gate-check.sh 2  # Core backends
```

Exit codes:
- 0: Phase complete, ready to advance
- 1: Issues found, fix before advancing

### check-docs.py

Analyzes PR changes and determines required documentation updates.

Used by CI automatically, but can run locally:

```bash
# Get changed files
git diff --name-only origin/develop...HEAD > changed_files.txt

# Check doc requirements
python3 .github/scripts/check-docs.py changed_files.txt
```

## PR Checklist

When creating a PR, ensure:

1. ✅ Branch name follows convention
2. ✅ Commits follow Conventional Commits
3. ✅ All tests passing
4. ✅ Coverage ≥ 95%
5. ✅ CHANGELOG.md updated
6. ✅ Relevant docs updated
7. ✅ Design compliance checks pass
8. ✅ CI checks pass
9. ✅ PR template checklist complete

## Troubleshooting

### "Coverage below 95%"

```bash
# See what's not covered
cd packages/<package>
uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

Add tests for uncovered code.

### "Branch name doesn't follow convention"

Rename your branch:
```bash
git branch -m feature/<package>/<description>
# or bugfix/*, docs/*, refactor/*
```

### "CHANGELOG.md not updated"

Add entry to CHANGELOG.md:
```markdown
## [Unreleased]

### Added (or Changed, Fixed, etc.)
- Your change description
```

### "Documentation requirements not met"

Run doc checker to see what's needed:
```bash
git diff --name-only origin/develop...HEAD > changed_files.txt
python3 .github/scripts/check-docs.py changed_files.txt
```

Update the required documentation files.

## Integration with IDE

### VS Code Tasks

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Verify Design Compliance",
      "type": "shell",
      "command": "./scripts/verify-design-compliance.sh",
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Run Phase Gate Check",
      "type": "shell",
      "command": "./scripts/phase-gate-check.sh ${input:phaseNumber}",
      "group": "test"
    }
  ],
  "inputs": [
    {
      "id": "phaseNumber",
      "type": "promptString",
      "description": "Phase number"
    }
  ]
}
```

### Pre-commit Hooks

The verification can be integrated with git hooks:

```bash
# .git/hooks/pre-push
#!/bin/bash
./scripts/verify-design-compliance.sh
```

## References

- Design Document: `docs/plans/2026-01-18-monorepo-architecture-design.md`
- Implementation Progress: `docs/implementation-progress.md`
- PR Template: `.github/pull_request_template.md`
