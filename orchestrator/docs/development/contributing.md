# Contributing

How to contribute to `color-scheme`.

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
```

### 2. Make Changes

- Write code
- Add tests
- Update documentation if needed

### 3. Rebuild Containers (if needed)

```bash
make docker-build
```

### 4. Run Checks

```bash
make check
```

### 5. Commit

```bash
git add .
git commit -m "feat: add new feature"
```

### 6. Push and PR

```bash
git push origin feature/my-feature
```

---

## Pull Request Guidelines

- Clear description of changes
- All checks must pass
- Tests for new functionality
- Documentation updates if needed

---

## Container Changes

If you modify Dockerfiles:

1. Rebuild images: `make docker-build`
2. Test with actual containers
3. Update documentation if behavior changes

---

## Questions?

Open an issue for questions or discussion.

