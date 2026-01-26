#!/usr/bin/env bash
#
# Development Environment Setup Script
# =====================================
# This script automates the setup of the development environment for color-scheme.
#
# System Requirements:
# - Python 3.12 or higher
# - Git
# - curl (for uv installation if needed)
# - bash or zsh shell
#
# What this script does:
# 1. Checks for required system dependencies (Python 3.12+, git)
# 2. Installs uv package manager if not present
# 3. Installs all project dependencies (core + orchestrator + dev tools)
# 4. Sets up pre-commit hooks for code quality
# 5. Verifies the installation by running tests
#
# Usage:
#   ./scripts/setup-dev.sh
#   ./scripts/setup-dev.sh --help

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source utility functions
source "$SCRIPT_DIR/utils.sh"

# Configuration
REQUIRED_PYTHON_VERSION="3.12"
UV_INSTALL_URL="https://astral.sh/uv/install.sh"

# Help message
show_help() {
    cat << EOF
Development Environment Setup Script

This script sets up your development environment for the color-scheme project.

USAGE:
    ./scripts/setup-dev.sh [OPTIONS]

OPTIONS:
    -h, --help              Show this help message and exit
    --skip-verification     Skip the final verification tests
    --no-precommit          Skip installing pre-commit hooks

SYSTEM REQUIREMENTS:
    - Python ${REQUIRED_PYTHON_VERSION}+
    - Git
    - curl (for uv installation)

WHAT IT DOES:
    1. Checks system prerequisites
    2. Installs uv package manager (if needed)
    3. Installs project dependencies
    4. Sets up pre-commit hooks
    5. Verifies installation

EOF
}

# Parse command line arguments
SKIP_VERIFICATION=false
NO_PRECOMMIT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --skip-verification)
            SKIP_VERIFICATION=true
            shift
            ;;
        --no-precommit)
            NO_PRECOMMIT=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to compare version numbers
version_ge() {
    # Returns 0 (true) if $1 >= $2
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Function to check Python version
check_python_version() {
    print_section "Checking Python Version"

    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        print_info "Please install Python ${REQUIRED_PYTHON_VERSION} or higher"
        print_info "Visit: https://www.python.org/downloads/"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f1,2)

    print_info "Found Python $PYTHON_VERSION"

    if ! version_ge "$PYTHON_MAJOR_MINOR" "$REQUIRED_PYTHON_VERSION"; then
        print_error "Python $PYTHON_VERSION is installed, but $REQUIRED_PYTHON_VERSION+ is required"
        print_info "Please upgrade Python to version $REQUIRED_PYTHON_VERSION or higher"
        exit 1
    fi

    print_success "Python version requirement satisfied"
}

# Function to check git
check_git() {
    print_section "Checking Git"

    if ! command_exists git; then
        print_error "Git is not installed"
        print_info "Please install git from your package manager or https://git-scm.com/"
        exit 1
    fi

    GIT_VERSION=$(git --version | awk '{print $3}')
    print_info "Found Git $GIT_VERSION"
    print_success "Git is installed"
}

# Function to check Docker or Podman (optional)
check_container_engine() {
    print_section "Checking Container Engine (Optional)"

    if command_exists docker; then
        DOCKER_VERSION=$(docker --version 2>&1 | awk '{print $3}' | tr -d ',')
        print_info "Found Docker $DOCKER_VERSION"
        print_success "Docker is available"
        return 0
    elif command_exists podman; then
        PODMAN_VERSION=$(podman --version 2>&1 | awk '{print $3}')
        print_info "Found Podman $PODMAN_VERSION"
        print_success "Podman is available"
        return 0
    else
        print_warning "Neither Docker nor Podman found"
        print_info "Container orchestration features will not be available"
        print_info "You can still use the core package for local color extraction"
        print_info "To enable containers later, install Docker: https://docs.docker.com/get-docker/"
        print_info "Or install Podman: https://podman.io/getting-started/installation"
        return 0
    fi
}

# Function to check and install uv
check_and_install_uv() {
    print_section "Checking uv Package Manager"

    if command_exists uv; then
        UV_VERSION=$(uv --version 2>&1 | awk '{print $2}')
        print_info "Found uv $UV_VERSION"
        print_success "uv is already installed"
        return 0
    fi

    print_warning "uv is not installed"
    print_info "Installing uv package manager..."

    if ! command_exists curl; then
        print_error "curl is required to install uv but is not found"
        print_info "Please install curl from your package manager"
        exit 1
    fi

    # Install uv
    if curl -LsSf "$UV_INSTALL_URL" | sh; then
        print_success "uv installed successfully"

        # Source the profile to get uv in PATH for this session
        if [ -f "$HOME/.cargo/env" ]; then
            source "$HOME/.cargo/env"
        fi

        # Verify installation
        if ! command_exists uv; then
            print_warning "uv was installed but is not in PATH"
            print_info "You may need to restart your shell or run: source \$HOME/.cargo/env"
            print_info "Trying to continue with direct path..."

            # Try to find uv in common locations
            if [ -f "$HOME/.cargo/bin/uv" ]; then
                export PATH="$HOME/.cargo/bin:$PATH"
                print_success "Found uv in ~/.cargo/bin"
            else
                print_error "Cannot find uv after installation"
                exit 1
            fi
        fi
    else
        print_error "Failed to install uv"
        print_info "Please install uv manually from: https://github.com/astral-sh/uv"
        exit 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_section "Installing Project Dependencies"

    cd "$REPO_ROOT"

    print_info "Running: uv sync"
    print_info "This will install all dependencies (core + orchestrator + dev tools)..."

    if uv sync; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Function to create necessary directories
create_directories() {
    print_section "Creating Necessary Directories"

    # Create config directory
    CONFIG_DIR="$HOME/.config/color-scheme"
    OUTPUT_DIR="$CONFIG_DIR/output"

    if [ ! -d "$CONFIG_DIR" ]; then
        print_info "Creating config directory: $CONFIG_DIR"
        mkdir -p "$CONFIG_DIR"
        print_success "Config directory created"
    else
        print_info "Config directory already exists: $CONFIG_DIR"
    fi

    if [ ! -d "$OUTPUT_DIR" ]; then
        print_info "Creating output directory: $OUTPUT_DIR"
        mkdir -p "$OUTPUT_DIR"
        print_success "Output directory created"
    else
        print_info "Output directory already exists: $OUTPUT_DIR"
    fi
}

# Function to install pre-commit hooks
install_precommit_hooks() {
    if [ "$NO_PRECOMMIT" = true ]; then
        print_section "Skipping Pre-commit Hooks"
        print_info "Pre-commit hooks installation skipped (--no-precommit flag)"
        return 0
    fi

    print_section "Installing Pre-commit Hooks"

    cd "$REPO_ROOT"

    # Check if .pre-commit-config.yaml exists
    if [ ! -f ".pre-commit-config.yaml" ]; then
        print_warning "No .pre-commit-config.yaml found"
        print_info "Skipping pre-commit hook installation"
        print_info "You can add a .pre-commit-config.yaml later and run: uv run pre-commit install"
        return 0
    fi

    print_info "Installing pre-commit hooks..."

    if uv run pre-commit install; then
        print_success "Pre-commit hooks installed successfully"
        print_info "Hooks will run automatically on git commit"
    else
        print_warning "Failed to install pre-commit hooks"
        print_info "You can install them later with: uv run pre-commit install"
    fi
}

# Function to verify installation
verify_installation() {
    if [ "$SKIP_VERIFICATION" = true ]; then
        print_section "Skipping Verification"
        print_info "Installation verification skipped (--skip-verification flag)"
        return 0
    fi

    print_section "Verifying Installation"

    cd "$REPO_ROOT"

    # Check if ruff is working
    print_info "Checking ruff..."
    if uv run ruff --version > /dev/null 2>&1; then
        print_success "ruff is working"
    else
        print_warning "ruff check failed"
    fi

    # Check if pytest is working
    print_info "Checking pytest..."
    if uv run pytest --version > /dev/null 2>&1; then
        print_success "pytest is working"
    else
        print_warning "pytest check failed"
    fi

    # Run config tests if they exist
    if [ -d "packages/core/tests/config" ]; then
        print_info "Running config tests to verify setup..."
        if uv run pytest packages/core/tests/config/ -v; then
            print_success "Configuration tests passed"
        else
            print_warning "Some tests failed - this might be expected if tests are still in development"
        fi
    else
        print_info "Config tests directory not found, skipping test verification"
    fi
}

# Function to print next steps
print_next_steps() {
    print_section "Setup Complete!"

    cat << EOF
Your development environment is ready to use.

NEXT STEPS:

  1. Start developing:
     $ uv run color-scheme --help

  2. Run tests:
     $ uv run pytest                    # Run all tests
     $ uv run pytest -n auto            # Run tests in parallel
     $ uv run pytest -v                 # Verbose output

  3. Code quality tools:
     $ uv run ruff check .              # Lint code
     $ uv run ruff format .             # Format code
     $ uv run black .                   # Alternative formatter
     $ uv run mypy src/                 # Type checking
     $ uv run bandit -r src/            # Security scanning

  4. Pre-commit hooks:
     $ uv run pre-commit run --all-files    # Run hooks manually

  5. Learn more:
     - Read CLAUDE.md for project guidance
     - Check docs/ for detailed documentation
     - Review packages/core/ and packages/orchestrator/ for code structure

HELPFUL COMMANDS:

  uv sync                               # Update dependencies
  uv add <package>                      # Add a new dependency
  uv run <command>                      # Run a command in the virtual environment

Happy coding!
EOF
}

# Main execution
main() {
    print_section "Color Scheme Development Setup"
    print_info "Setting up development environment for color-scheme"
    print_info "Repository: $REPO_ROOT"
    echo ""

    # Run all setup steps
    check_python_version
    check_git
    check_container_engine
    check_and_install_uv
    install_dependencies
    create_directories
    install_precommit_hooks
    verify_installation

    # Print next steps
    print_next_steps
}

# Run main function
main
