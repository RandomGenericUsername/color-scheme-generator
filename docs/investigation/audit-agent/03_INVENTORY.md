# Repo Inventory (Deterministic)

## Status values
- `in-scope`
- `ignored` (must cite `.auditignore` pattern)
- `binary`
- `too-large`
- `unknown`

## Files

| Path | Type | Status | Reason |
|------|------|--------|--------|
| packages/core/src/color_scheme/__init__.py | code | in-scope | |
| packages/core/src/color_scheme/backends/__init__.py | code | in-scope | |
| packages/core/src/color_scheme/backends/pywal.py | code | in-scope | |
| packages/core/src/color_scheme/backends/wallust.py | code | in-scope | |
| packages/core/src/color_scheme/backends/custom.py | code | in-scope | |
| packages/core/src/color_scheme/cli/__init__.py | code | in-scope | |
| packages/core/src/color_scheme/cli/main.py | code | in-scope | |
| packages/core/src/color_scheme/cli/dry_run.py | code | in-scope | |
| packages/core/src/color_scheme/config/__init__.py | code | in-scope | |
| packages/core/src/color_scheme/config/enums.py | code | in-scope | |
| packages/core/src/color_scheme/config/defaults.py | code | in-scope | |
| packages/core/src/color_scheme/config/config.py | code | in-scope | |
| packages/core/src/color_scheme/core/__init__.py | code | in-scope | |
| packages/core/src/color_scheme/core/exceptions.py | code | in-scope | |
| packages/core/src/color_scheme/core/types.py | code | in-scope | |
| packages/core/src/color_scheme/core/base.py | code | in-scope | |
| packages/core/src/color_scheme/factory.py | code | in-scope | |
| packages/core/src/color_scheme/output/__init__.py | code | in-scope | |
| packages/core/src/color_scheme/output/manager.py | code | in-scope | |
| packages/core/src/color_scheme/config/settings.toml | config | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/__init__.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/cli/__init__.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/cli/main.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/cli/dry_run.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/cli/commands/__init__.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/cli/commands/install.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/cli/commands/uninstall.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/config/__init__.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/config/settings.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/config/unified.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/container/__init__.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/container/manager.py | code | in-scope | |
| packages/orchestrator/src/color_scheme_orchestrator/config/settings.toml | config | in-scope | |
| packages/settings/src/color_scheme_settings/__init__.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/registry.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/loader.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/merger.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/overrides.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/resolver.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/models.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/transforms.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/errors.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/paths.py | code | in-scope | |
| packages/settings/src/color_scheme_settings/unified.py | code | in-scope | |
| packages/templates/src/color_scheme_templates/__init__.py | code | in-scope | |
| packages/templates/src/color_scheme_templates/registry.py | code | in-scope | |
| packages/templates/src/color_scheme_templates/loader.py | code | in-scope | |
| packages/templates/src/color_scheme_templates/resolver.py | code | in-scope | |
| packages/templates/src/color_scheme_templates/errors.py | code | in-scope | |
| packages/core/tests/conftest.py | test-config | in-scope | |
| packages/core/tests/config/conftest.py | test-config | in-scope | |
| packages/core/tests/config/test_settings.py | test | in-scope | |
| packages/core/tests/config/test_config.py | test | in-scope | |
| packages/core/tests/config/test_defaults.py | test | in-scope | |
| packages/core/tests/config/test_enums.py | test | in-scope | |
| packages/core/tests/integration/test_all_templates.py | test | in-scope | |
| packages/core/tests/integration/test_cli_dry_run.py | test | in-scope | |
| packages/core/tests/integration/test_cli_show.py | test | in-scope | |
| packages/core/tests/integration/test_cli_generate.py | test | in-scope | |
| packages/core/tests/unit/test_custom_backend.py | test | in-scope | |
| packages/core/tests/unit/test_output_exceptions.py | test | in-scope | |
| packages/core/tests/unit/test_config.py | test | in-scope | |
| packages/core/tests/unit/test_types.py | test | in-scope | |
| packages/core/tests/unit/test_wallust_backend.py | test | in-scope | |
| packages/core/tests/unit/test_cli_main.py | test | in-scope | |
| packages/core/tests/unit/test_output_manager.py | test | in-scope | |
| packages/core/tests/unit/test_pywal_backend.py | test | in-scope | |
| packages/core/tests/unit/test_factory.py | test | in-scope | |
| packages/core/tests/unit/test_dry_run.py | test | in-scope | |
| packages/orchestrator/tests/conftest.py | test-config | in-scope | |
| packages/orchestrator/tests/integration/conftest.py | test-config | in-scope | |
| packages/orchestrator/tests/integration/test_cli_dry_run.py | test | in-scope | |
| packages/orchestrator/tests/integration/test_cli_generate_orchestrator.py | test | in-scope | |
| packages/orchestrator/tests/integration/test_cli_show_delegation.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_main_error_handling.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_main_commands.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_container_manager_mounts.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_image_names.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_uninstall_unit.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_settings_validation.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_install_uninstall_dryrun.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_volume_mounts.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_install_unit.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_container_manager.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_container_execution.py | test | in-scope | |
| packages/orchestrator/tests/unit/test_dry_run.py | test | in-scope | |
| packages/settings/tests/conftest.py | test-config | in-scope | |
| packages/settings/tests/test_merger.py | test | in-scope | |
| packages/settings/tests/test_pipeline.py | test | in-scope | |
| packages/settings/tests/test_loader.py | test | in-scope | |
| packages/settings/tests/test_registry.py | test | in-scope | |
| packages/settings/tests/test_unified.py | test | in-scope | |
| packages/settings/tests/test_paths.py | test | in-scope | |
| packages/settings/tests/test_models.py | test | in-scope | |
| packages/settings/tests/test_errors.py | test | in-scope | |
| packages/settings/tests/test_resolver.py | test | in-scope | |
| packages/settings/tests/test_overrides.py | test | in-scope | |
| packages/templates/tests/conftest.py | test-config | in-scope | |
| packages/templates/tests/test_loader.py | test | in-scope | |
| packages/templates/tests/test_registry.py | test | in-scope | |
| packages/templates/tests/test_init.py | test | in-scope | |
| packages/templates/tests/test_resolver.py | test | in-scope | |
| README.md | doc | in-scope | |
| DEVELOPMENT.md | doc | in-scope | |
| CHANGELOG.md | doc | in-scope | |
| docs/README.md | doc | in-scope | |
| docs/reference/cli/core-commands.md | doc | in-scope | |
| docs/reference/cli/orchestrator-commands.md | doc | in-scope | |
| docs/reference/api/types.md | doc | in-scope | |
| docs/reference/api/backends.md | doc | in-scope | |
| docs/reference/api/output.md | doc | in-scope | |
| docs/reference/api/settings-api.md | doc | in-scope | |
| docs/reference/api/factory.md | doc | in-scope | |
| docs/reference/configuration/defaults.md | doc | in-scope | |
| docs/reference/configuration/settings-schema.md | doc | in-scope | |
| docs/reference/templates/format-reference.md | doc | in-scope | |
| docs/reference/templates/variables.md | doc | in-scope | |
| docs/reference/errors/exception-reference.md | doc | in-scope | |
| docs/reference/enums.md | doc | in-scope | |
| docs/reference/makefile.md | doc | in-scope | |
| docs/explanations/architecture.md | doc | in-scope | |
| docs/explanations/backends-explained.md | doc | in-scope | |
| docs/explanations/design-patterns.md | doc | in-scope | |
| docs/explanations/integration-patterns.md | doc | in-scope | |
| docs/explanations/settings-layers.md | doc | in-scope | |
| docs/how-to/configure-backends.md | doc | in-scope | |
| docs/how-to/use-dry-run.md | doc | in-scope | |
| docs/how-to/customize-output.md | doc | in-scope | |
| docs/how-to/troubleshoot-errors.md | doc | in-scope | |
| docs/how-to/integrate-shell.md | doc | in-scope | |
| docs/how-to/setup-pre-commit.md | doc | in-scope | |
| docs/how-to/run-tests.md | doc | in-scope | |
| docs/how-to/contribute.md | doc | in-scope | |
| docs/how-to/create-templates.md | doc | in-scope | |
| docs/how-to/generate-colors.md | doc | in-scope | |
| docs/tutorials/container-setup.md | doc | in-scope | |
| docs/tutorials/quick-start.md | doc | in-scope | |
| docs/tutorials/first-color-scheme.md | doc | in-scope | |
| docs/tutorials/developer-setup.md | doc | in-scope | |
| packages/core/README.md | doc | in-scope | |
| packages/orchestrator/README.md | doc | in-scope | |
| packages/settings/README.md | doc | in-scope | |
| packages/templates/README.md | doc | in-scope | |
| pyproject.toml | config | in-scope | |
| packages/core/pyproject.toml | config | in-scope | |
| packages/orchestrator/pyproject.toml | config | in-scope | |
| packages/settings/pyproject.toml | config | in-scope | |
| packages/templates/pyproject.toml | config | in-scope | |
| settings.toml | config | in-scope | |
| .pre-commit-config.yaml | config | in-scope | |
| Makefile | config | in-scope | |
| .github/workflows/ci-core.yml | config | in-scope | |
| .github/workflows/ci-orchestrator.yml | config | in-scope | |
| .github/workflows/ci-settings.yml | config | in-scope | |
| .github/workflows/ci-templates.yml | config | in-scope | |
| .github/pull_request_template.md | doc | in-scope | |
| packages/core/src/color_scheme/templates/colors.css.j2 | template | in-scope | |
| packages/core/src/color_scheme/templates/colors.yaml.j2 | template | in-scope | |
| packages/core/src/color_scheme/templates/colors.scss.j2 | template | in-scope | |
| packages/core/src/color_scheme/templates/colors.gtk.css.j2 | template | in-scope | |
| packages/core/src/color_scheme/templates/colors.sh.j2 | template | in-scope | |
| packages/core/src/color_scheme/templates/colors.json.j2 | template | in-scope | |
| packages/core/src/color_scheme/templates/colors.sequences.j2 | template | in-scope | |
| packages/core/src/color_scheme/templates/colors.rasi.j2 | template | in-scope | |
| templates/colors.css.j2 | template | in-scope | |
| templates/colors.yaml.j2 | template | in-scope | |
| templates/colors.scss.j2 | template | in-scope | |
| templates/colors.gtk.css.j2 | template | in-scope | |
| templates/colors.sh.j2 | template | in-scope | |
| templates/colors.json.j2 | template | in-scope | |
| templates/colors.sequences.j2 | template | in-scope | |
| templates/colors.rasi.j2 | template | in-scope | |
| tests/smoke/ | - | ignored | .auditignore: tests/smoke/ |
| .venv/ | - | ignored | .auditignore: .venv/ |
| docs/investigation/ | - | ignored | .auditignore: docs/investigation/ |
| docs/plans/ | - | ignored | .auditignore: docs/plans/ |
| docs/archive/ | - | ignored | .auditignore: docs/archive/ |
| uv.lock | - | ignored | .auditignore: uv.lock |
| package-lock.json | - | ignored | .auditignore: package-lock.json |
