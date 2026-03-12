# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed (Dev Setup)

- Smoke test `print_summary` now prints test output directory before final banner, matching wallpaper-effects-generator convention
- Smoke workflow (`smoke-tests.yml`) now runs in verbose mode by default on `push` events for easier CI debugging
- `make smoke-test` targets now support `WALLPAPER=/path/to/image.jpg` override; default fixture path unchanged
