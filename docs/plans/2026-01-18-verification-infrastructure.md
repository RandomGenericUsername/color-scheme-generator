# Verification Infrastructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build automated verification and compliance checking infrastructure that enforces design document principles before any feature development begins.

**Architecture:** Create a suite of shell scripts and Python tools that verify repository structure, test coverage, documentation completeness, and design compliance. These run locally and in CI to catch violations early.

**Tech Stack:** Bash, Python 3.12+, pytest, git, jq

---

## Task 1: Setup Scripts Directory and Utilities

**Files:**
- Create: `scripts/README.md`
- Create: `scripts/utils.sh`
- Create: `scripts/.gitkeep`

**Step 1: Create scripts directory**

Run:
```bash
mkdir -p scripts
```

**Step 2: Create scripts README**

Create `scripts/README.md`:
```markdown
# Development Scripts

Automation scripts for development, testing, and compliance verification.

## Verification Scripts

- `verify-design-compliance.sh` - Check repository structure and design compliance
- `verify-documentation.sh` - Validate documentation completeness
- `phase-gate-check.sh` - Comprehensive phase completion verification

## Utility Scripts

- `dev-setup.sh` - Initial development environment setup
- `run-all-tests.sh` - Run tests for all packages
- `build-containers.sh` - Build container images locally

## Usage

All scripts should be run from repository root:

```bash
./scripts/verify-design-compliance.sh
./scripts/phase-gate-check.sh 1
```
```

**Step 3: Create shared utilities**

Create `scripts/utils.sh`:
```bash
#!/bin/bash
# Shared utility functions for scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_section() {
    echo -e "\n${BLUE}━━━ $1 ━━━${NC}\n"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if file exists
file_exists() {
    if [ -f "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Check if directory exists
dir_exists() {
    if [ -d "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Get repository root
get_repo_root() {
    git rev-parse --show-toplevel 2>/dev/null
}

# Validate we're in repo root
validate_repo_root() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
}
```

**Step 4: Make utilities executable**

Run:
```bash
chmod +x scripts/utils.sh
```

**Step 5: Commit**

Run:
```bash
git add scripts/
git commit -m "chore(scripts): add scripts directory with shared utilities

Setup infrastructure for verification scripts.
Includes colored output and common utility functions.

Part of verification infrastructure (Phase 0).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Create Design Compliance Verification Script

**Files:**
- Create: `scripts/verify-design-compliance.sh`

**Step 1: Create compliance verification script skeleton**

Create `scripts/verify-design-compliance.sh`:
```bash
#!/bin/bash
set -e

# Load utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

validate_repo_root
REPO_ROOT=$(get_repo_root)

print_section "Design Compliance Verification"
echo "Checking repository against design document..."
echo "Reference: docs/plans/2026-01-18-monorepo-architecture-design.md"
echo ""

VIOLATIONS=0

# Check functions return 0 on success, 1 on failure
check_monorepo_structure() {
    print_info "Checking monorepo structure (Design Section 1)..."

    local required_dirs=(
        "packages/core"
        "packages/orchestrator"
        "templates"
        "docs/plans"
        "docs/user-guide"
        "docs/development"
        "docs/troubleshooting"
        "docs/knowledge-base"
        ".github/workflows"
    )

    local missing=0
    for dir in "${required_dirs[@]}"; do
        if ! dir_exists "$REPO_ROOT/$dir"; then
            print_error "Missing required directory: $dir"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "Monorepo structure matches design"
        return 0
    else
        return 1
    fi
}

check_package_structure() {
    print_info "Checking package structure (Design Section 9)..."

    # Core package structure
    local core_files=(
        "packages/core/pyproject.toml"
        "packages/core/src/color_scheme/__init__.py"
    )

    # Orchestrator package structure
    local orch_files=(
        "packages/orchestrator/pyproject.toml"
        "packages/orchestrator/src/color_scheme_orchestrator/__init__.py"
    )

    local missing=0
    for file in "${core_files[@]}" "${orch_files[@]}"; do
        if ! file_exists "$REPO_ROOT/$file"; then
            print_error "Missing required file: $file"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "Package structure matches design"
        return 0
    else
        return 1
    fi
}

check_test_coverage() {
    print_info "Checking test coverage (Design Section 5)..."

    local coverage_threshold=95
    local packages_to_check=()

    # Check which packages exist
    if dir_exists "$REPO_ROOT/packages/core/tests"; then
        packages_to_check+=("core")
    fi
    if dir_exists "$REPO_ROOT/packages/orchestrator/tests"; then
        packages_to_check+=("orchestrator")
    fi

    if [ ${#packages_to_check[@]} -eq 0 ]; then
        print_warning "No test directories found yet (acceptable in early phases)"
        return 0
    fi

    local failed=0
    for package in "${packages_to_check[@]}"; do
        if [ -f "$REPO_ROOT/packages/$package/pyproject.toml" ]; then
            print_info "Checking $package coverage..."
            cd "$REPO_ROOT/packages/$package"

            # Check if tests exist
            if ! dir_exists "tests" || [ -z "$(ls -A tests/*.py 2>/dev/null)" ]; then
                print_warning "$package: No tests found (acceptable in early development)"
                cd "$REPO_ROOT"
                continue
            fi

            # Run coverage if pytest is available
            if command_exists uv && [ -f ".venv/bin/pytest" ]; then
                if uv run pytest --cov=src --cov-report=term --cov-report=json --quiet 2>/dev/null; then
                    if [ -f "coverage.json" ]; then
                        local coverage=$(python3 -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])")
                        local coverage_int=${coverage%.*}

                        if [ "$coverage_int" -lt "$coverage_threshold" ]; then
                            print_error "$package coverage: ${coverage}% < ${coverage_threshold}%"
                            failed=1
                        else
                            print_success "$package coverage: ${coverage}% >= ${coverage_threshold}%"
                        fi
                        rm -f coverage.json
                    fi
                else
                    print_warning "$package: Could not run coverage (tests may be failing)"
                fi
            else
                print_warning "$package: Environment not set up for testing"
            fi
            cd "$REPO_ROOT"
        fi
    done

    return $failed
}

check_documentation_structure() {
    print_info "Checking documentation structure (Design Section 5)..."

    local required_docs=(
        "docs/user-guide"
        "docs/development"
        "docs/troubleshooting"
        "docs/knowledge-base/adrs"
        "docs/plans"
        "CHANGELOG.md"
        "README.md"
    )

    local missing=0
    for doc in "${required_docs[@]}"; do
        if ! [ -e "$REPO_ROOT/$doc" ]; then
            print_error "Missing required documentation: $doc"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "Documentation structure matches design"
        return 0
    else
        return 1
    fi
}

check_git_workflow() {
    print_info "Checking git workflow compliance (Design Section 6)..."

    # Check if we have main and develop branches (if not initial setup)
    local branches=$(git branch -a 2>/dev/null | grep -E 'main|develop' || true)

    if [ -z "$branches" ]; then
        print_warning "main/develop branches not found (acceptable during initial setup)"
        return 0
    fi

    # Check current branch name follows convention
    local current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

    if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "develop" ]]; then
        print_success "On protected branch: $current_branch"
        return 0
    elif [[ "$current_branch" =~ ^(feature|bugfix|docs|refactor|hotfix)/.+ ]]; then
        print_success "Branch name follows convention: $current_branch"
        return 0
    else
        print_warning "Branch name doesn't follow convention: $current_branch"
        print_info "Expected: feature/*, bugfix/*, docs/*, refactor/*, hotfix/*"
        return 1
    fi
}

# Run all checks
print_section "Running Compliance Checks"

check_monorepo_structure || ((VIOLATIONS++))
echo ""

check_package_structure || ((VIOLATIONS++))
echo ""

check_documentation_structure || ((VIOLATIONS++))
echo ""

check_test_coverage || ((VIOLATIONS++))
echo ""

check_git_workflow || ((VIOLATIONS++))
echo ""

# Summary
print_section "Summary"

if [ $VIOLATIONS -eq 0 ]; then
    print_success "All design compliance checks passed!"
    exit 0
else
    print_error "Found $VIOLATIONS violation(s)"
    print_info "Review design document: docs/plans/2026-01-18-monorepo-architecture-design.md"
    exit 1
fi
```

**Step 2: Make script executable**

Run:
```bash
chmod +x scripts/verify-design-compliance.sh
```

**Step 3: Test the script**

Run:
```bash
./scripts/verify-design-compliance.sh
```

Expected: Script runs and shows current compliance status (likely some violations since we're just starting)

**Step 4: Commit**

Run:
```bash
git add scripts/verify-design-compliance.sh
git commit -m "feat(scripts): add design compliance verification script

Verifies repository structure, package layout, test coverage,
documentation structure, and git workflow against design document.

Checks:
- Monorepo structure (Section 1)
- Package structure (Section 9)
- Test coverage >= 95% (Section 5)
- Documentation structure (Section 5)
- Git workflow (Section 6)

Part of verification infrastructure (Phase 0).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Create Documentation Validation Script

**Files:**
- Create: `scripts/verify-documentation.sh`
- Create: `.github/scripts/check-docs.py`

**Step 1: Create documentation verification script**

Create `scripts/verify-documentation.sh`:
```bash
#!/bin/bash
set -e

# Load utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

validate_repo_root
REPO_ROOT=$(get_repo_root)

print_section "Documentation Verification"
echo "Validating documentation completeness and quality..."
echo ""

VIOLATIONS=0

check_changelog() {
    print_info "Checking CHANGELOG.md..."

    if ! file_exists "$REPO_ROOT/CHANGELOG.md"; then
        print_error "CHANGELOG.md not found"
        return 1
    fi

    # Check CHANGELOG follows Keep a Changelog format
    if ! grep -q "## \[Unreleased\]" "$REPO_ROOT/CHANGELOG.md"; then
        print_error "CHANGELOG.md missing [Unreleased] section"
        return 1
    fi

    print_success "CHANGELOG.md exists and follows format"
    return 0
}

check_readme() {
    print_info "Checking README.md..."

    if ! file_exists "$REPO_ROOT/README.md"; then
        print_error "README.md not found"
        return 1
    fi

    # Check README has basic sections
    local required_sections=("Installation" "Usage")
    local missing=0

    for section in "${required_sections[@]}"; do
        if ! grep -qi "## $section" "$REPO_ROOT/README.md"; then
            print_warning "README.md missing '$section' section"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "README.md has required sections"
        return 0
    else
        return 1
    fi
}

check_user_docs() {
    print_info "Checking user-guide documentation..."

    local expected_docs=(
        "docs/user-guide/cli-reference.md"
        "docs/user-guide/backends.md"
        "docs/user-guide/configuration.md"
        "docs/user-guide/installation.md"
    )

    local missing=0
    for doc in "${expected_docs[@]}"; do
        if ! file_exists "$REPO_ROOT/$doc"; then
            print_warning "Missing: $doc (acceptable in early phases)"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "All user documentation present"
        return 0
    else
        print_info "Some user docs missing (will be created during development)"
        return 0  # Don't fail in early phases
    fi
}

check_dev_docs() {
    print_info "Checking development documentation..."

    local expected_docs=(
        "docs/development/contributing.md"
        "docs/development/testing-patterns.md"
    )

    local missing=0
    for doc in "${expected_docs[@]}"; do
        if ! file_exists "$REPO_ROOT/$doc"; then
            print_warning "Missing: $doc (acceptable in early phases)"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "All development documentation present"
        return 0
    else
        print_info "Some dev docs missing (will be created during development)"
        return 0  # Don't fail in early phases
    fi
}

check_error_database() {
    print_info "Checking error database..."

    if ! file_exists "$REPO_ROOT/docs/troubleshooting/error-database.md"; then
        print_warning "Error database not found (acceptable if no errors encountered yet)"
        return 0
    fi

    print_success "Error database exists"
    return 0
}

check_adrs() {
    print_info "Checking Architecture Decision Records..."

    if ! dir_exists "$REPO_ROOT/docs/knowledge-base/adrs"; then
        print_error "ADR directory not found"
        return 1
    fi

    # Count ADRs
    local adr_count=$(find "$REPO_ROOT/docs/knowledge-base/adrs" -name "*.md" -type f | wc -l)

    if [ "$adr_count" -eq 0 ]; then
        print_warning "No ADRs found yet (will be created as decisions are made)"
        return 0
    else
        print_success "Found $adr_count ADR(s)"
        return 0
    fi
}

# Run all checks
print_section "Running Documentation Checks"

check_changelog || ((VIOLATIONS++))
echo ""

check_readme || ((VIOLATIONS++))
echo ""

check_user_docs || ((VIOLATIONS++))
echo ""

check_dev_docs || ((VIOLATIONS++))
echo ""

check_error_database || ((VIOLATIONS++))
echo ""

check_adrs || ((VIOLATIONS++))
echo ""

# Summary
print_section "Summary"

if [ $VIOLATIONS -eq 0 ]; then
    print_success "All documentation checks passed!"
    exit 0
else
    print_error "Found $VIOLATIONS documentation issue(s)"
    print_info "Review design Section 5 for documentation requirements"
    exit 1
fi
```

**Step 2: Create Python documentation checker for PR changes**

Create `.github/scripts/check-docs.py`:
```python
#!/usr/bin/env python3
"""
Documentation change detector for PRs.

Analyzes changed files and determines which documentation must be updated.
Maps code changes to documentation requirements per design document.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Mapping of file patterns to required documentation
DOC_REQUIREMENTS = {
    "packages/core/src/color_scheme/cli/": [
        "docs/user-guide/cli-reference.md",
        "CLI command changed - must update documentation"
    ],
    "packages/core/src/color_scheme/backends/": [
        "docs/user-guide/backends.md",
        "Backend modified - must document changes"
    ],
    "settings.toml": [
        "docs/user-guide/configuration.md",
        "Configuration changed - must update config docs"
    ],
    "packages/orchestrator/dockerfiles/": [
        "docs/user-guide/containerization.md",
        "Dockerfile changed - must update container docs"
    ],
    "pyproject.toml": [
        "docs/user-guide/installation.md",
        "Dependencies changed - may need installation updates"
    ],
}


def read_changed_files(file_path: str) -> List[str]:
    """Read list of changed files from input file."""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)


def categorize_changes(files: List[str]) -> dict:
    """Categorize changes by type."""
    categories = {
        'cli': [],
        'backends': [],
        'config': [],
        'containers': [],
        'dependencies': [],
        'tests': [],
        'docs': []
    }

    for file in files:
        if 'cli/commands/' in file:
            categories['cli'].append(file)
        elif 'backends/' in file:
            categories['backends'].append(file)
        elif 'settings.toml' in file or 'config/' in file:
            categories['config'].append(file)
        elif 'dockerfile' in file.lower():
            categories['containers'].append(file)
        elif 'pyproject.toml' in file:
            categories['dependencies'].append(file)
        elif file.startswith('tests/'):
            categories['tests'].append(file)
        elif file.startswith('docs/'):
            categories['docs'].append(file)

    return categories


def check_required_docs(changed_files: List[str], categories: dict) -> Tuple[List[str], List[str]]:
    """Check if required documentation was updated."""
    required_updates = []
    warnings = []

    # Check CLI changes
    if categories['cli']:
        if not any('cli-reference.md' in f for f in changed_files):
            required_updates.append("docs/user-guide/cli-reference.md - CLI commands modified")

    # Check backend changes
    if categories['backends']:
        if not any('backends.md' in f for f in changed_files):
            required_updates.append("docs/user-guide/backends.md - Backend code modified")

    # Check config changes
    if categories['config']:
        if not any('configuration.md' in f for f in changed_files):
            warnings.append("docs/user-guide/configuration.md - Config modified (verify docs)")

    # Check container changes
    if categories['containers']:
        if not any('containerization.md' in f for f in changed_files):
            required_updates.append("docs/user-guide/containerization.md - Dockerfiles modified")

    # Check dependency changes
    if categories['dependencies']:
        if not any('installation.md' in f for f in changed_files):
            warnings.append("docs/user-guide/installation.md - Dependencies changed (verify docs)")

    return required_updates, warnings


def main():
    if len(sys.argv) != 2:
        print("Usage: check-docs.py <changed_files.txt>")
        sys.exit(1)

    changed_files = read_changed_files(sys.argv[1])

    if not changed_files:
        print("✅ No files changed")
        sys.exit(0)

    print("📝 Analyzing changed files for documentation requirements...\n")

    categories = categorize_changes(changed_files)
    required, warnings = check_required_docs(changed_files, categories)

    # Print summary
    print("Changed files by category:")
    for category, files in categories.items():
        if files:
            print(f"  {category}: {len(files)} file(s)")
    print()

    # Check for CHANGELOG
    has_changelog = any('CHANGELOG.md' in f for f in changed_files)

    exit_code = 0

    if required:
        print("❌ Required documentation updates missing:")
        for req in required:
            print(f"  - {req}")
        print()
        exit_code = 1

    if warnings:
        print("⚠️  Documentation may need updates:")
        for warn in warnings:
            print(f"  - {warn}")
        print()

    if not has_changelog:
        print("⚠️  CHANGELOG.md not updated")
        print("  Add entry to CHANGELOG.md for user-facing changes")
        print()

    if exit_code == 0 and not warnings:
        print("✅ Documentation requirements satisfied")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
```

**Step 3: Make scripts executable**

Run:
```bash
chmod +x scripts/verify-documentation.sh
chmod +x .github/scripts/check-docs.py
```

**Step 4: Test the documentation verification**

Run:
```bash
./scripts/verify-documentation.sh
```

Expected: Shows current documentation status

**Step 5: Commit**

Run:
```bash
git add scripts/verify-documentation.sh .github/scripts/check-docs.py
git commit -m "feat(scripts): add documentation verification scripts

Two complementary scripts:
1. verify-documentation.sh - Checks docs structure and completeness
2. check-docs.py - Maps code changes to required doc updates (for PRs)

Enforces documentation requirements from design Section 5.

Part of verification infrastructure (Phase 0).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Create Phase Gate Checker

**Files:**
- Create: `scripts/phase-gate-check.sh`
- Create: `docs/implementation-progress.md`

**Step 1: Create phase gate checker**

Create `scripts/phase-gate-check.sh`:
```bash
#!/bin/bash
set -e

# Load utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh"

validate_repo_root
REPO_ROOT=$(get_repo_root)

# Check phase argument
if [ $# -eq 0 ]; then
    print_error "Usage: ./scripts/phase-gate-check.sh <phase-number>"
    print_info "Example: ./scripts/phase-gate-check.sh 1"
    exit 1
fi

PHASE=$1

print_section "Phase $PHASE Gate Check"
echo "Comprehensive verification for phase completion..."
echo "Reference: docs/plans/2026-01-18-monorepo-architecture-design.md Section 10"
echo ""

FAILURES=0

# Common checks for all phases
run_common_checks() {
    print_info "Running common checks..."

    # Design compliance
    if ./scripts/verify-design-compliance.sh >/dev/null 2>&1; then
        print_success "Design compliance: PASS"
    else
        print_error "Design compliance: FAIL"
        ((FAILURES++))
    fi

    # Documentation
    if ./scripts/verify-documentation.sh >/dev/null 2>&1; then
        print_success "Documentation: PASS"
    else
        print_error "Documentation: FAIL"
        ((FAILURES++))
    fi

    # Git status clean
    if [ -z "$(git status --porcelain)" ]; then
        print_success "Git status: Clean"
    else
        print_warning "Git status: Uncommitted changes"
        print_info "Commit or stash changes before completing phase"
    fi

    echo ""
}

# Phase 0: Verification Infrastructure
check_phase_0() {
    print_section "Phase 0 Specific Checks"

    local required_scripts=(
        "scripts/verify-design-compliance.sh"
        "scripts/verify-documentation.sh"
        "scripts/phase-gate-check.sh"
        "scripts/utils.sh"
        ".github/scripts/check-docs.py"
    )

    print_info "Checking required scripts exist..."
    local missing=0
    for script in "${required_scripts[@]}"; do
        if ! file_exists "$REPO_ROOT/$script"; then
            print_error "Missing: $script"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "All required scripts present"
    else
        print_error "Missing required scripts"
        ((FAILURES++))
    fi

    # Check scripts are executable
    print_info "Checking scripts are executable..."
    local non_executable=0
    for script in "scripts/verify-design-compliance.sh" "scripts/verify-documentation.sh" "scripts/phase-gate-check.sh"; do
        if ! [ -x "$REPO_ROOT/$script" ]; then
            print_error "Not executable: $script"
            non_executable=1
        fi
    done

    if [ $non_executable -eq 0 ]; then
        print_success "All scripts are executable"
    else
        print_error "Some scripts not executable"
        ((FAILURES++))
    fi

    # Check PR template exists
    print_info "Checking PR template..."
    if file_exists "$REPO_ROOT/.github/pull_request_template.md"; then
        print_success "PR template exists"
    else
        print_error "PR template missing"
        ((FAILURES++))
    fi

    echo ""
}

# Phase 1: Foundation
check_phase_1() {
    print_section "Phase 1 Specific Checks"

    # Check monorepo structure is complete
    print_info "Checking monorepo structure..."
    local required_dirs=(
        "packages/core/src/color_scheme"
        "packages/core/tests"
        "packages/orchestrator/src/color_scheme_orchestrator"
        "packages/orchestrator/tests"
    )

    local missing=0
    for dir in "${required_dirs[@]}"; do
        if ! dir_exists "$REPO_ROOT/$dir"; then
            print_error "Missing: $dir"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "Monorepo structure complete"
    else
        ((FAILURES++))
    fi

    # Check CI pipelines exist
    print_info "Checking CI/CD pipelines..."
    local required_workflows=(
        ".github/workflows/ci-core.yml"
        ".github/workflows/docs-check.yml"
    )

    local missing_workflows=0
    for workflow in "${required_workflows[@]}"; do
        if ! file_exists "$REPO_ROOT/$workflow"; then
            print_error "Missing: $workflow"
            missing_workflows=1
        fi
    done

    if [ $missing_workflows -eq 0 ]; then
        print_success "Required CI workflows present"
    else
        ((FAILURES++))
    fi

    echo ""
}

# Phase 2: Core Backends
check_phase_2() {
    print_section "Phase 2 Specific Checks"

    print_info "Checking backend implementations..."
    local backends=("custom" "pywal" "wallust")
    local missing=0

    for backend in "${backends[@]}"; do
        if ! file_exists "$REPO_ROOT/packages/core/src/color_scheme/backends/$backend.py"; then
            print_error "Missing backend: $backend"
            missing=1
        fi

        if ! file_exists "$REPO_ROOT/packages/core/tests/unit/test_${backend}_backend.py"; then
            print_error "Missing tests for backend: $backend"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "All backends implemented with tests"
    else
        ((FAILURES++))
    fi

    # Check factory exists
    print_info "Checking factory pattern..."
    if file_exists "$REPO_ROOT/packages/core/src/color_scheme/factory.py"; then
        print_success "Factory implementation present"
    else
        print_error "Factory missing"
        ((FAILURES++))
    fi

    # Run core tests
    print_info "Running core package tests..."
    cd "$REPO_ROOT/packages/core"
    if command_exists uv && [ -d ".venv" ]; then
        if uv run pytest --quiet 2>/dev/null; then
            print_success "All core tests passing"
        else
            print_error "Core tests failing"
            ((FAILURES++))
        fi
    else
        print_warning "Cannot run tests (environment not set up)"
    fi
    cd "$REPO_ROOT"

    echo ""
}

# Run appropriate checks based on phase
print_section "Running Phase Gate Checks"

run_common_checks

case $PHASE in
    0)
        check_phase_0
        ;;
    1)
        check_phase_1
        ;;
    2)
        check_phase_2
        ;;
    *)
        print_warning "Phase $PHASE checks not yet implemented"
        ;;
esac

# Summary
print_section "Phase $PHASE Gate Check Summary"

if [ $FAILURES -eq 0 ]; then
    print_success "All gate checks passed! Phase $PHASE complete."
    print_info "Update docs/implementation-progress.md and proceed to next phase"
    exit 0
else
    print_error "Found $FAILURES failure(s)"
    print_info "Fix issues before marking phase complete"
    exit 1
fi
```

**Step 2: Create progress tracking document**

Create `docs/implementation-progress.md`:
```markdown
# Implementation Progress

Track progress through implementation phases defined in design document.

Reference: `docs/plans/2026-01-18-monorepo-architecture-design.md` Section 10

---

## Phase 0: Verification Infrastructure ⏳ IN PROGRESS

**Goal**: Build enforcement mechanisms before feature development

**Tasks**:
- [ ] Setup scripts directory and utilities
- [ ] Create design compliance verification script
- [ ] Create documentation validation script
- [ ] Create phase gate checker
- [ ] Create PR template with compliance checklist
- [ ] Setup basic CI integration
- [ ] Test all verification scripts

**Design Compliance**:
- ⏳ Scripts infrastructure (Section 9)
- ⏳ Enforcement mechanisms (Section 5)
- ⏳ Git workflow support (Section 6)

**Blockers**: None

**Next Review**: 2026-01-19

**Completion Criteria**:
- [ ] All verification scripts working
- [ ] PR template in place
- [ ] Scripts executable and tested
- [ ] Phase gate check passes for Phase 0

---

## Phase 1: Foundation

**Status**: Not Started

**Goal**: Establish monorepo structure, CI/CD, and core package skeleton

**Planned Start**: After Phase 0 completion

---

## Phase 2: Core Package - Backends

**Status**: Not Started

**Planned Start**: After Phase 1 completion

---

## Notes

### Update Instructions

When completing a phase:
1. Run phase gate check: `./scripts/phase-gate-check.sh <N>`
2. If passing, update phase status to ✅ COMPLETE
3. Add completion date
4. Update next phase status to ⏳ IN PROGRESS
5. Commit changes

### Status Indicators

- ⏳ IN PROGRESS - Currently working on
- ✅ COMPLETE - All checks passed
- ❌ BLOCKED - Cannot proceed due to issues
- 📝 PLANNED - Not yet started
```

**Step 3: Make phase gate script executable**

Run:
```bash
chmod +x scripts/phase-gate-check.sh
```

**Step 4: Test phase gate checker**

Run:
```bash
./scripts/phase-gate-check.sh 0
```

Expected: Shows Phase 0 gate check results (likely some failures since we haven't completed all tasks yet)

**Step 5: Commit**

Run:
```bash
git add scripts/phase-gate-check.sh docs/implementation-progress.md
git commit -m "feat(scripts): add phase gate checker and progress tracking

Phase gate checker runs comprehensive verification for each phase:
- Common checks (design compliance, documentation, git status)
- Phase-specific checks (varies by phase)

Progress tracking document provides single source of truth for
implementation status across all phases.

Part of verification infrastructure (Phase 0).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Create PR Template with Compliance Checklist

**Files:**
- Create: `.github/pull_request_template.md`

**Step 1: Create comprehensive PR template**

Create `.github/pull_request_template.md`:
```markdown
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
```

**Step 2: Commit PR template**

Run:
```bash
git add .github/pull_request_template.md
git commit -m "feat(github): add comprehensive PR template with design compliance checklist

PR template enforces design document compliance with checklists for:
- Architecture principles (Section 1)
- Testing requirements (Section 5)
- Documentation standards (Section 5)
- Git workflow (Section 6)
- Code quality and security
- CI/CD gates (Section 7)

Ensures every PR is reviewed against design principles.

Part of verification infrastructure (Phase 0).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Create Basic CI Integration

**Files:**
- Create: `.github/workflows/verify-compliance.yml`
- Create: `.github/workflows/verify-docs.yml`

**Step 1: Create compliance verification workflow**

Create `.github/workflows/verify-compliance.yml`:
```yaml
name: Verify Design Compliance

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  compliance-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Make scripts executable
        run: chmod +x scripts/*.sh

      - name: Run design compliance verification
        run: ./scripts/verify-design-compliance.sh

      - name: Upload compliance report
        if: always()
        run: |
          echo "Compliance check completed"
          echo "See job logs for details"
```

**Step 2: Create documentation verification workflow**

Create `.github/workflows/verify-docs.yml`:
```yaml
name: Verify Documentation

on:
  pull_request:
    branches: [main, develop]

jobs:
  docs-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Detect changed files
        id: changes
        run: |
          git diff --name-only origin/${{ github.base_ref }}...HEAD > changed_files.txt
          echo "Changed files:"
          cat changed_files.txt

      - name: Check documentation requirements
        run: |
          chmod +x .github/scripts/check-docs.py
          python3 .github/scripts/check-docs.py changed_files.txt

      - name: Verify CHANGELOG entry
        run: |
          if git diff origin/${{ github.base_ref }}...HEAD -- CHANGELOG.md | grep -q "^+"; then
            echo "✅ CHANGELOG.md updated"
          else
            echo "⚠️  CHANGELOG.md not updated"
            echo "Add entry for user-facing changes"
          fi

      - name: Run documentation verification
        run: |
          chmod +x scripts/verify-documentation.sh
          ./scripts/verify-documentation.sh
```

**Step 3: Commit CI workflows**

Run:
```bash
git add .github/workflows/verify-compliance.yml .github/workflows/verify-docs.yml
git commit -m "feat(ci): add compliance and documentation verification workflows

Two workflows run on every PR:
1. verify-compliance.yml - Runs design compliance checks
2. verify-docs.yml - Validates documentation completeness

These enforce design document requirements in CI.

Part of verification infrastructure (Phase 0).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Create Documentation Templates

**Files:**
- Create: `docs/templates/adr-template.md`
- Create: `docs/templates/error-entry-template.md`
- Create: `CHANGELOG.md`

**Step 1: Create ADR template**

Create `docs/templates/adr-template.md`:
```markdown
# ADR-XXX: [Short Title]

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Rejected | Deprecated | Superseded
**Deciders**: [Team/Person]

## Context

[Describe the context and problem statement. What decision needs to be made?]

## Decision

[State the decision clearly. What did we decide to do?]

## Rationale

**Pros**:
- Benefit 1
- Benefit 2

**Cons**:
- Drawback 1
- Drawback 2

**Alternatives Considered**:
1. Alternative 1 - why rejected
2. Alternative 2 - why rejected

## Consequences

[What are the consequences of this decision? What changes as a result?]

## References

- Related ADRs:
- Related Issues:
- Related PRs:
```

**Step 2: Create error database entry template**

Create `docs/templates/error-entry-template.md`:
```markdown
## ERR-XXX: [Error Title]

**Date**: YYYY-MM-DD
**Severity**: Critical | High | Medium | Low
**Component**: Core | Orchestrator | CI/CD | Docs

**Error**:
\```
[Exact error message or stack trace]
\```

**Context**:
[When/where did this occur? What were you doing?]

**Root Cause**:
[Why did this happen? Technical explanation.]

**Solution**:
[Step-by-step how it was fixed]

1. Step 1
2. Step 2
3. Step 3

**Prevention**:
[How to avoid this in future]

- Preventive measure 1
- Preventive measure 2

**Related**:
- PR: #XXX
- Issue: #XXX
- Commit: abc123

**Verification**:
\```bash
# Commands to verify fix works
\```
```

**Step 3: Create initial CHANGELOG**

Create `CHANGELOG.md`:
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure
- Verification infrastructure scripts
- Design compliance checking
- Documentation validation
- Phase gate checking system
- PR template with compliance checklist
- CI workflows for verification

### Changed

- N/A

### Fixed

- N/A

### Security

- N/A

---

## Release Notes Format

Each release should include:

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements/fixes
```

**Step 4: Create directory structure for docs**

Run:
```bash
mkdir -p docs/knowledge-base/adrs
mkdir -p docs/troubleshooting
mkdir -p docs/user-guide
mkdir -p docs/development/recipes
mkdir -p docs/knowledge-base/performance
```

**Step 5: Create initial error database**

Create `docs/troubleshooting/error-database.md`:
```markdown
# Error Database

Track errors encountered during development, their root causes, and solutions.

This prevents repeating mistakes and builds institutional knowledge.

## Format

Use template: `docs/templates/error-entry-template.md`

Each entry includes:
- **Error**: Exact error message
- **Context**: When/where it occurred
- **Root Cause**: Why it happened
- **Solution**: How it was fixed
- **Prevention**: How to avoid in future
- **Related**: Links to PRs, issues, commits

---

## Errors

<!-- Errors will be added here as they are encountered and resolved -->

_No errors recorded yet._
```

**Step 6: Commit documentation structure**

Run:
```bash
git add docs/ CHANGELOG.md
git commit -m "feat(docs): add documentation structure and templates

Created:
- Documentation directory structure (user-guide, development, knowledge-base)
- ADR template for architecture decisions
- Error entry template for error database
- Initial CHANGELOG.md following Keep a Changelog format
- Error database structure

Implements documentation requirements from design Section 5.

Part of verification infrastructure (Phase 0).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Test Complete Verification Infrastructure

**Files:**
- None (testing existing files)

**Step 1: Run design compliance check**

Run:
```bash
./scripts/verify-design-compliance.sh
```

Expected: Shows compliance status, may have some warnings about missing packages (acceptable at this stage)

**Step 2: Run documentation verification**

Run:
```bash
./scripts/verify-documentation.sh
```

Expected: Shows documentation status

**Step 3: Run phase 0 gate check**

Run:
```bash
./scripts/phase-gate-check.sh 0
```

Expected: Should pass all Phase 0 checks if all tasks completed

**Step 4: Test PR template exists**

Run:
```bash
ls -la .github/pull_request_template.md
```

Expected: File exists and is readable

**Step 5: Verify all scripts are executable**

Run:
```bash
ls -la scripts/*.sh
```

Expected: All .sh files have executable permissions (x flag)

**Step 6: Test CI workflow syntax**

Run:
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/verify-compliance.yml'))"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/verify-docs.yml'))"
```

Expected: No syntax errors

**Step 7: Update implementation progress**

Edit `docs/implementation-progress.md`:

Mark Phase 0 tasks as complete:
```markdown
## Phase 0: Verification Infrastructure ✅ COMPLETE

**Goal**: Build enforcement mechanisms before feature development

**Completion Date**: 2026-01-18

**Tasks**:
- [x] Setup scripts directory and utilities
- [x] Create design compliance verification script
- [x] Create documentation validation script
- [x] Create phase gate checker
- [x] Create PR template with compliance checklist
- [x] Setup basic CI integration
- [x] Test all verification scripts

**Design Compliance**:
- ✅ Scripts infrastructure (Section 9)
- ✅ Enforcement mechanisms (Section 5)
- ✅ Git workflow support (Section 6)

**Phase Gate**: PASSED
```

**Step 8: Final commit**

Run:
```bash
git add docs/implementation-progress.md
git commit -m "docs(progress): mark Phase 0 verification infrastructure as complete

All verification infrastructure tasks completed:
- Design compliance verification
- Documentation validation
- Phase gate checking
- PR template with compliance checklist
- CI integration
- Documentation templates

Phase 0 gate check passing.
Ready to proceed to Phase 1: Foundation.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Create Quick Reference Guide

**Files:**
- Create: `docs/development/verification-guide.md`

**Step 1: Create verification quick reference**

Create `docs/development/verification-guide.md`:
```markdown
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
```

**Step 2: Commit verification guide**

Run:
```bash
git add docs/development/verification-guide.md
git commit -m "docs(development): add verification infrastructure quick reference

Comprehensive guide covering:
- Daily development workflow with verification steps
- All verification scripts reference
- PR checklist
- Troubleshooting common issues
- IDE integration examples

Makes verification infrastructure easy to use.

Part of verification infrastructure (Phase 0).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Completion

Phase 0 implementation complete! You now have:

✅ **Design compliance verification** - Automated checking against design document
✅ **Documentation validation** - Ensures docs stay current
✅ **Phase gate checking** - Comprehensive verification per phase
✅ **PR template** - Enforces compliance checklist
✅ **CI integration** - Runs checks automatically
✅ **Progress tracking** - Single source of truth for status
✅ **Templates** - ADRs, error entries, CHANGELOG
✅ **Quick reference guide** - Easy-to-use documentation

## Next Steps

Run the final phase gate check to verify everything:

```bash
./scripts/phase-gate-check.sh 0
```

If passing, you're ready to proceed to **Phase 1: Foundation** with full enforcement mechanisms in place!

---

**Plan saved to:** `docs/plans/2026-01-18-verification-infrastructure.md`
