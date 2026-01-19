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
