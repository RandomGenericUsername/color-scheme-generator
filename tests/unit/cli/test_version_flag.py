from __future__ import annotations

from importlib.metadata import version as dist_version

from cli_invocation_contract import CONTRACT_VERSION
from typer.testing import CliRunner

from color_scheme_generator.cli.main import app

# The contract token is derived from the installed package, never duplicated in
# the CLI or the expectation below. This literal is a tripwire on the pin: if
# `[tool.uv.sources]` or `uv.lock` regresses to an older `contracts` tag, this
# assertion fails here instead of shipping a stale token.
EXPECTED_CONTRACT_VERSION = "0.2.0"


def test_version_flag_reports_package_and_contract_version() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0, result.output
    assert CONTRACT_VERSION == EXPECTED_CONTRACT_VERSION
    assert result.stdout.strip() == (
        f"{dist_version('color-scheme-generator')} contract {CONTRACT_VERSION}"
    )
