# Investigation + Synthesis Framework: Documentation Regeneration

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Run the full investigation+synthesis framework on the color-scheme-generator project to produce clean, test-grounded Diátaxis documentation, replacing the existing docs which contain critical errors.

**Architecture:** Copy the framework template into `docs/investigation/`, configure it for the project, run an autonomous audit agent through 8 phases until `INVESTIGATION_STATUS = PASS`, archive old docs, then run an autonomous synthesis agent to write verified-only Diátaxis docs.

**Tech Stack:** Python / uv monorepo. Framework state files are plain Markdown. Agents are dispatched via the `general-purpose` Task subagent.

---

## Task 1: Copy framework template into docs/investigation/

**Files:**
- Create: `docs/investigation/audit-agent/` (directory + all files)
- Create: `docs/investigation/synthesis-agent/` (directory + all files)

**Step 1: Copy the audit-agent template**

```bash
cp -r /home/inumaki/Development/investigation-framework/audit-agent \
      docs/investigation/audit-agent
```

**Step 2: Copy the synthesis-agent template**

```bash
cp -r /home/inumaki/Development/investigation-framework/synthesis-agent \
      docs/investigation/synthesis-agent
```

**Step 3: Verify the structure**

```bash
find docs/investigation -type f | sort
```

Expected output includes (among others):
```
docs/investigation/audit-agent/00_RULES.md
docs/investigation/audit-agent/01_REQUIREMENTS.md
docs/investigation/audit-agent/02_STATE.md
docs/investigation/audit-agent/10_METRICS.md
docs/investigation/synthesis-agent/00_SYNTHESIS_RULES.md
docs/investigation/synthesis-agent/01_OUTPUT_TARGET.md
docs/investigation/synthesis-agent/profiles/diataxis/00_PROFILE.md
```

---

## Task 2: Configure the audit-agent

**Files:**
- Modify: `docs/investigation/audit-agent/01_REQUIREMENTS.md`
- Modify: `docs/investigation/audit-agent/.auditignore`

**Step 1: Write the requirements file**

Replace the contents of `docs/investigation/audit-agent/01_REQUIREMENTS.md` with:

```markdown
# Investigation Requirements

## Repository
- Repo root: /home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/color-scheme-generator
- Primary language/ecosystem: Python (uv monorepo, 4 packages: core, orchestrator, settings, templates)
- Project type: CLI / monorepo

## Scope
- Documentation roots: docs/
- Interfaces of interest:
  - color-scheme-core CLI (packages/core)
  - color-scheme CLI / orchestrator (packages/orchestrator)
  - Python public API: types, exceptions (packages/core)
  - Settings API: SchemaRegistry, config layers, env vars (packages/settings)
  - Template system (packages/templates)

## Tests
- Preferred test command(s): uv run pytest packages/ -v
- Test categories: unit (packages/*/tests/unit/), integration (packages/*/tests/integration/)
- Environment notes:
  - Smoke tests at tests/smoke/ require Docker/Podman containers — EXCLUDE from investigation scope
  - Unit + integration tests run locally with no external dependencies (external backends are mocked)

## Contracts (optional)
- No OpenAPI/JSON schema/proto files. Pydantic models in packages/settings/ serve as schema.

## Acceptance thresholds (defaults)
- S0 must be: 0
- S1 must be: <= 3
- Open Unknowns must be: <= 5
```

**Step 2: Update .auditignore to exclude smoke tests and archive**

Append these lines to `docs/investigation/audit-agent/.auditignore`:

```
tests/smoke/
docs/archive/
docs/investigation/
docs/plans/
uv.lock
package-lock.json
```

**Step 3: Verify the file looks correct**

Read `docs/investigation/audit-agent/01_REQUIREMENTS.md` and confirm all fields are filled.

---

## Task 3: Configure the synthesis-agent

**Files:**
- Modify: `docs/investigation/synthesis-agent/01_OUTPUT_TARGET.md`

**Step 1: Write the output target file**

Replace the contents of `docs/investigation/synthesis-agent/01_OUTPUT_TARGET.md` with:

```markdown
# Output Target

OUTPUT_PROFILE = synthesis-agent/profiles/diataxis
VERIFICATION_POLICY = verified-only
PRIMARY_AUDIENCE = end-users
OUTPUT_DIR = ../../
# Note: OUTPUT_DIR is relative to this file's location (docs/investigation/synthesis-agent/).
# ../../ resolves to docs/ — write tutorials/, how-to/, reference/, explanation/ there.

Scope:
- Interfaces:
  - color-scheme-core CLI: generate, show, version commands and all flags
  - color-scheme CLI: generate, show, install, uninstall commands and all flags
  - Settings API: SchemaRegistry, config file format, env var format, layer precedence
  - Template system: variables, Jinja2 environment, custom template override
  - Types: Color, ColorScheme fields and validation rules
  - Exceptions: all public exception types
- Exclusions:
  - Smoke test infrastructure (tests/smoke/)
  - Internal container execution implementation
  - CI/GitHub Actions workflows
  - Package-internal implementation details not part of public interface

Formatting:
- Language: English
- Tone: technical, direct
- Examples runnable: yes
- Include BHV IDs near examples: no
```

**Step 2: Verify the file**

Read `docs/investigation/synthesis-agent/01_OUTPUT_TARGET.md` and confirm OUTPUT_DIR and scope.

---

## Task 4: Commit the initialized framework

**Step 1: Stage and commit**

```bash
git add docs/investigation/
git commit -m "chore: initialize investigation+synthesis framework in docs/investigation/"
```

---

## Task 5: Run the audit agent

This is a long-running autonomous step. Dispatch a `general-purpose` subagent with the following prompt. The agent will iterate through all 8 phases of the state machine, writing investigation artifacts and checkpoints, until `INVESTIGATION_STATUS = PASS`.

**Step 1: Dispatch the audit agent**

Use the Task tool with `subagent_type=general-purpose` and this prompt:

```
You are running the audit-agent investigation loop for the color-scheme-generator project.

Project root: /home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/color-scheme-generator
Framework state directory: docs/investigation/audit-agent/ (relative to project root)

Your job:
1. Read docs/investigation/audit-agent/00_RULES.md — follow it exactly and non-negotiably.
2. Read docs/investigation/audit-agent/01_REQUIREMENTS.md — this is your configuration.
3. Read docs/investigation/audit-agent/02_STATE.md to see the current phase.
4. Read the latest checkpoint in docs/investigation/audit-agent/iterations/.
5. Perform the work for the current phase (bounded iteration).
6. Write ALL mandatory artifacts listed in 00_RULES.md.
7. Append a new checkpoint to docs/investigation/audit-agent/iterations/.
8. Repeat from step 3 until docs/investigation/audit-agent/10_METRICS.md declares INVESTIGATION_STATUS = PASS.

Important constraints:
- No invention: every behavior, flag, env var, or file path you document must be traceable to a test assertion or code reference.
- Evidence hierarchy: tests > contracts > code > existing docs.
- Smoke tests (tests/smoke/) are explicitly out of scope — do not analyze them.
- If the stall rule triggers (two consecutive iterations with no reduction in S0, S1, or open unknowns), stop and set INVESTIGATION_STATUS = BLOCKED and document blockers in 11_NEXT_ACTIONS.md.
- When INVESTIGATION_STATUS = PASS, stop and report a summary of findings.
```

**Step 2: Monitor for completion**

The agent terminates when it either:
- Sets `INVESTIGATION_STATUS = PASS` in `docs/investigation/audit-agent/10_METRICS.md` → proceed to Task 6
- Sets `INVESTIGATION_STATUS = BLOCKED` → read `docs/investigation/audit-agent/11_NEXT_ACTIONS.md` and resolve blockers before continuing

---

## Task 6: Review audit findings

This is a manual review step. Do not skip it.

**Step 1: Read the findings**

```bash
cat docs/investigation/audit-agent/08_FINDINGS.md
```

**Step 2: Check the metrics**

```bash
cat docs/investigation/audit-agent/10_METRICS.md
```

Expected: `INVESTIGATION_STATUS = PASS`, S0 = 0, S1 <= 3, Open Unknowns <= 5.

**Step 3: Skim the traceability map**

```bash
cat docs/investigation/audit-agent/07_TRACEABILITY.md
```

Verify that the major public behaviors (generate, show, install, uninstall, settings layers, backends, types, exceptions) all have test evidence citations. If any important behavior is missing, note it as an unknown before proceeding.

**Step 4: Commit the audit artifacts**

```bash
git add docs/investigation/audit-agent/
git commit -m "docs: complete audit-agent investigation (INVESTIGATION_STATUS=PASS)"
```

---

## Task 7: Archive old docs

**Step 1: Create the archive directory**

```bash
mkdir -p docs/archive
```

**Step 2: Move existing docs into archive**

```bash
mv docs/tutorials docs/archive/tutorials
mv docs/how-to docs/archive/how-to
mv docs/reference docs/archive/reference
mv docs/explanations docs/archive/explanations
mv docs/README.md docs/archive/README.md
mv docs/audit-2026-02-20.md docs/archive/audit-2026-02-20.md
```

Note: `docs/plans/` stays in place — do not archive it.

**Step 3: Verify docs/ is clean**

```bash
ls docs/
```

Expected:
```
archive/
investigation/
plans/
```

**Step 4: Commit the archive**

```bash
git add docs/archive/ docs/
git commit -m "docs: archive old documentation before synthesis"
```

---

## Task 8: Run the synthesis agent

This is a long-running autonomous step. Dispatch a `general-purpose` subagent with the following prompt.

**Step 1: Dispatch the synthesis agent**

Use the Task tool with `subagent_type=general-purpose` and this prompt:

```
You are running the synthesis-agent loop for the color-scheme-generator project.

Project root: /home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/color-scheme-generator
Synthesis state directory: docs/investigation/synthesis-agent/ (relative to project root)
Investigation artifacts directory: docs/investigation/audit-agent/ (relative to project root)

Your job:
1. Read docs/investigation/synthesis-agent/00_SYNTHESIS_RULES.md — follow it exactly.
2. Read docs/investigation/synthesis-agent/01_OUTPUT_TARGET.md — this is your configuration.
3. Read docs/investigation/synthesis-agent/02_SYNTHESIS_STATE.md for current status.
4. Read the latest checkpoint in docs/investigation/synthesis-agent/iterations/.
5. Read the active profile files under docs/investigation/synthesis-agent/profiles/diataxis/:
   - 00_PROFILE.md, 01_STRUCTURE.md, 02_MAPPING_RULES.md, 03_CONFORMANCE_CHECKS.md
   - Templates under templates/ for document format reference
6. Read the investigation artifacts you need:
   - docs/investigation/audit-agent/05_TEST_SPEC.md
   - docs/investigation/audit-agent/07_TRACEABILITY.md
   - docs/investigation/audit-agent/08_FINDINGS.md
   - docs/investigation/audit-agent/09_UNKNOWNS.md
   - docs/investigation/audit-agent/04_TOPIC_MAP.md
7. Build documentation under OUTPUT_DIR (docs/) following the Diátaxis structure:
   - docs/tutorials/
   - docs/how-to/
   - docs/reference/
   - docs/explanation/
8. After each iteration, update synthesis state files and append a checkpoint.
9. Repeat until SYNTHESIS_STATUS = PASS in docs/investigation/synthesis-agent/04_CONFORMANCE.md.

Constraints:
- VERIFICATION_POLICY = verified-only: do not document any behavior not backed by test evidence in the audit artifacts.
- PRIMARY_AUDIENCE = end-users: focus on CLI usage and configuration, not internal implementation.
- Every generated doc file must be grounded in BHV entries from 07_TRACEABILITY.md.
- Do not reproduce any S0 findings from 08_FINDINGS.md.
- Examples must use the actual verified CLI syntax.
```

**Step 2: Monitor for completion**

The agent terminates when it either:
- Sets `SYNTHESIS_STATUS = PASS` in `docs/investigation/synthesis-agent/04_CONFORMANCE.md` → proceed to Task 9
- Sets `SYNTHESIS_STATUS = BLOCKED` → read `docs/investigation/synthesis-agent/02_SYNTHESIS_STATE.md` for the additional investigation requests and address them

---

## Task 9: Verify and final commit

**Step 1: Check conformance**

```bash
cat docs/investigation/synthesis-agent/04_CONFORMANCE.md
```

Expected: `SYNTHESIS_STATUS = PASS`, all four conformance checks passing.

**Step 2: Verify the four Diátaxis dirs exist and are populated**

```bash
find docs/tutorials docs/how-to docs/reference docs/explanation -name "*.md" | sort
```

Expected: at least one `.md` file in each directory.

**Step 3: Spot-check a reference doc**

Pick any reference file and verify it contains:
- A section header matching a real CLI command or API element
- At least one example using the verified CLI syntax (e.g. `color-scheme generate`, `color-scheme-core show`)
- No mention of the false flags (`--seed`, `--algorithm`, `--clusters`, `--template-dir`, `--output-file`)
- No mention of the wrong auto-detect order (pywal > wallust)

**Step 4: Commit everything**

```bash
git add docs/
git commit -m "docs: add verified Diátaxis documentation from investigation+synthesis framework"
```

---

## Notes

- The audit agent (Task 5) and synthesis agent (Task 8) are the most context-intensive steps. Give them high `max_turns` if the tool supports it — the audit has 8 phases, each potentially requiring multiple iterations.
- If the audit agent gets blocked mid-run, read `docs/investigation/audit-agent/11_NEXT_ACTIONS.md` for the blocker list. Most likely blockers are behaviors only covered by smoke tests (which are excluded from scope) — these should be listed as unknowns and accepted, not resolved by lowering the evidence bar.
- The `docs/archive/` directory is committed and permanent. If synthesis output needs to be compared against the old docs, they are always accessible there.
