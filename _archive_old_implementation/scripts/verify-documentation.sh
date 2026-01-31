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
