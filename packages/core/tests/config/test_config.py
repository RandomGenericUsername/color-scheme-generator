"""Tests for Pydantic configuration models."""

import logging
from pathlib import Path

import pytest
from pydantic import ValidationError

from color_scheme.config.config import (
    AppConfig,
    BackendSettings,
    ContainerSettings,
    CustomBackendSettings,
    GenerationSettings,
    LoggingSettings,
    OutputSettings,
    PywalBackendSettings,
    TemplateSettings,
    WallustBackendSettings,
)
from color_scheme.config.defaults import (
    custom_algorithm,
    custom_n_clusters,
    default_backend,
    default_formats,
    output_directory,
    pywal_backend_algorithm,
    saturation_adjustment,
    template_directory,
    wallust_backend_type,
)


class TestContainerSettings:
    """Tests for ContainerSettings model."""

    def test_default_engine(self):
        """Test default container engine is docker."""
        settings = ContainerSettings()
        assert settings.engine == "docker"

    def test_default_image_registry(self):
        """Test default image registry is None."""
        settings = ContainerSettings()
        assert settings.image_registry is None

    @pytest.mark.parametrize("engine", ["docker", "podman", "DOCKER", "PODMAN"])
    def test_valid_engines(self, engine: str):
        """Test valid container engines are accepted."""
        settings = ContainerSettings(engine=engine)
        assert settings.engine == engine.lower()

    def test_invalid_engine(self):
        """Test invalid container engine raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ContainerSettings(engine="kubernetes")

        error = exc_info.value.errors()[0]
        assert "Invalid container engine" in str(error["ctx"]["error"])

    def test_engine_case_insensitive(self):
        """Test engine validation is case-insensitive."""
        settings1 = ContainerSettings(engine="Docker")
        settings2 = ContainerSettings(engine="DOCKER")
        settings3 = ContainerSettings(engine="docker")

        assert settings1.engine == "docker"
        assert settings2.engine == "docker"
        assert settings3.engine == "docker"

    def test_custom_image_registry(self):
        """Test custom image registry can be set."""
        settings = ContainerSettings(image_registry="ghcr.io/myorg")
        assert settings.image_registry == "ghcr.io/myorg"

    def test_image_registry_with_engine(self):
        """Test image registry works with custom engine."""
        settings = ContainerSettings(
            engine="podman", image_registry="docker.io/username"
        )
        assert settings.engine == "podman"
        assert settings.image_registry == "docker.io/username"


class TestLoggingSettings:
    """Tests for LoggingSettings model."""

    def test_default_values(self):
        """Test default logging settings."""
        settings = LoggingSettings()
        assert settings.level == "INFO"
        assert settings.show_time is True
        assert settings.show_path is False

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_valid_log_levels(self, level: str):
        """Test valid log levels are accepted."""
        settings = LoggingSettings(level=level)
        assert settings.level == level

    def test_case_insensitive_level(self):
        """Test log level validation is case-insensitive."""
        settings1 = LoggingSettings(level="debug")
        settings2 = LoggingSettings(level="Debug")
        settings3 = LoggingSettings(level="DEBUG")

        assert settings1.level == "DEBUG"
        assert settings2.level == "DEBUG"
        assert settings3.level == "DEBUG"

    def test_invalid_log_level(self):
        """Test invalid log level raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingSettings(level="INVALID")

        error = exc_info.value.errors()[0]
        assert "Invalid logging level" in str(error["ctx"]["error"])

    def test_get_level_int(self):
        """Test get_level_int returns correct integer values."""
        assert LoggingSettings(level="DEBUG").get_level_int() == logging.DEBUG
        assert LoggingSettings(level="INFO").get_level_int() == logging.INFO
        assert LoggingSettings(level="WARNING").get_level_int() == logging.WARNING
        assert LoggingSettings(level="ERROR").get_level_int() == logging.ERROR
        assert LoggingSettings(level="CRITICAL").get_level_int() == logging.CRITICAL

    def test_show_time_boolean(self):
        """Test show_time accepts boolean values."""
        settings_true = LoggingSettings(show_time=True)
        settings_false = LoggingSettings(show_time=False)

        assert settings_true.show_time is True
        assert settings_false.show_time is False

    def test_show_path_boolean(self):
        """Test show_path accepts boolean values."""
        settings_true = LoggingSettings(show_path=True)
        settings_false = LoggingSettings(show_path=False)

        assert settings_true.show_path is True
        assert settings_false.show_path is False


class TestOutputSettings:
    """Tests for OutputSettings model."""

    def test_default_values(self):
        """Test default output settings."""
        settings = OutputSettings()
        assert settings.directory == output_directory
        assert settings.formats == default_formats

    def test_custom_directory(self):
        """Test custom output directory."""
        custom_dir = Path("/custom/output")
        settings = OutputSettings(directory=custom_dir)
        assert settings.directory == custom_dir

    def test_custom_formats(self):
        """Test custom output formats."""
        custom_formats = ["json", "yaml"]
        settings = OutputSettings(formats=custom_formats)
        assert settings.formats == custom_formats

    def test_formats_immutability(self):
        """Test that modifying formats doesn't affect defaults."""
        settings = OutputSettings()
        settings.formats.append("new_format")

        # Create a new instance - should have original defaults
        new_settings = OutputSettings()
        assert "new_format" not in new_settings.formats

    def test_directory_path_type(self):
        """Test directory is converted to Path."""
        settings = OutputSettings(directory="/tmp/output")
        assert isinstance(settings.directory, Path)
        assert settings.directory == Path("/tmp/output")


class TestGenerationSettings:
    """Tests for GenerationSettings model."""

    def test_default_values(self):
        """Test default generation settings."""
        settings = GenerationSettings()
        assert settings.default_backend == default_backend
        assert settings.saturation_adjustment == saturation_adjustment

    @pytest.mark.parametrize("backend", ["pywal", "wallust", "custom"])
    def test_valid_backends(self, backend: str):
        """Test valid backends are accepted."""
        settings = GenerationSettings(default_backend=backend)
        assert settings.default_backend == backend

    def test_invalid_backend(self):
        """Test invalid backend raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            GenerationSettings(default_backend="invalid")

        error = exc_info.value.errors()[0]
        assert "Invalid backend" in str(error["ctx"]["error"])

    @pytest.mark.parametrize("saturation", [0.0, 0.5, 1.0, 1.5, 2.0])
    def test_valid_saturation_range(self, saturation: float):
        """Test valid saturation values (0.0-2.0)."""
        settings = GenerationSettings(saturation_adjustment=saturation)
        assert settings.saturation_adjustment == saturation

    def test_saturation_below_minimum(self):
        """Test saturation below 0.0 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            GenerationSettings(saturation_adjustment=-0.1)

        error = exc_info.value.errors()[0]
        assert error["type"] == "greater_than_equal"

    def test_saturation_above_maximum(self):
        """Test saturation above 2.0 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            GenerationSettings(saturation_adjustment=2.1)

        error = exc_info.value.errors()[0]
        assert error["type"] == "less_than_equal"


class TestPywalBackendSettings:
    """Tests for PywalBackendSettings model."""

    def test_default_values(self):
        """Test default pywal backend settings."""
        settings = PywalBackendSettings()
        assert settings.backend_algorithm == pywal_backend_algorithm

    @pytest.mark.parametrize(
        "algorithm", ["wal", "colorz", "colorthief", "haishoku", "schemer2"]
    )
    def test_valid_algorithms(self, algorithm: str):
        """Test valid pywal algorithms are accepted."""
        settings = PywalBackendSettings(backend_algorithm=algorithm)
        assert settings.backend_algorithm == algorithm

    def test_invalid_algorithm(self):
        """Test invalid algorithm raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PywalBackendSettings(backend_algorithm="invalid")

        error = exc_info.value.errors()[0]
        assert "Invalid backend_algorithm" in str(error["ctx"]["error"])

    def test_algorithm_list_in_error(self):
        """Test that error message includes list of valid algorithms."""
        with pytest.raises(ValidationError) as exc_info:
            PywalBackendSettings(backend_algorithm="invalid")

        error_msg = str(exc_info.value.errors()[0]["ctx"]["error"])
        assert "colorz" in error_msg
        assert "haishoku" in error_msg


class TestWallustBackendSettings:
    """Tests for WallustBackendSettings model."""

    def test_default_values(self):
        """Test default wallust backend settings."""
        settings = WallustBackendSettings()
        assert settings.backend_type == wallust_backend_type

    def test_custom_backend_type(self):
        """Test custom backend type."""
        settings = WallustBackendSettings(backend_type="full")
        assert settings.backend_type == "full"

    def test_backend_type_no_validation(self):
        """Test that backend_type accepts any string (no validation)."""
        # Wallust backend type has no validation in the current implementation
        settings = WallustBackendSettings(backend_type="custom_value")
        assert settings.backend_type == "custom_value"


class TestCustomBackendSettings:
    """Tests for CustomBackendSettings model."""

    def test_default_values(self):
        """Test default custom backend settings."""
        settings = CustomBackendSettings()
        assert settings.algorithm == custom_algorithm
        assert settings.n_clusters == custom_n_clusters

    @pytest.mark.parametrize("algorithm", ["kmeans", "dominant"])
    def test_valid_algorithms(self, algorithm: str):
        """Test valid custom algorithms are accepted."""
        settings = CustomBackendSettings(algorithm=algorithm)
        assert settings.algorithm == algorithm

    def test_invalid_algorithm(self):
        """Test invalid algorithm raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CustomBackendSettings(algorithm="invalid")

        error = exc_info.value.errors()[0]
        assert "Invalid algorithm" in str(error["ctx"]["error"])

    @pytest.mark.parametrize("n_clusters", [8, 16, 32, 64, 128, 256])
    def test_valid_n_clusters(self, n_clusters: int):
        """Test valid n_clusters values (8-256)."""
        settings = CustomBackendSettings(n_clusters=n_clusters)
        assert settings.n_clusters == n_clusters

    def test_n_clusters_below_minimum(self):
        """Test n_clusters below 8 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CustomBackendSettings(n_clusters=7)

        error = exc_info.value.errors()[0]
        assert error["type"] == "greater_than_equal"

    def test_n_clusters_above_maximum(self):
        """Test n_clusters above 256 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            CustomBackendSettings(n_clusters=257)

        error = exc_info.value.errors()[0]
        assert error["type"] == "less_than_equal"

    def test_n_clusters_boundary_values(self):
        """Test n_clusters boundary values."""
        settings_min = CustomBackendSettings(n_clusters=8)
        settings_max = CustomBackendSettings(n_clusters=256)

        assert settings_min.n_clusters == 8
        assert settings_max.n_clusters == 256


class TestBackendSettings:
    """Tests for BackendSettings model."""

    def test_default_values(self):
        """Test default backend settings."""
        settings = BackendSettings()
        assert isinstance(settings.pywal, PywalBackendSettings)
        assert isinstance(settings.wallust, WallustBackendSettings)
        assert isinstance(settings.custom, CustomBackendSettings)

    def test_custom_pywal_settings(self):
        """Test custom pywal settings."""
        settings = BackendSettings(
            pywal=PywalBackendSettings(backend_algorithm="colorz")
        )
        assert settings.pywal.backend_algorithm == "colorz"

    def test_custom_wallust_settings(self):
        """Test custom wallust settings."""
        settings = BackendSettings(wallust=WallustBackendSettings(backend_type="full"))
        assert settings.wallust.backend_type == "full"

    def test_custom_custom_backend_settings(self):
        """Test custom custom backend settings."""
        settings = BackendSettings(
            custom=CustomBackendSettings(algorithm="dominant", n_clusters=32)
        )
        assert settings.custom.algorithm == "dominant"
        assert settings.custom.n_clusters == 32

    def test_partial_backend_settings(self):
        """Test providing only some backend settings."""
        settings = BackendSettings(pywal=PywalBackendSettings(backend_algorithm="wal"))
        # Others should use defaults
        assert settings.pywal.backend_algorithm == "wal"
        assert settings.wallust.backend_type == wallust_backend_type
        assert settings.custom.algorithm == custom_algorithm


class TestTemplateSettings:
    """Tests for TemplateSettings model."""

    def test_default_values(self):
        """Test default template settings."""
        settings = TemplateSettings()
        assert settings.directory == template_directory

    def test_custom_directory(self):
        """Test custom template directory."""
        custom_dir = Path("/custom/templates")
        settings = TemplateSettings(directory=custom_dir)
        assert settings.directory == custom_dir

    def test_directory_path_type(self):
        """Test directory is converted to Path."""
        settings = TemplateSettings(directory="/tmp/templates")
        assert isinstance(settings.directory, Path)


class TestAppConfig:
    """Tests for AppConfig model."""

    def test_default_values(self):
        """Test default app configuration."""
        config = AppConfig()
        assert isinstance(config.container, ContainerSettings)
        assert isinstance(config.logging, LoggingSettings)
        assert isinstance(config.output, OutputSettings)
        assert isinstance(config.generation, GenerationSettings)
        assert isinstance(config.backends, BackendSettings)
        assert isinstance(config.templates, TemplateSettings)

    def test_custom_logging(self):
        """Test custom logging configuration."""
        config = AppConfig(logging=LoggingSettings(level="DEBUG", show_path=True))
        assert config.logging.level == "DEBUG"
        assert config.logging.show_path is True

    def test_custom_output(self):
        """Test custom output configuration."""
        custom_dir = Path("/custom/output")
        config = AppConfig(
            output=OutputSettings(directory=custom_dir, formats=["json", "yaml"])
        )
        assert config.output.directory == custom_dir
        assert config.output.formats == ["json", "yaml"]

    def test_custom_generation(self):
        """Test custom generation configuration."""
        config = AppConfig(
            generation=GenerationSettings(
                default_backend="wallust", saturation_adjustment=1.5
            )
        )
        assert config.generation.default_backend == "wallust"
        assert config.generation.saturation_adjustment == 1.5

    def test_custom_backends(self):
        """Test custom backend configurations."""
        config = AppConfig(
            backends=BackendSettings(
                pywal=PywalBackendSettings(backend_algorithm="colorz"),
                custom=CustomBackendSettings(algorithm="dominant", n_clusters=64),
            )
        )
        assert config.backends.pywal.backend_algorithm == "colorz"
        assert config.backends.custom.algorithm == "dominant"
        assert config.backends.custom.n_clusters == 64

    def test_full_custom_config(self):
        """Test fully customized configuration."""
        config = AppConfig(
            container=ContainerSettings(engine="podman"),
            logging=LoggingSettings(level="DEBUG", show_time=False, show_path=True),
            output=OutputSettings(
                directory=Path("/custom/output"), formats=["json", "css"]
            ),
            generation=GenerationSettings(
                default_backend="custom", saturation_adjustment=1.2
            ),
            backends=BackendSettings(
                pywal=PywalBackendSettings(backend_algorithm="schemer2"),
                wallust=WallustBackendSettings(backend_type="full"),
                custom=CustomBackendSettings(algorithm="dominant", n_clusters=128),
            ),
            templates=TemplateSettings(directory=Path("/custom/templates")),
        )

        assert config.container.engine == "podman"
        assert config.logging.level == "DEBUG"
        assert config.output.directory == Path("/custom/output")
        assert config.generation.default_backend == "custom"
        assert config.backends.custom.n_clusters == 128
        assert config.templates.directory == Path("/custom/templates")

    def test_from_dict(self):
        """Test creating AppConfig from dictionary."""
        config_dict = {
            "logging": {"level": "WARNING", "show_time": False},
            "generation": {"default_backend": "wallust"},
        }
        config = AppConfig(**config_dict)
        assert config.logging.level == "WARNING"
        assert config.logging.show_time is False
        assert config.generation.default_backend == "wallust"

    def test_validation_error_propagation(self):
        """Test that validation errors from nested models propagate."""
        with pytest.raises(ValidationError):
            AppConfig(logging=LoggingSettings(level="INVALID"))

        with pytest.raises(ValidationError):
            AppConfig(generation=GenerationSettings(saturation_adjustment=3.0))

        with pytest.raises(ValidationError):
            AppConfig(
                backends=BackendSettings(custom=CustomBackendSettings(n_clusters=300))
            )


class TestFieldValidators:
    """Tests for field validators across all models."""

    def test_container_engine_validator(self):
        """Test container engine validator."""
        # Valid
        ContainerSettings(engine="docker")
        ContainerSettings(engine="podman")

        # Invalid
        with pytest.raises(ValidationError):
            ContainerSettings(engine="invalid")

    def test_logging_level_validator(self):
        """Test logging level validator."""
        # Valid
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            LoggingSettings(level=level)

        # Invalid
        with pytest.raises(ValidationError):
            LoggingSettings(level="TRACE")

    def test_generation_backend_validator(self):
        """Test generation backend validator."""
        # Valid
        for backend in ["pywal", "wallust", "custom"]:
            GenerationSettings(default_backend=backend)

        # Invalid
        with pytest.raises(ValidationError):
            GenerationSettings(default_backend="unknown")

    def test_pywal_algorithm_validator(self):
        """Test pywal algorithm validator."""
        # Valid
        for algo in ["wal", "colorz", "colorthief", "haishoku", "schemer2"]:
            PywalBackendSettings(backend_algorithm=algo)

        # Invalid
        with pytest.raises(ValidationError):
            PywalBackendSettings(backend_algorithm="unknown")

    def test_custom_algorithm_validator(self):
        """Test custom algorithm validator."""
        # Valid
        for algo in ["kmeans", "dominant"]:
            CustomBackendSettings(algorithm=algo)

        # Invalid
        with pytest.raises(ValidationError):
            CustomBackendSettings(algorithm="unknown")
