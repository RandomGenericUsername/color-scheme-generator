"""Tests for container manager volume mounts including edge cases."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from color_scheme_orchestrator.container.manager import ContainerManager


class TestVolumeMountsRelativePath:
    """Tests for volume mount handling with relative paths (manager.py line 75)."""

    def test_relative_template_directory_converted_to_absolute(self):
        """Verify relative template paths are converted to absolute (line 75)."""
        # Create mock config
        mock_config = MagicMock()
        mock_config.core.templates.directory = Path("templates")
        mock_config.orchestrator.engine = "docker"
        mock_config.orchestrator.image_registry = None

        manager = ContainerManager(mock_config)

        with patch(
            "color_scheme_orchestrator.container.manager.Path.cwd"
        ) as mock_cwd:
            mock_cwd.return_value = Path("/home/user/project")
            # Call build_volume_mounts with the patched cwd
            mounts = manager.build_volume_mounts(
                Path("/home/user/image.jpg"),
                Path("/home/user/output"),
            )

        # Should have 3 mounts (image, output, templates)
        assert len(mounts) == 3

        # Templates mount should be present and be converted to absolute
        templates_mount = mounts[2]  # Third mount is templates
        assert "templates" in templates_mount
        # It should have been converted to absolute path
        assert "/home/user/project/templates" in templates_mount

    def test_absolute_template_directory_unchanged(self):
        """Verify absolute template paths are not modified."""
        mock_config = MagicMock()
        mock_config.core.templates.directory = Path("/absolute/templates")
        mock_config.orchestrator.engine = "docker"
        mock_config.orchestrator.image_registry = None

        manager = ContainerManager(mock_config)
        mounts = manager.build_volume_mounts(
            Path("/home/user/image.jpg"),
            Path("/home/user/output"),
        )

        # Should have 3 mounts
        assert len(mounts) == 3
        # Templates mount should contain the absolute path
        templates_mount = mounts[2]
        assert "/absolute/templates" in templates_mount
