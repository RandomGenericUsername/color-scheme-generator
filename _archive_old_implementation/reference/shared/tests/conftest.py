"""Shared test fixtures."""

import pytest


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file."""
    file = tmp_path / "test_file.txt"
    file.write_text("test content")
    return file


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory."""
    return tmp_path / "test_dir"
