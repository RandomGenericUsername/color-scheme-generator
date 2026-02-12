# Smoke Tests

This directory contains end-to-end smoke tests for the color-scheme CLI tools.

## Overview

The smoke test suite validates the complete CLI workflow including:
- Core CLI commands (`color-scheme-core`)
- Orchestrator CLI commands (`color-scheme`)
- All three backends: custom, pywal, wallust
- Real image processing with ImageMagick
- Container image building and execution
- Settings and templates layered configuration
- Dry-run functionality

## Usage

### Local Execution

```bash
# Run all backends
make smoke-test

# Run specific backend
make smoke-test-custom
make smoke-test-pywal
make smoke-test-wallust

# Verbose output
make smoke-test VERBOSE=true
```

### CI Execution

Smoke tests are triggered manually via GitHub Actions:
- Navigate to Actions → Select workflow → Run workflow
- Or via CLI: `gh workflow run smoke-test-custom.yml`

### With make push

```bash
make push SMOKE=true
```

## Test Script

`run-smoke-tests.sh` - Main smoke test script

**Arguments:**
- `<wallpaper-path>` - Path to test wallpaper (required)
- `--verbose` or `-v` - Show detailed test information

**Returns:**
- Exit 0: All tests passed
- Exit 1: Some tests failed

## Requirements

- Python 3.12+ with uv
- ImageMagick (`magick` command)
- Docker or Podman
- Optional backends:
  - Pywal: `pip install pywal`
  - Wallust: `cargo install wallust`

## Test Fixtures

- `../fixtures/test-wallpaper.jpg` - Sample wallpaper for testing

## Architecture

```
tests/smoke/
├── README.md              # This file
└── run-smoke-tests.sh     # Main test script

tests/fixtures/
└── test-wallpaper.jpg     # Test wallpaper image

.github/workflows/
├── smoke-test-custom.yml  # Custom backend workflow
├── smoke-test-pywal.yml   # Pywal backend workflow
└── smoke-test-wallust.yml # Wallust backend workflow
```

## Interpreting Results

The script tracks tests as:
- **PASS** (✓) - Test succeeded
- **FAIL** (✗) - Test failed (hard failure)
- **SKIP** (⊘) - Test skipped (missing optional dependency)

Summary shows:
- Total tests run
- Pass/Fail/Skip counts per category
- Detailed failure/skip information

## Adding New Tests

1. Add test function to `run-smoke-tests.sh`
2. Call function in `main()` execution flow
3. Use existing helper functions:
   - `print_header(category)` - Start new test category
   - `print_test(description)` - Print test name
   - `test_passed()` - Mark test passed
   - `test_failed(reason)` - Mark test failed
   - `test_skipped(reason, hint)` - Mark test skipped

Example:
```bash
test_my_new_feature() {
    print_header "Testing My New Feature"

    print_test "Feature does X correctly"
    if my_feature_works; then
        test_passed
    else
        test_failed "Feature failed to do X"
    fi
}
```
