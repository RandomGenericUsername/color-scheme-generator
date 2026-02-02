# Pre-commit Hooks Setup

Your project now has automated pre-commit hooks configured to run GitHub Actions checks locally before each commit.

## Installation Status

✅ Pre-commit framework installed
✅ Git hooks configured at `.git/hooks/pre-commit`
✅ Hooks will run automatically on `git commit`

## What Gets Checked

### Basic File Checks
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML syntax validation
- Merge conflict detection
- Private key detection
- Case conflict checks

### Code Quality (Matching GitHub Actions)
- **Black**: Auto-format Python code
- **isort**: Sort imports automatically
- **Ruff**: Lint and fix common issues
- **mypy**: Type checking (Python 3.12)

### Security
- **Bandit**: Detect security vulnerabilities

### File Size
- Prevents committing files larger than 1MB

## How to Use

### Automatic (on every commit)
```bash
git commit -m "Your message"
# Hooks run automatically - must pass before commit succeeds
```

### Run all hooks manually
```bash
pre-commit run --all-files
```

### Run specific hook
```bash
pre-commit run black --all-files
pre-commit run ruff --all-files
pre-commit run mypy --all-files
```

### Run pipeline validation (optional - slower)
```bash
pre-commit run pipeline-validation --all-files
# This runs the full 'make pipeline' command
```

### Bypass hooks (not recommended)
```bash
git commit --no-verify
```

## Workflow

Your typical development workflow now becomes:

```bash
# 1. Make changes
vim src/color_scheme/main.py

# 2. Stage changes
git add src/color_scheme/main.py

# 3. Commit (hooks run automatically)
git commit -m "Add feature X"
# ✓ Trailing whitespace trimmed
# ✓ Code formatted with Black
# ✓ Imports sorted
# ✓ Ruff linting passed
# ✓ Type checking passed
# ✓ Security check passed

# 4. Push to GitHub
git push
# GitHub Actions will also run - but should pass!
```

## What Hooks Will Fix Automatically

The following issues are **automatically fixed** before commit:
- Trailing whitespace
- Incorrect file endings
- Import order
- Code formatting
- Some linting issues

## What Requires Manual Fixes

These must be fixed manually before commit can proceed:
- Type errors (mypy)
- Security issues (bandit)
- Complex ruff violations
- File size exceeds 1MB

## Configuration Details

The configuration is in `.pre-commit-config.yaml` with:
- **Stages**: Runs at `pre-commit` stage (before each commit)
- **Concurrency**: Runs all hooks (doesn't stop on first failure)
- **Python Version**: 3.12 (matching your project requirements)

## Troubleshooting

### Hooks not running on commit
```bash
# Reinstall hooks
pre-commit install
```

### Need to skip for a commit
```bash
git commit --no-verify  # Use sparingly!
```

### Want to run all hooks before committing
```bash
# Good practice before pushing
pre-commit run --all-files
```

### Update hook versions
```bash
pre-commit autoupdate
```

### See what hooks are installed
```bash
pre-commit run --list-files
```

## Integration with Makefile

The pre-commit hooks complement your Makefile:

- **make format** - Formats all code
- **pre-commit run --all-files** - Runs all checks (including formatting)
- **make pipeline** - Full GitHub Actions simulation (also available as hook)

## Benefits

✅ Catch issues **before** pushing to GitHub
✅ Consistent code quality across team
✅ Automated formatting saves time
✅ Security vulnerabilities detected early
✅ No more "fix linting" commits
✅ Reduced CI/CD pipeline failures

## Next Steps

1. Make a test commit to verify hooks work
2. Review fixed files
3. Stage and commit any remaining changes
4. Push to GitHub with confidence!

---

**Tip**: If you have many files that need formatting, run:
```bash
pre-commit run --all-files
```
This formats everything at once before making any commits.
