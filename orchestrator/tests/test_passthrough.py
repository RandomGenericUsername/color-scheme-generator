"""Tests for argument passthrough utilities."""

import pytest

from color_scheme.utils.passthrough import (
    build_passthrough_command,
    extract_backend_from_args,
    filter_orchestrator_args,
    parse_core_arguments,
    should_use_default_backends,
)


class TestParseCoreArguments:
    """Test core argument parsing."""

    def test_parse_install_command(self) -> None:
        """Test parsing install command."""
        cmd, args = parse_core_arguments(["install"])
        assert cmd == "install"
        assert args == []

    def test_parse_generate_command(self) -> None:
        """Test parsing generate command."""
        cmd, args = parse_core_arguments(["generate", "-i", "image.jpg"])
        assert cmd == "generate"
        assert args == ["-i", "image.jpg"]

    def test_parse_invalid_command(self) -> None:
        """Test parsing invalid command."""
        with pytest.raises(ValueError):
            parse_core_arguments(["invalid"])

    def test_parse_no_command(self) -> None:
        """Test parsing with no command."""
        with pytest.raises(ValueError):
            parse_core_arguments([])


class TestBuildPassthroughCommand:
    """Test passthrough command building.

    Note: Container images use ENTRYPOINT, so we only pass subcommand + args.
    """

    def test_build_simple_command(self) -> None:
        """Test building simple command."""
        cmd = build_passthrough_command("install", [])
        assert cmd == ["install"]

    def test_build_command_with_args(self) -> None:
        """Test building command with arguments."""
        cmd = build_passthrough_command(
            "generate",
            ["image.jpg", "--backend", "pywal"],
        )
        assert cmd == [
            "generate",
            "image.jpg",
            "--backend",
            "pywal",
        ]


class TestDefaultBackendDetection:
    """Test default backend detection."""

    def test_use_defaults_no_backend(self) -> None:
        """Test using defaults when no backend specified."""
        args = ["image.jpg", "--saturation", "0.5"]
        assert should_use_default_backends(args) is True

    def test_use_defaults_with_backend_flag(self) -> None:
        """Test not using defaults when --backend specified."""
        args = ["--backend", "pywal", "-i", "image.jpg"]
        assert should_use_default_backends(args) is False

    def test_use_defaults_with_backend_equals(self) -> None:
        """Test not using defaults with --backend=value."""
        args = ["--backend=pywal", "-i", "image.jpg"]
        assert should_use_default_backends(args) is False

    def test_use_defaults_with_custom(self) -> None:
        """Test not using defaults when custom backend specified."""
        args = ["--custom", "backend.py"]
        assert should_use_default_backends(args) is False


class TestExtractBackendFromArgs:
    """Test backend extraction from arguments."""

    def test_extract_backend_flag_value(self) -> None:
        """Test extracting backend with --backend value."""
        args = ["--backend", "wallust", "-i", "image.jpg"]
        backend = extract_backend_from_args(args)
        assert backend == "wallust"

    def test_extract_backend_short_flag(self) -> None:
        """Test extracting backend with -b value."""
        args = ["-b", "pywal", "-i", "image.jpg"]
        backend = extract_backend_from_args(args)
        assert backend == "pywal"

    def test_extract_backend_equals(self) -> None:
        """Test extracting backend with --backend=value."""
        args = ["--backend=custom", "-i", "image.jpg"]
        backend = extract_backend_from_args(args)
        assert backend == "custom"

    def test_extract_no_backend(self) -> None:
        """Test when no backend is specified."""
        args = ["-i", "image.jpg", "--saturation", "0.5"]
        backend = extract_backend_from_args(args)
        assert backend is None


class TestFilterOrchestratorArgs:
    """Test filtering orchestrator-specific arguments."""

    def test_filter_runtime_arg(self) -> None:
        """Test filtering --runtime argument."""
        args = ["--runtime", "podman", "-i", "image.jpg"]
        orch_args, core_args = filter_orchestrator_args(args)
        assert orch_args["runtime"] == "podman"
        assert core_args == ["-i", "image.jpg"]

    def test_filter_output_dir_arg(self) -> None:
        """Test filtering --output-dir argument."""
        args = ["--output-dir", "/tmp/output", "-i", "image.jpg"]
        orch_args, core_args = filter_orchestrator_args(args)
        assert orch_args["output_dir"] == "/tmp/output"
        assert core_args == ["-i", "image.jpg"]

    def test_filter_verbose_flag(self) -> None:
        """Test filtering --verbose flag."""
        args = ["--verbose", "-i", "image.jpg"]
        orch_args, core_args = filter_orchestrator_args(args)
        assert orch_args["verbose"] is True
        assert core_args == ["-i", "image.jpg"]

    def test_filter_multiple_orch_args(self) -> None:
        """Test filtering multiple orchestrator arguments."""
        args = [
            "--runtime", "docker",
            "--verbose",
            "-i", "image.jpg",
            "--output-dir", "/output",
            "--saturation", "0.8",
        ]
        orch_args, core_args = filter_orchestrator_args(args)
        assert orch_args["runtime"] == "docker"
        assert orch_args["verbose"] is True
        assert orch_args["output_dir"] == "/output"
        assert core_args == ["-i", "image.jpg", "--saturation", "0.8"]

    def test_filter_with_equals_syntax(self) -> None:
        """Test filtering with --key=value syntax."""
        args = ["--runtime=podman", "--output-dir=/tmp", "-i", "image.jpg"]
        orch_args, core_args = filter_orchestrator_args(args)
        assert orch_args["runtime"] == "podman"
        assert orch_args["output_dir"] == "/tmp"
        assert core_args == ["-i", "image.jpg"]
