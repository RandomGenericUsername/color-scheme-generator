"""Tests for the deep merge algorithm."""

from color_scheme_settings.loader import LayerSource
from color_scheme_settings.merger import deep_merge, merge_layers


class TestDeepMerge:
    """Tests for deep_merge function."""

    def test_empty_base(self):
        result = deep_merge({}, {"a": 1})
        assert result == {"a": 1}

    def test_empty_override(self):
        result = deep_merge({"a": 1}, {})
        assert result == {"a": 1}

    def test_both_empty(self):
        result = deep_merge({}, {})
        assert result == {}

    def test_scalar_override(self):
        result = deep_merge({"a": 1}, {"a": 2})
        assert result == {"a": 2}

    def test_base_keys_preserved(self):
        result = deep_merge({"a": 1, "b": 2}, {"a": 10})
        assert result == {"a": 10, "b": 2}

    def test_new_keys_added(self):
        result = deep_merge({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_nested_dict_merge(self):
        base = {"section": {"key1": "v1", "key2": "v2"}}
        override = {"section": {"key2": "override"}}
        result = deep_merge(base, override)
        assert result == {"section": {"key1": "v1", "key2": "override"}}

    def test_deeply_nested_merge(self):
        base = {"a": {"b": {"c": 1, "d": 2}}}
        override = {"a": {"b": {"c": 10}}}
        result = deep_merge(base, override)
        assert result == {"a": {"b": {"c": 10, "d": 2}}}

    def test_list_replaced_entirely(self):
        base = {"formats": ["json", "css", "yaml"]}
        override = {"formats": ["json"]}
        result = deep_merge(base, override)
        assert result == {"formats": ["json"]}

    def test_list_in_nested_dict_replaced(self):
        base = {"output": {"formats": ["json", "css", "yaml"]}}
        override = {"output": {"formats": ["json"]}}
        result = deep_merge(base, override)
        assert result == {"output": {"formats": ["json"]}}

    def test_dict_overrides_scalar(self):
        base = {"a": "string"}
        override = {"a": {"nested": True}}
        result = deep_merge(base, override)
        assert result == {"a": {"nested": True}}

    def test_scalar_overrides_dict(self):
        base = {"a": {"nested": True}}
        override = {"a": "string"}
        result = deep_merge(base, override)
        assert result == {"a": "string"}

    def test_does_not_mutate_base(self):
        base = {"a": 1, "b": {"c": 2}}
        base_copy = {"a": 1, "b": {"c": 2}}
        deep_merge(base, {"a": 10, "b": {"c": 20}})
        assert base == base_copy

    def test_does_not_mutate_override(self):
        override = {"a": {"b": 1}}
        override_copy = {"a": {"b": 1}}
        deep_merge({"a": {"b": 0}}, override)
        assert override == override_copy


class TestMergeLayers:
    """Tests for merge_layers function."""

    def test_empty_layers(self):
        result = merge_layers([])
        assert result == {}

    def test_single_layer(self):
        layers = [
            LayerSource(
                layer="package",
                namespace="core",
                file_path=None,
                data={"logging": {"level": "INFO"}},
            )
        ]
        result = merge_layers(layers)
        assert result == {"core": {"logging": {"level": "INFO"}}}

    def test_two_layers_same_namespace(self):
        layers = [
            LayerSource(
                layer="package",
                namespace="core",
                file_path=None,
                data={
                    "generation": {
                        "default_backend": "pywal",
                        "saturation_adjustment": 1.0,
                    }
                },
            ),
            LayerSource(
                layer="project",
                namespace="core",
                file_path=None,
                data={"generation": {"saturation_adjustment": 1.3}},
            ),
        ]
        result = merge_layers(layers)
        assert result["core"]["generation"]["default_backend"] == "pywal"
        assert result["core"]["generation"]["saturation_adjustment"] == 1.3

    def test_multiple_namespaces(self):
        layers = [
            LayerSource(
                layer="package",
                namespace="core",
                file_path=None,
                data={"logging": {"level": "INFO"}},
            ),
            LayerSource(
                layer="package",
                namespace="orchestrator",
                file_path=None,
                data={"container": {"engine": "docker"}},
            ),
        ]
        result = merge_layers(layers)
        assert "core" in result
        assert "orchestrator" in result
        assert result["core"]["logging"]["level"] == "INFO"
        assert result["orchestrator"]["container"]["engine"] == "docker"

    def test_three_layers_priority_order(self):
        """Package -> Project -> User, each overriding fields."""
        layers = [
            LayerSource(
                layer="package",
                namespace="core",
                file_path=None,
                data={
                    "generation": {
                        "default_backend": "pywal",
                        "saturation_adjustment": 1.0,
                    },
                    "output": {"formats": ["json", "css", "yaml"]},
                },
            ),
            LayerSource(
                layer="project",
                namespace="core",
                file_path=None,
                data={"generation": {"saturation_adjustment": 1.3}},
            ),
            LayerSource(
                layer="user",
                namespace="core",
                file_path=None,
                data={"output": {"formats": ["json"]}},
            ),
        ]
        result = merge_layers(layers)
        assert result["core"]["generation"]["default_backend"] == "pywal"
        assert result["core"]["generation"]["saturation_adjustment"] == 1.3
        assert result["core"]["output"]["formats"] == ["json"]
