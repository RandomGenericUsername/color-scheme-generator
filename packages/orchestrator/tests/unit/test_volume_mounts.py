"""Tests for volume mount configuration."""

from pathlib import Path

from color_scheme.config.config import AppConfig

from color_scheme_orchestrator.config.settings import ContainerSettings
from color_scheme_orchestrator.config.unified import UnifiedConfig
from color_scheme_orchestrator.container.manager import ContainerManager


class TestVolumeMounts:
    """Tests for constructing volume mounts."""

    def test_image_mount_readonly(self):
        """Test image file is mounted read-only."""
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        image_path = Path("/home/user/wallpaper.png")
        output_dir = Path("/tmp/output")

        mounts = manager.build_volume_mounts(image_path, output_dir)

        # Find image mount
        image_mount = next(m for m in mounts if "/input/image.png" in m)
        assert image_path.as_posix() in image_mount
        assert ":ro" in image_mount

    def test_output_mount_readwrite(self):
        """Test output directory is mounted read-write."""
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        image_path = Path("/home/user/wallpaper.png")
        output_dir = Path("/tmp/output")

        mounts = manager.build_volume_mounts(image_path, output_dir)

        # Find output mount
        output_mount = next(m for m in mounts if "/output" in m)
        assert output_dir.as_posix() in output_mount
        assert ":rw" in output_mount

    def test_templates_mount_readonly(self):
        """Test templates directory is mounted read-only."""
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        image_path = Path("/home/user/wallpaper.png")
        output_dir = Path("/tmp/output")

        mounts = manager.build_volume_mounts(image_path, output_dir)

        # Find templates mount
        template_mount = next(m for m in mounts if "/templates" in m)
        assert config.core.templates.directory.as_posix() in template_mount
        assert ":ro" in template_mount

    def test_mount_format_docker_style(self):
        """Test mounts are in Docker -v format."""
        config = UnifiedConfig(core=AppConfig(), orchestrator=ContainerSettings())
        manager = ContainerManager(config)
        image_path = Path("/home/user/wallpaper.png")
        output_dir = Path("/tmp/output")

        mounts = manager.build_volume_mounts(image_path, output_dir)

        # All mounts should be in format: host:container[:mode]
        for mount in mounts:
            parts = mount.split(":")
            assert len(parts) >= 2  # host:container or host:container:mode
