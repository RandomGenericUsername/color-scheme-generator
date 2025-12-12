# Contributing

How to contribute to `colorscheme-gen`.

---

## Getting Started

1. Fork the repository
2. Clone your fork
3. Set up development environment (see [Setup](setup.md))
4. Create a feature branch

---

## Development Process

### 1. Create Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bugfix
```

### 2. Make Changes

- Write code
- Add tests
- Update documentation if needed

### 3. Run Checks

```bash
make check  # Runs lint, type-check, and tests
```

### 4. Commit

```bash
git add .
git commit -m "feat: add new feature"
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring

### 5. Push and PR

```bash
git push origin feature/my-feature
```

Create a pull request on GitHub.

---

## Pull Request Guidelines

- Clear description of changes
- All checks must pass
- Tests for new functionality
- Documentation updates if needed

---

## Code Review

PRs require review before merging. Reviewers check:

- Code quality
- Test coverage
- Documentation
- Adherence to style guide

---

## Questions?

Open an issue for questions or discussion.

