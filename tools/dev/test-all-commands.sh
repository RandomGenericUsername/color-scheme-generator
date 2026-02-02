#!/bin/bash
##############################################################################
# Comprehensive Test Suite for color-scheme (core + orchestrator)
#
# Tests both the core CLI (native execution) and orchestrator CLI (containerized)
# Usage: ./test-all-commands.sh <wallpaper-path>
#
# Arguments:
#   wallpaper-path  Path to wallpaper image file (required)
#                   Example: ./test-all-commands.sh ~/Downloads/wallpaper.jpg
##############################################################################

# Validate arguments
if [ $# -eq 0 ]; then
    echo "Error: wallpaper path is required"
    echo "Usage: $0 <wallpaper-path>"
    echo ""
    echo "Example: $0 ~/Downloads/wallpaper.jpg"
    exit 1
fi

TEST_IMAGE="$1"

# Resolve to absolute path
TEST_IMAGE="$(cd "$(dirname "$TEST_IMAGE")" && pwd)/$(basename "$TEST_IMAGE")"

# Check if file exists
if [ ! -f "$TEST_IMAGE" ]; then
    echo "Error: Wallpaper file not found: $1"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
ORCH_VENV="$PROJECT_ROOT/packages/orchestrator/.venv"

if [ ! -f "$ORCH_VENV/bin/activate" ]; then
    echo "Error: Orchestrator venv not found at $ORCH_VENV"
    echo "Please run: make install-orchestrator"
    exit 1
fi

source "$ORCH_VENV/bin/activate"

TEST_OUTPUT_DIR="/tmp/color-scheme-test"
PASSED=0
FAILED=0

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

print_test() {
    echo -ne "  → $1 ... "
}

print_pass() {
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}✗${NC}"
    ((FAILED++))
}

echo -e "${BLUE}Checking prerequisites...${NC}"
echo -e "${GREEN}✓ Test image:${NC} $TEST_IMAGE"
mkdir -p "$TEST_OUTPUT_DIR"
echo -e "${GREEN}✓ Output directory ready${NC}\n"

# ============================================================================
# CORE CLI TESTS (color-scheme-core)
# ============================================================================

print_header "CORE CLI TESTS (color-scheme-core)"

print_test "Version command"
if color-scheme-core version > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Generate command (custom backend)"
core_out="$TEST_OUTPUT_DIR/core-generate"
mkdir -p "$core_out"
if color-scheme-core generate "$TEST_IMAGE" \
    --output-dir "$core_out" \
    --backend custom \
    --format json > /dev/null 2>&1 && [ -f "$core_out/colors.json" ]; then
    print_pass
else
    print_fail
fi

print_test "Show command"
if color-scheme-core show "$TEST_IMAGE" --backend custom > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

# ============================================================================
# ORCHESTRATOR CLI TESTS (color-scheme)
# ============================================================================

print_header "ORCHESTRATOR CLI TESTS (color-scheme)"

print_test "Version command"
if color-scheme version > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

# ============================================================================
# CONTAINER MANAGEMENT TESTS (primary use case)
# ============================================================================

print_header "CONTAINER MANAGEMENT TESTS"

print_test "Install custom backend"
if color-scheme install custom > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Generate with custom (containerized)"
custom_orch_out="$TEST_OUTPUT_DIR/orch-custom"
mkdir -p "$custom_orch_out"
if color-scheme generate "$TEST_IMAGE" \
    --output-dir "$custom_orch_out" \
    --backend custom \
    -f json > /dev/null 2>&1 && [ -f "$custom_orch_out/colors.json" ]; then
    print_pass
else
    print_fail
fi

print_test "Multiple output formats (json, sh, css, yaml)"
multi_out="$TEST_OUTPUT_DIR/multi-format"
mkdir -p "$multi_out"
if color-scheme generate "$TEST_IMAGE" \
    --output-dir "$multi_out" \
    --backend custom \
    -f json -f sh -f css -f yaml > /dev/null 2>&1; then

    all_ok=true
    for fmt in json sh css yaml; do
        if [ ! -f "$multi_out/colors.$fmt" ]; then
            all_ok=false
        fi
    done

    if [ "$all_ok" = true ]; then
        print_pass
    else
        print_fail
    fi
else
    print_fail
fi

print_test "Uninstall custom backend"
if color-scheme uninstall custom --yes > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Install wallust backend"
if color-scheme install wallust > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Generate with wallust (containerized)"
wallust_out="$TEST_OUTPUT_DIR/orch-wallust"
mkdir -p "$wallust_out"
if color-scheme generate "$TEST_IMAGE" \
    --output-dir "$wallust_out" \
    --backend wallust \
    -f json > /dev/null 2>&1 && [ -f "$wallust_out/colors.json" ]; then
    print_pass
else
    print_fail
fi

print_test "Uninstall wallust backend"
if color-scheme uninstall wallust --yes > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

# ============================================================================
# SUMMARY
# ============================================================================

print_header "TEST SUMMARY"

TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    PERCENT=$((PASSED * 100 / TOTAL))
else
    PERCENT=0
fi

echo -e "${GREEN}Passed:${NC}  $PASSED/$TOTAL (${PERCENT}%)"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed:${NC}  $FAILED/$TOTAL"
fi

echo ""
echo "Test outputs: $TEST_OUTPUT_DIR"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}\n"
    exit 0
else
    echo -e "${RED}✗ $FAILED test(s) failed${NC}\n"
    exit 1
fi
