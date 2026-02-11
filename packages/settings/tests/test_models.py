"""Tests for ResolvedValue, ResolvedConfig, Warning, and related models."""

from color_scheme_settings.models import (
    ConfigSource,
    ResolvedConfig,
    ResolvedValue,
    Warning,
    WarningLevel,
)


class TestConfigSource:
    """Test ConfigSource enum."""

    def test_cli_source(self):
        """Test CLI source value."""
        assert ConfigSource.CLI.value == "CLI argument"

    def test_env_source(self):
        """Test environment variable source value."""
        assert ConfigSource.ENV.value == "Environment variable"

    def test_user_config_source(self):
        """Test user config source value."""
        assert ConfigSource.USER_CONFIG.value == "User config"

    def test_project_config_source(self):
        """Test project config source value."""
        assert ConfigSource.PROJECT_CONFIG.value == "Project config"

    def test_package_default_source(self):
        """Test package default source value."""
        assert ConfigSource.PACKAGE_DEFAULT.value == "Package default"

    def test_all_sources_defined(self):
        """Test all sources are defined."""
        sources = [
            ConfigSource.CLI,
            ConfigSource.ENV,
            ConfigSource.USER_CONFIG,
            ConfigSource.PROJECT_CONFIG,
            ConfigSource.PACKAGE_DEFAULT,
        ]
        assert len(sources) == 5


class TestWarningLevel:
    """Test WarningLevel enum."""

    def test_info_level(self):
        """Test info warning level."""
        assert WarningLevel.INFO.value == "info"

    def test_warning_level(self):
        """Test warning level."""
        assert WarningLevel.WARNING.value == "warning"

    def test_error_level(self):
        """Test error warning level."""
        assert WarningLevel.ERROR.value == "error"


class TestResolvedValue:
    """Test ResolvedValue dataclass."""

    def test_basic_creation(self):
        """Test basic ResolvedValue creation."""
        resolved = ResolvedValue(
            value="test",
            source=ConfigSource.CLI,
            source_detail="--backend test",
        )
        assert resolved.value == "test"
        assert resolved.source == ConfigSource.CLI
        assert resolved.source_detail == "--backend test"
        assert resolved.overrides == []

    def test_with_overrides(self):
        """Test ResolvedValue with overrides."""
        resolved = ResolvedValue(
            value="cli_value",
            source=ConfigSource.CLI,
            source_detail="--backend",
            overrides=[(ConfigSource.ENV, "env_value")],
        )
        assert resolved.value == "cli_value"
        assert len(resolved.overrides) == 1
        assert resolved.overrides[0] == (ConfigSource.ENV, "env_value")

    def test_multiple_overrides(self):
        """Test ResolvedValue with multiple overrides."""
        resolved = ResolvedValue(
            value="final",
            source=ConfigSource.CLI,
            source_detail="--option final",
            overrides=[
                (ConfigSource.ENV, "env_value"),
                (ConfigSource.PACKAGE_DEFAULT, "default_value"),
            ],
        )
        assert len(resolved.overrides) == 2

    def test_complex_values(self):
        """Test ResolvedValue with complex data types."""
        resolved = ResolvedValue(
            value=["json", "yaml", "sh"],
            source=ConfigSource.CLI,
            source_detail="--format",
        )
        assert isinstance(resolved.value, list)
        assert resolved.value == ["json", "yaml", "sh"]

    def test_numeric_value(self):
        """Test ResolvedValue with numeric value."""
        resolved = ResolvedValue(
            value=1.5,
            source=ConfigSource.USER_CONFIG,
            source_detail="~/.config/settings.toml",
        )
        assert resolved.value == 1.5

    def test_dict_value(self):
        """Test ResolvedValue with dictionary value."""
        resolved = ResolvedValue(
            value={"algorithm": "kmeans", "n_clusters": 16},
            source=ConfigSource.PROJECT_CONFIG,
            source_detail="./settings.toml",
        )
        assert isinstance(resolved.value, dict)
        assert resolved.value["algorithm"] == "kmeans"


class TestWarning:
    """Test Warning dataclass."""

    def test_basic_warning(self):
        """Test basic warning creation."""
        warning = Warning(
            level=WarningLevel.WARNING,
            message="Test warning",
        )
        assert warning.level == WarningLevel.WARNING
        assert warning.message == "Test warning"
        assert warning.detail == ""
        assert warning.action == ""

    def test_full_warning(self):
        """Test warning with all fields."""
        warning = Warning(
            level=WarningLevel.ERROR,
            message="Critical issue",
            detail="Configuration file is malformed",
            action="Fix the TOML syntax",
        )
        assert warning.level == WarningLevel.ERROR
        assert warning.message == "Critical issue"
        assert warning.detail == "Configuration file is malformed"
        assert warning.action == "Fix the TOML syntax"

    def test_info_warning(self):
        """Test info-level warning."""
        warning = Warning(
            level=WarningLevel.INFO,
            message="Configuration loaded",
            detail="Using project settings",
        )
        assert warning.level == WarningLevel.INFO


class TestResolvedConfig:
    """Test ResolvedConfig class."""

    def test_empty_config_creation(self):
        """Test creating an empty resolved config."""
        config = ResolvedConfig()
        assert len(config) == 0
        assert config.items() == []

    def test_set_and_get_single_value(self):
        """Test setting and getting a single value."""
        config = ResolvedConfig()
        resolved = ResolvedValue(
            value="custom",
            source=ConfigSource.CLI,
            source_detail="--backend",
        )
        config.set("generation.default_backend", resolved)

        assert len(config) == 1
        retrieved = config.get("generation.default_backend")
        assert retrieved is not None
        assert retrieved.value == "custom"
        assert retrieved.source == ConfigSource.CLI

    def test_set_multiple_values(self):
        """Test setting multiple values."""
        config = ResolvedConfig()
        config.set(
            "generation.default_backend",
            ResolvedValue("pywal", ConfigSource.CLI, "--backend"),
        )
        config.set(
            "output.directory",
            ResolvedValue(
                "/tmp/output", ConfigSource.PACKAGE_DEFAULT, "Package default"
            ),
        )

        assert len(config) == 2

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        config = ResolvedConfig()
        assert config.get("nonexistent.key") is None

    def test_items_iteration(self):
        """Test iterating over config items."""
        config = ResolvedConfig()
        config.set(
            "key1",
            ResolvedValue("value1", ConfigSource.CLI, "detail1"),
        )
        config.set(
            "key2",
            ResolvedValue("value2", ConfigSource.ENV, "detail2"),
        )

        items = config.items()
        assert len(items) == 2
        keys = [k for k, _ in items]
        assert "key1" in keys
        assert "key2" in keys

    def test_to_dict_simple(self):
        """Test converting to dict with simple keys."""
        config = ResolvedConfig()
        config.set("backend", ResolvedValue("pywal", ConfigSource.CLI, "--backend"))
        config.set(
            "level", ResolvedValue("INFO", ConfigSource.ENV, "COLORSCHEME_LEVEL")
        )

        result = config.to_dict()
        assert result["backend"] == "pywal"
        assert result["level"] == "INFO"

    def test_to_dict_nested(self):
        """Test converting to dict with nested keys."""
        config = ResolvedConfig()
        config.set(
            "generation.default_backend",
            ResolvedValue("custom", ConfigSource.CLI, "--backend"),
        )
        config.set(
            "output.directory",
            ResolvedValue("/tmp/out", ConfigSource.PROJECT_CONFIG, "./settings.toml"),
        )

        result = config.to_dict()
        assert result["generation"]["default_backend"] == "custom"
        assert result["output"]["directory"] == "/tmp/out"

    def test_to_dict_deeply_nested(self):
        """Test converting to dict with deeply nested keys."""
        config = ResolvedConfig()
        config.set(
            "backend.pywal.algorithm",
            ResolvedValue("wal", ConfigSource.PACKAGE_DEFAULT, "Package default"),
        )
        config.set(
            "backend.pywal.recolor_wallpaper",
            ResolvedValue(True, ConfigSource.USER_CONFIG, "~/.config/settings.toml"),
        )

        result = config.to_dict()
        assert result["backend"]["pywal"]["algorithm"] == "wal"
        assert result["backend"]["pywal"]["recolor_wallpaper"] is True

    def test_overwrite_value(self):
        """Test overwriting an existing value."""
        config = ResolvedConfig()
        config.set(
            "key", ResolvedValue("value1", ConfigSource.PACKAGE_DEFAULT, "default")
        )
        assert config.get("key").value == "value1"

        config.set("key", ResolvedValue("value2", ConfigSource.CLI, "--key"))
        assert config.get("key").value == "value2"

    def test_repr(self):
        """Test string representation."""
        config = ResolvedConfig()
        assert "ResolvedConfig" in repr(config)
        assert "0 values" in repr(config)

        config.set("key", ResolvedValue("value", ConfigSource.CLI, "--key"))
        assert "1 values" in repr(config)

    def test_mixed_value_types_in_dict(self):
        """Test to_dict with mixed value types."""
        config = ResolvedConfig()
        config.set("string", ResolvedValue("text", ConfigSource.CLI, "--string"))
        config.set("number", ResolvedValue(42, ConfigSource.ENV, "NUMBER"))
        config.set(
            "list", ResolvedValue([1, 2, 3], ConfigSource.PACKAGE_DEFAULT, "default")
        )
        config.set(
            "nested.dict",
            ResolvedValue({"key": "val"}, ConfigSource.USER_CONFIG, "user"),
        )

        result = config.to_dict()
        assert result["string"] == "text"
        assert result["number"] == 42
        assert result["list"] == [1, 2, 3]
        assert result["nested"]["dict"] == {"key": "val"}

    def test_source_attribution_preserved(self):
        """Test that source attribution is preserved through operations."""
        config = ResolvedConfig()
        original = ResolvedValue(
            value="test",
            source=ConfigSource.CLI,
            source_detail="--option test",
            overrides=[(ConfigSource.ENV, "env_value")],
        )
        config.set("option", original)

        retrieved = config.get("option")
        assert retrieved.source == ConfigSource.CLI
        assert retrieved.source_detail == "--option test"
        assert retrieved.overrides == [(ConfigSource.ENV, "env_value")]
