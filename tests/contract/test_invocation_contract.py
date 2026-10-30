"""Prove this repo's own half of the `csg` invocation contract (AD-4) in CI.

The contract (`cli_invocation_contract.invocation-contract.json`) owns the argv,
the env keys and the artifact list. This test owns **execution only**: it runs
the installed `csg` console script with the record's argv, a scrubbed
environment and a temp output directory, then delegates the assertion to
``assert_cli_writes_artifacts`` from the pinned conformance kit.

Two documented settings overrides are injected on top of the record's own env
values (both are `COLORSCHEME__SECTION__KEY` env overrides, precedence rule 2 in
the README):

- ``COLORSCHEME__GENERATION__BACKEND=custom`` — the record's argv deliberately
  carries no ``--backend``. ``custom`` is the only backend that is pure Python
  (``pywal`` needs the ``wal`` binary, ``wallust`` needs ``wallust``), so it is
  the only one that runs on a bare CI runner. The dev dependency group carries
  ``color-scheme-generator[custom]`` so ``make sync`` installs it everywhere.
- ``COLORSCHEME__RUNTIME__MODE=local`` — pins extraction in-process, so a stray
  host ``settings.toml`` (discovery rule 4) cannot switch the run to container
  mode and demand an engine/network.

``COLORSCHEME__OUTPUT__APPLY_TO_TERMINAL`` is deliberately *not* injected: it is
not an override key, and the CLI only applies sequences when stdout is a real
TTY, which a captured subprocess is not.

The test never skips: a missing console script or missing backend dependency is
a failure that names the fix, not a green run that proved nothing.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from cli_invocation_contract import get
from cli_invocation_contract.testkit import assert_cli_writes_artifacts

_WALLPAPER = "wallpaper.png"


def _csg_executable() -> Path:
    """Locate the console script of *this* interpreter's env first, then PATH.

    The venv sibling wins over PATH on purpose: a host-wide ``csg`` install may
    exist (older version, no ``custom`` extra) and must not be picked up by a
    test that claims to prove *this* checkout's CLI.
    """
    candidates = (str(Path(sys.executable).with_name("csg")), shutil.which("csg"))
    for candidate in candidates:
        if candidate is not None and Path(candidate).is_file():
            return Path(candidate)
    pytest.fail(
        "the `csg` console script is not on PATH and not next to "
        f"{sys.executable}; run `make sync` first"
    )


def _write_wallpaper(path: Path) -> None:
    """Write a deterministic 16x16 RGB PNG (no checked-in binary fixture)."""
    from PIL import Image

    image = Image.new("RGB", (16, 16))
    pixels = image.load()
    assert pixels is not None
    for x in range(16):
        for y in range(16):
            pixels[x, y] = (x * 16, y * 16, (x * y) % 256)
    image.save(path, format="PNG")


def _contract_argv(record: dict[str, Any], wallpaper: Path) -> list[str]:
    """Build the record's argv with the wallpaper placeholder substituted."""
    substitutions = {"{wallpaper}": str(wallpaper)}
    argv = [str(_csg_executable())]
    for token in record["argv"]:
        argv.append(substitutions.get(token, token))
    unresolved = [token for token in argv[1:] if token.startswith("{") and token.endswith("}")]
    assert not unresolved, (
        f"the csg record gained placeholder(s) this test does not supply: {unresolved}"
    )
    return argv


def _scrubbed_env(root: Path, output_dir: Path, record: dict[str, Any]) -> dict[str, str]:
    """A minimal env: no host HOME/XDG/spine config leaks into the child."""
    for name in ("home", "config", "cache", "data", "state", "tmp"):
        (root / name).mkdir()
    injected = record["env"]["injected"]
    return {
        "PATH": os.pathsep.join([str(Path(sys.executable).parent), "/usr/bin", "/bin"]),
        "HOME": str(root / "home"),
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_CACHE_HOME": str(root / "cache"),
        "XDG_DATA_HOME": str(root / "data"),
        "XDG_STATE_HOME": str(root / "state"),
        "TMPDIR": str(root / "tmp"),
        "NO_COLOR": "1",
        "PYTHONNOUSERSITE": "1",
        # The record's own injected env values.
        "COLORSCHEME__OUTPUT__DIRECTORY": str(output_dir),
        "COLORSCHEME__OUTPUT__OVERWRITE": injected["COLORSCHEME__OUTPUT__OVERWRITE"],
        # Documented settings overrides: binary-free backend, in-process runtime.
        "COLORSCHEME__GENERATION__BACKEND": "custom",
        "COLORSCHEME__RUNTIME__MODE": "local",
    }


def _runner(
    argv: list[str],
    env: dict[str, str],
    cwd: Path,
    timeout: float,
) -> Any:
    """Return the zero-arg callable the kit runs; fail loudly with stderr on error."""

    def run() -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if completed.returncode != 0:
            pytest.fail(
                f"csg exited {completed.returncode}\n"
                f"argv: {argv}\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )
        return completed

    return run


def test_csg_writes_every_artifact_the_contract_requires(tmp_path: Path) -> None:
    record = get("csg")

    root = tmp_path / "contract"
    output_dir = root / "output"
    output_dir.mkdir(parents=True)
    wallpaper = root / _WALLPAPER
    _write_wallpaper(wallpaper)

    env = _scrubbed_env(root, output_dir, record)
    argv = _contract_argv(record, wallpaper)

    artifacts = assert_cli_writes_artifacts(
        record,
        "csg",
        _runner(argv, env, output_dir, record["timeout"]),
        output_dir,
    )

    expected = len(record["artifacts"]["filenames"])
    assert len(artifacts) == expected == record["artifacts"]["min_count"]
    for path in artifacts:
        assert path.stat().st_size > 0, f"{path.name} is an empty artifact"
    yaml_artifact = next(path for path in artifacts if path.suffix == ".yaml")
    assert 'backend: "custom"' in yaml_artifact.read_text(encoding="utf-8")


def test_decoy_cwd_templates_still_writes_every_artifact(tmp_path: Path) -> None:
    """BUG-002: a CWD ``templates/`` without a csg catalog is not selected.

    The AGS selector app's CWD contains ``templates/ags-app``. The contract
    record already declares ``success_requires_artifacts: true``; this test
    proves the decoy cannot turn into exit 0 with zero artifacts.
    """
    record = get("csg")
    assert record["exit_codes"]["success_requires_artifacts"] is True

    root = tmp_path / "selector-app"
    output_dir = root / "output"
    output_dir.mkdir(parents=True)
    decoy = root / "templates" / "ags-app"
    decoy.mkdir(parents=True)
    (decoy / "index.html").write_text("<html>selector</html>", encoding="utf-8")

    wallpaper = root / _WALLPAPER
    _write_wallpaper(wallpaper)
    env = _scrubbed_env(root, output_dir, record)
    argv = _contract_argv(record, wallpaper)

    completed = subprocess.run(
        argv,
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=record["timeout"],
        check=False,
    )

    assert completed.returncode == 0, (
        "decoy CWD templates/ forced a failure instead of falling back\n"
        f"argv: {argv}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )
    expected = set(record["artifacts"]["filenames"])
    written = {
        path.name
        for path in output_dir.iterdir()
        if path.is_file()
    }
    assert expected <= written, (
        f"exit 0 without every artifact; missing {sorted(expected - written)}\n"
        f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )
    for name in expected:
        assert (output_dir / name).stat().st_size > 0, f"{name} is empty"
