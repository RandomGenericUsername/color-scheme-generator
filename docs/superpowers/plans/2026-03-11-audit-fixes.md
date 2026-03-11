# Audit Fixes Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all critical, major, and minor issues found in the 2026-03-11 audit: deep merge mutation (CRIT-03), orchestrator settings.toml key mismatch (MAJ-02), import-time path constants (MIN-01), env-var layer not wired (CRIT-01), ConfigResolver stub (CRIT-02), double saturation in CLI (CRIT-04), stale show-command docs (MAJ-01), and missing env-var layer in settings docs (MIN-03).

**Architecture:** TDD throughout — every implementation change is preceded by a failing test. Phases are ordered by dependency: foundation fixes first, then the shared `parse_env_vars()` utility, then wiring it into both `SettingsLoader` and `ConfigResolver`, then test quality cleanup, then the core saturation bug, then docs and changelog. Run `make test-all` after each commit.

**Tech Stack:** Python 3.12, pytest, pydantic v2, pytest-monkeypatch, `copy` stdlib, MkDocs.

---

## Chunk 1: Phase 1 — Foundation Fixes

### Task 1: Fix deep_merge shallow copy (CRIT-03)

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/merger.py`
- Modify: `packages/settings/tests/test_merger.py`

- [ ] **Step 1: Write the failing test**

  Add to `packages/settings/tests/test_merger.py` inside `class TestDeepMerge`:

  ```python
  def test_deep_merge_result_not_mutated_by_second_merge(self):
      """CRIT-03: result of first merge must not be mutated by a second merge."""
      base = {"section": {"key": "original"}}
      override1 = {"section": {"other": "value1"}}
      override2 = {"section": {"key": "mutated"}}

      result1 = deep_merge(base, override1)
      deep_merge(result1, override2)

      assert result1["section"]["key"] == "original"
  ```

- [ ] **Step 2: Run test to confirm it fails**

  Run: `cd packages/settings && python -m pytest tests/test_merger.py::TestDeepMerge::test_deep_merge_result_not_mutated_by_second_merge -v`

  Expected: FAIL — `result1["section"]["key"]` is `"mutated"` because `base.copy()` is shallow.

- [ ] **Step 3: Fix deep_merge to use deepcopy**

  In `packages/settings/src/color_scheme_settings/merger.py`, change the import and line 17:

  ```python
  # Add at top of file:
  import copy

  # Change line 17 from:
  result = base.copy()
  # To:
  result = copy.deepcopy(base)
  ```

- [ ] **Step 4: Run test to confirm it passes**

  Run: `cd packages/settings && python -m pytest tests/test_merger.py -v`

  Expected: All tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add packages/settings/src/color_scheme_settings/merger.py \
          packages/settings/tests/test_merger.py
  git commit -m "fix(settings): deep_merge uses deepcopy to prevent cross-layer mutation (CRIT-03)"
  ```

---

### Task 2: Fix orchestrator settings.toml key mismatch (MAJ-02)

**Files:**
- Modify: `packages/orchestrator/src/color_scheme_orchestrator/config/settings.toml`
- Modify: `packages/settings/tests/conftest.py` (fixture `orchestrator_defaults_toml`)
- Create: `packages/settings/tests/test_settings_validation.py`

**Context:** `ContainerSettings` has top-level fields (e.g., `engine`). The TOML currently wraps them in `[container]`, which Pydantic ignores as an unknown key, so `engine = "docker"` is never loaded. Fix: remove the `[container]` wrapper so `engine = "docker"` is at the top level.

- [ ] **Step 1: Write the failing test**

  Create `packages/settings/tests/test_settings_validation.py`:

  ```python
  """Tests for settings model validation against real TOML defaults."""

  import pytest
  from pathlib import Path
  from unittest.mock import patch
  from pydantic import BaseModel, Field

  from color_scheme_settings.loader import load_toml
  from color_scheme_settings.registry import SchemaRegistry


  class MockContainerSettings(BaseModel):
      engine: str = Field(default="podman")  # default deliberately NOT docker


  @pytest.fixture(autouse=True)
  def clean_registry():
      SchemaRegistry.clear()
      yield
      SchemaRegistry.clear()


  class TestOrchestratorEngineDefault:
      def test_orchestrator_engine_default_comes_from_toml(self):
          """MAJ-02: engine=docker must come from the TOML file, not the model default."""
          # Use Path(__file__) to build an absolute path regardless of working directory
          toml_path = (
              Path(__file__).parent.parent.parent.parent
              / "orchestrator"
              / "src"
              / "color_scheme_orchestrator"
              / "config"
              / "settings.toml"
          )
          data = load_toml(toml_path)
          # After fix: top-level key 'engine' = 'docker'
          # Before fix: only key is 'container' (a nested dict), no 'engine' at top level
          assert data.get("engine") == "docker", (
              f"Expected top-level engine='docker' in TOML, got: {data}"
          )
  ```

- [ ] **Step 2: Run test to confirm it fails**

  Run: `cd packages/settings && python -m pytest tests/test_settings_validation.py -v`

  Expected: FAIL — `data` is `{"container": {"engine": "docker"}}`, not `{"engine": "docker"}`.

- [ ] **Step 3: Fix the orchestrator settings.toml**

  Rewrite `packages/orchestrator/src/color_scheme_orchestrator/config/settings.toml`:

  ```toml
  engine = "docker"
  ```

  (Remove the `[container]` table wrapper.)

- [ ] **Step 4: Fix the conftest.py fixture**

  In `packages/settings/tests/conftest.py`, update `orchestrator_defaults_toml` fixture content from:
  ```python
      content = """\
  [container]
  engine = "docker"
  """
  ```
  To:
  ```python
      content = """\
  engine = "docker"
  """
  ```

- [ ] **Step 5: Run tests to confirm they pass**

  Run: `cd packages/settings && python -m pytest tests/test_settings_validation.py tests/test_pipeline.py -v`

  Expected: All tests PASS.

- [ ] **Step 6: Commit**

  ```bash
  git add packages/orchestrator/src/color_scheme_orchestrator/config/settings.toml \
          packages/settings/tests/conftest.py \
          packages/settings/tests/test_settings_validation.py
  git commit -m "fix(settings): remove [container] wrapper from orchestrator settings.toml (MAJ-02)"
  ```

---

### Task 3: Fix import-time path constants (MIN-01)

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/paths.py`
- Modify: `packages/settings/tests/test_paths.py`

**Context:** `XDG_CONFIG_HOME` and `USER_SETTINGS_FILE` are module-level constants evaluated at import time. Any test or production code that sets `XDG_CONFIG_HOME` *after* import gets the stale value. Fix: convert them to functions. The derived constants `USER_CONFIG_DIR`, `USER_TEMPLATES_DIR`, `USER_OUTPUT_DIR` must also become functions.

- [ ] **Step 1: Write the failing test**

  Add to `packages/settings/tests/test_paths.py` inside a new class:

  ```python
  class TestXdgConfigHomeFunctions:
      """Tests for the dynamic path functions (MIN-01)."""

      def test_xdg_config_home_respects_env_var_after_import(
          self, monkeypatch: pytest.MonkeyPatch
      ):
          from color_scheme_settings import paths
          monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/test-xdg")
          result = paths.get_xdg_config_home()
          assert str(result) == "/tmp/test-xdg"

      def test_get_user_settings_file_uses_current_xdg(
          self, monkeypatch: pytest.MonkeyPatch
      ):
          from color_scheme_settings import paths
          monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/test-xdg")
          result = paths.get_user_settings_file()
          assert str(result) == "/tmp/test-xdg/color-scheme/settings.toml"
  ```

- [ ] **Step 2: Run tests to confirm they fail**

  Run: `cd packages/settings && python -m pytest tests/test_paths.py::TestXdgConfigHomeFunctions -v`

  Expected: FAIL — `get_xdg_config_home` does not exist yet.

- [ ] **Step 3: Add get_xdg_config_home() and get_user_settings_file() to paths.py**

  In `packages/settings/src/color_scheme_settings/paths.py`, add these two functions after the existing `USER_OUTPUT_DIR` constant block:

  ```python
  def get_xdg_config_home() -> Path:
      """Return XDG_CONFIG_HOME, reading the environment at call time."""
      return Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))


  def get_user_settings_file() -> Path:
      """Return the user settings file path, reading XDG_CONFIG_HOME at call time."""
      return get_xdg_config_home() / APP_NAME / SETTINGS_FILENAME
  ```

  Keep all existing module-level constants (`XDG_CONFIG_HOME`, `USER_SETTINGS_FILE`, etc.) — other code imports them by name and they remain for backward compatibility. Only add the new functions.

- [ ] **Step 4: Run tests to confirm they pass**

  Run: `cd packages/settings && python -m pytest tests/test_paths.py -v`

  Expected: All tests PASS (existing tests still pass; new tests now pass).

- [ ] **Step 5: Commit**

  ```bash
  git add packages/settings/src/color_scheme_settings/paths.py \
          packages/settings/tests/test_paths.py
  git commit -m "fix(settings): add get_xdg_config_home/get_user_settings_file for dynamic resolution (MIN-01)"
  ```

---

### Task 4: Fix overrides.py model_dump mode (IMP-6)

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/overrides.py`
- Modify: `packages/settings/tests/test_overrides.py`

- [ ] **Step 1: Write the failing test**

  Add to `packages/settings/tests/test_overrides.py` inside a new or existing class:

  ```python
  class TestOverrideModePreservesTypes:
      """IMP-6: model_dump(mode='python') must preserve validated types."""

      def test_override_with_path_field_preserves_path_type(self):
          """Path fields must stay as Path after round-trip through apply_overrides."""
          from pathlib import Path as PyPath

          class ConfigWithPath(BaseModel):
              output_dir: PyPath = Field(default=PyPath("/default"))

          config = ConfigWithPath()
          result = apply_overrides(config, {"output_dir": PyPath("/overridden")})
          assert isinstance(result.output_dir, PyPath)
          assert result.output_dir == PyPath("/overridden")
  ```

- [ ] **Step 2: Run test to confirm it passes (or note it already passes)**

  Run: `cd packages/settings && python -m pytest tests/test_overrides.py::TestOverrideModePreservesTypes -v`

  Note: This test may already pass. If it does, the implementation fix (Step 3) still needs to be made for correctness.

- [ ] **Step 3: Fix the model_dump call in overrides.py**

  In `packages/settings/src/color_scheme_settings/overrides.py`, change line 34:
  ```python
  # Before:
  config_dict = config.model_dump()
  # After:
  config_dict = config.model_dump(mode="python")
  ```

- [ ] **Step 4: Run full test suite**

  Run: `cd packages/settings && python -m pytest tests/test_overrides.py -v`

  Expected: All tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add packages/settings/src/color_scheme_settings/overrides.py \
          packages/settings/tests/test_overrides.py
  git commit -m "fix(settings): use model_dump(mode='python') to preserve validated types (IMP-6)"
  ```

---

### Task 5: Pass source_layer to SettingsValidationError (MIN-4)

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/unified.py`
- Modify: `packages/settings/tests/test_unified.py`

**Context:** `build_validated_namespace()` raises `SettingsValidationError` but never passes `source_layer`, so the error message never includes layer attribution. The parameter exists on the exception class — it just isn't used.

- [ ] **Step 1: Write the failing test**

  Add to `packages/settings/tests/test_unified.py`:

  ```python
  import pytest
  from pydantic import BaseModel, Field
  from color_scheme_settings.errors import SettingsValidationError
  from color_scheme_settings.unified import build_validated_namespace


  class StrictModel(BaseModel):
      value: int = Field(ge=0)


  class TestValidationErrorIncludesSourceLayer:
      """MIN-4: SettingsValidationError must include source_layer when provided."""

      def test_validation_error_includes_source_layer(self):
          with pytest.raises(SettingsValidationError) as exc_info:
              build_validated_namespace(
                  namespace="test",
                  model=StrictModel,
                  data={"value": -1},  # fails ge=0 constraint
                  source_layer="user",
              )
          assert exc_info.value.source_layer == "user"
  ```

- [ ] **Step 2: Run test to confirm it fails**

  Run: `cd packages/settings && python -m pytest tests/test_unified.py::TestValidationErrorIncludesSourceLayer -v`

  Expected: FAIL — `build_validated_namespace` does not accept `source_layer` argument yet.

- [ ] **Step 3: Add source_layer parameter to build_validated_namespace**

  In `packages/settings/src/color_scheme_settings/unified.py`, update `build_validated_namespace`:

  ```python
  def build_validated_namespace(
      namespace: str,
      model: type[BaseModel],
      data: dict[str, Any],
      source_layer: str | None = None,
  ) -> BaseModel:
      """Validate a single namespace's merged data through its Pydantic model.

      Args:
          namespace: The namespace identifier
          model: Pydantic model class
          data: Merged settings data
          source_layer: Which settings layer this data came from (for error attribution)

      Returns:
          Validated Pydantic model instance

      Raises:
          SettingsValidationError: If validation fails
      """
      try:
          transformed = resolve_environment_variables(data)
          transformed = convert_keys_to_lowercase(transformed)
          return model(**transformed)
      except Exception as e:
          raise SettingsValidationError(
              namespace=namespace,
              validation_error=e,
              source_layer=source_layer,
          ) from e
  ```

- [ ] **Step 4: Run tests to confirm they pass**

  Run: `cd packages/settings && python -m pytest tests/test_unified.py -v`

  Expected: All tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add packages/settings/src/color_scheme_settings/unified.py \
          packages/settings/tests/test_unified.py
  git commit -m "fix(settings): pass source_layer to SettingsValidationError for layer attribution (MIN-4)"
  ```

---

### Task 6: Fix reload_config() docstring (MIN-5)

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/__init__.py`

- [ ] **Step 1: Update the docstring**

  In `packages/settings/src/color_scheme_settings/__init__.py`, change the `reload_config()` docstring from:
  ```python
  def reload_config() -> BaseModel:
      """Force reload from all layers. Useful for testing."""
  ```
  To:
  ```python
  def reload_config() -> BaseModel:
      """Force reload from all layers.

      Clears the settings cache and reloads from all configured layers.
      Use this when runtime conditions change (e.g., config files updated
      while the process is running). For test isolation, prefer calling
      reset() followed by configure() instead.
      """
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add packages/settings/src/color_scheme_settings/__init__.py
  git commit -m "docs(settings): fix reload_config docstring — it is a public API, not a test utility (MIN-5)"
  ```

---

## Chunk 2: Phase 2 — Extract parse_env_vars() Shared Utility

### Task 7: Add parse_env_vars() to transforms.py

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/transforms.py`
- Modify: `packages/settings/tests/test_unified.py` (add TestParseEnvVars class — file covers transforms too)

**Note:** The test file is named `test_unified.py` but already covers `transforms.py` functions. Add the new class there to match the existing pattern.

- [ ] **Step 1: Write all failing tests first**

  Add to `packages/settings/tests/test_unified.py`:

  ```python
  from color_scheme_settings.transforms import parse_env_vars


  class TestParseEnvVars:
      """Tests for parse_env_vars() shared utility."""

      def test_single_key(self, monkeypatch: pytest.MonkeyPatch):
          monkeypatch.setenv("COLORSCHEME_OUTPUT__DIRECTORY", "/tmp/out")
          result = parse_env_vars()
          assert result == {"output": {"directory": "/tmp/out"}}

      def test_nested_double_underscore(self, monkeypatch: pytest.MonkeyPatch):
          monkeypatch.setenv("COLORSCHEME_GENERATION__DEFAULT_BACKEND", "wallust")
          result = parse_env_vars()
          assert result["generation"]["default_backend"] == "wallust"

      def test_color_scheme_templates_special_case(self, monkeypatch: pytest.MonkeyPatch):
          monkeypatch.setenv("COLOR_SCHEME_TEMPLATES", "/custom/templates")
          result = parse_env_vars()
          assert result == {"templates": {"directory": "/custom/templates"}}

      def test_unrelated_vars_ignored(self, monkeypatch: pytest.MonkeyPatch):
          monkeypatch.setenv("HOME", "/home/user")
          monkeypatch.setenv("PATH", "/usr/bin")
          result = parse_env_vars()
          assert "home" not in result
          assert "path" not in result

      def test_empty_environ(self):
          result = parse_env_vars(environ={})
          assert result == {}

      def test_keys_normalised_to_lowercase(self, monkeypatch: pytest.MonkeyPatch):
          monkeypatch.setenv("COLORSCHEME_OUTPUT__DIRECTORY", "/tmp")
          result = parse_env_vars()
          # Both section and key must be lowercase
          assert "output" in result
          assert "directory" in result["output"]

      def test_explicit_environ_overrides_os_environ(self):
          result = parse_env_vars(
              environ={"COLORSCHEME_OUTPUT__DIRECTORY": "/explicit"}
          )
          assert result == {"output": {"directory": "/explicit"}}
  ```

- [ ] **Step 2: Run tests to confirm they all fail**

  Run: `cd packages/settings && python -m pytest tests/test_unified.py::TestParseEnvVars -v`

  Expected: All 7 tests FAIL — `ImportError: cannot import name 'parse_env_vars'`.

- [ ] **Step 3: Implement parse_env_vars() in transforms.py**

  Append to `packages/settings/src/color_scheme_settings/transforms.py`:

  ```python
  def parse_env_vars(environ: dict | None = None) -> dict[str, dict]:
      """Parse COLORSCHEME_* environment variables into a section-keyed dict.

      Pattern: COLORSCHEME_SECTION__KEY (double underscore separates section from key)
      Special case: COLOR_SCHEME_TEMPLATES=/path → {"templates": {"directory": "/path"}}

      Keys are normalised to lowercase.
      Unrecognised environment variables are ignored.

      Args:
          environ: Environment dict to parse. Defaults to os.environ if None.

      Returns:
          Dict mapping section name to {key: value} pairs.
          Example: {"output": {"directory": "/tmp"}, "generation": {"default_backend": "pywal"}}
      """
      if environ is None:
          environ = dict(os.environ)

      result: dict[str, dict] = {}
      prefix = "COLORSCHEME_"

      for key, value in environ.items():
          if key.startswith(prefix):
              config_key = key[len(prefix):]
              parts = config_key.split("__", 1)
              if len(parts) == 2:
                  section, field = parts[0].lower(), parts[1].lower()
              else:
                  section, field = parts[0].lower(), parts[0].lower()
              if section not in result:
                  result[section] = {}
              result[section][field] = value

      # Special case: COLOR_SCHEME_TEMPLATES
      if "COLOR_SCHEME_TEMPLATES" in environ:
          if "templates" not in result:
              result["templates"] = {}
          result["templates"]["directory"] = environ["COLOR_SCHEME_TEMPLATES"]

      return result
  ```

- [ ] **Step 4: Run tests to confirm they pass**

  Run: `cd packages/settings && python -m pytest tests/test_unified.py::TestParseEnvVars -v`

  Expected: All 7 tests PASS.

- [ ] **Step 5: Run full settings test suite**

  Run: `cd packages/settings && python -m pytest -v`

  Expected: All tests PASS.

- [ ] **Step 6: Commit**

  ```bash
  git add packages/settings/src/color_scheme_settings/transforms.py \
          packages/settings/tests/test_unified.py
  git commit -m "feat(settings): add parse_env_vars() shared utility to transforms.py (Phase 2)"
  ```

---

## Chunk 3: Phase 3 — Wire Env-Var Layer into SettingsLoader (CRIT-01)

### Task 8: Add env-var layer to discover_layers()

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/loader.py`
- Modify: `packages/settings/tests/test_loader.py`
- Modify: `packages/settings/tests/test_pipeline.py`

- [ ] **Step 1: Write failing loader tests**

  Add to `packages/settings/tests/test_loader.py`:

  ```python
  class TestEnvVarLayer:
      """CRIT-01: env-var layer must appear in discover_layers() output."""

      def test_env_var_layer_present_when_set(
          self, core_defaults_toml: Path, monkeypatch: pytest.MonkeyPatch
      ):
          SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
          monkeypatch.setenv("COLORSCHEME_CORE__LEVEL", "DEBUG")
          loader = SettingsLoader(project_root=None, user_config_path=None)
          layers = loader.discover_layers()
          env_layers = [l for l in layers if l.layer == "env"]
          assert len(env_layers) >= 1

      def test_env_var_layer_absent_when_no_colorscheme_vars(
          self, core_defaults_toml: Path, monkeypatch: pytest.MonkeyPatch
      ):
          SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
          # Remove any COLORSCHEME_* vars that may exist in the environment
          for key in list(monkeypatch._env_patches if hasattr(monkeypatch, '_env_patches') else {}):
              if key.startswith("COLORSCHEME_"):
                  monkeypatch.delenv(key, raising=False)
          # Use explicit clean environ
          loader = SettingsLoader(project_root=None, user_config_path=None)
          # Call with empty environ override by monkeypatching parse_env_vars
          import color_scheme_settings.loader as loader_mod
          original = loader_mod.parse_env_vars
          loader_mod.parse_env_vars = lambda: {}
          try:
              layers = loader.discover_layers()
              env_layers = [l for l in layers if l.layer == "env"]
              assert len(env_layers) == 0
          finally:
              loader_mod.parse_env_vars = original

      def test_env_var_layer_has_no_file_path(
          self, core_defaults_toml: Path, monkeypatch: pytest.MonkeyPatch
      ):
          SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
          monkeypatch.setenv("COLORSCHEME_CORE__LEVEL", "DEBUG")
          loader = SettingsLoader(project_root=None, user_config_path=None)
          layers = loader.discover_layers()
          env_layers = [l for l in layers if l.layer == "env"]
          for layer in env_layers:
              assert layer.file_path is None

      def test_env_var_unknown_section_ignored(
          self, core_defaults_toml: Path, monkeypatch: pytest.MonkeyPatch
      ):
          SchemaRegistry.register("core", MockCoreConfig, core_defaults_toml)
          monkeypatch.setenv("COLORSCHEME_UNKNOWNSECTION__KEY", "value")
          loader = SettingsLoader(project_root=None, user_config_path=None)
          layers = loader.discover_layers()
          env_layers = [l for l in layers if l.layer == "env"]
          namespaces = [l.namespace for l in env_layers]
          assert "unknownsection" not in namespaces
  ```

- [ ] **Step 2: Run failing loader tests**

  Run: `cd packages/settings && python -m pytest tests/test_loader.py::TestEnvVarLayer -v`

  Expected: FAIL — `ImportError: cannot import name 'parse_env_vars' from loader` or similar, since the wiring doesn't exist yet.

- [ ] **Step 3: Wire env-var layer into loader.py**

  In `packages/settings/src/color_scheme_settings/loader.py`:

  1. Add import at the top:
     ```python
     from color_scheme_settings.transforms import parse_env_vars
     ```

  2. Add Layer 4 block at the end of `discover_layers()`, after the Layer 3 user config block and before `return layers`:

     ```python
     # Layer 4: Environment variables (COLORSCHEME_* namespace)
     raw_env = parse_env_vars()
     for entry in SchemaRegistry.all_entries():
         model_sections = set(entry.model.model_fields.keys())
         # raw_env keys are section names; keep only sections this model knows about
         namespace_data = {k: v for k, v in raw_env.items() if k in model_sections}
         if namespace_data:
             layers.append(
                 LayerSource(
                     layer="env",
                     namespace=entry.namespace,
                     file_path=None,
                     data=namespace_data,
                 )
             )
     ```

- [ ] **Step 4: Run loader tests**

  Run: `cd packages/settings && python -m pytest tests/test_loader.py -v`

  Expected: All tests PASS.

- [ ] **Step 5: Write failing pipeline tests**

  Add to `packages/settings/tests/test_pipeline.py`. The existing models in that file are `PipelineCoreConfig`, `PipelineContainerConfig`, `PipelineUnifiedConfig`, and `package_files`/`project_root_dir`/`user_config_file` fixtures. Use them directly:

  ```python
  class TestEnvVarLayerPipeline:
      """CRIT-01: env-var layer must override lower layers in the full pipeline."""

      def test_env_var_overrides_user_config(
          self,
          package_files: tuple[Path, Path],
          user_config_file: Path,
          monkeypatch: pytest.MonkeyPatch,
      ):
          """Env var must beat user config file value.
          user_config_file sets saturation_adjustment=1.5; env var overrides it.
          """
          core_file, orch_file = package_files
          SchemaRegistry.register("core", PipelineCoreConfig, core_file)
          SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
          # env var overrides the user config's saturation_adjustment
          monkeypatch.setenv("COLORSCHEME_GENERATION__SATURATION_ADJUSTMENT", "1.8")
          configure(PipelineUnifiedConfig, user_config_path=user_config_file)

          config = load_config()
          # user_config_file would give 1.5; env var gives 1.8
          assert config.core.generation.saturation_adjustment == pytest.approx(1.8)

      def test_env_var_beaten_by_cli_override(
          self,
          package_files: tuple[Path, Path],
          monkeypatch: pytest.MonkeyPatch,
      ):
          """CLI override (get_config overrides) must beat env-var layer value."""
          core_file, orch_file = package_files
          SchemaRegistry.register("core", PipelineCoreConfig, core_file)
          SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
          monkeypatch.setenv("COLORSCHEME_GENERATION__DEFAULT_BACKEND", "wallust")
          configure(PipelineUnifiedConfig)

          config = get_config(overrides={"core.generation.default_backend": "pywal"})
          # CLI override wins over env var
          assert config.core.generation.default_backend == "pywal"

      def test_env_var_beats_project_config(
          self,
          package_files: tuple[Path, Path],
          project_root_dir: Path,
          monkeypatch: pytest.MonkeyPatch,
      ):
          """Env var must override project config file value.
          project_root_dir sets default_backend=wallust; env var must win.
          """
          core_file, orch_file = package_files
          SchemaRegistry.register("core", PipelineCoreConfig, core_file)
          SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
          monkeypatch.setenv("COLORSCHEME_GENERATION__DEFAULT_BACKEND", "custom")
          configure(PipelineUnifiedConfig, project_root=project_root_dir)

          config = load_config()
          # project sets wallust; env var must override to custom
          assert config.core.generation.default_backend == "custom"
  ```

- [ ] **Step 6: Run pipeline tests and fix as needed**

  Run: `cd packages/settings && python -m pytest tests/test_pipeline.py -v`

  Expected: All tests PASS including new `TestEnvVarLayerPipeline`.

- [ ] **Step 7: Commit**

  ```bash
  git add packages/settings/src/color_scheme_settings/loader.py \
          packages/settings/tests/test_loader.py \
          packages/settings/tests/test_pipeline.py
  git commit -m "feat(settings): wire COLORSCHEME_* env-var layer into SettingsLoader.discover_layers() (CRIT-01)"
  ```

---

## Chunk 4: Phase 4 — Complete ConfigResolver (CRIT-02)

### Task 9: Replace _load_package_defaults() stub

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/resolver.py`
- Modify: `packages/settings/tests/test_resolver.py`

- [ ] **Step 1: Write failing test for _load_package_defaults**

  Add to `packages/settings/tests/test_resolver.py`:

  ```python
  from color_scheme_settings.registry import SchemaRegistry
  from color_scheme_settings.errors import SettingsFileError

  class TestLoadPackageDefaults:
      """CRIT-02: _load_package_defaults must return real values from registry."""

      def test_load_package_defaults_returns_real_values(
          self, tmp_path: Path
      ):
          """Registered package TOML must be read and returned."""
          from pydantic import BaseModel, Field
          toml_file = tmp_path / "settings.toml"
          toml_file.write_text('[generation]\ndefault_backend = "pywal"\n')

          class MockCoreConfig(BaseModel):
              generation: dict = Field(default_factory=dict)

          SchemaRegistry.clear()
          SchemaRegistry.register("core", MockCoreConfig, toml_file)

          resolver = ConfigResolver()
          defaults = resolver._load_package_defaults()
          assert "core" in defaults
          assert defaults["core"].get("generation", {}).get("default_backend") == "pywal"

      def test_load_package_defaults_warns_on_missing_file(
          self, tmp_path: Path
      ):
          """Missing defaults file produces a warning, not an exception."""
          from pydantic import BaseModel, Field

          class MockCoreConfig(BaseModel):
              pass

          SchemaRegistry.clear()
          SchemaRegistry.register("core", MockCoreConfig, tmp_path / "nonexistent.toml")

          resolver = ConfigResolver()
          result = resolver._load_package_defaults()
          assert result == {} or "core" not in result
          assert len(resolver.warnings) >= 1
  ```

- [ ] **Step 2: Run tests to confirm they fail**

  Run: `cd packages/settings && python -m pytest tests/test_resolver.py::TestLoadPackageDefaults -v`

  Expected: FAIL — `_load_package_defaults()` returns `{}` always.

- [ ] **Step 3: Implement _load_package_defaults() in resolver.py**

  Replace the stub in `packages/settings/src/color_scheme_settings/resolver.py`:

  Add imports at the top of the file:
  ```python
  from color_scheme_settings.errors import SettingsFileError
  from color_scheme_settings.loader import load_toml
  from color_scheme_settings.registry import SchemaRegistry
  ```

  Replace the `_load_package_defaults` method body:
  ```python
  def _load_package_defaults(self) -> dict[str, Any]:
      """Load package default settings from registered TOML files."""
      result: dict[str, Any] = {}
      for entry in SchemaRegistry.all_entries():
          try:
              data = load_toml(entry.defaults_file)
              result[entry.namespace] = data
          except SettingsFileError as e:
              self.warnings.append(
                  Warning(
                      message=f"Could not load package defaults for {entry.namespace}: {e}",
                      level=WarningLevel.INFO,
                  )
              )
      return result
  ```

- [ ] **Step 4: Run tests to confirm they pass**

  Run: `cd packages/settings && python -m pytest tests/test_resolver.py::TestLoadPackageDefaults -v`

  Expected: Both tests PASS.

---

### Task 10: Delegate _collect_env_vars() to shared utility

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/resolver.py`
- Modify: `packages/settings/tests/test_resolver.py`

- [ ] **Step 1: Write failing test**

  Add to `packages/settings/tests/test_resolver.py`:

  ```python
  from unittest.mock import patch

  class TestCollectEnvVars:
      """CRIT-02: _collect_env_vars must delegate to parse_env_vars()."""

      def test_env_vars_delegate_to_shared_parser(self):
          """_collect_env_vars must call parse_env_vars from transforms."""
          resolver = ConfigResolver()
          with patch(
              "color_scheme_settings.resolver.parse_env_vars",
              return_value={"output": {"directory": "/patched"}},
          ) as mock_parse:
              result = resolver._collect_env_vars()
          mock_parse.assert_called_once()
          assert result == {"output": {"directory": "/patched"}}
  ```

- [ ] **Step 2: Run test to confirm it fails**

  Run: `cd packages/settings && python -m pytest tests/test_resolver.py::TestCollectEnvVars -v`

  Expected: FAIL — `parse_env_vars` not yet imported in resolver.

- [ ] **Step 3: Update _collect_env_vars() in resolver.py**

  Add import to `resolver.py`:
  ```python
  from color_scheme_settings.transforms import parse_env_vars
  ```

  Replace the `_collect_env_vars` method body:
  ```python
  def _collect_env_vars(self) -> dict[str, Any]:
      """Collect COLORSCHEME_* environment variables using shared parser."""
      return parse_env_vars()
  ```

- [ ] **Step 4: Run tests to confirm they pass**

  Run: `cd packages/settings && python -m pytest tests/test_resolver.py -v`

  Expected: All tests PASS.

---

### Task 11: Fix error handling in _load_project_config and _load_user_config

**Files:**
- Modify: `packages/settings/src/color_scheme_settings/resolver.py`
- Modify: `packages/settings/tests/test_resolver.py`

- [ ] **Step 1: Write failing test**

  Add to `packages/settings/tests/test_resolver.py`:

  ```python
  class TestResolverErrorHandling:
      """IMP-2: malformed config files must raise, not silently warn."""

      def test_malformed_project_config_raises_settings_file_error(
          self, tmp_path: Path
      ):
          bad_toml = tmp_path / "settings.toml"
          bad_toml.write_text("this is not [[ valid toml")

          resolver = ConfigResolver()
          import os
          original_cwd = os.getcwd()
          os.chdir(tmp_path)
          try:
              with pytest.raises(SettingsFileError):
                  resolver._load_project_config()
          finally:
              os.chdir(original_cwd)
  ```

- [ ] **Step 2: Run test to confirm it fails**

  Run: `cd packages/settings && python -m pytest tests/test_resolver.py::TestResolverErrorHandling -v`

  Expected: FAIL — currently swallows the error as a warning.

- [ ] **Step 3: Fix error handling in resolver.py**

  In `_load_project_config()`, change the broad exception handler to:
  ```python
  try:
      with project_settings.open("rb") as f:
          return tomllib.load(f)
  except tomllib.TOMLDecodeError as e:
      raise SettingsFileError(file_path=project_settings, reason=str(e)) from e
  except OSError as e:
      raise SettingsFileError(file_path=project_settings, reason=str(e)) from e
  ```

  Apply the same change to `_load_user_config()`.

  Remove the broad `except Exception` handler and the associated `self.warnings.append(...)` blocks from both methods.

- [ ] **Step 4: Run all resolver tests**

  Run: `cd packages/settings && python -m pytest tests/test_resolver.py -v`

  Expected: All tests PASS.

- [ ] **Step 5: Commit (Tasks 9–11 together)**

  ```bash
  git add packages/settings/src/color_scheme_settings/resolver.py \
          packages/settings/tests/test_resolver.py
  git commit -m "fix(settings): complete ConfigResolver — real defaults, shared env parser, strict error handling (CRIT-02)"
  ```

---

## Chunk 5: Phase 5 — Test Quality

### Task 12: Remove direct _entries access from test_registry.py

**Files:**
- Modify: `packages/settings/tests/test_registry.py`

**Context:** The `clean_registry` fixture uses `SchemaRegistry._entries.clear()` directly, bypassing the public API. The public API is `SchemaRegistry.clear()`, which is what `test_loader.py` already uses.

- [ ] **Step 1: Update the clean_registry fixture in test_registry.py**

  In `packages/settings/tests/test_registry.py`, change the `clean_registry` fixture:

  ```python
  # Before:
  @pytest.fixture(autouse=True)
  def clean_registry():
      """Reset registry before each test."""
      SchemaRegistry._entries.clear()
      yield
      SchemaRegistry._entries.clear()

  # After:
  @pytest.fixture(autouse=True)
  def clean_registry():
      """Reset registry before each test."""
      SchemaRegistry.clear()
      yield
      SchemaRegistry.clear()
  ```

- [ ] **Step 2: Run registry tests to confirm behaviour is unchanged**

  Run: `cd packages/settings && python -m pytest tests/test_registry.py -v`

  Expected: All tests PASS.

- [ ] **Step 3: Commit**

  ```bash
  git add packages/settings/tests/test_registry.py
  git commit -m "test(settings): use SchemaRegistry.clear() public API in clean_registry fixture (Phase 5)"
  ```

---

### Task 13: Add registration bleed guard to test_pipeline.py

**Files:**
- Modify: `packages/settings/tests/test_pipeline.py`

**Context:** Pipeline tests register schemas but a leaked registration could affect other tests in the suite. Add a hermetic guard test that verifies the registry is empty at the start.

- [ ] **Step 1: Add test_registration_bleed_guard to test_pipeline.py**

  Add to `packages/settings/tests/test_pipeline.py` (inside a suitable class or as a standalone test):

  ```python
  class TestRegistrationBleedGuard:
      """Guard against test registration leaking between test sessions."""

      def test_registry_is_empty_before_test_setup(self):
          """The registry must be empty unless this test registers something.

          If this test fails, a previous test is leaking schema registrations.
          Check that all tests using SchemaRegistry call SchemaRegistry.clear()
          in an autouse fixture.
          """
          # This test has no autouse fixture — it sees the raw registry state
          # at the point it runs. If another test leaked a registration, it fails.
          # If the suite's autouse fixtures are working correctly, it passes.
          # NOTE: This test must run BEFORE any fixture registers schemas.
          # Place it at the top of the class.
          assert SchemaRegistry.all_namespaces() == [], (
              f"Registry leaked from a previous test: {SchemaRegistry.all_namespaces()}"
          )
  ```

  Also ensure the pipeline test module's `autouse` fixture calls `SchemaRegistry.clear()` before and after each test (match the pattern in `test_loader.py`).

- [ ] **Step 2: Run pipeline tests**

  Run: `cd packages/settings && python -m pytest tests/test_pipeline.py -v`

  Expected: All tests PASS including the new bleed guard.

- [ ] **Step 3: Commit**

  ```bash
  git add packages/settings/tests/test_pipeline.py
  git commit -m "test(settings): add registration bleed guard to test_pipeline.py (Phase 5)"
  ```

---

## Chunk 6: Phase 6 — Smoke Test Updates

### Task 14: Strengthen test_settings_precedence in smoke tests

**Files:**
- Modify: smoke test script (find with: `grep -rn "test_settings_precedence" .`)

- [ ] **Step 1: Locate the smoke test**

  Run: `grep -rn "test_settings_precedence\|test_dry_run" smoke-tests/ scripts/ bin/ --include="*.sh" -l 2>/dev/null || find . -name "*.sh" | xargs grep -l "test_settings_precedence" 2>/dev/null`

  Note the file path.

- [ ] **Step 2: Update test_settings_precedence**

  Find the `test_settings_precedence` section. Replace the current implementation with the one from the spec:

  ```bash
  env_test_dir="$TEST_OUTPUT_DIR/env-override-test"
  COLORSCHEME_OUTPUT__DIRECTORY="$env_test_dir" \
    run_cmd color-scheme-core generate "$WALLPAPER"
  if [ -f "$env_test_dir/colors.json" ]; then
      test_passed "env var COLORSCHEME_OUTPUT__DIRECTORY overrides output directory"
  else
      test_failed "env var COLORSCHEME_OUTPUT__DIRECTORY had no effect"
  fi
  ```

  Remove any fallback `pass` branch that would make the test vacuously pass.

- [ ] **Step 3: Update test_dry_run_configuration_resolution**

  Find the `test_dry_run_configuration_resolution` section. Replace the generic word-match assertion with a specific known default value check:

  ```bash
  # Assert 'docker' appears with 'Default' attribution
  if dry_run_output | grep -q "Default.*docker\|docker.*Default"; then
      test_passed "dry-run shows docker as package default with Default attribution"
  else
      test_failed "dry-run did not show docker with Default attribution"
  fi
  ```

  (Adjust the grep pattern to match the actual output format of the dry-run reporter.)

- [ ] **Step 4: Run the smoke tests (if environment is available)**

  Run: `make smoke-test-custom` (or the appropriate target)

  Expected: Both `test_settings_precedence` and `test_dry_run_configuration_resolution` PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add <smoke-test-file>
  git commit -m "test(smoke): strengthen env-var and dry-run configuration assertions (Phase 6)"
  ```

---

## Chunk 7: Phase 7 — Fix Double Saturation (CRIT-04)

### Task 15: Remove redundant saturation blocks from cli/main.py

**Files:**
- Modify: `packages/core/src/color_scheme/cli/main.py`
- Modify: `packages/core/tests/test_cli_main.py` (or create if it doesn't exist — check first)

**Context:** Three backends apply saturation in `generate()`. Then `cli/main.py` applies it again in two places: lines 215–229 (generate command) and lines 419–430 (show command TTY branch). The non-TTY show path (lines 432–444) does NOT double-apply — making TTY and non-TTY inconsistent. Fix: remove the two redundant blocks from `cli/main.py`.

- [ ] **Step 1: Locate and read the test file**

  Run: `find packages/core/tests -name "test_cli_main.py" 2>/dev/null || find packages/core -name "test_cli_main.py"`

  Read the file to understand existing test structure.

- [ ] **Step 2: Write failing tests for generate command**

  Add to the CLI test file, in or alongside `TestGenerateSaturation`:

  ```python
  class TestGenerateSaturationAppliedOnce:
      """CRIT-04: saturation must be applied exactly once — by the backend."""

      def test_saturation_applied_exactly_once_in_generate(self):
          """adjust_saturation must be called exactly once per color, not twice."""
          from unittest.mock import MagicMock, patch, call
          from color_scheme.types import Color, ColorScheme

          mock_color = MagicMock(spec=Color)
          mock_color.adjust_saturation.return_value = mock_color
          mock_color.hex = "#aabbcc"

          mock_scheme = MagicMock(spec=ColorScheme)
          mock_scheme.background = mock_color
          mock_scheme.foreground = mock_color
          mock_scheme.cursor = mock_color
          mock_scheme.colors = [mock_color] * 16

          with patch("color_scheme.cli.main.BackendFactory") as mock_factory_cls, \
               patch("color_scheme.cli.main.OutputManager"), \
               patch("color_scheme.cli.main.load_config"):
              mock_backend = MagicMock()
              mock_backend.generate.return_value = mock_scheme
              mock_factory_cls.return_value.create.return_value = mock_backend
              mock_factory_cls.return_value.auto_detect.return_value = MagicMock()

              from click.testing import CliRunner
              from color_scheme.cli.main import cli
              runner = CliRunner()
              runner.invoke(cli, ["generate", "/fake/image.jpg", "--saturation", "1.5"])

          # Each color's adjust_saturation must be called exactly once
          assert mock_color.adjust_saturation.call_count == 1, (
              f"adjust_saturation called {mock_color.adjust_saturation.call_count} times, expected 1"
          )
  ```

- [ ] **Step 3: Run tests to confirm they fail**

  Run: `cd packages/core && python -m pytest tests/test_cli_main.py::TestGenerateSaturationAppliedOnce -v`

  Expected: FAIL — `adjust_saturation` is called more than once.

- [ ] **Step 4: Write failing tests for show command**

  Add to the CLI test file:

  ```python
  class TestShowSaturationAppliedOnce:
      """CRIT-04: show command TTY path must apply saturation exactly once."""

      def test_saturation_applied_exactly_once_in_show_tty(self):
          """TTY show path must not double-apply saturation."""
          # Similar mock setup as generate test above
          # Invoke: runner.invoke(cli, ["show", "/fake/image.jpg", "--saturation", "1.5"])
          # with console.is_terminal = True patched
          # assert mock_color.adjust_saturation.call_count == 1

      def test_saturation_consistent_between_tty_and_nontty(self):
          """TTY and non-TTY show must call adjust_saturation the same number of times."""
          # Run both paths with same inputs; compare call counts
          # Both should be 1 after the fix
  ```

- [ ] **Step 5: Run tests to confirm they fail**

  Run: `cd packages/core && python -m pytest tests/test_cli_main.py::TestShowSaturationAppliedOnce -v`

  Expected: FAIL — TTY path calls `adjust_saturation` twice.

- [ ] **Step 6: Remove lines 215–229 from cli/main.py (generate command)**

  In `packages/core/src/color_scheme/cli/main.py`, delete the entire block:

  ```python
  # Apply saturation adjustment if specified
  if (
      generator_config.saturation_adjustment is not None
      and generator_config.saturation_adjustment != 1.0
  ):
      sat = generator_config.saturation_adjustment
      console.print(f"[cyan]Adjusting saturation:[/cyan] {sat}")
      # Adjust all colors
      color_scheme.background = color_scheme.background.adjust_saturation(sat)
      color_scheme.foreground = color_scheme.foreground.adjust_saturation(sat)
      color_scheme.cursor = color_scheme.cursor.adjust_saturation(sat)
      color_scheme.colors = [
          c.adjust_saturation(sat) for c in color_scheme.colors
      ]
  ```

  This is the block immediately after `color_scheme = generator.generate(image_path, generator_config)` in the `generate` command handler.

- [ ] **Step 7: Remove lines 419–430 from cli/main.py (show command TTY)**

  In the `show` command handler, delete the block:

  ```python
  # Apply saturation adjustment if specified
  if (
      generator_config.saturation_adjustment is not None
      and generator_config.saturation_adjustment != 1.0
  ):
      sat = generator_config.saturation_adjustment
      color_scheme.background = color_scheme.background.adjust_saturation(sat)
      color_scheme.foreground = color_scheme.foreground.adjust_saturation(sat)
      color_scheme.cursor = color_scheme.cursor.adjust_saturation(sat)
      color_scheme.colors = [
          c.adjust_saturation(sat) for c in color_scheme.colors
      ]
  ```

  This is the block immediately after `color_scheme = generator.generate(image_path, generator_config)` in the TTY branch of the `show` command.

- [ ] **Step 8: Run all tests to confirm they pass**

  Run: `cd packages/core && python -m pytest -v`

  Expected: All tests PASS.

- [ ] **Step 9: Commit**

  ```bash
  git add packages/core/src/color_scheme/cli/main.py \
          packages/core/tests/test_cli_main.py
  git commit -m "fix(core): remove redundant saturation application from cli/main.py — backends are the single authority (CRIT-04)"
  ```

---

## Chunk 8: Phase 8 — Documentation Corrections

### Task 16: Fix show command docs (MAJ-01)

**Files:**
- Modify: `docs/reference/cli-orchestrator.md`
- Modify: `docs/explanation/architecture.md`

- [ ] **Step 1: Fix cli-orchestrator.md command summary table**

  In `docs/reference/cli-orchestrator.md`, find the command summary table row:
  ```
  show | No | Display colors (delegates to core CLI on host)
  ```
  Change it to:
  ```
  show | Yes | Display colors via container
  ```

  (The exact column format may differ — adjust to match the existing table style.)

- [ ] **Step 2: Fix architecture.md**

  In `docs/explanation/architecture.md`, find and remove the paragraph that says something like:
  > "The show command is an exception: the orchestrator's show delegates directly to the core CLI on the host"

  Replace it with:
  > "`show` runs inside a container, like all other orchestrator commands. TTY detection is performed inside the container so that Rich renders colour tables interactively when the host terminal supports it."

- [ ] **Step 3: Commit**

  ```bash
  git add docs/reference/cli-orchestrator.md docs/explanation/architecture.md
  git commit -m "docs: fix stale show-command documentation — show now runs in a container (MAJ-01)"
  ```

---

### Task 17: Update settings layer documentation (MIN-03)

**Files:**
- Modify: `docs/reference/settings-api.md`
- Modify: `docs/how-to/configure-settings.md`

- [ ] **Step 1: Update BHV-0019 in settings-api.md**

  Find BHV-0019 in `docs/reference/settings-api.md`. Change:
  ```
  package < project < user < CLI
  ```
  To:
  ```
  package < project < user < env < CLI
  ```

- [ ] **Step 2: Add BHV-0038 to settings-api.md**

  After the BHV-0019 entry, add:
  ```
  **BHV-0038:** Env-var layer (`COLORSCHEME_*`) is processed by `load_config()` as layer 4,
  between user config and CLI overrides. Variables follow the pattern
  `COLORSCHEME_SECTION__KEY` (double underscore separates section from key).
  ```

- [ ] **Step 3: Update load_config() description in settings-api.md**

  Find the `load_config()` description and update it to list all five layers in order:
  1. Package defaults (from registered `settings.toml` files)
  2. Project config (`./settings.toml`)
  3. User config (`$XDG_CONFIG_HOME/color-scheme/settings.toml`)
  4. Environment variables (`COLORSCHEME_*`)
  5. CLI overrides (applied by `get_config(overrides=...)`)

- [ ] **Step 4: Add BHV-0038 row to configure-settings.md**

  In `docs/how-to/configure-settings.md`, find the verification table and add a row for BHV-0038:
  ```
  | BHV-0038 | Set `COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom` and run `color-scheme-core generate`; verify `custom` backend is used |
  ```

- [ ] **Step 5: Commit**

  ```bash
  git add docs/reference/settings-api.md docs/how-to/configure-settings.md
  git commit -m "docs: add env-var layer to settings documentation (BHV-0019 update + BHV-0038) (MIN-03)"
  ```

---

## Chunk 9: Phase 9 — Changelog and Final Verification

### Task 18: Add changelog entries

**Files:**
- Modify: `docs/changelog.md`

- [ ] **Step 1: Add entries under ## [Unreleased]**

  In `docs/changelog.md`, add these items under `## [Unreleased]` (create a `### Added` / `### Fixed` / `### Changed` grouping as appropriate):

  ```markdown
  ### Fixed

  - Settings: `COLORSCHEME_*` environment variable layer now active in `load_config()` (CRIT-01)
  - Settings: deep merge no longer mutates earlier layers when 3+ layers are present (CRIT-03)
  - Settings: orchestrator `settings.toml` `[container]` key wrapper removed — `engine` field now correctly loaded from package defaults (MAJ-02)
  - Core: saturation adjustment no longer applied twice when using `--saturation` (CRIT-04)

  ### Added

  - Settings: `get_xdg_config_home()` and `get_user_settings_file()` functions in `paths.py` that read `XDG_CONFIG_HOME` at call time rather than import time (MIN-01)

  ### Changed

  - Docs: `show` command correctly documented as container-based (MAJ-01)
  - Docs: settings layer order updated to include env-var layer (MIN-03)
  - Docs: `docs/archive/`, `docs/plans/`, and `docs/superpowers/` removed
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add docs/changelog.md
  git commit -m "docs: add changelog entries for 2026-03-11 audit fixes (Phase 9)"
  ```

---

### Task 19: Final verification

- [ ] **Step 1: Run the full test suite**

  Run: `make test-all`

  Expected: All tests PASS; coverage >= 95% on all packages.

- [ ] **Step 2: Run smoke tests**

  Run: `make smoke-test-custom`

  Expected: All smoke tests PASS, including:
  - `test_settings_precedence` (env var override)
  - `test_dry_run_configuration_resolution` (docker shown with Default attribution)

- [ ] **Step 3: Verify saturation applied once**

  Run:
  ```bash
  color-scheme-core generate /path/to/test/image.jpg --saturation 1.5 --dry-run
  ```

  Expected: Saturation listed once in output; no double-application log entry.

- [ ] **Step 4: Verify env-var layer works end-to-end**

  Run:
  ```bash
  COLORSCHEME_GENERATION__DEFAULT_BACKEND=custom color-scheme-core generate /path/to/image.jpg
  ```

  Expected: `custom` backend is used.

- [ ] **Step 5: Run MkDocs build**

  Run: `make docs-build`

  Expected: Build passes with `--strict` (no broken links, no warnings).
