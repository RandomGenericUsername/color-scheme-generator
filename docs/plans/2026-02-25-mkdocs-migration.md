# MkDocs Material Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add MkDocs Material as a local doc site generator with Diataxis quadrant tabs, touching zero existing doc content.

**Architecture:** Drop a `mkdocs.yml` at the repo root that points at the existing `docs/` tree. The four Diataxis quadrant folders become Material navigation tabs. `docs/README.md` is renamed to `docs/index.md` (the only structural change). Archive and audit files are excluded via config.

**Tech Stack:** `mkdocs-material`, `uv` (package manager), `make` (task runner)

---

### Task 1: Add mkdocs-material dev dependency

**Files:**
- Modify: `pyproject.toml:28-39`

**Step 1: Add the dependency**

In `pyproject.toml`, add `"mkdocs-material"` to the `[dependency-groups] dev` list:

```toml
[dependency-groups]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=7.0.0",
    "pytest-xdist>=3.8.0",
    "mypy>=1.19.0",
    "black>=26.0.0",
    "ruff>=0.14.0",
    "isort>=7.0.0",
    "bandit>=1.8.6",
    "pre-commit>=3.8.0",
    "pywal>=3.3.0",
    "mkdocs-material",
]
```

**Step 2: Install**

```bash
uv sync
```

Expected: resolves and installs `mkdocs-material` and its deps (click, jinja2, etc.) into `.venv`. No errors.

**Step 3: Verify binary is available**

```bash
uv run mkdocs --version
```

Expected output: `mkdocs, version 1.x.x from ...`

**Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add mkdocs-material dev dependency"
```

---

### Task 2: Rename docs/README.md to docs/index.md

**Files:**
- Rename: `docs/README.md` → `docs/index.md`

**Step 1: Rename the file**

```bash
git mv docs/README.md docs/index.md
```

**Step 2: Verify git tracks it as a rename**

```bash
git status
```

Expected: shows `renamed: docs/README.md -> docs/index.md`

**Step 3: Commit**

```bash
git commit -m "docs: rename README.md to index.md for MkDocs home page"
```

---

### Task 3: Create mkdocs.yml

**Files:**
- Create: `mkdocs.yml` (at repo root, same level as `pyproject.toml`)

**Step 1: Create the file**

```yaml
site_name: Color Scheme Generator
docs_dir: docs
theme:
  name: material
  palette:
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.top
    - search.highlight

exclude_docs: |
  archive/
  audit-*.md

nav:
  - Tutorial:
    - Getting Started: tutorials/getting-started.md
  - How-To:
    - Configure Settings: how-to/configure-settings.md
    - Install Backends: how-to/install-backends.md
    - Use Dry Run: how-to/use-dry-run.md
    - Integrate with Shell: how-to/integrate-shell.md
    - Create Templates: how-to/create-templates.md
    - Troubleshoot Errors: how-to/troubleshoot-errors.md
  - Reference:
    - CLI (color-scheme-core): reference/cli-core.md
    - CLI (color-scheme): reference/cli-orchestrator.md
    - Settings API: reference/settings-api.md
    - Exceptions: reference/exceptions.md
    - Types: reference/types.md
  - Explanation:
    - Architecture: explanation/architecture.md
```

**Step 2: Verify it builds cleanly**

```bash
uv run mkdocs build --strict
```

Expected:
- Output ends with `INFO  -  Documentation built in X.XX seconds`
- Zero warnings or errors
- A `site/` directory appears at the repo root

**Step 3: Commit**

```bash
git add mkdocs.yml
git commit -m "docs: add mkdocs.yml with Material theme and Diataxis nav tabs"
```

---

### Task 4: Update Makefile

**Files:**
- Modify: `Makefile:1` (PHONY line)
- Modify: `Makefile:418` (insert new section before `##@ Cleanup`)

**Step 1: Add targets to .PHONY**

The current `.PHONY` line at line 1 ends with `...test-templates push clean`. Append `docs-serve docs-build`:

```makefile
.PHONY: help dev lint format build install-core install-orchestrator install-settings install-templates test-all test-run pipeline lint-templates format-templates security-templates test-templates push clean docs-serve docs-build
```

**Step 2: Add Documentation section before `##@ Cleanup`**

Insert before the `##@ Cleanup` line (line 418):

```makefile
##@ Documentation
docs-serve: ## Serve docs locally with live reload (http://127.0.0.1:8000)
	uv run mkdocs serve

docs-build: ## Build static docs site to site/ (--strict fails on broken links)
	uv run mkdocs build --strict

```

**Step 3: Verify make help shows the new targets**

```bash
make help | grep docs
```

Expected:
```
  docs-serve       Serve docs locally with live reload (http://127.0.0.1:8000)
  docs-build       Build static docs site to site/ (--strict fails on broken links)
```

**Step 4: Commit**

```bash
git add Makefile
git commit -m "chore: add docs-serve and docs-build Makefile targets"
```

---

### Task 5: Update .gitignore

**Files:**
- Modify: `.gitignore`

**Step 1: Add site/ under the `# Project specific` block**

The current `.gitignore` has a `# Project specific` section at line 73. Add `site/` to it:

```gitignore
# Project specific
*.log
.archive/
.mypy_cache/
.ruff_cache/
bandit-report.json
site/
```

**Step 2: Verify site/ is ignored**

```bash
git status
```

Expected: the `site/` directory created by `mkdocs build` in Task 3 does NOT appear in untracked files.

**Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: ignore MkDocs generated site/ directory"
```

---

### Task 6: Final verification

**Step 1: Run mkdocs build --strict one more time**

```bash
make docs-build
```

Expected: exits 0, no warnings, no broken link errors.

**Step 2: Spot-check the live site**

```bash
make docs-serve
```

Open `http://127.0.0.1:8000` in a browser and verify:
- Four tabs in the header: **Tutorial**, **How-To**, **Reference**, **Explanation**
- Each tab shows the correct pages in the left sidebar
- Dark/light mode toggle works
- Search box finds content
- `docs/archive/` pages do NOT appear anywhere in the nav

Press `Ctrl+C` to stop the server.

**Step 3: Clean up build artifact**

```bash
rm -rf site/
```

`site/` is gitignored so this is safe — it will be regenerated on next `make docs-serve`.
