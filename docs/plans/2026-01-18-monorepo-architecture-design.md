# Color Scheme Generator - Monorepo Architecture Design

**Date**: 2026-01-18
**Status**: Approved
**Author**: Design Session

## Overview

This document outlines the complete architecture, development workflow, and implementation strategy for the color-scheme project - a CLI tool for extracting and generating color schemes from images with support for multiple backends and containerized execution.

## Table of Contents

1. [High-Level Architecture](#1-high-level-architecture)
2. [Container Architecture](#2-container-architecture)
3. [CLI Design and Command Delegation](#3-cli-design-and-command-delegation)
4. [Configuration and Settings Management](#4-configuration-and-settings-management)
5. [Testing Strategy and Documentation Pipeline](#5-testing-strategy-and-documentation-pipeline)
6. [Git Workflow and Branching Strategy](#6-git-workflow-and-branching-strategy)
7. [CI/CD Pipeline Design](#7-cicd-pipeline-design)
8. [Versioning and Release Process](#8-versioning-and-release-process)
9. [Development Environment Setup](#9-development-environment-setup)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. High-Level Architecture

### Package Structure

The project uses a **monorepo with two independent packages** that work together but can be installed separately:

```
color-scheme/
├── packages/
│   ├── core/                          # Standalone color scheme generator
│   │   ├── src/color_scheme/
│   │   │   ├── cli/                   # Core CLI (generate, show)
│   │   │   ├── backends/              # pywal, wallust, custom
│   │   │   ├── core/                  # ColorScheme types, managers
│   │   │   └── config/                # Settings loading
│   │   ├── pyproject.toml             # Core dependencies
│   │   └── tests/
│   │
│   └── orchestrator/                  # Container orchestration layer
│       ├── src/color_scheme_orchestrator/
│       │   ├── cli/                   # Orchestrator CLI (wraps core)
│       │   ├── container/             # Container management logic
│       │   └── config/                # Container-specific config
│       ├── pyproject.toml             # Depends on: color-scheme-core, container-manager
│       └── tests/
│
├── templates/                         # Jinja2 templates (mounted, not baked)
├── docs/
│   └── plans/                         # Design documents
└── .github/workflows/                 # CI/CD pipelines
```

### Key Principles

**Single Responsibility**: Core handles color extraction and output generation. Orchestrator handles container lifecycle and delegates to core.

**Reusability**: Both packages expose identical `color-scheme` CLI. User chooses which to install based on their needs (host dependencies vs containers).

**Clean Dependencies**: Orchestrator → Core (one-way dependency). Core has zero knowledge of containers.

---

## 2. Container Architecture

### Image Hierarchy

```
color-scheme-base:latest
├── Python 3.12+
├── color-scheme-core package
├── Common system dependencies
└── Template directory structure

    ↓ (extends base)

color-scheme-pywal:latest
├── FROM color-scheme-base
├── pywal + Python dependencies
└── Backend-specific tools (imagemagick, etc.)

color-scheme-wallust:latest
├── FROM color-scheme-base
├── wallust binary
└── Rust runtime dependencies

color-scheme-custom:latest
├── FROM color-scheme-base
├── PIL/Pillow
└── scikit-learn (for k-means)
```

### Volume Mounts Strategy

When orchestrator runs `generate`:

1. **Image file**: Read-only mount of the source image
2. **Output directory**: Read-write mount to host's output directory
3. **Templates directory**: Read-only mount from host (allows user customization without rebuild)
4. **Settings file**: Read-only mount of `settings.toml` from host

### Container Execution Flow

```
User: color-scheme generate wallpaper.png --backend pywal

Orchestrator:
1. Checks if pywal image exists locally (via container-manager)
2. If missing: prompt user to run `color-scheme install pywal`
3. Constructs volume mounts (image, output, templates, settings)
4. Runs: docker run --rm \
        -v /path/to/wallpaper.png:/input/image.png:ro \
        -v ~/.config/color-scheme/output:/output:rw \
        -v ./templates:/templates:ro \
        -v ./settings.toml:/config/settings.toml:ro \
        color-scheme-pywal:latest \
        color-scheme generate /input/image.png <all-cli-args>
5. Container writes output files directly to mounted /output
6. Container exits, orchestrator returns
```

---

## 3. CLI Design and Command Delegation

### Core CLI (`color-scheme-core` package)

**Commands**:
- `generate <image>` - Extract colors and generate output files
- `show [--file | --last]` - Display color schemes

**Execution**: Runs directly on host. User must have backend dependencies installed (pywal, wallust, etc.).

**Entry Point**: `pyproject.toml` → `color-scheme = "color_scheme.cli.main:app"`

### Orchestrator CLI (`color-scheme-orchestrator` package)

**Commands**:
- `generate <image>` - Runs core's generate inside container
- `show [--file | --last]` - Delegates directly to core (no container)
- `install [backend...]` - Pull/build container images
- `uninstall [backend...]` - Remove container images
- `list-images` - Show available backend images (local + remote)

**Entry Point**: Same name! `pyproject.toml` → `color-scheme = "color_scheme_orchestrator.cli.main:app"`

### Delegation Strategy

**For `show` command** (no backend needed):
```python
# orchestrator/cli/commands/show.py
from color_scheme.cli.commands.show import show as core_show

@app.command()
def show(...):
    """Display color scheme - delegates to core."""
    core_show(file=file, last=last, verbose=verbose)
```

**For `generate` command** (needs backend):
```python
# orchestrator/cli/commands/generate.py
from color_scheme_orchestrator.container import ContainerRunner

@app.command()
def generate(image, backend, ...):
    """Generate color scheme - runs in container."""
    runner = ContainerRunner(settings)
    runner.execute_generate(
        image=image,
        backend=backend,
        cli_args=construct_cli_args(...)
    )
```

The orchestrator executes `color-scheme generate ...` as a subprocess inside the container via Docker/Podman.

---

## 4. Configuration and Settings Management

### Settings File Location

**Core Package**:
- Default: `~/.config/color-scheme/settings.toml` (or `./settings.toml` in dev)
- Can be overridden via environment variable: `COLOR_SCHEME_CONFIG`

**Orchestrator Package**:
- Uses same settings file as core (reuses core's settings system)
- Adds container-specific settings in same file

### Settings Structure

```toml
# settings.toml (shared by both packages)

[logging]
level = "INFO"
show_time = true
show_path = false

[container]
engine = "docker"  # docker | podman
auto_pull = true   # Auto-pull missing images
image_registry = "ghcr.io/your-org"

[output]
directory = "$HOME/.config/color-scheme/output"
formats = ["json", "sh", "css", "gtk.css", "yaml", "sequences", "rasi", "scss"]

[templates]
directory = "./templates"

[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

[backends.pywal]
backend_algorithm = "haishoku"

[backends.wallust]
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16
```

### Override Hierarchy

1. **CLI arguments** (highest priority)
2. **Environment variables**
3. **settings.toml** file
4. **Hardcoded defaults** (lowest priority)

### Implementation Pattern

Both packages use:
- `dynaconf` loads TOML → resolves env vars → converts to dict
- Pydantic models validate the structure
- CLI uses Typer options to collect overrides
- Overrides are applied to settings object before creating generators

---

## 5. Testing Strategy and Documentation Pipeline

### Test Organization

```
packages/core/tests/
├── unit/
│   ├── test_backends.py
│   ├── test_output_manager.py
│   ├── test_config.py
│   └── test_types.py
├── integration/
│   ├── test_cli.py
│   └── test_generation_flow.py
└── fixtures/
    ├── test_images/
    └── expected_outputs/

packages/orchestrator/tests/
├── unit/
│   ├── test_container_runner.py
│   └── test_image_manager.py
├── integration/
│   ├── test_cli_delegation.py
│   └── test_containerized_generate.py
└── fixtures/
```

### Coverage Requirements

- **Minimum**: 95% code coverage for both packages
- Exclusions: Only truly untestable code (explicit `# pragma: no cover`)

### CI/CD Test Gates

**On every PR**:
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Code coverage ≥ 95%
- ✅ Linting passes (ruff, black, isort)
- ✅ Type checking passes (mypy)
- ✅ Security scan passes (bandit)

### Extended Documentation Structure

```
docs/
├── user-guide/
│   ├── cli-reference.md
│   ├── backends.md
│   ├── configuration.md
│   ├── installation.md
│   └── containerization.md
│
├── development/
│   ├── setup.md
│   ├── contributing.md
│   ├── testing-patterns.md
│   ├── release-process.md
│   └── recipes/
│       ├── adding-backend.md
│       └── adding-format.md
│
├── troubleshooting/
│   ├── error-database.md        # Known errors and solutions
│   ├── common-issues.md
│   └── container-issues.md
│
├── knowledge-base/
│   ├── adrs/                    # Architecture Decision Records
│   ├── performance/
│   │   ├── benchmarks.md
│   │   └── optimization-notes.md
│   ├── dependency-notes.md
│   └── limitations.md
│
└── plans/
```

### Error Database Format

Each error entry includes:
- **Error**: Exact error message
- **Context**: When/where it occurred
- **Root Cause**: Why it happened
- **Solution**: How it was fixed
- **Prevention**: How to avoid in future
- **Related**: Links to PRs, issues, commits

### Documentation Gate Rules

PR checks fail if:
- Code coverage < 95%
- New public API without docstrings
- CLI command added/changed without updating docs
- Backend added/modified without updating docs
- settings.toml changed without updating configuration docs
- No CHANGELOG.md entry for user-facing changes
- Broken links in documentation

---

## 6. Git Workflow and Branching Strategy

### Branch Structure

```
main                    # Production-ready, tagged releases only
├── develop            # Integration branch for next release
│   ├── feature/*      # New features
│   ├── bugfix/*       # Bug fixes
│   ├── docs/*         # Documentation updates
│   └── refactor/*     # Code improvements
│
└── hotfix/*           # Emergency production fixes (branch from main)
```

### Branch Naming Convention

```
feature/<package>/<short-description>
  └─ feature/core/add-haishoku-backend
  └─ feature/orchestrator/add-list-images-command

bugfix/<issue-number>-<short-description>
  └─ bugfix/123-pywal-imagemagick-policy

docs/<area>-<description>
  └─ docs/api-docstrings-cleanup

refactor/<area>-<description>
  └─ refactor/core-settings-consolidation

hotfix/<version>-<critical-issue>
  └─ hotfix/1.2.1-security-vulnerability
```

### Workflow Rules (Solo Developer with PRs)

**Feature Development**:
1. Create branch from `develop`
2. Make commits with conventional commit format
3. Push branch to remote
4. Create PR from feature branch → `develop`
5. CI runs automatically on PR
6. Self-review in PR interface
7. Merge when ready (no approval required)

### Commit Message Convention

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `ci`

**Example**:
```
feat(core): add haishoku backend support

Implement haishoku color extraction algorithm as alternative to
pywal's default 'wal' backend. Haishoku doesn't require ImageMagick,
avoiding policy issues on Ubuntu systems.

Closes #38
```

### Protected Branch Rules

**`main` branch**:
- ❌ No direct commits
- ✅ Requires PR
- ✅ CI must pass
- ❌ No approval required (solo dev)
- ✅ Enforce linear history (squash merge)

**`develop` branch**:
- ❌ No direct commits
- ✅ Requires PR
- ✅ CI must pass
- ❌ No approval required (solo dev)

### PR Template

Located at `.github/pull_request_template.md` with self-review checklist covering:
- Code quality
- Testing (coverage ≥ 95%)
- Documentation updates
- Quality gates (linting, type checking, security)
- Manual testing

---

## 7. CI/CD Pipeline Design

### Pipeline Structure

```
.github/workflows/
├── ci-core.yml              # Core package testing
├── ci-orchestrator.yml      # Orchestrator package testing
├── docs-check.yml           # Documentation validation
├── security-scan.yml        # Security scanning
├── release-core.yml         # Core package release
├── release-orchestrator.yml # Orchestrator release
└── container-build.yml      # Container image building
```

### Core Package CI Pipeline

**Triggers**:
- Push to any branch
- PR to `develop` or `main`
- Paths: `packages/core/**`, `templates/**`

**Jobs**:
1. **lint**: Ruff, Black, isort, mypy
2. **security**: Bandit scan
3. **test**: Matrix (Ubuntu/macOS, Python 3.12/3.13), coverage ≥ 95%
4. **test-integration**: Full CLI flow with real backends

### Orchestrator Package CI Pipeline

Same structure as core, plus:
- **test-with-containers**: Build test images, run containerized tests

### Documentation Check Pipeline

**On every PR**:
1. Detect changed files
2. Check documentation requirements (mapping changes to required docs)
3. Verify CHANGELOG.md entry
4. Check for broken links
5. Build docs (test)

### Container Build Pipeline

**Triggers**:
- PR to `develop`/`main` (build only)
- Push to `main` (build and push)
- Tags matching `v*.*.*`

**Strategy**:
1. Build base image
2. Build backend images in parallel (matrix: pywal, wallust, custom)
3. Push to GitHub Container Registry (ghcr.io)
4. Tag with version and `latest`

### Required Status Checks

**For PRs to `develop`**:
- Core: lint, security, test
- Orchestrator: lint, test (if changed)
- Documentation check
- Container build (if Dockerfiles changed)

---

## 8. Versioning and Release Process

### Versioning Strategy

**Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

### Independent Package Versioning

Core and orchestrator have **independent version numbers**:

```
color-scheme-core: v1.5.0
color-scheme-orchestrator: v1.2.0
```

Compatibility matrix documented in README.

### Version Storage

Single source of truth per package:

```python
# packages/core/src/color_scheme/__init__.py
__version__ = "1.5.0"

# packages/orchestrator/src/color_scheme_orchestrator/__init__.py
__version__ = "1.2.0"
```

### Release Process

1. **Prepare Release Branch**
   ```bash
   git checkout -b release/core-v1.5.0 develop
   ```

2. **Update Version and Changelog**
   - Update `__version__` in `__init__.py`
   - Move CHANGELOG entries from "Unreleased" to version section
   - Update compatibility matrix

3. **Create Release PR**
   - PR: `release/core-v1.5.0` → `main`
   - Complete release checklist

4. **Merge and Tag**
   ```bash
   git tag -a v1.5.0 -m "Release version 1.5.0"
   git push origin v1.5.0
   ```

5. **Automated Release Pipeline**
   - Triggered by tag push
   - Verifies version matches code
   - Builds package
   - Publishes to PyPI
   - Creates GitHub Release

6. **Post-Release**
   ```bash
   git checkout develop
   git merge main
   # Bump to next dev version
   __version__ = "1.6.0-dev"
   ```

### CHANGELOG.md Format

Following [Keep a Changelog](https://keepachangelog.com/) format with sections:
- Added
- Changed
- Fixed
- Security

### Pre-commit Hooks

Configured via `.pre-commit-config.yaml`:
- Ruff (lint + format)
- isort
- Trailing whitespace, EOF fixer
- YAML check, large files check
- Bandit security scan
- pytest check

---

## 9. Development Environment Setup

### Initial Setup Script

`scripts/dev-setup.sh` automates:
1. Check prerequisites (Python 3.12+, git, docker)
2. Install uv package manager
3. Setup core and orchestrator packages
4. Install pre-commit hooks
5. Create necessary directories
6. Copy settings template
7. Run initial tests

### Project Root Structure

```
color-scheme/
├── .github/                    # CI/CD and automation
├── packages/
│   ├── core/
│   │   ├── src/color_scheme/
│   │   │   ├── cli/
│   │   │   ├── backends/
│   │   │   ├── core/
│   │   │   ├── config/
│   │   │   └── factory.py
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── orchestrator/
│       ├── src/color_scheme_orchestrator/
│       │   ├── cli/
│       │   ├── container/
│       │   └── config/
│       ├── dockerfiles/
│       ├── tests/
│       └── pyproject.toml
├── templates/                  # Jinja2 templates
├── docs/                       # Documentation
├── scripts/                    # Helper scripts
│   ├── dev-setup.sh
│   ├── run-all-tests.sh
│   └── build-containers.sh
├── .pre-commit-config.yaml
├── settings.toml.example
├── settings.toml               # Gitignored
├── CHANGELOG.md
└── README.md
```

### Development Tools Configuration

Root `pyproject.toml` contains shared tooling config:
- Ruff (linting, formatting)
- Black (code formatting)
- isort (import sorting)
- mypy (type checking)
- pytest (testing)
- coverage (code coverage)

### Helper Scripts

- `scripts/run-all-tests.sh`: Run tests for both packages
- `scripts/build-containers.sh`: Build all container images locally

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal**: Establish monorepo structure, CI/CD, and core package skeleton

**Deliverable**: Empty but fully functional monorepo with CI/CD

**Success Criteria**:
- ✓ CI pipeline runs successfully
- ✓ Pre-commit hooks work
- ✓ Can install core package locally
- ✓ Settings load correctly

### Phase 2: Core Package - Backends (Week 3-4)

**Goal**: Implement all three color extraction backends with full test coverage

**Tasks**:
1. Port core types and base classes
2. Implement backends (custom → pywal → wallust)
3. Implement factory pattern
4. Create test fixtures

**Deliverable**: Working backends with comprehensive tests

**Success Criteria**:
- ✓ All backends pass tests
- ✓ Code coverage ≥ 95%
- ✓ Factory auto-detection works

### Phase 3: Core Package - Output Generation (Week 5)

**Goal**: Template rendering and output file generation

**Tasks**:
1. Port OutputManager
2. Port/create templates (8 formats)
3. Implement CLI commands (generate, show)

**Deliverable**: Complete core package with CLI

**Success Criteria**:
- ✓ All output formats render correctly
- ✓ CLI commands work end-to-end
- ✓ User-friendly error messages

### Phase 4: Core Package Release (Week 6)

**Goal**: First production release of core package

**Tasks**:
1. Final testing and bug fixes
2. Documentation polish
3. Release preparation (v1.0.0)
4. Publish to PyPI

**Deliverable**: `color-scheme-core==1.0.0` on PyPI

### Phase 5: Orchestrator - Container Foundation (Week 7-8)

**Goal**: Container management infrastructure

**Tasks**:
1. Create Dockerfiles (base + backends)
2. Implement container management
3. Setup container build pipeline

**Deliverable**: Working container images

**Success Criteria**:
- ✓ All backend images build successfully
- ✓ Images pushed to registry
- ✓ Volume mounts work correctly

### Phase 6: Orchestrator - CLI Integration (Week 9)

**Goal**: Orchestrator CLI that delegates to core

**Tasks**:
1. Implement CLI commands (all 5 commands)
2. Implement ContainerRunner
3. End-to-end testing

**Deliverable**: Complete orchestrator package

**Success Criteria**:
- ✓ All commands work end-to-end
- ✓ Delegation to core works
- ✓ Container execution reliable

### Phase 7: Orchestrator Release (Week 10)

**Goal**: First production release of orchestrator

**Tasks**:
1. Final integration testing
2. Documentation updates
3. Release v1.0.0
4. Publish to PyPI

**Deliverable**: `color-scheme-orchestrator==1.0.0` on PyPI

### Post-Release: Continuous Improvement

**Ongoing**:
- Monitor and respond to issues
- Performance optimization
- Feature additions
- Dependency updates

---

## Key Design Principles

1. **Test-First Development**: Write tests before/alongside implementation, maintain 95%+ coverage
2. **Documentation as Code**: Update docs with every change, ADRs for decisions, error database for bugs
3. **Small, Focused PRs**: One feature/fix per PR, easy to review
4. **Fail Fast, Fail Loud**: Validate early, clear error messages
5. **Separation of Concerns**: Core knows nothing about containers
6. **Backward Compatibility**: Semantic versioning, deprecation warnings, migration guides

---

## Success Metrics

**Technical**:
- Code coverage: ≥95%
- CI pipeline: <5 minutes
- Test suite: <2 minutes
- Container overhead: <1 second
- Zero critical vulnerabilities

**Process**:
- Every PR has tests
- Every PR updates docs
- CHANGELOG always current
- All releases follow process

**Quality**:
- Bug rate decreases over time
- Error database grows
- Performance stable/improving
- User issues have solutions in docs
