# Contributing Guide

Thank you for contributing to color-scheme!

## Development Workflow

### 1. Setup Development Environment

```bash
./scripts/dev-setup.sh
```

See [Installation Guide](../user-guide/installation.md) for details.

### 2. Create Feature Branch

```bash
git checkout develop
git pull
git checkout -b feature/core/your-feature
```

Branch naming convention:
- `feature/<package>/<description>` - New features
- `bugfix/<issue>-<description>` - Bug fixes
- `docs/<description>` - Documentation
- `refactor/<description>` - Code improvements

### 3. Make Changes

Follow these principles:
- **YAGNI**: Only implement what's needed
- **DRY**: Don't repeat yourself
- **TDD**: Write tests first

### 4. Write Tests

All code must have tests with ≥95% coverage:

```bash
cd packages/core
uv run pytest tests/unit/test_your_feature.py -v
uv run pytest --cov=src/color_scheme --cov-report=term
```

### 5. Update Documentation

- Update CHANGELOG.md
- Update relevant docs in `docs/`
- Add docstrings to public APIs

### 6. Run Verification

```bash
./scripts/verify-design-compliance.sh
./scripts/verify-documentation.sh
```

### 7. Commit Changes

Use Conventional Commits format:

```bash
git commit -m "feat(core): add new feature

Detailed description of changes.

Closes #123"
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `ci`

### 8. Create Pull Request

1. Push branch: `git push origin feature/core/your-feature`
2. Create PR on GitHub
3. Fill out PR template completely
4. Wait for CI to pass
5. Self-review using PR checklist

### 9. Merge

Once CI passes and self-review is complete, merge your PR.

## Code Standards

### Python Style

- Black formatting (88 char line length)
- isort for imports
- Ruff for linting
- Type hints where practical

Run formatters:

```bash
cd packages/core
uv run black .
uv run isort .
uv run ruff check --fix .
```

### Testing

- Unit tests for individual components
- Integration tests for end-to-end flows
- Use pytest fixtures for common setup
- Mock external dependencies

See [Testing Patterns](testing-patterns.md) for examples.

### Documentation

- Docstrings for all public APIs
- User-facing docs in `docs/user-guide/`
- Development docs in `docs/development/`
- Architecture decisions in `docs/knowledge-base/adrs/`

## Getting Help

- Check [Troubleshooting](../troubleshooting/common-issues.md)
- Review [Error Database](../troubleshooting/error-database.md)
- Open an issue on GitHub

## Design Compliance

All contributions must follow the design document:
- `docs/plans/2026-01-18-monorepo-architecture-design.md`

The verification scripts enforce this automatically.
