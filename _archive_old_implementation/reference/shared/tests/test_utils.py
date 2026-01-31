"""Tests for shared utility functions."""

from pathlib import Path

import pytest

from colorscheme_shared.utils import expand_path, validate_directory, validate_file


class TestExpandPath:
    """Test expand_path function."""

    def test_expand_path_tilde(self):
        """Test expand_path expands tilde."""
        result = expand_path("~/test")
        assert result == Path.home() / "test"

    def test_expand_path_string(self):
        """Test expand_path accepts string."""
        result = expand_path("~/test")
        assert isinstance(result, Path)

    def test_expand_path_path(self):
        """Test expand_path accepts Path."""
        result = expand_path(Path("~/test"))
        assert isinstance(result, Path)

    def test_expand_path_absolute(self):
        """Test expand_path with absolute path."""
        result = expand_path("/tmp/test")
        assert result == Path("/tmp/test")


class TestValidateFile:
    """Test validate_file function."""

    def test_validate_file_exists(self, temp_file):
        """Test validate_file with existing file."""
        result = validate_file(temp_file)
        assert result == temp_file

    def test_validate_file_not_found(self):
        """Test validate_file with non-existent file."""
        with pytest.raises(FileNotFoundError):
            validate_file("/nonexistent/file.txt")

    def test_validate_file_is_directory(self, tmp_path):
        """Test validate_file with directory path."""
        with pytest.raises(IsADirectoryError):
            validate_file(tmp_path)

    def test_validate_file_returns_path(self, temp_file):
        """Test validate_file returns Path object."""
        result = validate_file(temp_file)
        assert isinstance(result, Path)


class TestValidateDirectory:
    """Test validate_directory function."""

    def test_validate_directory_exists(self, tmp_path):
        """Test validate_directory with existing directory."""
        result = validate_directory(tmp_path)
        assert result == tmp_path

    def test_validate_directory_not_exists_no_create(self):
        """Test validate_directory with non-existent directory (no create)."""
        # Should not raise if create=False and dir doesn't exist
        result = validate_directory("/nonexistent/path")
        assert result == Path("/nonexistent/path")

    def test_validate_directory_not_exists_create(self, tmp_path):
        """Test validate_directory with non-existent directory (create=True)."""
        new_dir = tmp_path / "new_dir"
        result = validate_directory(new_dir, create=True)
        assert result.exists()
        assert result.is_dir()

    def test_validate_directory_is_file(self, temp_file):
        """Test validate_directory with file path."""
        with pytest.raises(NotADirectoryError):
            validate_directory(temp_file)

    def test_validate_directory_returns_path(self, tmp_path):
        """Test validate_directory returns Path object."""
        result = validate_directory(tmp_path)
        assert isinstance(result, Path)

    def test_validate_directory_create_nested(self, tmp_path):
        """Test validate_directory creates nested directories."""
        nested_dir = tmp_path / "a" / "b" / "c"
        result = validate_directory(nested_dir, create=True)
        assert result.exists()
        assert result.is_dir()
