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
