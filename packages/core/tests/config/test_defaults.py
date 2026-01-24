"""Tests for default configuration values."""

from pathlib import Path

import pytest

from color_scheme.config import defaults


class TestLoggingDefaults:
    """Tests for logging default values."""

    def test_default_log_level(self):
        """Test default log level is INFO."""
        assert defaults.default_log_level == "INFO"
        assert isinstance(defaults.default_log_level, str)

    def test_default_show_time(self):
        """Test default show_time is True."""
        assert defaults.default_show_time is True
        assert isinstance(defaults.default_show_time, bool)

    def test_default_show_path(self):
        """Test default show_path is False."""
        assert defaults.default_show_path is False
        assert isinstance(defaults.default_show_path, bool)


class TestOutputDefaults:
    """Tests for output default values."""

    def test_output_directory(self):
        """Test output directory default is correct path."""
        expected = Path.home() / ".config" / "color-scheme" / "output"
        assert defaults.output_directory == expected
        assert isinstance(defaults.output_directory, Path)

    def test_output_directory_is_absolute(self):
        """Test output directory is an absolute path."""
        assert defaults.output_directory.is_absolute()

    def test_default_formats(self):
        """Test default formats list contains expected formats."""
        expected_formats = [
            "json",
            "sh",
            "css",
            "gtk.css",
            "yaml",
            "sequences",
            "rasi",
            "scss",
        ]
        assert defaults.default_formats == expected_formats
        assert isinstance(defaults.default_formats, list)

    def test_default_formats_all_strings(self):
        """Test that all format values are strings."""
        assert all(isinstance(fmt, str) for fmt in defaults.default_formats)

    def test_default_formats_length(self):
        """Test default formats list has expected length."""
        assert len(defaults.default_formats) == 8


class TestGenerationDefaults:
    """Tests for generation default values."""

    def test_default_backend(self):
        """Test default backend is pywal."""
        assert defaults.default_backend == "pywal"
        assert isinstance(defaults.default_backend, str)

    def test_saturation_adjustment(self):
        """Test default saturation adjustment is 1.0."""
        assert defaults.saturation_adjustment == 1.0
        assert isinstance(defaults.saturation_adjustment, float)

    def test_saturation_adjustment_in_range(self):
        """Test saturation adjustment is within valid range (0.0-2.0)."""
        assert 0.0 <= defaults.saturation_adjustment <= 2.0


class TestBackendDefaults:
    """Tests for backend-specific default values."""

    def test_pywal_backend_algorithm(self):
        """Test pywal backend algorithm default."""
        assert defaults.pywal_backend_algorithm == "haishoku"
        assert isinstance(defaults.pywal_backend_algorithm, str)

    def test_wallust_backend_type(self):
        """Test wallust backend type default."""
        assert defaults.wallust_backend_type == "resized"
        assert isinstance(defaults.wallust_backend_type, str)

    def test_custom_algorithm(self):
        """Test custom algorithm default."""
        assert defaults.custom_algorithm == "kmeans"
        assert isinstance(defaults.custom_algorithm, str)

    def test_custom_n_clusters(self):
        """Test custom n_clusters default."""
        assert defaults.custom_n_clusters == 16
        assert isinstance(defaults.custom_n_clusters, int)

    def test_custom_n_clusters_in_range(self):
        """Test custom n_clusters is within valid range (8-256)."""
        assert 8 <= defaults.custom_n_clusters <= 256


class TestTemplateDefaults:
    """Tests for template default values."""

    def test_template_directory(self):
        """Test template directory points to package templates."""
        assert isinstance(defaults.template_directory, Path)
        # Should point to templates directory relative to package
        assert defaults.template_directory.name == "templates"

    def test_template_directory_is_absolute(self):
        """Test template directory is an absolute path."""
        assert defaults.template_directory.is_absolute()

    def test_template_directory_from_env_var(self, monkeypatch: pytest.MonkeyPatch):
        """Test template directory can be overridden via environment variable."""
        import importlib

        custom_path = "/custom/templates"
        monkeypatch.setenv("COLOR_SCHEME_TEMPLATES", custom_path)

        # Reload the module to pick up the new environment variable
        importlib.reload(defaults)

        assert defaults.template_directory == Path(custom_path)

        # Clean up - reload without the env var
        monkeypatch.delenv("COLOR_SCHEME_TEMPLATES")
        importlib.reload(defaults)

    def test_package_templates_path(self):
        """Test internal _package_templates variable exists and is valid."""
        assert hasattr(defaults, "_package_templates")
        assert isinstance(defaults._package_templates, Path)
        assert defaults._package_templates.name == "templates"


class TestDefaultValueTypes:
    """Tests to ensure all default values have correct types."""

    @pytest.mark.parametrize(
        "default_name,expected_type",
        [
            ("default_log_level", str),
            ("default_show_time", bool),
            ("default_show_path", bool),
            ("output_directory", Path),
            ("default_formats", list),
            ("default_backend", str),
            ("saturation_adjustment", float),
            ("pywal_backend_algorithm", str),
            ("wallust_backend_type", str),
            ("custom_algorithm", str),
            ("custom_n_clusters", int),
            ("template_directory", Path),
        ],
    )
    def test_default_value_type(self, default_name: str, expected_type: type):
        """Test that default values have expected types."""
        value = getattr(defaults, default_name)
        assert isinstance(value, expected_type)


class TestDefaultsImmutability:
    """Tests to ensure defaults are not accidentally modified."""

    def test_default_formats_is_list(self):
        """Test that default_formats is a list (not tuple)."""
        # It should be a list so it can be copied, but we should
        # never modify the original
        assert isinstance(defaults.default_formats, list)

    def test_modifying_formats_doesnt_affect_original(self):
        """Test that modifying a copy doesn't affect the original."""
        original_formats = defaults.default_formats.copy()
        copy_formats = defaults.default_formats.copy()
        copy_formats.append("new_format")

        # Original should be unchanged
        assert defaults.default_formats == original_formats
        assert "new_format" not in defaults.default_formats
        assert "new_format" in copy_formats
