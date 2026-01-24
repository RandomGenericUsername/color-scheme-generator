"""Tests for configuration enumerations."""

import pytest

from color_scheme.config.enums import Backend, ColorAlgorithm


class TestBackendEnum:
    """Tests for Backend enumeration."""

    def test_backend_values(self):
        """Test that all Backend enum values are correct."""
        assert Backend.PYWAL.value == "pywal"
        assert Backend.WALLUST.value == "wallust"
        assert Backend.CUSTOM.value == "custom"

    def test_backend_membership(self):
        """Test that valid strings are members of Backend enum."""
        assert "pywal" in [b.value for b in Backend]
        assert "wallust" in [b.value for b in Backend]
        assert "custom" in [b.value for b in Backend]

    def test_backend_invalid_value(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError):
            Backend("invalid")

    def test_backend_string_representation(self):
        """Test string representation of Backend enum."""
        assert str(Backend.PYWAL) == "Backend.PYWAL"
        assert Backend.PYWAL.value == "pywal"

    def test_backend_equality(self):
        """Test Backend enum equality."""
        assert Backend.PYWAL == Backend.PYWAL
        assert Backend.PYWAL != Backend.WALLUST
        assert Backend.PYWAL.value == "pywal"

    def test_backend_iteration(self):
        """Test iterating over Backend enum."""
        backends = list(Backend)
        assert len(backends) == 3
        assert Backend.PYWAL in backends
        assert Backend.WALLUST in backends
        assert Backend.CUSTOM in backends

    @pytest.mark.parametrize(
        "backend_value,expected_enum",
        [
            ("pywal", Backend.PYWAL),
            ("wallust", Backend.WALLUST),
            ("custom", Backend.CUSTOM),
        ],
    )
    def test_backend_from_string(self, backend_value: str, expected_enum: Backend):
        """Test creating Backend enum from string values."""
        assert Backend(backend_value) == expected_enum


class TestColorAlgorithmEnum:
    """Tests for ColorAlgorithm enumeration."""

    def test_color_algorithm_values(self):
        """Test that all ColorAlgorithm enum values are correct."""
        assert ColorAlgorithm.KMEANS.value == "kmeans"
        assert ColorAlgorithm.DOMINANT.value == "dominant"

    def test_color_algorithm_membership(self):
        """Test that valid strings are members of ColorAlgorithm enum."""
        assert "kmeans" in [a.value for a in ColorAlgorithm]
        assert "dominant" in [a.value for a in ColorAlgorithm]

    def test_color_algorithm_invalid_value(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError):
            ColorAlgorithm("invalid")

    def test_color_algorithm_string_representation(self):
        """Test string representation of ColorAlgorithm enum."""
        assert str(ColorAlgorithm.KMEANS) == "ColorAlgorithm.KMEANS"
        assert ColorAlgorithm.KMEANS.value == "kmeans"

    def test_color_algorithm_equality(self):
        """Test ColorAlgorithm enum equality."""
        assert ColorAlgorithm.KMEANS == ColorAlgorithm.KMEANS
        assert ColorAlgorithm.KMEANS != ColorAlgorithm.DOMINANT
        assert ColorAlgorithm.KMEANS.value == "kmeans"

    def test_color_algorithm_iteration(self):
        """Test iterating over ColorAlgorithm enum."""
        algorithms = list(ColorAlgorithm)
        assert len(algorithms) == 2
        assert ColorAlgorithm.KMEANS in algorithms
        assert ColorAlgorithm.DOMINANT in algorithms

    @pytest.mark.parametrize(
        "algorithm_value,expected_enum",
        [
            ("kmeans", ColorAlgorithm.KMEANS),
            ("dominant", ColorAlgorithm.DOMINANT),
        ],
    )
    def test_color_algorithm_from_string(
        self, algorithm_value: str, expected_enum: ColorAlgorithm
    ):
        """Test creating ColorAlgorithm enum from string values."""
        assert ColorAlgorithm(algorithm_value) == expected_enum

    def test_color_algorithm_is_string_enum(self):
        """Test that ColorAlgorithm inherits from str."""
        assert isinstance(ColorAlgorithm.KMEANS, str)
        assert ColorAlgorithm.KMEANS == "kmeans"


class TestEnumInteraction:
    """Tests for enum interaction and type checking."""

    def test_backend_is_string_enum(self):
        """Test that Backend inherits from str."""
        assert isinstance(Backend.PYWAL, str)
        assert Backend.PYWAL == "pywal"

    def test_enum_comparison_with_strings(self):
        """Test that enums can be compared with strings."""
        assert Backend.PYWAL == "pywal"
        assert ColorAlgorithm.KMEANS == "kmeans"

    def test_enum_types_are_different(self):
        """Test that Backend and ColorAlgorithm are different types."""
        # Even though both are str enums, they are from different enum classes
        assert Backend.PYWAL.__class__ != ColorAlgorithm.KMEANS.__class__
