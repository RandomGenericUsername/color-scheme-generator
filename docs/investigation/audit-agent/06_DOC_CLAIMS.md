# Documentation Claims Catalog

Claim IDs: `DOC-0001`, `DOC-0002`, ...

Required fields:
- Text (atomic)
- Source location (file + line range)
- Category (how-to/reference/concept/contract/troubleshooting)
- Evidence status (verified/unverified/contradicted)
- Evidence pointers

---

## CLI Core Commands

- DOC-0001:
  - Text: "Auto-detection attempts to find an available backend in order: pywal, wallust, custom."
  - Source: docs/reference/cli/core-commands.md lines 66, 107-110
  - Category: reference/contract
  - Evidence status: contradicted
  - Evidence: factory.py line 130 iterates [WALLUST, PYWAL, CUSTOM]; test_factory.py line 71 asserts WALLUST is selected when all available

- DOC-0002:
  - Text: "color-scheme-core generate" writes output files to output directory in formats: json, sh, css, gtk.css, yaml, sequences, rasi, scss (all 8 by default)
  - Source: docs/reference/cli/core-commands.md lines 67, 119-126
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: test_cli_generate.py lines 24-67; enums.py lines 22-31

- DOC-0003:
  - Text: "If not specified, all 8 formats are generated."
  - Source: docs/reference/cli/core-commands.md line 67
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: config/defaults.py lines 13-22 (default_formats = all 8 formats)

- DOC-0004:
  - Text: "Output directory default is ~/.config/color-scheme/output"
  - Source: docs/reference/cli/core-commands.md line 65
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: config/defaults.py line 12: output_directory = Path.home() / ".config" / "color-scheme" / "output"

- DOC-0005:
  - Text: "--dry-run shows what would be done without executing"
  - Source: docs/reference/cli/core-commands.md (not documented — see finding)
  - Category: reference/contract
  - Evidence status: unverified (absent from docs)
  - Evidence: test_cli_dry_run.py lines 24-64; cli/main.py lines 96-154

- DOC-0006:
  - Text: "Saturation adjustment factor range is 0.0 to 2.0 (default 1.0)"
  - Source: docs/reference/cli/core-commands.md line 68
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: cli/main.py lines 88-95 (min=0.0, max=2.0); config/defaults.py line 26: saturation_adjustment = 1.0

- DOC-0007:
  - Text: "Exit code 0 on success, exit code 1 on error"
  - Source: docs/reference/cli/core-commands.md lines 144-147
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: test_cli_generate.py lines 40, 111; cli/main.py (typer.Exit(1) on all errors, typer.Exit(0) on dry-run)

- DOC-0008:
  - Text: "Backend auto-detection: pywal checks if 'wal' binary is in PATH; wallust checks if 'wallust' binary is in PATH; custom is always available"
  - Source: docs/reference/cli/core-commands.md lines 107-110
  - Category: reference/concept
  - Evidence status: verified (mechanism correct, order wrong — see DOC-0001)
  - Evidence: backends/pywal.py (is_available via shutil.which); backends/custom.py (always returns True); test_factory.py

- DOC-0009:
  - Text: "Output files are named colors.<format> (e.g., colors.json, colors.sh)"
  - Source: docs/reference/cli/core-commands.md lines 119-126
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: cli/main.py line 236: f"colors.{fmt.value}"; test_cli_generate.py lines 92-96

---

## CLI Orchestrator Commands

- DOC-0010:
  - Text: "Orchestrator generate uses containerized backend; image names: color-scheme-pywal:latest, color-scheme-wallust:latest, color-scheme-custom:latest"
  - Source: docs/reference/cli/orchestrator-commands.md lines 125-129
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: test_image_names.py lines 14-48; container/manager.py

- DOC-0011:
  - Text: "Volume mounts: IMAGE_PATH → /input/image.png (ro); --output-dir → /output (rw); template dir → /templates (ro)"
  - Source: docs/reference/cli/orchestrator-commands.md lines 172-177
  - Category: reference/contract
  - Evidence status: unverified (requires smoke tests to fully verify)
  - Evidence: orchestrator-commands.md (doc claim only; unit tests for mounts exist in test_container_manager_mounts.py, test_volume_mounts.py)

- DOC-0012:
  - Text: "install command supports --engine docker or --engine podman; default is docker"
  - Source: docs/reference/cli/orchestrator-commands.md lines 340, 413
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: test_install_unit.py lines 17-39; test_settings_validation.py lines 19-25; install.py lines 90-101

- DOC-0013:
  - Text: "uninstall supports --yes/-y to skip confirmation prompt"
  - Source: docs/reference/cli/orchestrator-commands.md lines 553-554
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: test_uninstall_unit.py (confirmation tests)

- DOC-0014:
  - Text: "orchestrator show delegates to color-scheme-core show (runs on host, no container)"
  - Source: docs/reference/cli/orchestrator-commands.md lines 220-222
  - Category: reference/concept
  - Evidence status: verified
  - Evidence: orchestrator/cli/main.py lines 270-292 (subprocess calls color-scheme-core show)

- DOC-0015:
  - Text: "install --dry-run and uninstall --dry-run are supported" (ABSENT from doc)
  - Source: docs/reference/cli/orchestrator-commands.md — NOT documented
  - Category: reference/contract
  - Evidence status: contradicted (behavior exists but is undocumented)
  - Evidence: install.py lines 34-87; test_cli_dry_run.py (orchestrator) lines 17-79

---

## Settings API

- DOC-0016:
  - Text: "get_config(**overrides) takes keyword arguments with dotted-key paths"
  - Source: docs/reference/api/settings-api.md lines 147-175
  - Category: reference/contract
  - Evidence status: contradicted
  - Evidence: packages/settings/src/color_scheme_settings/__init__.py line 84: signature is get_config(overrides: dict[str, Any] | None = None); test_pipeline.py line 170: called as get_config({"core.generation.saturation_adjustment": 0.5, ...})

- DOC-0017:
  - Text: "load_config() result is cached; second call returns same object"
  - Source: docs/reference/api/settings-api.md lines 101-114
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: test_pipeline.py lines 183-191 (assert config1 is config2)

- DOC-0018:
  - Text: "SchemaRegistry.register() raises SettingsRegistryError on duplicate namespace"
  - Source: docs/reference/api/settings-api.md lines 199-200
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: test_registry.py lines 67-70; registry.py lines 44-48

- DOC-0019:
  - Text: "Settings layers: Package (lowest) → Project → User → CLI (highest)"
  - Source: docs/reference/api/settings-api.md lines 13-19
  - Category: reference/concept
  - Evidence status: verified
  - Evidence: test_pipeline.py lines 98-181; loader.py layers 1-3; ConfigResolver._apply_precedence

- DOC-0020:
  - Text: "COLORSCHEME_SECTION__KEY environment variables are collected (double underscore as separator)"
  - Source: docs/reference/api/settings-api.md (resolver section); docs/reference/cli/core-commands.md lines 352-358
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: resolver.py lines 154-191; test_resolver.py lines 169-196

- DOC-0021:
  - Text: "reload_config() forces fresh load; returned object is not same as previous"
  - Source: docs/reference/api/settings-api.md lines 123-143
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: test_pipeline.py lines 193-201 (assert config1 is not config2)

---

## Types API

- DOC-0022:
  - Text: "Color.hex must match pattern ^#[0-9a-fA-F]{6}$"
  - Source: docs/reference/api/types.md lines 33-34
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: types.py line 23: hex: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")

- DOC-0023:
  - Text: "Color.rgb must be tuple[int, int, int] with each value 0-255"
  - Source: docs/reference/api/types.md line 34
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: types.py lines 27-33; test_types.py lines 37-57

- DOC-0024:
  - Text: "ColorScheme.colors must have exactly 16 items"
  - Source: docs/reference/api/types.md line 133
  - Category: reference/contract
  - Evidence status: verified
  - Evidence: types.py line 100: colors: list[Color] = Field(..., min_length=16, max_length=16); test_types.py lines 135-147

- DOC-0025:
  - Text: "GeneratorConfig.color_count is always 16 (hardcoded, not configurable)"
  - Source: docs/reference/api/types.md line 223
  - Category: reference/concept
  - Evidence status: verified
  - Evidence: types.py line 125: color_count: int = 16  # Hardcoded, not configurable
