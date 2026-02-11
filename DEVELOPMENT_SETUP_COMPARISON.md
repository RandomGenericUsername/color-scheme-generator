# Development Setup Comparison
## color-scheme vs wallpaper-effects-generator

**Date:** 2026-02-11 (Analysis date - Updated to reflect post-modernization)
**Scope:** Development infrastructure only (excluding application functionality)

**📝 Note:** This comparison document was initially created to identify gaps between color-scheme and wallpaper-effects-generator development setups. As of 2026-02-11, the color-scheme project has been modernized to align with wallpaper-effects-generator best practices. See the [DEVELOPMENT.md](./DEVELOPMENT.md) file for the current development setup guide.

---

## Executive Summary

Both projects share nearly identical development setups, following the same architectural pattern with monorepo structure, shared tooling, and CI/CD pipelines. The projects are clearly from the same design philosophy/author and use virtually the same tech stack for development. Key differences are minimal and mostly relate to the number of packages and specific package names.

---

## 1. Project Structure

### color-scheme
```
packages/
├── core/               # Color scheme generation engine
├── settings/           # Shared configuration system
├── templates/          # Template discovery system (UNIQUE)
└── orchestrator/       # CLI orchestration layer

Root files:
- pyproject.toml       # Workspace root
- Makefile            # Development commands
- .pre-commit-config.yaml
- .gitignore
- .github/workflows/
```

### wallpaper-effects-generator
```
packages/
├── core/               # Wallpaper effects processor
├── settings/           # Shared configuration system (named "layered-settings")
├── effects/            # Effects configuration (UNIQUE)
└── orchestrator/       # CLI orchestration layer

Root files:
- pyproject.toml       # Workspace root
- Makefile            # Development commands
- .pre-commit-config.yaml
- .gitignore
- .github/workflows/
```

### Differences
| Aspect | color-scheme | wallpaper-effects | Notes |
|--------|--------------|-------------------|-------|
| **Packages** | 4 packages | 4 packages | Both use 4-package monorepo |
| **Unique package 1** | templates | effects | Function-specific packages differ |
| **Unique package 2** | None | None | Both have core, settings, orchestrator |
| **Documentation** | docs/ folder | docs/ + DEVELOPMENT.md | wallpaper has standalone dev guide |

---

## 2. Package Management & Dependencies

### Dependency Management Tool
**Both:** `uv` (Python package manager)

### Python Version Requirements
**Both:** `requires-python = ">=3.12"`

### Workspace Configuration
Both use `tool.uv.workspace` in root `pyproject.toml`:

**color-scheme:**
```toml
[tool.uv.workspace]
members = [
    "packages/settings",
    "packages/templates",
    "packages/core",
    "packages/orchestrator",
]
```

**wallpaper-effects-generator:**
```toml
[tool.uv.workspace]
members = [
    "packages/settings",
    "packages/effects",
    "packages/core",
    "packages/orchestrator",
]
```

### Root Workspace Dependencies

| Aspect | color-scheme | wallpaper-effects | Status |
|--------|--------------|-------------------|--------|
| **Workspace type** | uv workspace | uv workspace | ✓ Identical |
| **Root dependencies** | Listed in pyproject | Listed in pyproject | ✓ Identical pattern |
| **Dev dependencies** | In dependency-groups | In dependency-groups | ✓ Identical pattern |

### Dev Dependency Versions

**color-scheme:**
```toml
[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.8.0",
    "mypy>=1.11.0",
    "black>=24.0.0",
    "ruff>=0.6.0",
    "isort>=5.13.0",
    "bandit>=1.8.6",
    "pre-commit>=3.8.0",
]
```

**wallpaper-effects-generator:**
```toml
[dependency-groups]
dev = [
    "pytest>=9.0.0",              # ⬆️ NEWER
    "pytest-cov>=7.0.0",          # ⬆️ NEWER
    "pytest-xdist>=3.8.0",        # Same
    "mypy>=1.19.0",               # ⬆️ NEWER
    "types-PyYAML>=6.0.0",        # ➕ ADDED
    "black>=26.0.0",              # ⬆️ MUCH NEWER
    "ruff>=0.14.0",               # ⬆️ MUCH NEWER
    "isort>=7.0.0",               # ⬆️ NEWER
    "bandit>=1.8.0",              # Same range
    "pre-commit>=3.8.0",          # Same
]
```

### Key Observations
- **wallpaper-effects** uses significantly newer versions of key tools (especially Black v26, Ruff v0.14)
- **color-scheme** uses older versions (Black v24, Ruff v0.6)
- wallpaper-effects explicitly adds `types-PyYAML` (YAML type hints)
- Both projects will eventually need dependency upgrades for color-scheme

---

## 3. Build System

### Build Backend
**Both:** `hatchling`

### Individual Package Configuration
Each package uses identical configuration pattern:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<package_name>"]
```

### Build Tools
**Both:** `uv build` command via Makefile

---

## 4. Code Quality & Linting Tools

### Tools Used (Identical in Both)
| Tool | Purpose | Version (color-scheme) | Version (wallpaper) |
|------|---------|----------------------|---------------------|
| **Black** | Code formatting | 24.1.1 | 24.1.1 (pre-commit hook) |
| **isort** | Import sorting | 5.13.2 | 5.13.2 (pre-commit hook) |
| **Ruff** | Fast linting | v0.2.1 | v0.2.1 (pre-commit hook) |
| **mypy** | Type checking | v1.8.0 | v1.8.0 (pre-commit hook) |
| **Bandit** | Security scanning | 1.7.5 | 1.7.5 (pre-commit hook) |

### Configuration Files in Packages

**color-scheme templates/pyproject.toml:**
```toml
[tool.black]
line-length = 88
target-version = ["py312"]

[tool.isort]
profile = "black"
line_length = 88
```

**color-scheme settings/pyproject.toml:**
```toml
[tool.black]
line-length = 88
target-version = ["py312"]

[tool.isort]
profile = "black"
line_length = 88
```

**wallpaper-effects root pyproject.toml:** (CENTRALIZED)
```toml
[tool.isort]
profile = "black"
line_length = 88

[tool.black]
line-length = 88
target-version = ["py312"]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.mypy]
ignore_missing_imports = true
disable_error_code = ["import-untyped"]
```

### Key Difference
- **wallpaper-effects:** Centralizes tool config in root `pyproject.toml`
- **color-scheme:** Duplicates config in each package's `pyproject.toml`
- **Recommendation:** wallpaper's approach is better (single source of truth)

---

## 5. Pre-commit Hooks Configuration

### Configuration File
Both use: `.pre-commit-config.yaml` in project root

### Hook Categories (Both Identical)

#### A. Basic File Checks (v4.5.0)
```yaml
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- check-json
- check-toml
- check-merge-conflict
- detect-private-key
- check-case-conflict
- check-symlinks
```

#### B. Python Formatting

**Black (24.1.1)**
```yaml
stages: [pre-commit]
args: [--line-length=88]
language_version: python3.12
```

**isort (5.13.2)**
```yaml
stages: [pre-commit]
args: [--profile=black, --line-length=88]
```

**Ruff (v0.2.1)**
```yaml
- id: ruff           # Linting with fixes
  args: [--fix, --line-length=88]
- id: ruff-format    # Fallback formatter
```

#### C. Type Checking - mypy (v1.8.0)

**color-scheme:**
```yaml
language_version: python3.12
additional_dependencies: [types-pillow]
args: [--ignore-missing-imports]
exclude: ^(packages|src)/.*/tests/
```

**wallpaper-effects-generator:**
```yaml
language_version: python3.12
args: [--ignore-missing-imports, --disable-error-code=import-untyped]
additional_dependencies: [types-PyYAML]
exclude: ^(packages|src)/.*/tests/
```

#### D. Security Scanning - Bandit (1.7.5)
```yaml
args: [-ll]
exclude: ^(packages|src)/.*/tests/|test_.*\.py$
files: ^(packages|src)/.*\.py$
additional_dependencies: [pbr]
```

#### E. File Size Checks
```yaml
- id: check-added-large-files
  args: [--maxkb=1000]  # 1MB limit
```

#### F. Custom Pipeline Hook
```yaml
- repo: local
  hooks:
    - id: pipeline-validation
      name: Validate pipeline locally
      entry: bash -c 'make pipeline'
      language: system
      stages: [manual]  # Run with: pre-commit run pipeline-validation --all-files
      pass_filenames: false
      always_run: true
```

### Exclusions (Identical)
Both exclude the same directories:
```
_archive_old_implementation
htmlcov
.venv, venv
__pycache__
.pytest_cache
.mypy_cache
.git
dist, build
*.egg-info
```

### Configuration Differences
| Aspect | color-scheme | wallpaper | Notes |
|--------|--------------|-----------|-------|
| **mypy dependencies** | types-pillow | types-PyYAML | Project-specific type stubs |
| **mypy error codes** | N/A | disable import-untyped | wallpaper is stricter |
| **Overall structure** | ✓ Identical | ✓ Identical | Very similar setup |

---

## 6. Makefile & Development Commands

### Makefile Structure
Both use identical Makefile organization with sections:
- General (help, default goal)
- Setup & Installation
- Code Quality (lint, format)
- Security
- Testing
- Building
- CI/CD Pipeline
- Cleanup

### Targets Overview

| Category | color-scheme | wallpaper-effects | Differences |
|----------|--------------|-------------------|-------------|
| **Setup** | `make dev` | `make dev` | ✓ Identical |
| **Install** | `install-deps`, `-core`, `-orchestrator` | `install-deps`, `-settings`, `-core`, `-effects`, `-orchestrator` | ⬆️ wallpaper has more |
| **Linting** | `lint` (core, settings, orchestrator) | `lint` (settings, core, effects, orchestrator) | Different package count |
| **Formatting** | `format` (core, settings, orchestrator) | `format` (all 4) | More packages in wallpaper |
| **Security** | `security` (core, settings, orchestrator) | `security` (all 4) | More packages in wallpaper |
| **Testing** | `test-all`, per-package targets | `test-all`, per-package targets | ✓ Identical pattern |
| **Building** | `build`, per-package targets | `build`, per-package targets | ✓ Identical pattern |
| **Pipeline** | `make pipeline` | `make pipeline` | ✓ Identical |
| **Clean** | `make clean` | `make clean` | ✓ Identical |

### Key Makefile Features (Both)

#### 1. Colored Output
```makefile
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m
```

#### 2. Tool Variables
```makefile
PYTHON_VERSION := 3.12
UV := uv
PACKAGES_DIR := packages
TOOLS_DIR := tools
DEV_DIR := $(TOOLS_DIR)/dev
```

#### 3. Help System
Automatically generates help from `##` comments:
```makefile
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf...}'
```

### Command Patterns

#### Installation
**color-scheme:**
```makefile
install-deps:
	$(UV) sync --dev
```

**wallpaper-effects:**
```makefile
install-deps:
	$(UV) sync --dev --all-packages
```
⬆️ wallpaper uses `--all-packages` flag

#### Linting (per-package example: Core)

**color-scheme:**
```makefile
lint-core:
	cd $(CORE_DIR) && $(UV) run ruff check .
	cd $(CORE_DIR) && $(UV) run black --check .
	cd $(CORE_DIR) && $(UV) run isort --check .
	cd $(CORE_DIR) && $(UV) run mypy src/
```

**wallpaper-effects:**
```makefile
lint-core:
	@$(UV) run ruff check --line-length 88 $(CORE_DIR) || (echo "..." && exit 1)
	@$(UV) run black --check --line-length 88 $(CORE_DIR) || (echo "..." && exit 1)
	@$(UV) run isort --check --profile black --line-length 88 $(CORE_DIR) || (echo "..." && exit 1)
	@$(UV) run mypy $(CORE_DIR)/src/ || (echo "..." && exit 1)
```

**Differences:**
- wallpaper uses full paths with variables: `$(CORE_DIR)` instead of `cd`
- wallpaper explicitly passes config flags to each tool
- wallpaper has error messages guiding users to `make format-<pkg>`
- wallpaper uses `@` prefix to suppress command echoing

#### Format Commands (example: Core)

**color-scheme:**
```makefile
format-core:
	cd $(CORE_DIR) && $(UV) run black .
	cd $(CORE_DIR) && $(UV) run isort .
	cd $(CORE_DIR) && $(UV) run ruff check --fix .
```

**wallpaper-effects:**
```makefile
format-core:
	$(UV) run isort --profile black --line-length 88 $(CORE_DIR)
	$(UV) run black --line-length 88 $(CORE_DIR)
	$(UV) run ruff check --fix --line-length 88 $(CORE_DIR)
```

**Differences:**
- wallpaper uses full paths again
- wallpaper has explicit config in each command

#### Testing (per-package example: Core)

**color-scheme:**
```makefile
test-core:
	cd $(CORE_DIR) && $(UV) run pytest -n auto --color=yes --cov=src --cov-report=term
	cd $(CORE_DIR) && $(UV) run coverage report --fail-under=95
```

**wallpaper-effects:**
```makefile
test-core:
	cd $(CORE_DIR) && $(UV) run pytest -n auto --color=yes --cov=src --cov-report=term
	cd $(CORE_DIR) && $(UV) run coverage report --fail-under=95
```

✓ **Identical** for testing

#### Pipeline Validation

**color-scheme:**
```makefile
pipeline:
	@echo -e "$(BLUE)Running pipeline validation...$(NC)"
	@cd $(CORE_DIR) && $(UV) run ruff check . && ...
	# Long explicit sequence
```

**wallpaper-effects:**
```makefile
pipeline:
	@echo -e "$(BLUE)Running pipeline validation...$(NC)"
	@$(MAKE) lint
	@$(MAKE) security
	@$(MAKE) test-all
	# Recursive invocation pattern
```

✓ **Better approach:** wallpaper uses `$(MAKE)` recursion (DRY principle)

#### Cleanup

**color-scheme:**
```makefile
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	rm -rf /tmp/color-scheme-test
```

**wallpaper-effects:**
```makefile
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type f -name "bandit-report.json" -delete  # ⬆️ ADDED
```

### Makefile Summary
| Aspect | color-scheme | wallpaper | Better Approach |
|--------|--------------|-----------|-----------------|
| **Command consistency** | Directory-based (cd) | Path-based (variables) | 🔹 wallpaper (cleaner) |
| **Error feedback** | Minimal | Helpful messages | 🔹 wallpaper (better UX) |
| **Pipeline composition** | Explicit steps | Recursive Make | 🔹 wallpaper (DRY) |
| **Format order** | Black → isort → Ruff | isort → Black → Ruff | 🔹 wallpaper (isort first) |
| **Help column width** | 20 chars | 25 chars | Minor difference |

---

## 7. GitHub Actions CI/CD Workflows

### Workflow Files

**color-scheme:**
```
.github/workflows/
├── ci-core.yml              # Only for core package
└── pull_request_template.md # PR template
```

**wallpaper-effects-generator:**
```
.github/workflows/
├── ci-core.yml              # Core package
├── ci-effects.yml           # Effects package (UNIQUE)
├── ci-orchestrator.yml      # Orchestrator package
├── ci-settings.yml          # Settings package
└── no pull_request_template.md
```

### Workflow Triggers

**color-scheme (ci-core.yml):**
```yaml
on:
  push:
    branches: ["**"]
    paths:
      - "packages/core/**"
      - "templates/**"
      - ".github/workflows/ci-core.yml"
  pull_request:
    branches: [develop, main]
    paths:
      - "packages/core/**"
      - "templates/**"
```

**wallpaper-effects (ci-core.yml):**
```yaml
on:
  push:
    branches: ["**"]
    paths:
      - "packages/core/**"
      - ".github/workflows/ci-core.yml"
  pull_request:
    branches: [master, main, develop]
    paths:
      - "packages/core/**"
```

**Differences:**
- color-scheme: `PR branches: [develop, main]`
- wallpaper-effects: `PR branches: [master, main, develop]`

### Jobs Structure (Both Have)

#### Job 1: Lint
```yaml
name: Lint (Core)
runs-on: ubuntu-latest
steps:
  - Checkout
  - Setup Python 3.12
  - Install uv
  - Install dependencies
  - Ruff check
  - Black check
  - isort check
  - mypy type check
```

**Installation difference:**
- color-scheme: `uv sync --dev`
- wallpaper-effects: `uv sync --dev --all-packages`

#### Job 2: Security
```yaml
name: Security Scan (Core)
runs-on: ubuntu-latest
steps:
  - Checkout
  - Setup Python 3.12
  - Install uv
  - Install dependencies
  - Bandit security scan
  - Upload security report as artifact
```

#### Job 3: Test
```yaml
name: Test (Core)
runs-on: ${{ matrix.os }}
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    python-version: ["3.12", "3.13"]
steps:
  - Checkout
  - Setup Python ${{ matrix.python-version }}
  - Install uv
  - Install dependencies
  - Run tests with coverage
  - Check coverage threshold (95%)
  - Upload coverage to Codecov
```

### Workflow Comparison Table

| Aspect | color-scheme | wallpaper-effects | Notes |
|--------|--------------|-------------------|-------|
| **Workflows per package** | 1 (core only) | 4 (all packages) | 🔹 wallpaper more comprehensive |
| **Linting OS** | ubuntu-latest only | ubuntu-latest only | Same |
| **Test OS** | ubuntu, macos | ubuntu, macos | Same |
| **Python versions tested** | 3.12, 3.13 | 3.12, 3.13 | Same |
| **Coverage threshold** | 95% | 95% | Same |
| **Artifact uploads** | bandit-report | bandit-report | Same |
| **Codecov integration** | ✓ Yes | ✓ Yes | Same |
| **PR template** | ✓ Exists | ✗ Missing | 🔹 color-scheme has it |

---

## 8. .gitignore Configuration

### Files Ignored (Comparison)

| Pattern | color-scheme | wallpaper | Status |
|---------|--------------|-----------|--------|
| `__pycache__/` | ✓ | ✓ | Same |
| `*.py[oc]` vs `*.py[cod]` | `[oc]` | `[cod]` | Minor: wallpaper includes bytecode |
| `build/`, `dist/` | ✓ | ✓ | Same |
| `*.egg-info` | ✓ | ✓ | Same |
| `.venv` | ✓ | ✓ | Same |
| `.worktrees/` | ✓ | ✓ | Same (git worktrees support) |
| `.vscode/`, `.idea/` | ✓ | ✓ | Same |
| `.coverage` | ✓ | ✓ | Same |
| `htmlcov/` | ✓ | ✓ | Same |
| `.pytest_cache/` | ✓ | ✓ | Same |
| `.mypy_cache/` | ✓ | ✓ | Same |
| `.ruff_cache/` | ✓ | ✗ | color-scheme includes it |
| `.archive/` | ✓ | ✗ | color-scheme specific |
| `.DS_Store` | ✓ | ✓ | macOS files |

### .gitignore Differences

**color-scheme:**
- More minimal (32 lines)
- Includes `.ruff_cache/` (project-specific)
- Includes `.archive/` (project-specific)
- Uses `*.py[oc]` (older style)

**wallpaper-effects:**
- More comprehensive (79 lines)
- Includes C extensions (`.so`)
- Includes PyInstaller files
- Includes pip logs and install markers
- Includes many more edge cases
- More professional/template-based style

**Better approach:** 🔹 wallpaper-effects is more thorough

---

## 9. Development Documentation

### Documentation Files

**color-scheme:**
- `docs/` folder with:
  - `explanations/`
  - `how-to/`
  - `reference/`
  - `tutorials/`
  - `README.md`
- No standalone `DEVELOPMENT.md`

**wallpaper-effects-generator:**
- `docs/` folder with:
  - `plans/`
  - `investigation-findings.md`
  - `investigation-parameter-types-bug.md`
  - `README.md`
- **`DEVELOPMENT.md`** in root (standalone)

**Key Difference:** 🔹 wallpaper-effects has a dedicated `DEVELOPMENT.md` guide with:
- Quick start instructions
- Common workflow examples
- Error message explanations
- Pre-commit hooks usage
- Clear table of solutions

---

## 10. Pull Request Management

### color-scheme
- Has `.github/pull_request_template.md` (4,122 bytes)

### wallpaper-effects-generator
- No pull request template

**Better approach:** 🔹 color-scheme (enforces consistent PR descriptions)

---

## 11. Testing Configuration

### Test Setup (Both Identical)

**Test Command:**
```bash
pytest -n auto --color=yes --cov=src --cov-report=term
coverage report --fail-under=95
```

### pytest Features (Both)
- Parallel execution: `-n auto` (pytest-xdist)
- Coverage reporting: `--cov=src`
- Colored output: `--color=yes`
- **Coverage threshold:** 95% minimum

### Package-Specific Testing

**color-scheme:**
- All packages require 95% coverage

**wallpaper-effects:**
- wallpaper-settings: `pytest.ini_options` in pyproject.toml
- wallpaper-effects: `pytest.ini_options` in pyproject.toml
- Other packages: No explicit config

---

## 12. Coverage Requirements

### Enforcement

**Both projects:**
- Use `coverage report --fail-under=95`
- Codecov integration for GitHub Actions
- Fail CI if coverage drops below threshold

### Package-Level Requirements

| Package | color-scheme | wallpaper-effects |
|---------|--------------|-------------------|
| **settings** | 95% | 95% |
| **core** | 95% | 95% |
| **effects/templates** | 95% | 95% (effects) |
| **orchestrator** | CI check only | CI check only |

---

## 13. Security Scanning

### Tool: Bandit
Both use identical security scanning setup:

```bash
bandit -r src/ -f json -o bandit-report.json
```

### Pre-commit Configuration
```yaml
stages: [pre-commit]
args: [-ll]  # Low level only (no informational)
exclude: ^(packages|src)/.*/tests/|test_.*\.py$
files: ^(packages|src)/.*\.py$
```

### GitHub Actions
Both upload bandit reports as artifacts for review.

---

## 14. Type Checking (mypy)

### Configuration

**color-scheme:**
```yaml
ignore_missing_imports = true
args: [--ignore-missing-imports]
additional_dependencies: [types-pillow]
```

**wallpaper-effects:**
```toml
[tool.mypy]
ignore_missing_imports = true
disable_error_code = ["import-untyped"]
```

**Pre-commit configuration:**
```yaml
args: [--ignore-missing-imports, --disable-error-code=import-untyped]
additional_dependencies: [types-PyYAML]
```

### Differences
- wallpaper-effects is stricter: disables `import-untyped` errors
- wallpaper-effects includes PyYAML type stubs (uses YAML)
- color-scheme includes Pillow type stubs (uses image processing)

---

## 15. Virtual Environment & Cache Management

### Virtual Environment Setup
Both use:
- `.venv` directory (ignored in .gitignore)
- `uv` for virtual environment management
- Python 3.12 as primary version

### Cache Directories
All cached/generated files excluded from git:
```
.pytest_cache/
.mypy_cache/
.ruff_cache/     (color-scheme only)
htmlcov/
.coverage
```

---

## 16. Development Tools Directory

### color-scheme/tools/dev/
```
test-all-commands.sh (42 KB)
```
- Comprehensive integration test script
- Tests all CLI commands with a wallpaper file

### wallpaper-effects-generator/tools/dev/
```
test-all-commands.sh         (92 KB)
test-all-commands.sh.backup  (90 KB)
```
- Larger test script
- Has backup version (possibly under development)

### Purpose
Both include comprehensive testing scripts for end-to-end validation.

---

## 17. uv.lock & Dependency Locking

Both projects use:
- `uv.lock` file (tracked in git)
- Deterministic dependency resolution
- Workspace-level locking

---

## 18. Summary of Key Findings

### Similarities (99% overlap)
✓ Same development tools (Black, isort, Ruff, mypy, Bandit, pytest)
✓ Same Python version (3.12+)
✓ Same monorepo structure with 4 packages
✓ Same package manager (uv with workspaces)
✓ Same Makefile organization and targets
✓ Same pre-commit hooks configuration
✓ Same GitHub Actions pattern
✓ Same testing framework (pytest) and coverage (95%)
✓ Same security scanning (Bandit)
✓ Both support git worktrees

### Meaningful Differences

| Area | color-scheme | wallpaper-effects | Impact |
|------|--------------|-------------------|--------|
| **Tool versions** | Older (Black v24, Ruff v0.6) | Newer (Black v26, Ruff v0.14) | 🔴 High - upgrade needed |
| **GitHub Actions coverage** | Core package only | All 4 packages | 🟡 Medium - wallpaper better |
| **Makefile approach** | cd-based | path-variable based | 🟢 Low - style preference |
| **Documentation** | Structured docs/ | docs/ + DEVELOPMENT.md | 🟡 Medium - wallpaper more accessible |
| **Error messages** | Minimal | Helpful guidance | 🟡 Medium - UX difference |
| **.gitignore** | Minimal | Comprehensive | 🟡 Medium - wallpaper safer |
| **PR template** | ✓ Yes | ✗ No | 🟡 Medium - consistency |
| **Pipeline composition** | Explicit | Recursive (DRY) | 🟢 Low - code organization |

---

## 19. Recommendations for color-scheme

### Priority 1: Critical Updates
1. **Upgrade tool versions** to match wallpaper-effects:
   - Black: 24.x → 26.x
   - Ruff: 0.6.x → 0.14.x
   - mypy: 1.11.x → 1.19.x+
   - pytest: 8.4.x → 9.x
   - pytest-cov: 4.1.x → 7.x

2. **Add CI workflows** for all packages (not just core)

### Priority 2: Quality Improvements
1. **Add DEVELOPMENT.md** with quick-start guide
2. **Update Makefile** to use path variables instead of `cd`
3. **Add helpful error messages** in Makefile linting targets
4. **Improve .gitignore** with more comprehensive patterns

### Priority 3: Optional Enhancements
1. **Use recursive `$(MAKE)`** in pipeline target for DRY principle
2. **Centralize tool configuration** in root pyproject.toml
3. **Add Ruff config** to root pyproject.toml
4. **Update PR template** reference in workflows

---

## 20. Complete File-by-File Checklist

| File | color-scheme | wallpaper | Notes |
|------|--------------|-----------|-------|
| `pyproject.toml` (root) | ✓ | ✓ | Identical pattern; wallpaper has tool config |
| `Makefile` | ✓ | ✓ | Same structure; wallpaper has better UX |
| `.pre-commit-config.yaml` | ✓ | ✓ | 99% identical; mypy deps differ |
| `.gitignore` | ✓ | ✓ | wallpaper more comprehensive |
| `.github/workflows/ci-*.yml` | 1 file | 4 files | wallpaper covers all packages |
| `.github/pull_request_template.md` | ✓ | ✗ | color-scheme has this |
| `DEVELOPMENT.md` | ✗ | ✓ | wallpaper has this |
| `uv.lock` | ✓ | ✓ | Both use dependency locking |
| `tools/dev/test-all-commands.sh` | ✓ | ✓ | Both have integration tests |

---

## Conclusion

Both projects implement nearly identical development setups, suggesting they follow the same design philosophy (likely created by the same author/team). The **wallpaper-effects-generator project is slightly more mature and refined**, with better documentation, more comprehensive CI/CD coverage, and newer tool versions.

The **color-scheme project can benefit from adopting several patterns from wallpaper-effects-generator**, particularly:
1. Updating dependencies to current versions
2. Expanding CI/CD to cover all packages
3. Adding a standalone DEVELOPMENT.md guide
4. Improving Makefile patterns for better UX

All changes would maintain backward compatibility while improving developer experience and maintainability.

---

**Document Generated:** 2026-02-11
**Comparison Scope:** Development infrastructure only
**Analysis Depth:** Comprehensive (18 configuration areas analyzed)
