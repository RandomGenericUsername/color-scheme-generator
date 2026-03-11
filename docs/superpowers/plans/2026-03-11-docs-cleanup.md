# Docs Cleanup Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up `docs/` by removing archived/superseded content, migrating `CHANGELOG.md` into `docs/`, and updating `mkdocs.yml` so `make docs-build --strict` passes.

**Architecture:** Pure file operations and text edits — no code changes, no tests. Order matters: migrate changelog and update nav before deleting `docs/superpowers/` (which contains this plan file).

**Tech Stack:** MkDocs with Material theme, Keep a Changelog format.

---

## Chunk 1: Migrate Changelog and Update Nav

### Task 1: Copy CHANGELOG.md to docs/changelog.md

**Files:**
- Create: `docs/changelog.md` (copy of `CHANGELOG.md`)
- Modify: `CHANGELOG.md` (root, replace with redirect)

- [ ] **Step 1: Copy CHANGELOG.md to docs/changelog.md**

  ```bash
  cp CHANGELOG.md docs/changelog.md
  ```

  This preserves the full current content without risk of truncation.

- [ ] **Step 2: Replace root CHANGELOG.md with one-liner redirect**

  Overwrite `CHANGELOG.md` at the project root with:

  ```markdown
  See [docs/changelog.md](docs/changelog.md) for the full changelog.
  ```

- [ ] **Step 3: Verify files look correct**

  Run: `cat docs/changelog.md | head -5`
  Expected: `# Changelog`

  Run: `cat CHANGELOG.md`
  Expected: `See [docs/changelog.md](docs/changelog.md) for the full changelog.`

- [ ] **Step 4: Commit**

  ```bash
  git add docs/changelog.md CHANGELOG.md
  git commit -m "docs: migrate CHANGELOG.md into docs/changelog.md"
  ```

---

### Task 2: Update mkdocs.yml

**Files:**
- Modify: `mkdocs.yml`

- [ ] **Step 1: Remove the exclude_docs block**

  In `mkdocs.yml`, delete this verbatim block (4 lines):
  ```yaml
  exclude_docs: |
    archive/
    audit-*.md
    plans/
  ```
  After removal, `nav:` should follow directly after the blank line that ends the `features:` list.

  > **Warning:** Do NOT run `make docs-build` after this step. The `docs/superpowers/` directory still exists and is no longer excluded. Running a strict build now will fail. Complete all deletion tasks (Tasks 4–7) before running the build in Task 8.

- [ ] **Step 2: Add Changelog to the nav between Home and Tutorial**

  Change:
  ```yaml
  nav:
    - Home: index.md
    - Tutorial:
  ```
  To:
  ```yaml
  nav:
    - Home: index.md
    - Changelog: changelog.md
    - Tutorial:
  ```

- [ ] **Step 3: Verify mkdocs.yml**

  Run: `cat mkdocs.yml`

  Expected: No `exclude_docs` block; nav has `- Changelog: changelog.md` as second entry.

- [ ] **Step 4: Commit**

  ```bash
  git add mkdocs.yml
  git commit -m "docs: remove exclude_docs block and add Changelog to mkdocs nav"
  ```

---

### Task 3: Update docs/index.md

**Files:**
- Modify: `docs/index.md`

- [ ] **Step 1: Add changelog link to the "Start here" section**

  In `docs/index.md`, find the existing `---` divider that separates the "Start here" block from the "## How-to guides" section. Insert the following two lines immediately before `## How-to guides` (after the existing `---`):

  ```markdown
  ## Changelog

  See [Changelog](changelog.md) for a history of all notable changes.

  ---
  ```

  The result: "Start here" → `---` → Changelog section → `---` → "## How-to guides".

- [ ] **Step 2: Commit**

  ```bash
  git add docs/index.md
  git commit -m "docs: add changelog link to index.md"
  ```

---

## Chunk 2: Delete Stale Directories and Files

> **Note:** `docs/superpowers/` contains this plan file. Delete it last. Once deleted, the plan is gone — that is expected and correct.

### Task 4: Delete docs/archive/

**Files:**
- Delete: `docs/archive/` (entire directory)

- [ ] **Step 1: Remove the archive directory**

  ```bash
  rm -rf docs/archive/
  ```

- [ ] **Step 2: Stage and commit**

  ```bash
  git add -A docs/archive/
  git commit -m "docs: remove docs/archive/ — superseded content"
  ```

---

### Task 5: Delete docs/plans/

**Files:**
- Delete: `docs/plans/` (entire directory)

- [ ] **Step 1: Remove the plans directory**

  ```bash
  rm -rf docs/plans/
  ```

- [ ] **Step 2: Stage and commit**

  ```bash
  git add -A docs/plans/
  git commit -m "docs: remove docs/plans/ — completed implementation plans"
  ```

---

### Task 6: Delete docs/audit-2026-02-23.md

**Files:**
- Delete: `docs/audit-2026-02-23.md`

- [ ] **Step 1: Remove the stale audit file**

  ```bash
  rm docs/audit-2026-02-23.md
  ```

- [ ] **Step 2: Stage and commit**

  ```bash
  git add docs/audit-2026-02-23.md
  git commit -m "docs: remove docs/audit-2026-02-23.md — superseded by 2026-03-11 audit"
  ```

---

### Task 7: Delete docs/superpowers/ (LAST STEP)

**Files:**
- Delete: `docs/superpowers/` (entire directory — includes this plan file)

- [ ] **Step 1: Remove the superpowers directory**

  ```bash
  rm -rf docs/superpowers/
  ```

- [ ] **Step 2: Stage and commit**

  ```bash
  git add -A docs/superpowers/
  git commit -m "docs: remove docs/superpowers/ — internal AI specs replaced by implementation"
  ```

---

## Chunk 3: Verification

### Task 8: Verify docs/ structure and MkDocs build

**Files:** None (read-only verification)

- [ ] **Step 1: Confirm final docs/ structure**

  Run: `find docs/ -type f | sort`

  Expected files (only these, no others):
  ```
  docs/changelog.md
  docs/explanation/architecture.md
  docs/how-to/configure-settings.md
  docs/how-to/create-templates.md
  docs/how-to/install-backends.md
  docs/how-to/integrate-shell.md
  docs/how-to/troubleshoot-errors.md
  docs/how-to/use-dry-run.md
  docs/index.md
  docs/reference/cli-core.md
  docs/reference/cli-orchestrator.md
  docs/reference/exceptions.md
  docs/reference/settings-api.md
  docs/reference/types.md
  docs/tutorials/getting-started.md
  ```

- [ ] **Step 2: Run MkDocs build with strict mode**

  Run: `make docs-build`

  Expected: Build succeeds with zero warnings and zero errors.

  If `make docs-build` is not available, run directly:
  ```bash
  mkdocs build --strict
  ```

- [ ] **Step 3: Confirm root CHANGELOG.md is a redirect**

  Run: `cat CHANGELOG.md`
  Expected: `See [docs/changelog.md](docs/changelog.md) for the full changelog.`

- [ ] **Step 4: Confirm mkdocs.yml has no exclude_docs**

  Run: `grep -n "exclude_docs" mkdocs.yml`
  Expected: no output (grep exits 1, meaning the key is gone)
