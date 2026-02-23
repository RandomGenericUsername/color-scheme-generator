# Test Spec and Behavior Catalog

## Test execution
- Test command used: uv run pytest packages/ -v (unit + integration, excludes smoke)
- Last run result: NOT RUN (static analysis only; all assertions extracted from source)
- Notes: External backends (pywal, wallust) are mocked in unit tests. Custom backend is always available.

---

## Behaviors

### BHV-0001 — Core CLI: generate command produces output files
- Title: `color-scheme-core generate` extracts colors and writes output files
- Publicity: public
- Preconditions: valid image file exists; at least one backend available
- Steps: invoke `color-scheme-core generate <IMAGE_PATH> --output-dir <DIR> --backend custom`
- Expected: exit code 0; stdout contains "Generated color scheme"; output files created in DIR
- Errors: exit 1 if image not found; exit 1 if backend unavailable
- Evidence: packages/core/tests/integration/test_cli_generate.py lines 24-67

### BHV-0002 — Core CLI: generate writes only requested formats
- Title: `--format` flag restricts output to specified formats
- Publicity: public
- Preconditions: valid image; custom backend
- Steps: invoke generate with `--format json --format css`
- Expected: only `colors.json` and `colors.css` created; `colors.sh` NOT created
- Errors: N/A
- Evidence: packages/core/tests/integration/test_cli_generate.py lines 69-100

### BHV-0003 — Core CLI: generate with invalid image returns exit 1
- Title: Missing image path causes exit code 1
- Publicity: public
- Preconditions: image path does not exist
- Steps: invoke generate with non-existent path
- Expected: exit code 1; stdout contains "Error"
- Evidence: packages/core/tests/integration/test_cli_generate.py lines 102-112

### BHV-0004 — Core CLI: generate --dry-run shows plan and exits 0
- Title: `--dry-run` flag shows execution plan without writing files
- Publicity: public
- Preconditions: any valid image path
- Steps: invoke generate with `--dry-run`
- Expected: exit code 0; stdout contains "DRY-RUN", "Execution Plan", "color-scheme-core generate"
- Errors: N/A
- Evidence: packages/core/tests/integration/test_cli_dry_run.py lines 24-44

### BHV-0005 — Core CLI: generate -n is alias for --dry-run
- Title: `-n` short flag works as alias for `--dry-run`
- Publicity: public
- Steps: invoke generate with `-n`
- Expected: exit code 0; stdout contains "DRY-RUN"
- Evidence: packages/core/tests/integration/test_cli_dry_run.py lines 36-44

### BHV-0006 — Core CLI: dry-run creates no output files
- Title: Dry-run mode does not write any files to output directory
- Publicity: public
- Steps: invoke generate with `--dry-run --output-dir <DIR>`
- Expected: DIR is empty after command
- Evidence: packages/core/tests/integration/test_cli_dry_run.py lines 46-64

### BHV-0007 — Core CLI: show command displays color tables
- Title: `color-scheme-core show` displays background, foreground, cursor, and ANSI colors
- Publicity: public
- Preconditions: valid image
- Steps: invoke show with `--backend custom`
- Expected: exit code 0; stdout contains "Background" or "background"; contains "#" (hex codes)
- Evidence: packages/core/tests/integration/test_cli_show.py lines 24-48

### BHV-0008 — Core CLI: show --dry-run does not display terminal colors
- Title: show --dry-run shows plan only, not actual color tables
- Publicity: public
- Steps: invoke show with `--dry-run`
- Expected: stdout contains "DRY-RUN", "Execution Plan"; does NOT contain "Terminal Colors (ANSI)"
- Evidence: packages/core/tests/integration/test_cli_dry_run.py lines 101-134

### BHV-0009 — BackendFactory: auto_detect preference is wallust > pywal > custom
- Title: auto_detect returns wallust when all available, then pywal, then custom
- Publicity: public
- Steps: call factory.auto_detect() with all backends available
- Expected: returns Backend.WALLUST
- Steps2: only pywal available → returns Backend.PYWAL
- Steps3: none available → returns Backend.CUSTOM (fallback)
- Evidence: packages/core/tests/unit/test_factory.py lines 65-107; factory.py lines 130

### BHV-0010 — BackendFactory: create raises BackendNotAvailableError when binary missing
- Title: create() raises BackendNotAvailableError if requested backend is not installed
- Publicity: public
- Steps: call factory.create(Backend.PYWAL) when wal binary absent
- Expected: raises BackendNotAvailableError
- Evidence: packages/core/tests/unit/test_factory.py lines 47-53

### BHV-0011 — BackendFactory: detect_available handles exceptions gracefully
- Title: detect_available returns empty list if all backends throw exceptions
- Publicity: internal
- Steps: all backend is_available() methods raise exceptions
- Expected: returns []
- Evidence: packages/core/tests/unit/test_factory.py lines 87-96

### BHV-0012 — Color: validate hex pattern and RGB range
- Title: Color rejects invalid hex pattern and out-of-range RGB values
- Publicity: public
- Steps: construct Color with invalid hex or RGB values
- Expected: raises ValueError
- Specific: hex must match ^#[0-9a-fA-F]{6}$; each RGB channel 0-255
- Evidence: packages/core/tests/unit/test_types.py lines 22-111

### BHV-0013 — Color: hex and RGB must be consistent
- Title: Color rejects mismatched hex and RGB values
- Publicity: public
- Steps: Color(hex="#FF5733", rgb=(255, 255, 255))
- Expected: raises ValueError matching "RGB .* does not match hex"
- Evidence: packages/core/tests/unit/test_types.py lines 73-82

### BHV-0014 — Color.adjust_saturation: returns new Color with modified saturation
- Title: adjust_saturation(1.0) returns color with same hex; other factors change hex
- Publicity: public
- Steps: call adjust_saturation(1.0); call adjust_saturation(0.5)
- Expected: 1.0 → same hex; 0.5 → different hex
- Evidence: packages/core/tests/unit/test_types.py lines 25-35

### BHV-0015 — ColorScheme: requires exactly 16 colors
- Title: ColorScheme validates colors list has exactly 16 entries
- Publicity: public
- Steps: create ColorScheme with 15 colors
- Expected: raises ValueError
- Evidence: packages/core/tests/unit/test_types.py lines 135-147

### BHV-0016 — GeneratorConfig.from_settings: creates config from AppConfig
- Title: from_settings() populates all fields from AppConfig with optional overrides
- Publicity: public
- Steps: call GeneratorConfig.from_settings(app_config)
- Expected: config.color_count == 16; backend, output_dir, formats non-None
- Evidence: packages/core/tests/unit/test_types.py lines 153-162

### BHV-0017 — SchemaRegistry: duplicate namespace raises SettingsRegistryError
- Title: Registering the same namespace twice raises SettingsRegistryError
- Publicity: public
- Steps: register("core", ...) twice
- Expected: raises SettingsRegistryError on second call
- Evidence: packages/settings/tests/test_registry.py lines 67-70

### BHV-0018 — SchemaRegistry: get unregistered namespace raises SettingsRegistryError
- Title: get() for unknown namespace raises SettingsRegistryError
- Publicity: public
- Steps: SchemaRegistry.get("nonexistent")
- Expected: raises SettingsRegistryError
- Evidence: packages/settings/tests/test_registry.py lines 81-83

### BHV-0019 — SettingsLoader: layers arrive in order package, project, user
- Title: discover_layers() returns layers in priority order: package first, user last
- Publicity: internal
- Steps: loader with all three files; filter by namespace
- Expected: layer_names == ["package", "project", "user"]
- Evidence: packages/settings/tests/test_loader.py lines 127-143

### BHV-0020 — deep_merge: lists are replaced entirely (not merged)
- Title: When override contains a list, it replaces the base list completely
- Publicity: internal
- Steps: deep_merge({"formats": ["json", "css", "yaml"]}, {"formats": ["json"]})
- Expected: result == {"formats": ["json"]}
- Evidence: packages/settings/tests/test_merger.py lines 46-56

### BHV-0021 — Settings pipeline: CLI overrides everything
- Title: get_config(overrides) values take precedence over all layers
- Publicity: public
- Steps: configure with all layers; call get_config({"core.generation.saturation_adjustment": 0.5, ...})
- Expected: config.core.generation.saturation_adjustment == 0.5
- Evidence: packages/settings/tests/test_pipeline.py lines 155-181

### BHV-0022 — Settings pipeline: load_config() caches result
- Title: Second call to load_config() returns same object (identity)
- Publicity: public
- Steps: config1 = load_config(); config2 = load_config()
- Expected: config1 is config2
- Evidence: packages/settings/tests/test_pipeline.py lines 183-191

### BHV-0023 — ContainerSettings: engine accepts only docker or podman (case-insensitive)
- Title: ContainerSettings rejects engines other than docker/podman; accepts uppercase
- Publicity: public
- Steps: ContainerSettings(engine="invalid_engine")
- Expected: raises ValidationError containing "Invalid container engine"
- Steps2: ContainerSettings(engine="DOCKER") → engine == "docker"
- Evidence: packages/orchestrator/tests/unit/test_settings_validation.py lines 12-33

### BHV-0024 — ContainerManager: image name format
- Title: get_image_name() returns "color-scheme-<backend>:latest" (with registry prefix if set)
- Publicity: public
- Steps: get_image_name(Backend.PYWAL) → "color-scheme-pywal:latest"
- Steps2: with image_registry="ghcr.io/myorg" → "ghcr.io/myorg/color-scheme-pywal:latest"
- Evidence: packages/orchestrator/tests/unit/test_image_names.py lines 14-62

### BHV-0025 — install command: default engine is docker
- Title: install without --engine uses docker
- Publicity: public
- Steps: invoke install pywal (no --engine)
- Expected: subprocess called with "docker" as first argument
- Evidence: packages/orchestrator/tests/unit/test_install_unit.py lines 17-39

### BHV-0026 — install command: rejects invalid engine
- Title: install with invalid engine value returns exit 1
- Publicity: public
- Steps: color-scheme install pywal --engine invalid
- Expected: exit code 1; stdout contains "Invalid engine" and "Must be 'docker' or 'podman'"
- Evidence: packages/orchestrator/tests/unit/test_install_unit.py lines 87-97

### BHV-0027 — install command: no backend arg installs all three backends
- Title: When backend is omitted, installs pywal, wallust, and custom
- Publicity: public
- Steps: invoke install (no backend argument)
- Expected: subprocess called at least 3 times
- Evidence: packages/orchestrator/tests/unit/test_install_unit.py lines 153-173

### BHV-0028 — install command: build command structure
- Title: docker build command uses -f <dockerfile> -t <image-name> <context>
- Publicity: internal
- Steps: invoke install pywal
- Expected: subprocess call args: [docker, build, -f, <path>, -t, color-scheme-pywal:latest, <project_root>]
- Evidence: packages/orchestrator/tests/unit/test_install_unit.py lines 187-213

### BHV-0029 — install command: --dry-run shows build plan
- Title: install --dry-run and -n show DRY-RUN output without building
- Publicity: public
- Steps: invoke install custom --dry-run
- Expected: exit 0; stdout contains "DRY-RUN", "Build Plan"
- Evidence: packages/orchestrator/tests/integration/test_cli_dry_run.py lines 17-36

### BHV-0030 — uninstall command: --dry-run bypasses confirmation
- Title: uninstall --dry-run shows removal plan without asking for confirmation
- Publicity: public
- Steps: invoke uninstall custom --dry-run (with input "n")
- Expected: exit 0; "Are you sure" NOT in stdout
- Evidence: packages/orchestrator/tests/integration/test_cli_dry_run.py lines 68-79

### BHV-0031 — ConfigResolver: COLORSCHEME_ env vars mapped to nested config
- Title: COLORSCHEME_SECTION__KEY env vars are collected with double underscore as nesting separator
- Publicity: public
- Steps: set COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom
- Expected: result["generation"]["default_backend"] == "custom"
- Evidence: packages/settings/tests/test_resolver.py lines 169-183

### BHV-0032 — ConfigResolver: COLOR_SCHEME_TEMPLATES env var collected
- Title: COLOR_SCHEME_TEMPLATES env var maps to templates.directory
- Publicity: public
- Steps: set COLOR_SCHEME_TEMPLATES=/custom/templates
- Expected: result["templates"]["directory"] == "/custom/templates"
- Evidence: packages/settings/tests/test_resolver.py lines 185-196

### BHV-0033 — TemplateRegistry: duplicate namespace raises TemplateRegistryError
- Title: Registering same namespace twice raises TemplateRegistryError
- Publicity: public
- Steps: TemplateRegistry.register("test", ...) twice
- Expected: raises TemplateRegistryError matching "already registered"
- Evidence: packages/templates/tests/test_registry.py lines 20-23

### BHV-0034 — install command: build success message
- Title: Successful build shows "Built successfully" and summary with "All backend images built successfully!"
- Publicity: public
- Steps: invoke install pywal, subprocess returns 0
- Expected: stdout contains "Built successfully", "Build Summary", "Success:", "All backend images built successfully!"
- Evidence: packages/orchestrator/tests/unit/test_install_unit.py lines 221-319

### BHV-0035 — install command: build failure reports failure
- Title: Failed build (non-zero returncode) shows "Build failed" and exit 1
- Publicity: public
- Steps: subprocess returns returncode=1
- Expected: exit code 1; stdout contains "Build failed"
- Evidence: packages/orchestrator/tests/unit/test_install_unit.py lines 241-263

### BHV-0036 — ContainerSettings: registry trailing slash is stripped
- Title: image_registry field strips trailing slashes
- Publicity: public
- Steps: ContainerSettings(image_registry="docker.io/") → image_registry == "docker.io"
- Evidence: packages/orchestrator/tests/unit/test_settings_validation.py lines 39-57
