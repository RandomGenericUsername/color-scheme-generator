"""Shared fixtures for colorscheme-generator tests."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from colorscheme_generator.config.config import AppConfig
from colorscheme_generator.config.enums import (
    Backend,
    ColorFormat,
)
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.core.types import (
    Color,
    ColorScheme,
    GeneratorConfig,
)


@pytest.fixture
def mock_settings(tmp_path):
    """Create mock settings for testing."""
    # Create a temporary config directory
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create minimal settings.toml
    settings_file = config_dir / "settings.toml"
    settings_file.write_text(
        """
[backends.pywal]
use_library = false
cache_dir = "$HOME/.cache/wal"

[backends.wallust]
binary_path = "wallust"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16

[output]
default_formats = ["json", "css"]
default_output_dir = "$HOME/.cache/colorscheme"
"""
    )

    # Load settings
    with patch.object(Settings, "_config_path", settings_file):
        settings = Settings.get()

    return settings


@pytest.fixture
def sample_image(tmp_path):
    """Create a small test image."""
    img_path = tmp_path / "test_image.png"
    img = Image.new("RGB", (100, 100), color=(255, 87, 51))
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_image_pil():
    """Create a PIL Image object for testing."""
    return Image.new("RGB", (100, 100), color=(255, 87, 51))


@pytest.fixture
def sample_color():
    """Create a sample Color object."""
    return Color(hex="#FF5733", rgb=(255, 87, 51), hsl=(11.0, 1.0, 0.6))


@pytest.fixture
def sample_colors():
    """Create a list of 16 sample colors."""
    colors = []
    for i in range(16):
        r = (i * 16) % 256
        g = (i * 32) % 256
        b = (i * 64) % 256
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        colors.append(Color(hex=hex_color, rgb=(r, g, b)))
    return colors


@pytest.fixture
def sample_color_scheme(sample_image, sample_colors):
    """Create a sample ColorScheme object."""
    return ColorScheme(
        background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
        foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
        cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
        colors=sample_colors,
        source_image=sample_image,
        backend="pywal",
    )


@pytest.fixture
def sample_generator_config(tmp_path):
    """Create a sample GeneratorConfig."""
    return GeneratorConfig(
        backend=Backend.PYWAL,
        output_dir=tmp_path / "output",
        formats=[ColorFormat.JSON, ColorFormat.CSS],

        backend_options={},
    )


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for command execution."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["test"], returncode=0, stdout="", stderr=""
        )
        yield mock_run


@pytest.fixture
def mock_shutil_which():
    """Mock shutil.which for executable detection."""
    with patch("shutil.which") as mock_which:
        yield mock_which


@pytest.fixture
def mock_pywal_cache(tmp_path):
    """Create mock pywal cache directory with colors.json."""
    cache_dir = tmp_path / ".cache" / "wal"
    cache_dir.mkdir(parents=True)

    colors_json = cache_dir / "colors.json"
    colors_data = {
        "special": {
            "background": "#1a1a1a",
            "foreground": "#ffffff",
            "cursor": "#ff0000",
        },
        "colors": {
            f"color{i}": f"#{i * 16:02x}{i * 32:02x}{i * 64:02x}"
            for i in range(16)
        },
    }
    colors_json.write_text(json.dumps(colors_data))

    return cache_dir


@pytest.fixture
def mock_pil_image():
    """Mock PIL Image for testing."""
    with patch("PIL.Image.open") as mock_open:
        mock_img = MagicMock(spec=Image.Image)
        mock_img.convert.return_value = mock_img
        mock_img.size = (100, 100)
        mock_img.mode = "RGB"
        mock_open.return_value = mock_img
        yield mock_open


@pytest.fixture
def mock_kmeans():
    """Mock sklearn KMeans for testing."""
    with patch("sklearn.cluster.KMeans") as mock_kmeans_class:
        mock_kmeans = MagicMock()
        mock_kmeans.cluster_centers_ = [
            [255, 87, 51],
            [26, 26, 26],
            [255, 255, 255],
            [255, 0, 0],
        ] + [[i * 16, i * 32, i * 64] for i in range(12)]
        mock_kmeans_class.return_value = mock_kmeans
        yield mock_kmeans_class


@pytest.fixture
def mock_template_renderer():
    """Mock template renderer for testing."""
    with patch(
        "colorscheme_generator.core.managers.output_manager.Jinja2Renderer"
    ) as mock_renderer_class:
        mock_renderer = MagicMock()
        mock_renderer.render_to_string.return_value = "rendered content"
        mock_renderer_class.return_value = mock_renderer
        yield mock_renderer


@pytest.fixture
def sample_pywal_output():
    """Sample pywal CLI output."""
    return json.dumps(
        {
            "special": {
                "background": "#1a1a1a",
                "foreground": "#ffffff",
                "cursor": "#ff0000",
            },
            "colors": {
                f"color{i}": f"#{i * 16:02x}{i * 32:02x}{i * 64:02x}"
                for i in range(16)
            },
        }
    )


@pytest.fixture
def sample_wallust_output():
    """Sample wallust CLI output."""
    colors = [f"#{i * 16:02x}{i * 32:02x}{i * 64:02x}" for i in range(16)]
    return "\n".join(colors)


@pytest.fixture
def mock_app_config():
    """Create a mock AppConfig object."""
    from colorscheme_generator.config.config import (
        BackendSettings,
        CustomBackendSettings,
        GenerationSettings,
        OutputSettings,
        PywalBackendSettings,
        TemplateSettings,
        WallustBackendSettings,
    )

    # Create actual config objects with defaults
    config = AppConfig(
        backends=BackendSettings(
            pywal=PywalBackendSettings(),
            wallust=WallustBackendSettings(
                backend_type="resized"
            ),
            custom=CustomBackendSettings(algorithm="kmeans", n_clusters=16),
        ),
        output=OutputSettings(
            directory=Path.home() / ".cache" / "colorscheme",
            formats=["json", "css"],
        ),
        generation=GenerationSettings(
            default_backend="pywal",

            saturation_adjustment=1.0,
        ),
        templates=TemplateSettings(
            directory=Path(__file__).parent.parent
            / "src"
            / "colorscheme_generator"
            / "templates",

        ),
    )

    return config
