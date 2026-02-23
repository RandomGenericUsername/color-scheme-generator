# Topic Map (Repo-wide)

## File summaries

| File | Primary topics | Secondary topics | Key entities | Notes |
|------|----------------|------------------|--------------|-------|
| packages/core/src/color_scheme/cli/main.py | core-cli, generate, show | dry-run, error-handling | app (Typer), generate(), show(), version() | Entry: color-scheme-core |
| packages/core/src/color_scheme/cli/dry_run.py | dry-run | reporter | GenerateDryRunReporter, ShowDryRunReporter | |
| packages/core/src/color_scheme/factory.py | backends, auto-detect | factory | BackendFactory, auto_detect(), detect_available() | Preference: wallust>pywal>custom |
| packages/core/src/color_scheme/core/types.py | types | Color, ColorScheme, GeneratorConfig | Color, ColorScheme, GeneratorConfig | Core data models |
| packages/core/src/color_scheme/core/exceptions.py | exceptions | error-hierarchy | ColorSchemeError, InvalidImageError, BackendNotAvailableError, ColorExtractionError, TemplateRenderError, OutputWriteError | |
| packages/core/src/color_scheme/core/base.py | backends | abstract | ColorSchemeGenerator (ABC) | |
| packages/core/src/color_scheme/backends/pywal.py | backends | pywal | PywalGenerator | |
| packages/core/src/color_scheme/backends/wallust.py | backends | wallust | WallustGenerator | |
| packages/core/src/color_scheme/backends/custom.py | backends | custom | CustomGenerator | Pure Python, always available |
| packages/core/src/color_scheme/config/enums.py | enums | config | Backend, ColorFormat, ColorAlgorithm | StrEnum |
| packages/core/src/color_scheme/config/config.py | settings, config | AppConfig | AppConfig, GenerationSettings, OutputSettings, BackendSettings, TemplateSettings, LoggingSettings | |
| packages/core/src/color_scheme/config/defaults.py | defaults | template-dir, env-vars | output_directory, default_formats, default_backend | COLOR_SCHEME_TEMPLATES env var |
| packages/core/src/color_scheme/output/manager.py | output | templates | OutputManager | |
| packages/orchestrator/src/color_scheme_orchestrator/cli/main.py | orchestrator-cli, generate, show, install, uninstall | dry-run | app (Typer), generate(), show(), install, uninstall | Entry: color-scheme |
| packages/orchestrator/src/color_scheme_orchestrator/cli/commands/install.py | install | container-build, dry-run | install(), DOCKERFILE_MAP | docker/podman build |
| packages/orchestrator/src/color_scheme_orchestrator/cli/commands/uninstall.py | uninstall | container-remove, dry-run | uninstall() | |
| packages/orchestrator/src/color_scheme_orchestrator/config/settings.py | container-settings | validation | ContainerSettings | engine: docker/podman |
| packages/orchestrator/src/color_scheme_orchestrator/container/manager.py | container-manager | image-names, volume-mounts | ContainerManager, get_image_name(), run_generate() | |
| packages/settings/src/color_scheme_settings/__init__.py | settings-api | public-api | configure(), load_config(), reload_config(), get_config(), apply_overrides(), reset() | |
| packages/settings/src/color_scheme_settings/registry.py | settings-registry | namespace | SchemaRegistry, SchemaEntry | |
| packages/settings/src/color_scheme_settings/loader.py | settings-loader | layers, toml | SettingsLoader, LayerSource, load_toml() | 3 layers: package/project/user |
| packages/settings/src/color_scheme_settings/merger.py | settings-merge | deep-merge | deep_merge(), merge_layers() | Lists replaced entirely |
| packages/settings/src/color_scheme_settings/resolver.py | config-resolver | dry-run, precedence | ConfigResolver, COLORSCHEME_* env vars | Precedence: CLI>ENV>user>project>defaults |
| packages/settings/src/color_scheme_settings/errors.py | settings-errors | exceptions | SettingsError, SettingsFileError, SettingsValidationError, SettingsOverrideError, SettingsRegistryError | |
| packages/templates/src/color_scheme_templates/registry.py | template-registry | namespace | TemplateRegistry, TemplateEntry | |
| docs/reference/cli/core-commands.md | core-cli, generate, show | dry-run, backends, formats | generate, show, version | |
| docs/reference/cli/orchestrator-commands.md | orchestrator-cli, generate, show, install, uninstall | container, backends | generate, show, install, uninstall, version | --dry-run missing for install/uninstall |
| docs/reference/api/settings-api.md | settings-api | config-layers, overrides | configure, load_config, get_config, SchemaRegistry | get_config signature wrong |
| docs/reference/api/types.md | types | Color, ColorScheme, GeneratorConfig | Color, ColorScheme, GeneratorConfig | |

---

## Topic index

- **core-cli** (generate, show, version commands)
  - packages/core/src/color_scheme/cli/main.py
  - docs/reference/cli/core-commands.md
  - packages/core/tests/integration/test_cli_generate.py
  - packages/core/tests/integration/test_cli_show.py
  - packages/core/tests/integration/test_cli_dry_run.py

- **orchestrator-cli** (generate, show, install, uninstall, version)
  - packages/orchestrator/src/color_scheme_orchestrator/cli/main.py
  - packages/orchestrator/src/color_scheme_orchestrator/cli/commands/install.py
  - packages/orchestrator/src/color_scheme_orchestrator/cli/commands/uninstall.py
  - docs/reference/cli/orchestrator-commands.md
  - packages/orchestrator/tests/integration/test_cli_dry_run.py
  - packages/orchestrator/tests/unit/test_install_unit.py

- **backends** (pywal, wallust, custom, factory, auto-detection)
  - packages/core/src/color_scheme/backends/pywal.py
  - packages/core/src/color_scheme/backends/wallust.py
  - packages/core/src/color_scheme/backends/custom.py
  - packages/core/src/color_scheme/factory.py
  - packages/core/tests/unit/test_factory.py
  - packages/core/tests/unit/test_pywal_backend.py
  - packages/core/tests/unit/test_wallust_backend.py
  - packages/core/tests/unit/test_custom_backend.py

- **types** (Color, ColorScheme, GeneratorConfig)
  - packages/core/src/color_scheme/core/types.py
  - packages/core/tests/unit/test_types.py
  - docs/reference/api/types.md

- **exceptions** (exception hierarchy)
  - packages/core/src/color_scheme/core/exceptions.py
  - packages/core/tests/unit/test_output_exceptions.py
  - docs/reference/errors/exception-reference.md

- **settings-api** (configure, load_config, get_config, SchemaRegistry, layers)
  - packages/settings/src/color_scheme_settings/__init__.py
  - packages/settings/src/color_scheme_settings/registry.py
  - packages/settings/src/color_scheme_settings/loader.py
  - packages/settings/src/color_scheme_settings/merger.py
  - packages/settings/tests/test_registry.py
  - packages/settings/tests/test_loader.py
  - packages/settings/tests/test_merger.py
  - packages/settings/tests/test_pipeline.py
  - docs/reference/api/settings-api.md

- **config-resolver** (dry-run resolution, precedence, env vars)
  - packages/settings/src/color_scheme_settings/resolver.py
  - packages/settings/tests/test_resolver.py

- **templates** (Jinja2, TemplateRegistry)
  - packages/templates/src/color_scheme_templates/registry.py
  - packages/core/src/color_scheme/templates/*.j2
  - templates/*.j2
  - packages/templates/tests/

- **container** (Docker/Podman, image names, volume mounts)
  - packages/orchestrator/src/color_scheme_orchestrator/container/manager.py
  - packages/orchestrator/tests/unit/test_image_names.py
  - packages/orchestrator/tests/unit/test_container_manager.py
  - packages/orchestrator/tests/unit/test_volume_mounts.py

- **dry-run** (--dry-run flag, -n flag)
  - packages/core/src/color_scheme/cli/dry_run.py
  - packages/orchestrator/src/color_scheme_orchestrator/cli/dry_run.py
  - packages/core/tests/integration/test_cli_dry_run.py
  - packages/orchestrator/tests/integration/test_cli_dry_run.py
  - packages/orchestrator/tests/unit/test_install_uninstall_dryrun.py

- **enums** (Backend, ColorFormat, ColorAlgorithm)
  - packages/core/src/color_scheme/config/enums.py
  - packages/core/tests/config/test_enums.py
  - docs/reference/enums.md
