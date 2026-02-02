# Coverage Gap Analysis

## Overview

Current coverage: **90%** (778 statements, 78 missed)  
Required coverage: **95%**  
Gap: **5% (~39 statements to cover or exclude)**

---

## Coverage Report

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/color_scheme/cli/main.py              195     65    67%   [see below]
src/color_scheme/core/base.py              18      3    83%   31, 40, 50
src/color_scheme/backends/wallust.py       89      6    93%   107, 114, 126, 167-169
src/color_scheme/backends/pywal.py         88      1    99%   138
src/color_scheme/config/defaults.py        22      1    95%   48
src/color_scheme/core/types.py             61      1    98%   162
src/color_scheme/factory.py                51      1    98%   55
---------------------------------------------------------------------
TOTAL                                     778     78    90%
```

---

## Gap 1: CLI Main (67% → 95%)

**File:** `src/color_scheme/cli/main.py`  
**Missing:** 65 lines  
**Impact:** This is the primary coverage gap

### Uncovered Code Categories

| Category | Lines | Why Uncovered | Solution |
|----------|-------|---------------|----------|
| `version` command | 59-61 | No test calls it | Add test |
| Error: InvalidImageError | 200-202 | Exception not triggered | Mock test |
| Error: BackendNotAvailableError | 205-212 | Exception not triggered | Mock test |
| Error: ColorExtractionError | 215-217 | Exception not triggered | Mock test |
| Error: TemplateRenderError | 220-223 | Exception not triggered | Mock test |
| Error: OutputWriteError | 226-229 | Exception not triggered | Mock test |
| Error: ColorSchemeError | 232-234 | Exception not triggered | Mock test |
| Error: Exception (catch-all) | 240-243 | Exception not triggered | Mock test |
| Saturation display (generate) | 162-168 | Conditional branch | Add test with `--saturation` |
| Show command errors | 418-449 | Same as generate | Mock tests |
| Entry point | 454, 458 | `main()` function | Simple test |

### Why These Are Uncovered

The integration tests in `tests/integration/test_cli_generate.py` test the happy path with real backends. They don't:
- Trigger specific exceptions
- Test the `version` command
- Test with saturation adjustment

### Solution

Create unit tests with mocking to trigger each exception handler.

---

## Gap 2: Abstract Base Class (83% → 100%)

**File:** `src/color_scheme/core/base.py`  
**Missing:** 3 lines (31, 40, 50)

### Uncovered Code

```python
@abstractmethod
def generate(...):
    pass  # Line 31 - NEVER EXECUTED

@abstractmethod
def is_available(...):
    pass  # Line 40 - NEVER EXECUTED

@abstractmethod
def backend_name(...):
    pass  # Line 50 - NEVER EXECUTED
```

### Why These Are Uncovered

**These lines can NEVER be executed.** They are abstract method bodies. Python's ABC mechanism ensures:
1. You cannot instantiate `ColorSchemeGenerator` directly
2. Subclasses must override these methods
3. The `pass` statement in the base class is never reached

### Solution

Add `# pragma: no cover` to exclude from coverage. This is standard practice for abstract methods.

---

## Gap 3: Wallust Backend (93% → 98%)

**File:** `src/color_scheme/backends/wallust.py`  
**Missing:** 6 lines

### Uncovered Code

| Lines | Code | Why Uncovered |
|-------|------|---------------|
| 107 | `raise ColorExtractionError(...)` | Cache dir missing |
| 114 | `raise ColorExtractionError(...)` | No subdirectory |
| 126 | `raise ColorExtractionError(...)` | No palette file |
| 167-169 | `_hex_to_rgb` return | Partial coverage |

### Analysis

These are error paths for when wallust's cache is in an unexpected state:
1. `~/.cache/wallust/` doesn't exist
2. No subdirectory inside cache
3. No valid palette file found

### Solution

Add unit tests that mock `Path.home()` to return a temp directory with controlled cache states.

---

## Gap 4: Minor Gaps (Each ~1 line)

| File | Line | Code | Solution |
|------|------|------|----------|
| `pywal.py` | 138 | Cache read error | Low priority, skip |
| `defaults.py` | 48 | Container path branch | Low priority, skip |
| `types.py` | 162 | Unknown backend else | Low priority, skip |
| `factory.py` | 55 | Unknown backend error | Low priority, skip |

These are edge cases that are unlikely in practice. The main coverage gain comes from testing the CLI.

---

## Coverage Strategy

### Must Cover (High Impact)

| Priority | File | Expected Gain |
|----------|------|---------------|
| 1 | `cli/main.py` | +28% → 95% |
| 2 | `core/base.py` | +17% → 100% (exclude) |
| 3 | `backends/wallust.py` | +5% → 98% |

### Implementation Plan

1. **Create `tests/unit/test_cli_main.py`**
   - Version command test
   - Error handler tests (mocked)
   - Saturation display tests

2. **Modify `core/base.py`**
   - Add `# pragma: no cover` to abstract methods

3. **Modify `tests/unit/test_wallust_backend.py`**
   - Add cache error path tests

### Expected Result

| File | Before | After |
|------|--------|-------|
| `cli/main.py` | 67% | ~95% |
| `core/base.py` | 83% | 100% |
| `backends/wallust.py` | 93% | ~98% |
| **TOTAL** | **90%** | **~96%** |
