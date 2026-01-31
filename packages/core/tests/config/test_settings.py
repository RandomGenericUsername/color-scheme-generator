"""Tests for settings integration with color_scheme_settings package."""

from pathlib import Path

import pytest
from color_scheme_settings import SchemaRegistry, configure, get_config, reset

from color_scheme.config.config import AppConfig


@pytest.fixture
def clean_settings():
    """Reset settings system before and after each test."""
    from pydantic import BaseModel, ConfigDict, Field

    class CoreTestConfig(BaseModel):
        """Test config with just core namespace."""
        model_config = ConfigDict(frozen=True)
        core: AppConfig = Field(default_factory=AppConfig)

    reset()
    # Re-register core schema after reset (reset() clears the registry)
    if "core" not in SchemaRegistry.all_namespaces():
        SchemaRegistry.register(
            namespace="core",
            model=AppConfig,
            defaults_file=Path(__file__).parent.parent.parent / "src" / "color_scheme" / "config" / "settings.toml",
        )
    # Re-configure with core-only config
    configure(CoreTestConfig)
    yield
    # Clean up and restore default configuration for other tests
    reset()
    if "core" not in SchemaRegistry.all_namespaces():
        SchemaRegistry.register(
            namespace="core",
            model=AppConfig,
            defaults_file=Path(__file__).parent.parent.parent / "src" / "color_scheme" / "config" / "settings.toml",
        )
    configure(CoreTestConfig)


@pytest.mark.usefixtures("clean_settings")
class TestCoreSchemaRegistration:
    """Tests for core schema registration."""

    def test_core_schema_registered(self):
        """Test that core schema is registered on import."""
        # Import triggers registration
        from color_scheme.config import AppConfig  # noqa: F401

        namespaces = SchemaRegistry.all_namespaces()
        assert "core" in namespaces

    def test_core_schema_has_correct_model(self):
        """Test that core schema uses AppConfig model."""
        from color_scheme.config import AppConfig  # noqa: F401

        entry = SchemaRegistry.get("core")
        assert entry.model is AppConfig


@pytest.mark.usefixtures("clean_settings")
class TestSettingsLoading:
    """Tests for loading settings through the new system."""

    def test_load_default_settings(self, tmp_path: Path):
        """Test loading with package defaults only."""
        # Create a minimal UnifiedConfig for testing
        from pydantic import BaseModel, ConfigDict, Field

        class TestConfig(BaseModel):
            model_config = ConfigDict(frozen=True)
            core: AppConfig = Field(default_factory=AppConfig)

        # Register and configure
        configure(TestConfig)
        config = get_config()

        assert config.core.logging.level == "INFO"
        assert config.core.generation.default_backend == "pywal"

    def test_environment_variable_resolution(self, tmp_path: Path, monkeypatch):
        """Test that environment variables are resolved."""
        from pydantic import BaseModel, ConfigDict, Field

        class TestConfig(BaseModel):
            model_config = ConfigDict(frozen=True)
            core: AppConfig = Field(default_factory=AppConfig)

        # Create project root with env vars
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        settings_file = project_dir / "settings.toml"
        settings_file.write_text("""\
[core.output]
directory = "$HOME/.config/color-scheme/output"
""")

        monkeypatch.setenv("HOME", "/home/testuser")

        configure(TestConfig, project_root=project_dir)
        config = get_config()

        assert str(config.core.output.directory) == "/home/testuser/.config/color-scheme/output"

    def test_case_insensitive_keys(self, tmp_path: Path):
        """Test that TOML keys are converted to lowercase."""
        from pydantic import BaseModel, ConfigDict, Field

        class TestConfig(BaseModel):
            model_config = ConfigDict(frozen=True)
            core: AppConfig = Field(default_factory=AppConfig)

        # Create project root with uppercase keys
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        settings_file = project_dir / "settings.toml"
        settings_file.write_text("""\
[CORE.LOGGING]
LEVEL = "DEBUG"
""")

        configure(TestConfig, project_root=project_dir)
        config = get_config()

        assert config.core.logging.level == "DEBUG"

    def test_nested_backend_settings(self, tmp_path: Path):
        """Test loading nested backend settings."""
        from pydantic import BaseModel, ConfigDict, Field

        class TestConfig(BaseModel):
            model_config = ConfigDict(frozen=True)
            core: AppConfig = Field(default_factory=AppConfig)

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        settings_file = project_dir / "settings.toml"
        settings_file.write_text("""\
[core.backends.pywal]
backend_algorithm = "colorz"

[core.backends.custom]
algorithm = "dominant"
n_clusters = 64
""")

        configure(TestConfig, project_root=project_dir)
        config = get_config()

        assert config.core.backends.pywal.backend_algorithm == "colorz"
        assert config.core.backends.custom.algorithm == "dominant"
        assert config.core.backends.custom.n_clusters == 64

    def test_path_conversion(self, tmp_path: Path):
        """Test that string paths are converted to Path objects."""
        from pydantic import BaseModel, ConfigDict, Field

        class TestConfig(BaseModel):
            model_config = ConfigDict(frozen=True)
            core: AppConfig = Field(default_factory=AppConfig)

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        settings_file = project_dir / "settings.toml"
        settings_file.write_text("""\
[core.output]
directory = "/tmp/test/output"

[core.templates]
directory = "/tmp/test/templates"
""")

        configure(TestConfig, project_root=project_dir)
        config = get_config()

        assert isinstance(config.core.output.directory, Path)
        assert isinstance(config.core.templates.directory, Path)
        assert config.core.output.directory == Path("/tmp/test/output")
        assert config.core.templates.directory == Path("/tmp/test/templates")

    def test_validation_error_on_invalid_data(self, tmp_path: Path):
        """Test that invalid config raises ValidationError."""
        from color_scheme_settings.errors import SettingsValidationError
        from pydantic import BaseModel, ConfigDict, Field

        class TestConfig(BaseModel):
            model_config = ConfigDict(frozen=True)
            core: AppConfig = Field(default_factory=AppConfig)

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        settings_file = project_dir / "settings.toml"
        # Invalid: saturation_adjustment outside range
        settings_file.write_text("""\
[core.generation]
saturation_adjustment = 5.0
""")

        configure(TestConfig, project_root=project_dir)

        with pytest.raises(SettingsValidationError):
            get_config()


@pytest.mark.usefixtures("clean_settings")
class TestLayerMerging:
    """Tests for layer merging behavior."""

    def test_project_overrides_package_defaults(self, tmp_path: Path):
        """Test that project settings override package defaults."""
        from pydantic import BaseModel, ConfigDict, Field

        class TestConfig(BaseModel):
            model_config = ConfigDict(frozen=True)
            core: AppConfig = Field(default_factory=AppConfig)

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        settings_file = project_dir / "settings.toml"
        settings_file.write_text("""\
[core.generation]
default_backend = "wallust"
saturation_adjustment = 1.5
""")

        configure(TestConfig, project_root=project_dir)
        config = get_config()

        # Overridden values
        assert config.core.generation.default_backend == "wallust"
        assert config.core.generation.saturation_adjustment == 1.5

        # Default values preserved
        assert config.core.logging.level == "INFO"
