# Synthesis Agent Rules (Fixed Core + Pluggable Profiles)

Synthesis consumes investigation artifacts from `../audit-agent/` and produces documentation deliverables in `../documentation/`.

The synthesis core is **generic**. Output structure, mapping, and conformance are defined by the selected **profile**.

## Non-negotiable principles
1. Do not modify `../audit-agent/*` (only request more investigation via `02_SYNTHESIS_STATE.md`).
2. No invention: documentation must be grounded in evidence from investigation artifacts.
3. Profile-driven execution: follow the profile in `01_OUTPUT_TARGET.md`.

## Mandatory read order (every synthesis iteration)
1. `00_SYNTHESIS_RULES.md`
2. `01_OUTPUT_TARGET.md`
3. `02_SYNTHESIS_STATE.md`
4. Latest `iterations/####_SYNTH_CHECKPOINT.md` (or 0000)
5. Profile files (from OUTPUT_PROFILE):
   - `00_PROFILE.md`
   - `01_STRUCTURE.md`
   - `02_MAPPING_RULES.md`
   - `03_CONFORMANCE_CHECKS.md`
6. Investigation artifacts (as needed):
   - `../audit-agent/05_TEST_SPEC.md`
   - `../audit-agent/07_TRACEABILITY.md`
   - `../audit-agent/08_FINDINGS.md`
   - `../audit-agent/09_UNKNOWNS.md`
   - `../audit-agent/04_TOPIC_MAP.md`

## Mandatory write set
- `02_SYNTHESIS_STATE.md`
- `03_DOC_PLAN.md`
- `04_CONFORMANCE.md`
- `05_CHANGELOG.md`
- Append: `iterations/####_SYNTH_CHECKPOINT.md`
- Write deliverables under `OUTPUT_DIR`

## Verification policy
Set in `01_OUTPUT_TARGET.md`:
- `verified-only` (default) or `allow-unverified-labeled`
