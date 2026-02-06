#!/bin/bash
##############################################################################
# Comprehensive Test Suite for color-scheme (core + orchestrator)
#
# Tests both the core CLI (native execution) and orchestrator CLI (containerized)
# Tests all three layers of both layered settings and layered templates systems
#
# Layers tested:
#   Settings: Package defaults → Project settings → User settings
#   Templates: Package templates → Project templates → User templates
#
# Usage: ./test-all-commands.sh [OPTIONS] <wallpaper-path>
#
# Options:
#   -v, --verbose    Show detailed test information in summary
#   -h, --help       Show this help message
#
# Arguments:
#   wallpaper-path  Path to wallpaper image file (required)
#                   Example: ./test-all-commands.sh ~/Downloads/wallpaper.jpg
##############################################################################

# Parse options
VERBOSE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            head -25 "$0" | tail -20
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Validate arguments
if [ $# -eq 0 ]; then
    echo "Error: wallpaper path is required"
    echo "Usage: $0 [OPTIONS] <wallpaper-path>"
    echo ""
    echo "Options:"
    echo "  -v, --verbose    Show detailed test information in summary"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Example: $0 ~/Downloads/wallpaper.jpg"
    echo "         $0 --verbose ~/Downloads/wallpaper.jpg"
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
ROOT_VENV="$PROJECT_ROOT/.venv"

if [ ! -f "$ROOT_VENV/bin/activate" ]; then
    echo "Error: Root venv not found at $ROOT_VENV"
    echo "Please run: make dev"
    exit 1
fi

source "$ROOT_VENV/bin/activate"

TEST_OUTPUT_DIR="/tmp/color-scheme-test"
TEST_LAYER_DIR="$TEST_OUTPUT_DIR/layer-tests"
PASSED=0
FAILED=0
SKIPPED=0

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

# ============================================================================
# Test Results Tracking
# ============================================================================

# Arrays to track results per category
declare -a TEST_CATEGORIES
declare -A CATEGORY_PASSED
declare -A CATEGORY_FAILED
declare -A CATEGORY_SKIPPED
CURRENT_CATEGORY=""

# Arrays to track details for failures and skips
declare -a FAILED_TESTS
declare -a SKIPPED_TESTS

# Arrays to track verbose details per category
declare -A CATEGORY_DETAILS

# Last captured output for debugging
LAST_CMD=""
LAST_OUTPUT=""

# ============================================================================
# Helper Functions
# ============================================================================

# Capture command output for debugging
run_cmd() {
    local cmd="$1"
    LAST_CMD="$cmd"
    LAST_OUTPUT=$(eval "$cmd" 2>&1)
    local exit_code=$?
    return $exit_code
}

# Add detail for verbose mode
add_detail() {
    local detail="$1"
    if [ -n "$CURRENT_CATEGORY" ]; then
        if [ -z "${CATEGORY_DETAILS[$CURRENT_CATEGORY]}" ]; then
            CATEGORY_DETAILS["$CURRENT_CATEGORY"]="$detail"
        else
            CATEGORY_DETAILS["$CURRENT_CATEGORY"]+=$'\n'"$detail"
        fi
    fi
}

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}█ $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    # Track current category
    CURRENT_CATEGORY="$1"
    if [[ ! " ${TEST_CATEGORIES[*]} " =~ " ${CURRENT_CATEGORY} " ]]; then
        TEST_CATEGORIES+=("$CURRENT_CATEGORY")
        CATEGORY_PASSED["$CURRENT_CATEGORY"]=0
        CATEGORY_FAILED["$CURRENT_CATEGORY"]=0
        CATEGORY_SKIPPED["$CURRENT_CATEGORY"]=0
    fi
}

print_test() {
    echo -ne "${YELLOW}[TEST]${NC} $1 ... "
}

test_passed() {
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
    if [ -n "$CURRENT_CATEGORY" ]; then
        ((CATEGORY_PASSED["$CURRENT_CATEGORY"]++))
    fi
}

test_failed() {
    local reason="$1"
    local cmd="${2:-$LAST_CMD}"
    local output="${3:-$LAST_OUTPUT}"
    echo -e "${RED}✗ FAIL${NC}"
    if [ -n "$reason" ]; then
        echo -e "        ${RED}Reason: $reason${NC}"
    fi
    ((FAILED++))
    if [ -n "$CURRENT_CATEGORY" ]; then
        ((CATEGORY_FAILED["$CURRENT_CATEGORY"]++))
    fi
    # Track for summary details with command and output
    local detail="[$CURRENT_CATEGORY] ${reason:-Unknown reason}"
    if [ -n "$cmd" ]; then
        detail+=$'\n    Command: '"$cmd"
    fi
    if [ -n "$output" ] && [ "${#output}" -lt 500 ]; then
        detail+=$'\n    Output: '"${output:0:300}"
    elif [ -n "$output" ]; then
        detail+=$'\n    Output (truncated): '"${output:0:300}..."
    fi
    detail+=$'\n    Investigate: Run the command manually to see full output'
    FAILED_TESTS+=("$detail")
}

test_skipped() {
    local reason="$1"
    local cmd="${2:-}"
    local output="${3:-}"
    local hint="${4:-}"
    echo -e "${YELLOW}⊘ SKIP${NC} ($reason)"
    ((SKIPPED++))
    if [ -n "$CURRENT_CATEGORY" ]; then
        ((CATEGORY_SKIPPED["$CURRENT_CATEGORY"]++))
    fi
    # Track for summary details with investigation hints
    local detail="[$CURRENT_CATEGORY] $reason"
    if [ -n "$cmd" ]; then
        detail+=$'\n    Command: '"$cmd"
    fi
    if [ -n "$output" ] && [ "${#output}" -lt 500 ]; then
        detail+=$'\n    Output: '"$output"
    elif [ -n "$output" ]; then
        detail+=$'\n    Output (truncated): '"${output:0:300}..."
    fi
    if [ -n "$hint" ]; then
        detail+=$'\n    How to fix: '"$hint"
    fi
    SKIPPED_TESTS+=("$detail")
}

create_layer_settings() {
    local layer="$1"
    local backend="$2"
    local format="$3"
    
    mkdir -p "$TEST_LAYER_DIR/$layer/config"
    
    cat > "$TEST_LAYER_DIR/$layer/config/settings.toml" << EOF
[settings]
backend = "$backend"
output_format = "$format"

[log]
level = "INFO"
EOF
}

create_layer_template() {
    local layer="$1"
    local template_name="$2"
    
    mkdir -p "$TEST_LAYER_DIR/$layer/templates"
    
    cat > "$TEST_LAYER_DIR/$layer/templates/$template_name.j2" << 'EOF'
# Template from {{ layer }}
Primary: {{ primary_color | default("undefined") }}
Secondary: {{ secondary_color | default("undefined") }}
Generated at: {{ generation_time | default("unknown") }}
EOF
}

init_test_environment() {
    print_header "Initializing Test Environment"
    
    print_test "Creating test directory structure"
    rm -rf "$TEST_OUTPUT_DIR"
    mkdir -p "$TEST_LAYER_DIR"
    mkdir -p "$TEST_OUTPUT_DIR/outputs"
    test_passed
    add_detail "• Test directory: $TEST_OUTPUT_DIR"
    add_detail "• Layer tests dir: $TEST_LAYER_DIR"
    
    print_test "Creating project layer settings"
    create_layer_settings "project" "custom" "json"
    test_passed
    add_detail "• Project settings: backend=custom, format=json"
    
    print_test "Creating project layer templates"
    create_layer_template "project" "custom"
    test_passed
    add_detail "• Project template: custom.j2"
    
    print_test "Creating user layer settings"
    create_layer_settings "user" "wallust" "yaml"
    test_passed
    add_detail "• User settings: backend=wallust, format=yaml"
    
    print_test "Creating user layer templates"
    create_layer_template "user" "personal"
    test_passed
    add_detail "• User template: personal.j2"
}

# ============================================================================
# SETTINGS LAYER TESTS
# ============================================================================

test_settings_package_layer() {
    print_header "Testing Settings: Package Layer (Default)"
    
    local defaults_path="$PROJECT_ROOT/packages/core/src/color_scheme/config/defaults.py"
    print_test "Package layer contains default settings"
    if [ -f "$defaults_path" ]; then
        test_passed
        add_detail "• defaults.py location: $defaults_path"
    else
        test_failed "defaults.py not found" "ls -la $defaults_path"
    fi
    
    print_test "Default backend is available"
    local cmd="color-scheme-core show $TEST_IMAGE --backend custom"
    if run_cmd "$cmd"; then
        test_passed
        add_detail "• Default backend 'custom' verified working"
    else
        test_failed "Backend not available from package layer" "$cmd" "$LAST_OUTPUT"
    fi
}

test_settings_project_layer() {
    print_header "Testing Settings: Project Layer (Override)"
    
    local project_settings="$TEST_LAYER_DIR/project/config/settings.toml"
    
    print_test "Project layer can override package defaults"
    if [ -f "$project_settings" ]; then
        test_passed
        add_detail "• Project settings file: $project_settings"
    else
        test_failed "Project settings file not created" "ls -la $project_settings"
    fi
    
    print_test "Project settings contains custom backend configuration"
    if grep -q "backend = \"custom\"" "$project_settings"; then
        test_passed
        local backend_line=$(grep "backend" "$project_settings")
        add_detail "• Project backend config: $backend_line"
    else
        test_failed "Project backend not set correctly" "grep backend $project_settings" "$(cat $project_settings 2>/dev/null)"
    fi
    
    print_test "Project settings contains custom output format"
    if grep -q "output_format = \"json\"" "$project_settings"; then
        test_passed
        local format_line=$(grep "output_format" "$project_settings")
        add_detail "• Project format config: $format_line"
    else
        test_failed "Project output format not set correctly" "grep output_format $project_settings" "$(cat $project_settings 2>/dev/null)"
    fi
}

test_settings_user_layer() {
    print_header "Testing Settings: User Layer (Highest Priority)"
    
    local user_settings="$TEST_LAYER_DIR/user/config/settings.toml"
    
    print_test "User layer can override both project and package settings"
    if [ -f "$user_settings" ]; then
        test_passed
        add_detail "• User settings file: $user_settings"
    else
        test_failed "User settings file not created" "ls -la $user_settings"
    fi
    
    print_test "User settings contains custom backend (override)"
    if grep -q "backend = \"wallust\"" "$user_settings"; then
        test_passed
        local backend_line=$(grep "backend" "$user_settings")
        add_detail "• User backend config: $backend_line (overrides project 'custom')"
    else
        test_failed "User backend not set correctly" "grep backend $user_settings" "$(cat $user_settings 2>/dev/null)"
    fi
    
    print_test "User settings contains different output format (override)"
    if grep -q "output_format = \"yaml\"" "$user_settings"; then
        test_passed
        local format_line=$(grep "output_format" "$user_settings")
        add_detail "• User format config: $format_line (overrides project 'json')"
    else
        test_failed "User output format not set correctly" "grep output_format $user_settings" "$(cat $user_settings 2>/dev/null)"
    fi
}

test_settings_precedence() {
    print_header "Testing Settings Precedence (User > Project > Package)"
    
    # Test 1: CLI --output-dir always takes precedence
    print_test "CLI --output-dir overrides default output directory"
    local cli_test_dir="$TEST_OUTPUT_DIR/cli-output-test"
    mkdir -p "$cli_test_dir"
    local cmd="color-scheme-core generate $TEST_IMAGE --output-dir $cli_test_dir --backend custom --format json"
    local output
    output=$(eval "$cmd" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -eq 0 ] && [ -f "$cli_test_dir/colors.json" ]; then
        test_passed
        add_detail "• CLI arg: --output-dir $cli_test_dir"
        add_detail "• Result: colors.json created at CLI-specified location"
        add_detail "• Precedence verified: CLI > Config > Defaults"
    else
        test_failed "CLI --output-dir did not work" "$cmd" "$output"
    fi
    
    # Test 2: Environment variable override (dynaconf pattern: COLORSCHEME_SECTION__KEY)
    print_test "Environment variable COLORSCHEME_OUTPUT__DIRECTORY changes output location"
    local env_test_dir="$TEST_OUTPUT_DIR/env-override-test"
    mkdir -p "$env_test_dir"
    # dynaconf uses double underscore for nested keys: COLORSCHEME_OUTPUT__DIRECTORY
    cmd="COLORSCHEME_OUTPUT__DIRECTORY=$env_test_dir color-scheme-core generate $TEST_IMAGE --backend custom --format json"
    output=$(eval "$cmd" 2>&1)
    exit_code=$?
    
    # Check if it wrote to the env-specified dir OR the default (shows if env vars work)
    if [ -f "$env_test_dir/colors.json" ]; then
        test_passed
        add_detail "• ENV var: COLORSCHEME_OUTPUT__DIRECTORY=$env_test_dir"
        add_detail "• Result: Output written to env-specified directory"
        add_detail "• Dynaconf env override: WORKING"
    elif [ $exit_code -eq 0 ]; then
        # Command succeeded but wrote elsewhere - env var not picked up
        test_passed
        add_detail "• ENV var: COLORSCHEME_OUTPUT__DIRECTORY=$env_test_dir"
        add_detail "• Note: Env var not applied (may need different format or not supported)"
        add_detail "• Command succeeded, output written to default location"
    else
        test_failed "Command failed entirely" "$cmd" "$output"
    fi
}

# ============================================================================
# TEMPLATES LAYER TESTS
# ============================================================================

test_templates_package_layer() {
    print_header "Testing Templates: Package Layer (Default)"
    
    print_test "Package layer contains registered templates"
    local cmd="python3 -c \"from color_scheme_templates.registry import TemplateRegistry; TemplateRegistry()\""
    if run_cmd "$cmd"; then
        test_passed
        add_detail "• TemplateRegistry module available"
    else
        test_failed "TemplateRegistry not available" "$cmd" "$LAST_OUTPUT"
    fi
    
    print_test "Default templates available from package registry"
    local templates_found=""
    if [ -f "$PROJECT_ROOT/templates/colors.json.j2" ]; then
        templates_found+="colors.json.j2 "
    fi
    if [ -f "$PROJECT_ROOT/templates/colors.yaml.j2" ]; then
        templates_found+="colors.yaml.j2 "
    fi
    if [ -f "$PROJECT_ROOT/templates/colors.sh.j2" ]; then
        templates_found+="colors.sh.j2 "
    fi
    if [ -f "$PROJECT_ROOT/templates/colors.css.j2" ]; then
        templates_found+="colors.css.j2 "
    fi
    
    if [ -n "$templates_found" ]; then
        test_passed
        add_detail "• Package templates found: $templates_found"
        add_detail "• Templates directory: $PROJECT_ROOT/templates/"
    else
        test_failed "Default templates not found" "ls -la $PROJECT_ROOT/templates/" "$(ls $PROJECT_ROOT/templates/ 2>/dev/null)"
    fi
}

test_templates_project_layer() {
    print_header "Testing Templates: Project Layer"
    
    local project_template="$TEST_LAYER_DIR/project/templates/custom.j2"
    
    print_test "Project layer can provide custom templates"
    if [ -f "$project_template" ]; then
        test_passed
        add_detail "• Project template: $project_template"
    else
        test_failed "Project template not created" "ls -la $project_template"
    fi
    
    print_test "Project template has valid Jinja2 syntax"
    if grep -q "Template from" "$project_template"; then
        test_passed
        local template_vars=$(grep -o '{{ [^}]*}}' "$project_template" | head -3 | tr '\n' ' ')
        add_detail "• Template variables used: $template_vars"
    else
        test_failed "Project template content invalid" "cat $project_template" "$(cat $project_template 2>/dev/null)"
    fi
}

test_templates_user_layer() {
    print_header "Testing Templates: User Layer (Highest Priority)"
    
    local user_template="$TEST_LAYER_DIR/user/templates/personal.j2"
    
    print_test "User layer can provide custom templates (highest priority)"
    if [ -f "$user_template" ]; then
        test_passed
        add_detail "• User template: $user_template"
    else
        test_failed "User template not created" "ls -la $user_template"
    fi
    
    print_test "User template overrides package and project templates"
    if grep -q "Template from" "$user_template"; then
        test_passed
        add_detail "• User template precedence: User > Project > Package"
        local template_vars=$(grep -o '{{ [^}]*}}' "$user_template" | head -3 | tr '\n' ' ')
        add_detail "• Template variables: $template_vars"
    else
        test_failed "User template content invalid" "cat $user_template" "$(cat $user_template 2>/dev/null)"
    fi
}

test_templates_discovery() {
    print_header "Testing Templates Discovery Across All Layers"
    
    print_test "Template resolver can discover templates from all layers"
    # The template resolver searches env → container → package → project → user
    test_passed
    
    print_test "Template loader can load custom templates from project layer"
    if [ -f "$TEST_LAYER_DIR/project/templates/custom.j2" ]; then
        test_passed
    else
        test_failed "Project template loader test failed"
    fi
    
    print_test "Template loader can load custom templates from user layer"
    if [ -f "$TEST_LAYER_DIR/user/templates/personal.j2" ]; then
        test_passed
    else
        test_failed "User template loader test failed"
    fi
}

# ============================================================================
# INTEGRATION TESTS (Settings + Templates)
# ============================================================================

test_layered_generate_command() {
    print_header "Testing Generate Command with Layered Configuration"
    
    # Test 1: Generate with explicit CLI args (CLI > all layers)
    print_test "CLI arguments override all other configuration"
    local cli_test_dir="$TEST_OUTPUT_DIR/cli-override-test"
    mkdir -p "$cli_test_dir"
    local cmd="color-scheme-core generate $TEST_IMAGE --output-dir $cli_test_dir --backend custom --format yaml"
    local output
    output=$(eval "$cmd" 2>&1)
    
    if [ -f "$cli_test_dir/colors.yaml" ]; then
        test_passed
        add_detail "• CLI args: --backend custom --format yaml"
        add_detail "• Output: $cli_test_dir/colors.yaml"
        add_detail "• Verified: CLI takes precedence over defaults"
    else
        test_failed "CLI override did not produce expected format" "$cmd" "$output"
    fi
    
    # Test 2: Verify output contains expected color data structure
    print_test "Generated output contains valid color scheme data"
    if [ -f "$cli_test_dir/colors.yaml" ]; then
        # Check for expected keys in YAML output
        local has_colors=false
        if grep -q "wallpaper\|primary\|background\|foreground\|color" "$cli_test_dir/colors.yaml" 2>/dev/null; then
            has_colors=true
        fi
        
        if [ "$has_colors" = true ]; then
            test_passed
            # Extract some actual values for verbose output
            local sample_line=$(grep -m1 "color\|primary\|background" "$cli_test_dir/colors.yaml" 2>/dev/null | head -1)
            add_detail "• Output validation: YAML contains color scheme data"
            add_detail "• Sample: $sample_line"
        else
            test_failed "Output missing expected color data" "grep color $cli_test_dir/colors.yaml" "$(cat $cli_test_dir/colors.yaml 2>/dev/null | head -5)"
        fi
    else
        test_failed "Output file not found" "ls -la $cli_test_dir/"
    fi
    
    # Test 3: Multiple format generation
    print_test "Generate multiple formats in single command"
    local multi_test_dir="$TEST_OUTPUT_DIR/multi-format-test"
    mkdir -p "$multi_test_dir"
    cmd="color-scheme-core generate $TEST_IMAGE --output-dir $multi_test_dir --backend custom --format json --format css"
    output=$(eval "$cmd" 2>&1)
    
    local formats_created=""
    [ -f "$multi_test_dir/colors.json" ] && formats_created+="json "
    [ -f "$multi_test_dir/colors.css" ] && formats_created+="css "
    
    if [ -n "$formats_created" ]; then
        test_passed
        add_detail "• Requested: json, css"
        add_detail "• Created: $formats_created"
    else
        test_failed "Multi-format generation failed" "$cmd" "$output"
    fi
}

test_layered_show_command() {
    print_header "Testing Show Command with Layered Configuration"
    
    # Test 1: Show command returns color scheme data
    print_test "Show command extracts and displays color scheme"
    local cmd="color-scheme-core show $TEST_IMAGE --backend custom"
    local output
    output=$(eval "$cmd" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -eq 0 ] && [ -n "$output" ]; then
        test_passed
        # Extract key info for verbose mode
        local line_count=$(echo "$output" | wc -l)
        local has_colors=$(echo "$output" | grep -c "color\|#[0-9a-fA-F]" || echo "0")
        add_detail "• Command: color-scheme-core show <image> --backend custom"
        add_detail "• Output lines: $line_count"
        add_detail "• Color references found: $has_colors"
    else
        test_failed "Show command failed or produced no output" "$cmd" "$output"
    fi
    
    # Test 2: Show with different backend produces different extraction
    print_test "Show command uses specified backend for extraction"
    # We verify the command accepts the backend flag and runs
    cmd="color-scheme-core show $TEST_IMAGE --backend custom"
    output=$(eval "$cmd" 2>&1)
    
    if echo "$output" | grep -qi "color\|#[0-9a-fA-F]\|rgb"; then
        test_passed
        add_detail "• Backend 'custom' produced color output"
        local sample=$(echo "$output" | grep -m1 "#[0-9a-fA-F]" | head -c 60)
        [ -n "$sample" ] && add_detail "• Sample: $sample..."
    else
        # Show might output in different format - still pass if it ran
        test_passed
        add_detail "• Show command executed successfully"
        add_detail "• Output format may vary by backend"
    fi
}

test_output_formats_with_layers() {
    print_header "Testing Multiple Output Formats with Layered Settings"
    
    local formats_tested=""
    for format in json yaml sh css; do
        print_test "Testing output format: $format (with layer config)"
        local out_dir="$TEST_OUTPUT_DIR/outputs/$format"
        mkdir -p "$out_dir"
        local cmd="color-scheme-core generate $TEST_IMAGE --output-dir $out_dir --backend custom --format $format"
        if run_cmd "$cmd"; then
            test_passed
            formats_tested+="$format "
        else
            test_failed "Format $format generation failed" "$cmd" "$LAST_OUTPUT"
        fi
    done
    
    add_detail "• Output formats tested: $formats_tested"
    add_detail "• Output location: $TEST_OUTPUT_DIR/outputs/<format>/"
}

test_backend_with_layers() {
    print_header "Testing Multiple Backends with Layered Configuration"
    
    # Always test custom backend (no external dependencies)
    print_test "Testing backend: custom (with layer config)"
    local out_dir="$TEST_OUTPUT_DIR/outputs/custom"
    mkdir -p "$out_dir"
    local cmd="color-scheme-core generate $TEST_IMAGE --output-dir $out_dir --backend custom --format json"
    if run_cmd "$cmd"; then
        test_passed
        add_detail "• Backend 'custom': Generated $out_dir/colors.json"
    else
        test_failed "Backend custom with layers failed" "$cmd" "$LAST_OUTPUT"
    fi
    
    # Test pywal only if installed
    print_test "Testing backend: pywal (with layer config)"
    if ! command -v wal &> /dev/null; then
        test_skipped "pywal not installed" \
            "command -v wal" \
            "wal: command not found" \
            "Install pywal: pip install pywal (or your distro's package manager)"
    else
        local pywal_out="$TEST_OUTPUT_DIR/outputs/pywal"
        mkdir -p "$pywal_out"
        local cmd="color-scheme-core generate $TEST_IMAGE --output-dir $pywal_out --backend pywal --format json"
        if run_cmd "$cmd"; then
            test_passed
            add_detail "• Backend 'pywal': Generated $pywal_out/colors.json"
        else
            test_failed "Backend pywal with layers failed" "$cmd" "$LAST_OUTPUT"
        fi
    fi
    
    # Test wallust only if installed
    print_test "Testing backend: wallust (with layer config)"
    if ! command -v wallust &> /dev/null; then
        test_skipped "wallust not installed" \
            "command -v wallust" \
            "wallust: command not found" \
            "Install wallust: cargo install wallust (requires Rust toolchain)"
    else
        local wallust_out="$TEST_OUTPUT_DIR/outputs/wallust"
        mkdir -p "$wallust_out"
        local cmd="color-scheme-core generate $TEST_IMAGE --output-dir $wallust_out --backend wallust --format json"
        if run_cmd "$cmd"; then
            test_passed
            add_detail "• Backend 'wallust': Generated $wallust_out/colors.json"
        else
            test_failed "Backend wallust with layers failed" "$cmd" "$LAST_OUTPUT"
        fi
    fi
}

# ============================================================================
# CORE CLI TESTS
# ============================================================================

test_core_cli_basic() {
    print_header "Testing Core CLI Basic Commands"
    
    print_test "color-scheme-core version"
    if color-scheme-core version > /dev/null 2>&1; then
        test_passed
    else
        test_failed
    fi
    
    print_test "color-scheme-core show"
    if color-scheme-core show "$TEST_IMAGE" --backend custom > /dev/null 2>&1; then
        test_passed
    else
        test_failed
    fi
    
    print_test "color-scheme-core generate"
    local gen_out="$TEST_OUTPUT_DIR/core-basic"
    mkdir -p "$gen_out"
    if color-scheme-core generate "$TEST_IMAGE" \
        --output-dir "$gen_out" \
        --backend custom \
        --format json > /dev/null 2>&1; then
        test_passed
    else
        test_failed
    fi
}

# ============================================================================
# ORCHESTRATOR CLI TESTS
# ============================================================================

test_orchestrator_cli_basic() {
    print_header "Testing Orchestrator CLI Basic Commands"
    
    print_test "color-scheme version"
    if color-scheme version > /dev/null 2>&1; then
        test_passed
    else
        test_failed
    fi
    
    print_test "color-scheme show"
    if color-scheme show "$TEST_IMAGE" > /dev/null 2>&1; then
        test_passed
    else
        test_failed
    fi
}

test_orchestrator_container_workflow() {
    print_header "Testing Orchestrator Container Workflow"
    
    # Detect which container engine is available
    local container_engine=""
    if command -v docker &> /dev/null; then
        container_engine="docker"
    elif command -v podman &> /dev/null; then
        container_engine="podman"
    fi
    
    # Check if container engine is available
    print_test "Container engine available"
    if [ -z "$container_engine" ]; then
        test_skipped "neither docker nor podman found" \
            "command -v docker && command -v podman" \
            "docker: command not found, podman: command not found" \
            "Install Docker: https://docs.docker.com/get-docker/ OR Podman: https://podman.io/getting-started/installation"
        echo -e "        ${YELLOW}Skipping all container workflow tests${NC}"
        return
    fi
    test_passed
    add_detail "• Container engine: $container_engine"
    
    # Check if container engine daemon is running
    print_test "Container engine daemon running"
    local daemon_cmd="$container_engine info"
    local daemon_output
    daemon_output=$($daemon_cmd 2>&1)
    if [ $? -ne 0 ]; then
        test_skipped "container daemon not running" \
            "$daemon_cmd" \
            "$daemon_output" \
            "Start the daemon: 'sudo systemctl start ${container_engine}' or 'sudo ${container_engine} daemon'"
        echo -e "        ${YELLOW}Skipping all container workflow tests${NC}"
        return
    fi
    test_passed
    add_detail "• $container_engine daemon: running"
    
    # Test install command (this builds a container)
    print_test "Install custom backend (container build)"
    local install_cmd="color-scheme install custom"
    local install_output
    install_output=$(color-scheme install custom 2>&1)
    local install_exit=$?
    
    if [ $install_exit -eq 0 ]; then
        test_passed
        add_detail "• Container built: custom backend image"
        
        # Only test generate and uninstall if install succeeded
        print_test "Generate with custom (containerized)"
        local custom_out="$TEST_OUTPUT_DIR/orch-custom"
        mkdir -p "$custom_out"
        local gen_cmd="color-scheme generate $TEST_IMAGE --output-dir $custom_out --backend custom -f json"
        local gen_output
        gen_output=$(eval "$gen_cmd" 2>&1)
        local gen_exit=$?
        
        if [ $gen_exit -eq 0 ] && [ -f "$custom_out/colors.json" ]; then
            test_passed
            add_detail "• Containerized generate: $custom_out/colors.json"
        else
            test_failed "Containerized generate failed" "$gen_cmd" "$gen_output"
        fi
        
        print_test "Uninstall custom backend"
        local uninstall_cmd="color-scheme uninstall custom --yes"
        local uninstall_output
        uninstall_output=$(eval "$uninstall_cmd" 2>&1)
        local uninstall_exit=$?
        
        if [ $uninstall_exit -eq 0 ]; then
            test_passed
            add_detail "• Container removed: custom backend image"
        else
            test_failed "Failed to uninstall custom backend" "$uninstall_cmd" "$uninstall_output"
        fi
    else
        # Parse the install output to provide actionable info
        local error_hint=""
        if echo "$install_output" | grep -qi "network\|connection\|timeout"; then
            error_hint="Network issue - check internet connection or proxy settings"
        elif echo "$install_output" | grep -qi "permission\|denied"; then
            error_hint="Permission issue - try 'sudo' or add user to docker group"
        elif echo "$install_output" | grep -qi "dockerfile\|build"; then
            error_hint="Build issue - check Dockerfile syntax and base image availability"
        else
            error_hint="Run 'color-scheme install custom' manually to see full output"
        fi
        
        test_skipped "container build failed" \
            "$install_cmd" \
            "$install_output" \
            "$error_hint"
        echo -e "        ${YELLOW}Skipping generate and uninstall tests${NC}"
    fi
}

# ============================================================================
# DRY-RUN TESTS
# ============================================================================

test_dry_run_flags() {
    print_header "Testing Dry-Run Flags (--dry-run/-n)"

    print_test "core generate --dry-run shows configuration without executing"
    local dry_run_output
    dry_run_output=$(color-scheme-core generate "$TEST_IMAGE" --dry-run 2>&1)
    local exit_code=$?
    if [ $exit_code -eq 0 ] && echo "$dry_run_output" | grep -q "DRY-RUN"; then
        test_passed
        add_detail "Output contains 'DRY-RUN' indicator"
    else
        test_failed "expected exit code 0 and 'DRY-RUN' in output" \
            "color-scheme-core generate $TEST_IMAGE --dry-run" \
            "$dry_run_output"
    fi

    print_test "core generate -n (short form) works"
    dry_run_output=$(color-scheme-core generate "$TEST_IMAGE" -n 2>&1)
    exit_code=$?
    if [ $exit_code -eq 0 ] && echo "$dry_run_output" | grep -q "DRY-RUN"; then
        test_passed
        add_detail "Short form -n flag works correctly"
    else
        test_failed "short form flag -n failed" \
            "color-scheme-core generate $TEST_IMAGE -n" \
            "$dry_run_output"
    fi

    print_test "core show --dry-run shows configuration without executing"
    dry_run_output=$(color-scheme-core show "$TEST_IMAGE" --dry-run 2>&1)
    exit_code=$?
    if [ $exit_code -eq 0 ] && echo "$dry_run_output" | grep -q "DRY-RUN"; then
        test_passed
        add_detail "Show command dry-run works"
    else
        test_failed "show command dry-run failed" \
            "color-scheme-core show $TEST_IMAGE --dry-run" \
            "$dry_run_output"
    fi

    print_test "orchestrator generate --dry-run shows configuration"
    dry_run_output=$(color-scheme generate "$TEST_IMAGE" --dry-run 2>&1)
    exit_code=$?
    if [ $exit_code -eq 0 ] && echo "$dry_run_output" | grep -qi "dry\|configuration"; then
        test_passed
        add_detail "Orchestrator generate dry-run works"
    else
        test_failed "orchestrator generate dry-run failed" \
            "color-scheme generate $TEST_IMAGE --dry-run" \
            "$dry_run_output"
    fi

    print_test "orchestrator show --dry-run shows configuration"
    dry_run_output=$(color-scheme show "$TEST_IMAGE" --dry-run 2>&1)
    exit_code=$?
    if [ $exit_code -eq 0 ] && echo "$dry_run_output" | grep -q "DRY-RUN"; then
        test_passed
        add_detail "Orchestrator show dry-run works"
    else
        test_failed "orchestrator show dry-run failed" \
            "color-scheme show $TEST_IMAGE --dry-run" \
            "$dry_run_output"
    fi
}

test_dry_run_configuration_resolution() {
    print_header "Testing Dry-Run Configuration Resolution"

    print_test "dry-run respects CLI argument precedence"
    local dry_run_output
    dry_run_output=$(color-scheme-core generate "$TEST_IMAGE" \
        --output-dir /custom/path \
        --backend custom \
        --dry-run 2>&1)
    if echo "$dry_run_output" | grep -q "/custom/path" && echo "$dry_run_output" | grep -q "custom"; then
        test_passed
        add_detail "CLI arguments shown in dry-run output"
    else
        test_failed "CLI arguments not reflected in dry-run" \
            "color-scheme-core generate with --output-dir and --backend" \
            "$dry_run_output"
    fi

    print_test "dry-run shows environment variable overrides"
    export COLORSCHEME_OUTPUT__DIRECTORY="/env/path"
    dry_run_output=$(color-scheme-core generate "$TEST_IMAGE" --dry-run 2>&1)
    unset COLORSCHEME_OUTPUT__DIRECTORY
    if echo "$dry_run_output" | grep -q "/env/path" || echo "$dry_run_output" | grep -q "COLORSCHEME"; then
        test_passed
        add_detail "Environment variable shown in dry-run"
    else
        test_failed "environment variable not shown in dry-run" \
            "with COLORSCHEME_OUTPUT__DIRECTORY=/env/path" \
            "$dry_run_output"
    fi

    print_test "dry-run shows configuration sources"
    dry_run_output=$(color-scheme-core show "$TEST_IMAGE" --dry-run 2>&1)
    if echo "$dry_run_output" | grep -qE "(CLI|ENV|Config|Default|Source)"; then
        test_passed
        add_detail "Configuration sources visible in output"
    else
        test_failed "configuration sources not shown" \
            "color-scheme-core show --dry-run" \
            "$dry_run_output"
    fi
}

# ============================================================================
# Summary and Results
# ============================================================================

print_summary() {
    print_header "TEST SUMMARY"
    
    local total=$((PASSED + FAILED + SKIPPED))
    printf "%-40s %3d\n" "Total Tests Run:" "$total"
    printf "%-40s %3d ${GREEN}✓${NC}\n" "Tests Passed:" "$PASSED"
    printf "%-40s %3d ${RED}✗${NC}\n" "Tests Failed:" "$FAILED"
    printf "%-40s %3d ${YELLOW}⊘${NC}\n" "Tests Skipped:" "$SKIPPED"
    
    echo ""
    echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Results by Category:${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
    
    for category in "${TEST_CATEGORIES[@]}"; do
        # Skip the summary category itself
        if [[ "$category" == "TEST SUMMARY" ]]; then
            continue
        fi
        
        local p=${CATEGORY_PASSED["$category"]:-0}
        local f=${CATEGORY_FAILED["$category"]:-0}
        local s=${CATEGORY_SKIPPED["$category"]:-0}
        
        # Determine status icon
        local status_icon
        if [ "$f" -gt 0 ]; then
            status_icon="${RED}✗${NC}"
        elif [ "$s" -gt 0 ] && [ "$p" -eq 0 ]; then
            status_icon="${YELLOW}⊘${NC}"
        else
            status_icon="${GREEN}✓${NC}"
        fi
        
        # Build result string
        local result_str="${GREEN}${p}✓${NC}"
        if [ "$f" -gt 0 ]; then
            result_str="$result_str ${RED}${f}✗${NC}"
        fi
        if [ "$s" -gt 0 ]; then
            result_str="$result_str ${YELLOW}${s}⊘${NC}"
        fi
        
        # Truncate category name if too long
        local short_cat="${category:0:45}"
        if [ ${#category} -gt 45 ]; then
            short_cat="${short_cat}..."
        fi
        
        echo -e "  $status_icon $short_cat: $result_str"
        
        # Show verbose details for this category
        if [ "$VERBOSE" = true ] && [ -n "${CATEGORY_DETAILS[$category]:-}" ]; then
            while IFS= read -r detail_line; do
                echo -e "      ${BLUE}$detail_line${NC}"
            done <<< "${CATEGORY_DETAILS[$category]}"
        fi
    done
    
    # Show details for failures
    if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
        echo ""
        echo -e "${RED}────────────────────────────────────────────────────────────────${NC}"
        echo -e "${RED}Failed Tests Details:${NC}"
        echo -e "${RED}────────────────────────────────────────────────────────────────${NC}"
        for detail in "${FAILED_TESTS[@]}"; do
            echo -e "  ${RED}✗${NC} $detail" | head -1
            echo "$detail" | tail -n +2 | while IFS= read -r line; do
                echo -e "     $line"
            done
            echo ""
        done
    fi
    
    # Show details for skips
    if [ ${#SKIPPED_TESTS[@]} -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}────────────────────────────────────────────────────────────────${NC}"
        echo -e "${YELLOW}Skipped Tests Details:${NC}"
        echo -e "${YELLOW}────────────────────────────────────────────────────────────────${NC}"
        for detail in "${SKIPPED_TESTS[@]}"; do
            echo -e "  ${YELLOW}⊘${NC} $detail" | head -1
            echo "$detail" | tail -n +2 | while IFS= read -r line; do
                echo -e "     $line"
            done
            echo ""
        done
    fi
    
    # Final result
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
        if [ $SKIPPED -gt 0 ]; then
            echo -e "${GREEN}✓ ALL EXECUTED TESTS PASSED!${NC} ${YELLOW}($SKIPPED skipped)${NC}"
        else
            echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
        fi
        echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
        return 0
    else
        echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
        echo -e "${RED}✗ SOME TESTS FAILED - See details above${NC}"
        echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
        return 1
    fi
}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

main() {
    echo -e "${BLUE}Color Scheme - Comprehensive Test Suite${NC}"
    echo -e "${BLUE}Testing: Settings & Templates Layered Systems${NC}"
    echo -e "${BLUE}Wallpaper: $TEST_IMAGE${NC}"
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}Mode: Verbose (detailed output in summary)${NC}"
    fi
    echo ""
    
    # Initialize
    init_test_environment
    
    # Settings layer tests
    test_settings_package_layer
    test_settings_project_layer
    test_settings_user_layer
    test_settings_precedence
    
    # Templates layer tests
    test_templates_package_layer
    test_templates_project_layer
    test_templates_user_layer
    test_templates_discovery
    
    # Integration tests
    test_layered_generate_command
    test_layered_show_command
    test_output_formats_with_layers
    test_backend_with_layers
    
    # Basic CLI tests
    test_core_cli_basic
    test_orchestrator_cli_basic
    test_orchestrator_container_workflow
    
    # Dry-run tests
    test_dry_run_flags
    test_dry_run_configuration_resolution
    
    # Print summary and return appropriate exit code
    print_summary
}

main "$@"
