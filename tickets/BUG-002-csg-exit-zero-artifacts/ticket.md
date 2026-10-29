---
id: BUG-002
title: "csg generate exits 0 without artifacts when CWD templates/ is not a csg catalog"
kind: bug
status: in-progress
lane: 2
severity: high
links:
  openspec: csg-generate-fail-closed
  bmad: none
worktree: .worktrees/BUG-002/
branch: ticket/BUG-002-csg-exit-zero-artifacts
repro: "Run csg generate from a directory containing an unrelated templates/ (the AGS wallpaper-selector app dir). The resolver selects that directory, finds no colors.*.j2, writes zero artifacts, and exits 0."
observed: "2026-10-29: the AGS selector's CWD is /home/inumaki/.local/share/dotfiles/apps/wallpaper-selector/v0.1.0, which contains templates/ags-app. csg generate with the runtime's 8 formats selected that directory, printed success:true/output_files:[], wrote 0 files, and exited 0. The runtime then failed with `csg did not write expected artifact: .../colors.yaml`; failures at 22:53:24Z, 22:55:27Z and 22:59:00Z. From /tmp the same command writes all 8 files; pinning COLORSCHEME_TEMPLATES_TEMPLATES_DIR to the spine catalog also writes all 8."
expected: "csg never exits 0 unless every requested colors.<format> artifact exists; a CWD templates/ directory without a csg catalog is not silently selected; container mode propagates inner failure; diagnostics name the missing formats/templates."
---

# BUG-002 — csg exits 0 without artifacts on a decoy CWD templates/

## Root cause

The template resolver accepts the first `templates/` directory found in CWD
(or up to three parents) without validating that it contains the requested
`colors.*.j2` catalog. The AGS selector app directory has a `templates/ags-app/`
tree, so a runtime `csg generate` spawned by the selector inherits that CWD,
mounts the wrong directory in container mode, renders nothing, and exits 0.

Evidence:

```bash
cd /home/inumaki/.local/share/dotfiles/apps/wallpaper-selector/v0.1.0
python -c "from color_scheme_generator.adapters.template_dir_resolver import TemplateDirResolver; \
  p=TemplateDirResolver().resolve(); print(p); print(sorted(x.name for x in p.glob('colors.*.j2')))"
# /home/inumaki/.../apps/wallpaper-selector/v0.1.0/templates
# []
```

The same resolver from `/tmp` returns the provisioned catalog with 12
templates. From the selector CWD the runtime’s exact 8-format invocation
returns `success: true`, `output_files: []`, 0 files, rc 0; from `/tmp` it
writes all 8 files. Pinning `COLORSCHEME_TEMPLATES_TEMPLATES_DIR` to the spine
catalog fixes the same selector-CWD invocation (8 files, rc 0).

The failure semantics are also broken:

- `LocalProcessor._render_formats` returns `([], "")` when the renderer is
  missing and collects per-format `ColorSchemeError`s without failing the run.
- `ContainerProcessor.process_generate` sets
  `success = container_result.return_code == 0`, ignoring the inner
  `success:false`/empty `output_files`.
- `cli/generate` calls `process_result(result)` without turning
  `result.success is False` into a non-zero exit.
- The JSON projector omits `stderr`/render errors.

## Proper fix

1. **Resolver:** content-validate a CWD-discovered candidate (require the
   requested `colors.*.j2` catalog, or fall through to XDG/packaged defaults).
   An explicitly supplied `--templates-dir`/env must fail loudly when invalid.
   Amend the `csg-template-catalog` spec if the “CWD templates/ wins” rule
   changes.
2. **Local processor:** if the renderer is missing or a requested format fails,
   return `success=False` with a clear error; verify every requested host
   artifact after rendering.
3. **Container processor:** validate the resolved catalog before mounting; set
   `success` from both the container rc and the inner `success`/artifact set;
   never report success for an empty or partial artifact set.
4. **CLI:** after `process_result`, exit non-zero when `result.success` is
   false, while still emitting the JSON/plain diagnostic.
5. **Diagnostics:** include the resolved templates directory, missing formats,
   inner stdout/stderr and `output_files` in the failure result.

## Tests

- Resolver: CWD `templates/` with only `ags-app/` → not selected (fallback), or
  explicit error; never silent success.
- Local CLI: renderer raises `TemplateNotFoundError` for one format → exit 1;
  diagnostic names the format/template.
- Container CLI: fake runtime rc 0 + inner `{"success": false,
  "output_files": []}` + empty host dir → `success=False`, stderr preserved,
  exit 1.
- End-to-end: run the installed csg from a temp CWD containing
  `templates/ags-app` with the runtime’s 8 formats → non-zero and no
  exit-0/no-artifact result.
- Add a decoy-`templates/` case to `tests/contract/test_invocation_contract.py`
  (`success_requires_artifacts: true`).

## Done-when

- [ ] From the selector app CWD, `csg generate` either falls back to the real
  catalog and writes all 8 artifacts, or exits non-zero with a precise
  diagnostic; it never exits 0 with missing output.
- [ ] A requested artifact missing on disk forces a non-zero CLI exit.
- [ ] Container mode propagates inner failure and preserves stderr.
- [ ] Targeted tests and `make gates` green; release `v0.2.2`; push the tag.
- [ ] Runtime adapter is separately hardened to pin the spine templates dir and
  capture diagnostics (`dotfiles-runtime` BUG-007).

## Cross-references

- `dotfiles-runtime` BUG-007 — palette missing-artifact diagnostics and
  templates pin.
- `ags-wallpaper-selector` BUG-001 — stale producer / selector CWD context.
- Implement on `origin/main` (includes v0.2.1); do not use the stale local
  checkout at `dd8e226`.
