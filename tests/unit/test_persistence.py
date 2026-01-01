"""
Unit tests for persistence layer (Phase II)

Tests atomic writes, directory creation, and core persistence functions.
"""

import json
import pytest
from pathlib import Path
from src.persistence import ensure_data_directory, ensure_atomic_write


class TestEnsureDataDirectory:
    """Tests for ensure_data_directory() function"""

    def test_creates_directory_if_missing(self, tmp_path, monkeypatch):
        """Test that directory is created when it doesn't exist"""
        test_dir = tmp_path / "test_data"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_dir)

        # Directory should not exist yet
        assert not test_dir.exists()

        # Call function
        ensure_data_directory()

        # Directory should now exist
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_does_not_fail_if_directory_exists(self, tmp_path, monkeypatch):
        """Test that function handles existing directory gracefully"""
        test_dir = tmp_path / "existing_data"
        test_dir.mkdir()
        monkeypatch.setattr('src.persistence.DATA_DIR', test_dir)

        # Should not raise exception
        ensure_data_directory()

        # Directory should still exist
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_creates_parent_directories_if_needed(self, tmp_path, monkeypatch):
        """Test that parent directories are created"""
        test_dir = tmp_path / "parent" / "child" / "data"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_dir)

        # Call function
        ensure_data_directory()

        # All directories should be created
        assert test_dir.exists()
        assert test_dir.is_dir()


class TestEnsureAtomicWrite:
    """Tests for ensure_atomic_write() function"""

    def test_writes_valid_json_to_file(self, tmp_path):
        """Test that function writes valid JSON"""
        test_file = tmp_path / "test.json"
        test_data = {"version": "1.0", "tasks": []}

        ensure_atomic_write(test_data, test_file)

        # File should exist
        assert test_file.exists()

        # File should contain valid JSON
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert loaded_data == test_data

    def test_uses_temporary_file_during_write(self, tmp_path, monkeypatch):
        """Test that function writes to .tmp file first"""
        test_file = tmp_path / "test.json"
        test_data = {"version": "1.0", "tasks": []}

        # Track if tmp file is used
        tmp_used = []

        original_open = open

        def tracked_open(path, *args, **kwargs):
            if str(path).endswith('.tmp'):
                tmp_used.append(True)
            return original_open(path, *args, **kwargs)

        monkeypatch.setattr('builtins.open', tracked_open)

        ensure_atomic_write(test_data, test_file)

        # Temporary file should have been used
        assert len(tmp_used) > 0

    def test_overwrites_existing_file(self, tmp_path):
        """Test that function replaces existing file"""
        test_file = tmp_path / "test.json"

        # Write initial data
        initial_data = {"version": "1.0", "tasks": [{"id": 1}]}
        ensure_atomic_write(initial_data, test_file)

        # Overwrite with new data
        new_data = {"version": "1.0", "tasks": [{"id": 2}]}
        ensure_atomic_write(new_data, test_file)

        # File should contain new data
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert loaded_data == new_data
        assert loaded_data != initial_data

    def test_json_formatted_with_indentation(self, tmp_path):
        """Test that JSON is formatted with indentation for readability"""
        test_file = tmp_path / "test.json"
        test_data = {"version": "1.0", "tasks": [{"id": 1, "title": "Test"}]}

        ensure_atomic_write(test_data, test_file)

        # Read file content as string
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Should have newlines (indentation)
        assert '\n' in content
        # Should have proper JSON structure
        assert '"version"' in content
        assert '"tasks"' in content

    def test_handles_unicode_characters(self, tmp_path):
        """Test that function handles UTF-8 characters correctly"""
        test_file = tmp_path / "test.json"
        test_data = {"version": "1.0", "tasks": [{"id": 1, "title": "Test émoji 🎉"}]}

        ensure_atomic_write(test_data, test_file)

        # Read and verify
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert loaded_data == test_data
        assert loaded_data["tasks"][0]["title"] == "Test émoji 🎉"

    def test_no_temporary_file_remains_after_write(self, tmp_path):
        """Test that .tmp file is removed after successful write"""
        test_file = tmp_path / "test.json"
        test_data = {"version": "1.0", "tasks": []}

        ensure_atomic_write(test_data, test_file)

        # Temporary file should not exist
        tmp_file = Path(str(test_file) + '.tmp')
        assert not tmp_file.exists()

        # Target file should exist
        assert test_file.exists()
