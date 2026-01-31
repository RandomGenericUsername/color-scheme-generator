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
