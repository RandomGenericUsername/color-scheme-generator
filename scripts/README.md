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
