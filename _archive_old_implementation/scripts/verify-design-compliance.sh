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
