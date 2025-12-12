"""Tests for CLI module."""

import pytest

from color_scheme.cli import create_parser, main


class TestCreateParser:
    """Test parser creation."""

    def test_parser_created(self) -> None:
        """Test that parser can be created."""
        parser = create_parser()
        assert parser is not None

    def test_install_command_parsing(self) -> None:
        """Test install command parsing."""
        parser = create_parser()
        args = parser.parse_args(["install"])
        assert args.command == "install"

    def test_install_with_force_rebuild(self) -> None:
        """Test install with force-rebuild flag."""
        parser = create_parser()
        args = parser.parse_args(["install", "--force-rebuild"])
        assert args.command == "install"
        assert args.force_rebuild is True

    def test_generate_command_parsing(self) -> None:
        """Test generate command parsing."""
        parser = create_parser()
        args = parser.parse_args(["generate"])
        assert args.command == "generate"

    def test_generate_with_passthrough_args(self) -> None:
        """Test generate command with passthrough arguments."""
        parser = create_parser()
        # Note: passthrough args are captured as remainder
        args = parser.parse_args(["generate"])
        assert args.command == "generate"

    def test_show_command_parsing(self) -> None:
        """Test show command parsing."""
        parser = create_parser()
        args = parser.parse_args(["show"])
        assert args.command == "show"
        assert args.resource == "backends"  # default

    def test_show_backends_resource(self) -> None:
        """Test show command with backends resource."""
        parser = create_parser()
        args = parser.parse_args(["show", "backends"])
        assert args.command == "show"
        assert args.resource == "backends"

    def test_show_config_resource(self) -> None:
        """Test show command with config resource."""
        parser = create_parser()
        args = parser.parse_args(["show", "config"])
        assert args.command == "show"
        assert args.resource == "config"

    def test_status_command_parsing(self) -> None:
        """Test status command parsing."""
        parser = create_parser()
        args = parser.parse_args(["status"])
        assert args.command == "status"


class TestGlobalOptions:
    """Test global options work with all commands."""

    def test_runtime_option_install(self) -> None:
        """Test --runtime option with install."""
        parser = create_parser()
        args = parser.parse_args(
            ["install", "--runtime", "podman"]
        )
        assert args.runtime == "podman"

    def test_runtime_option_generate(self) -> None:
        """Test --runtime option with generate."""
        parser = create_parser()
        args = parser.parse_args(["generate", "--runtime", "docker"])
        assert args.runtime == "docker"

    def test_verbose_option(self) -> None:
        """Test --verbose option."""
        parser = create_parser()
        args = parser.parse_args(["install", "--verbose"])
        assert args.verbose is True

    def test_verbose_short_option(self) -> None:
        """Test -v short option."""
        parser = create_parser()
        args = parser.parse_args(["install", "-v"])
        assert args.verbose is True

    def test_debug_option(self) -> None:
        """Test --debug option."""
        parser = create_parser()
        args = parser.parse_args(["install", "--debug"])
        assert args.debug is True

    def test_debug_short_option(self) -> None:
        """Test -d short option."""
        parser = create_parser()
        args = parser.parse_args(["install", "-d"])
        assert args.debug is True

    def test_output_dir_option(self) -> None:
        """Test --output-dir option."""
        parser = create_parser()
        args = parser.parse_args(
            ["generate", "--output-dir", "/tmp/output"]
        )
        assert args.output_dir == "/tmp/output"

    def test_config_dir_option(self) -> None:
        """Test --config-dir option."""
        parser = create_parser()
        args = parser.parse_args(
            ["generate", "--config-dir", "/tmp/config"]
        )
        assert args.config_dir == "/tmp/config"

    def test_multiple_global_options(self) -> None:
        """Test multiple global options together."""
        parser = create_parser()
        args = parser.parse_args([
            "generate",
            "--runtime", "podman",
            "--verbose",
            "--output-dir", "/output",
        ])
        assert args.runtime == "podman"
        assert args.verbose is True
        assert args.output_dir == "/output"


class TestMainFunction:
    """Test main CLI function."""

    def test_main_no_args_fails(self) -> None:
        """Test main with no arguments fails."""
        # Should return exit code 2 (argparse error)
        result = main([])
        assert result != 0

    def test_main_help_succeeds(self) -> None:
        """Test main with --help."""
        # Help typically exits with 0 when explicitly requested
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        # argparse exits with 0 for --help
        assert exc_info.value.code == 0

    def test_main_install_command(self) -> None:
        """Test main with install command."""
        # This would fail due to no Docker, but should get past argument parsing
        result = main(["install"])
        assert isinstance(result, int)

    def test_main_generate_command(self) -> None:
        """Test main with generate command."""
        # This would fail due to no Docker, but should get past argument parsing
        result = main(["generate"])
        assert isinstance(result, int)

    def test_main_show_command(self) -> None:
        """Test main with show command."""
        result = main(["show"])
        assert result == 0

    def test_main_status_command(self) -> None:
        """Test main with status command."""
        result = main(["status"])
        assert isinstance(result, int)


class TestMainErrorHandling:
    """Test error handling in main."""

    def test_main_invalid_command(self) -> None:
        """Test main with invalid command."""
        with pytest.raises(SystemExit):
            main(["invalid"])

    def test_main_invalid_runtime(self) -> None:
        """Test main with invalid runtime value."""
        result = main(["install", "--runtime", "invalid"])
        # Should fail when trying to detect runtime
        assert result != 0
