# Implementation Specification

## File Change Summary

| File | Action | Lines Changed |
|------|--------|---------------|
| `src/color_scheme/output/manager.py` | Modify | +3 |
| `src/color_scheme/backends/pywal.py` | Modify | +4 |
| `src/color_scheme/backends/wallust.py` | Modify | +4 |
| `src/color_scheme/cli/main.py` | Modify | +4, -2 |
| `src/color_scheme/core/base.py` | Modify | +3 |
| `tests/unit/test_cli_main.py` | Create | ~320 |
| `tests/unit/test_wallust_backend.py` | Modify | +45 |

---

## Change 1: output/manager.py

**Location:** Lines 42-48  
**Type:** Add security annotation

### Before
```python
        # Setup Jinja2 environment with StrictUndefined
        self.template_env = Environment(
```

### After
```python
        # Setup Jinja2 environment with StrictUndefined
        # NOTE: Autoescape disabled because we generate config files (CSS/JSON/YAML),
        # not HTML. Enabling it would corrupt hex colors: #FF0000 → &#35;FF0000
        self.template_env = Environment(  # nosec B701
```

---

## Change 2: backends/pywal.py (import)

**Location:** Line 6  
**Type:** Add security annotation

### Before
```python
import subprocess
```

### After
```python
import subprocess  # nosec B404 - Required for external tool invocation
```

---

## Change 3: backends/pywal.py (subprocess call)

**Location:** Lines 92-99  
**Type:** Add security annotation

### Before
```python
            logger.debug("Running pywal command: %s", " ".join(cmd))
            subprocess.run(
```

### After
```python
            logger.debug("Running pywal command: %s", " ".join(cmd))
            # Security: command hardcoded, image_path validated, shell=False, timeout set
            subprocess.run(  # nosec B603
```

---

## Change 4: backends/wallust.py (import)

**Location:** Line 6  
**Type:** Add security annotation

### Before
```python
import subprocess
```

### After
```python
import subprocess  # nosec B404 - Required for external tool invocation
```

---

## Change 5: backends/wallust.py (subprocess call)

**Location:** Lines 93-100  
**Type:** Add security annotation

### Before
```python
            logger.debug("Running wallust command: %s", " ".join(cmd))
            subprocess.run(
```

### After
```python
            logger.debug("Running wallust command: %s", " ".join(cmd))
            # Security: command hardcoded, image_path validated, shell=False, timeout set
            subprocess.run(  # nosec B603
```

---

## Change 6: cli/main.py (assert statements)

**Location:** Lines 174-175  
**Type:** Replace assert with explicit checks

### Before
```python
        output_manager = OutputManager(config.core)
        assert generator_config.output_dir is not None
        assert generator_config.formats is not None
        console.print(
```

### After
```python
        output_manager = OutputManager(config.core)
        if generator_config.output_dir is None:
            raise ValueError("output_dir must be configured for generate command")
        if generator_config.formats is None:
            raise ValueError("formats must be configured for generate command")
        console.print(
```

---

## Change 7: core/base.py (coverage exclusion)

**Location:** Lines 31, 40, 50  
**Type:** Add coverage pragma

### Before
```python
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        ...
        """
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        ...
        """
        pass
```

### After
```python
        """
        pass  # pragma: no cover

    @abstractmethod
    def is_available(self) -> bool:
        ...
        """
        pass  # pragma: no cover

    @property
    @abstractmethod
    def backend_name(self) -> str:
        ...
        """
        pass  # pragma: no cover
```

---

## Change 8: Create tests/unit/test_cli_main.py

**Type:** New file  
**Purpose:** Test CLI error handling and uncovered paths

### Required Test Classes

```
TestVersionCommand
├── test_version_command_success
└── test_version_contains_version_number

TestGenerateCommandErrors  
├── test_generate_image_not_found
├── test_generate_path_is_directory
├── test_generate_invalid_image_error
├── test_generate_backend_not_available_error
├── test_generate_color_extraction_error
├── test_generate_template_render_error
├── test_generate_output_write_error
├── test_generate_generic_colorscheme_error
└── test_generate_unexpected_exception

TestGenerateCommandSaturation
└── test_generate_with_saturation_adjustment

TestShowCommandErrors
├── test_show_image_not_found
├── test_show_path_is_directory
├── test_show_invalid_image_error
├── test_show_backend_not_available_error
├── test_show_color_extraction_error
├── test_show_generic_colorscheme_error
└── test_show_unexpected_exception

TestShowCommandSaturation
└── test_show_with_saturation_adjustment

TestMainEntryPoint
├── test_main_function_exists_and_callable
└── test_main_function_is_typer_app
```

### Test Pattern

Each error test follows this pattern:
1. Create valid test image using PIL
2. Patch `BackendFactory` or `OutputManager`
3. Configure mock to raise specific exception
4. Invoke CLI command
5. Assert exit code 1
6. Assert error message in stdout

---

## Change 9: Modify tests/unit/test_wallust_backend.py

**Type:** Add tests  
**Location:** End of `TestWallustGenerator` class

### Tests to Add

```
test_generate_cache_dir_not_found
├── Mock Path.home() to temp dir (no .cache/wallust)
├── Expect ColorExtractionError
└── Assert "cache directory not found" in message

test_generate_no_cache_subdirectory
├── Create .cache/wallust/ but empty
├── Expect ColorExtractionError
└── Assert "subdirectory" in message

test_generate_no_palette_file
├── Create .cache/wallust/hash/ with only large files
├── Expect ColorExtractionError
└── Assert "palette file" in message
```

---

## Verification Commands

```bash
cd /home/inumaki/Development/color-scheme/packages/core

# Bandit (expect: exit 0, no findings)
uv run bandit -r src/ -f screen

# Tests (expect: all pass)
uv run pytest -v

# Coverage (expect: ≥95%)
uv run coverage report --fail-under=95
```
