"""Tests for CLI override mechanism."""

from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict, Field

from color_scheme_settings.errors import SettingsOverrideError
from color_scheme_settings.overrides import apply_overrides


class MockLogging(BaseModel):
    level: str = Field(default="INFO")


class MockOutput(BaseModel):
    directory: Path = Field(default=Path("/default/output"))
    formats: list[str] = Field(default_factory=lambda: ["json", "css"])


class MockGeneration(BaseModel):
    default_backend: str = Field(default="pywal")
    saturation_adjustment: float = Field(default=1.0, ge=0.0, le=2.0)


class MockCoreConfig(BaseModel):
    logging: MockLogging = Field(default_factory=MockLogging)
    output: MockOutput = Field(default_factory=MockOutput)
    generation: MockGeneration = Field(default_factory=MockGeneration)


class MockContainer(BaseModel):
    engine: str = Field(default="docker")


class MockUnifiedConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    core: MockCoreConfig
    orchestrator: MockContainer


@pytest.fixture
def base_config() -> MockUnifiedConfig:
    return MockUnifiedConfig(
        core=MockCoreConfig(),
        orchestrator=MockContainer(),
    )


class TestApplyOverrides:
    """Tests for applying CLI overrides."""

    def test_override_scalar(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {"core.generation.saturation_adjustment": 1.5},
        )
        assert result.core.generation.saturation_adjustment == 1.5

    def test_override_path(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {"core.output.directory": Path("/custom/output")},
        )
        assert result.core.output.directory == Path("/custom/output")

    def test_override_list(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {"core.output.formats": ["json"]},
        )
        assert result.core.output.formats == ["json"]

    def test_override_orchestrator(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {"orchestrator.engine": "podman"},
        )
        assert result.orchestrator.engine == "podman"

    def test_multiple_overrides(self, base_config: MockUnifiedConfig):
        result = apply_overrides(
            base_config,
            {
                "core.generation.saturation_adjustment": 0.5,
                "core.output.formats": ["yaml"],
                "orchestrator.engine": "podman",
            },
        )
        assert result.core.generation.saturation_adjustment == 0.5
        assert result.core.output.formats == ["yaml"]
        assert result.orchestrator.engine == "podman"

    def test_nonexistent_key_raises_error(self, base_config: MockUnifiedConfig):
        with pytest.raises(SettingsOverrideError) as exc_info:
            apply_overrides(base_config, {"core.nonexistent.key": "value"})
        assert "core.nonexistent.key" in str(exc_info.value)

    def test_nonexistent_leaf_raises_error(self, base_config: MockUnifiedConfig):
        with pytest.raises(SettingsOverrideError):
            apply_overrides(base_config, {"core.generation.nonexistent": 1.0})

    def test_original_not_mutated(self, base_config: MockUnifiedConfig):
        apply_overrides(
            base_config,
            {"core.generation.saturation_adjustment": 1.5},
        )
        assert base_config.core.generation.saturation_adjustment == 1.0

    def test_empty_overrides_returns_equivalent(self, base_config: MockUnifiedConfig):
        result = apply_overrides(base_config, {})
        assert result.core.generation.saturation_adjustment == base_config.core.generation.saturation_adjustment
