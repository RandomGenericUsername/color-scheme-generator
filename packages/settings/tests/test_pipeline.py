"""End-to-end pipeline tests: files -> merge -> validate -> override."""

from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict, Field

from color_scheme_settings import (
    SchemaRegistry,
    configure,
    get_config,
    load_config,
    reload_config,
    reset,
)


class PipelineCoreGeneration(BaseModel):
    default_backend: str = Field(default="pywal")
    saturation_adjustment: float = Field(default=1.0, ge=0.0, le=2.0)


class PipelineCoreOutput(BaseModel):
    formats: list[str] = Field(default_factory=lambda: ["json", "css"])


class PipelineCoreConfig(BaseModel):
    generation: PipelineCoreGeneration = Field(default_factory=PipelineCoreGeneration)
    output: PipelineCoreOutput = Field(default_factory=PipelineCoreOutput)


class PipelineContainerConfig(BaseModel):
    engine: str = Field(default="docker")


class PipelineUnifiedConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    core: PipelineCoreConfig
    orchestrator: PipelineContainerConfig


@pytest.fixture(autouse=True)
def clean_state():
    reset()
    yield
    reset()


@pytest.fixture
def package_files(tmp_path: Path) -> tuple[Path, Path]:
    """Create package-level settings files."""
    core_file = tmp_path / "core_settings.toml"
    core_file.write_text("""\
[generation]
default_backend = "pywal"
saturation_adjustment = 1.0

[output]
formats = ["json", "sh", "css"]
""")
    orch_file = tmp_path / "orch_settings.toml"
    orch_file.write_text("""\
engine = "docker"
""")
    return core_file, orch_file


@pytest.fixture
def project_root_dir(tmp_path: Path) -> Path:
    """Create project root with namespaced settings."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    settings_file = project_dir / "settings.toml"
    settings_file.write_text("""\
[core.generation]
default_backend = "wallust"

[core.output]
formats = ["json", "yaml"]

[orchestrator]
engine = "podman"
""")
    return project_dir


@pytest.fixture
def user_config_file(tmp_path: Path) -> Path:
    """Create user config with namespaced settings."""
    user_file = tmp_path / "user_settings.toml"
    user_file.write_text("""\
[core.generation]
saturation_adjustment = 1.5
""")
    return user_file


class TestFullPipeline:
    """End-to-end tests for the complete settings pipeline."""

    def test_package_defaults_only(self, package_files: tuple[Path, Path]):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(PipelineUnifiedConfig)

        config = load_config()
        assert config.core.generation.default_backend == "pywal"
        assert config.core.generation.saturation_adjustment == 1.0
        assert config.core.output.formats == ["json", "sh", "css"]
        assert config.orchestrator.engine == "docker"

    def test_project_overrides_package(
        self,
        package_files: tuple[Path, Path],
        project_root_dir: Path,
    ):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(PipelineUnifiedConfig, project_root=project_root_dir)

        config = load_config()
        # Project overrides backend and formats
        assert config.core.generation.default_backend == "wallust"
        assert config.core.output.formats == ["json", "yaml"]
        # Package default preserved for saturation
        assert config.core.generation.saturation_adjustment == 1.0
        # Orchestrator overridden
        assert config.orchestrator.engine == "podman"

    def test_user_overrides_project(
        self,
        package_files: tuple[Path, Path],
        project_root_dir: Path,
        user_config_file: Path,
    ):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(
            PipelineUnifiedConfig,
            project_root=project_root_dir,
            user_config_path=user_config_file,
        )

        config = load_config()
        # User overrides saturation
        assert config.core.generation.saturation_adjustment == 1.5
        # Project override preserved for backend
        assert config.core.generation.default_backend == "wallust"
        # Project override preserved for formats
        assert config.core.output.formats == ["json", "yaml"]

    def test_cli_overrides_everything(
        self,
        package_files: tuple[Path, Path],
        project_root_dir: Path,
        user_config_file: Path,
    ):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(
            PipelineUnifiedConfig,
            project_root=project_root_dir,
            user_config_path=user_config_file,
        )

        config = get_config(
            {
                "core.generation.saturation_adjustment": 0.5,
                "core.output.formats": ["scss"],
                "orchestrator.engine": "docker",
            }
        )
        assert config.core.generation.saturation_adjustment == 0.5
        assert config.core.output.formats == ["scss"]
        assert config.orchestrator.engine == "docker"
        # backend still from project layer
        assert config.core.generation.default_backend == "wallust"

    def test_caching(self, package_files: tuple[Path, Path]):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(PipelineUnifiedConfig)

        config1 = load_config()
        config2 = load_config()
        assert config1 is config2

    def test_reload_reloads(self, package_files: tuple[Path, Path]):
        core_file, orch_file = package_files
        SchemaRegistry.register("core", PipelineCoreConfig, core_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, orch_file)
        configure(PipelineUnifiedConfig)

        config1 = load_config()
        config2 = reload_config()
        assert config1 is not config2

    def test_missing_package_file_uses_pydantic_defaults(self, tmp_path: Path):
        missing_file = tmp_path / "nonexistent.toml"
        SchemaRegistry.register("core", PipelineCoreConfig, missing_file)
        SchemaRegistry.register("orchestrator", PipelineContainerConfig, missing_file)
        configure(PipelineUnifiedConfig)

        config = load_config()
        assert config.core.generation.default_backend == "pywal"  # Pydantic default
        assert config.orchestrator.engine == "docker"  # Pydantic default
