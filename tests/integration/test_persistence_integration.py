"""
Integration tests for persistence layer (Phase II)

Tests that verify persistence works end-to-end with real file operations,
including restart scenarios, atomic writes, and corruption recovery.
"""

import pytest
import json
from pathlib import Path
from src.persistence import initialize_persistence, save_tasks, load_tasks
from src.models.task import Task


class TestPersistenceIntegration:
    """Integration tests for full persistence workflow"""

    def test_fresh_start_creates_empty_file(self, tmp_path, monkeypatch):
        """Test that fresh start creates empty todo_data.json"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        # Initialize on fresh system
        tasks, next_id = initialize_persistence()

        # Should have empty state
        assert len(tasks) == 0
        assert next_id == 1

        # File should exist with correct structure
        assert test_data_file.exists()
        with open(test_data_file, 'r') as f:
            data = json.load(f)
        assert data == {"version": "1.0", "tasks": []}

    def test_add_task_persists_immediately(self, tmp_path, monkeypatch):
        """Test that adding a task saves to file immediately"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        # Initialize
        tasks, next_id = initialize_persistence()

        # Add a task
        new_task = Task(id=next_id, title="Test Task", description="Description", completed=False)
        tasks.append(new_task)
        save_tasks(tasks)

        # Verify file was updated
        with open(test_data_file, 'r') as f:
            data = json.load(f)

        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Test Task"

    def test_restart_loads_previous_session(self, tmp_path, monkeypatch):
        """Test that restarting loads tasks from previous session"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        # First session: add tasks
        tasks, next_id = initialize_persistence()
        task1 = Task(id=next_id, title="Task 1", description=None, completed=False)
        task2 = Task(id=next_id+1, title="Task 2", description=None, completed=True)
        tasks.extend([task1, task2])
        save_tasks(tasks)

        # Simulate restart: re-initialize
        tasks_loaded, next_id_loaded = initialize_persistence()

        # Should load both tasks
        assert len(tasks_loaded) == 2
        assert tasks_loaded[0].title == "Task 1"
        assert tasks_loaded[0].completed == False
        assert tasks_loaded[1].title == "Task 2"
        assert tasks_loaded[1].completed == True
        assert next_id_loaded == 3  # max(2) + 1

    def test_task_id_continuity_after_restart(self, tmp_path, monkeypatch):
        """Test that task IDs continue correctly after restart"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        # Add 3 tasks, delete task 2
        tasks, next_id = initialize_persistence()
        task1 = Task(id=1, title="Task 1", description=None, completed=False)
        task2 = Task(id=2, title="Task 2", description=None, completed=False)
        task3 = Task(id=3, title="Task 3", description=None, completed=False)
        tasks = [task1, task2, task3]
        save_tasks(tasks)

        # Delete task 2
        tasks = [task1, task3]
        save_tasks(tasks)

        # Restart
        tasks_loaded, next_id_loaded = initialize_persistence()

        # Next ID should be 4 (max(3) + 1), not 2
        assert next_id_loaded == 4
        assert len(tasks_loaded) == 2

    def test_update_task_persists_changes(self, tmp_path, monkeypatch):
        """Test that updating a task persists changes"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        # Add a task
        tasks, next_id = initialize_persistence()
        task = Task(id=1, title="Original", description="Old", completed=False)
        tasks.append(task)
        save_tasks(tasks)

        # Update the task
        tasks[0].title = "Updated"
        tasks[0].description = "New"
        save_tasks(tasks)

        # Restart and verify
        tasks_loaded, _ = initialize_persistence()
        assert tasks_loaded[0].title == "Updated"
        assert tasks_loaded[0].description == "New"

    def test_delete_task_persists_removal(self, tmp_path, monkeypatch):
        """Test that deleting a task persists the removal"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        # Add two tasks
        tasks, next_id = initialize_persistence()
        task1 = Task(id=1, title="Task 1", description=None, completed=False)
        task2 = Task(id=2, title="Task 2", description=None, completed=False)
        tasks.extend([task1, task2])
        save_tasks(tasks)

        # Delete task 1
        tasks = [task2]
        save_tasks(tasks)

        # Restart and verify
        tasks_loaded, _ = initialize_persistence()
        assert len(tasks_loaded) == 1
        assert tasks_loaded[0].id == 2

    def test_toggle_status_persists_state(self, tmp_path, monkeypatch):
        """Test that toggling status persists the change"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        # Add incomplete task
        tasks, next_id = initialize_persistence()
        task = Task(id=1, title="Task", description=None, completed=False)
        tasks.append(task)
        save_tasks(tasks)

        # Toggle to complete
        tasks[0].completed = True
        save_tasks(tasks)

        # Restart and verify
        tasks_loaded, _ = initialize_persistence()
        assert tasks_loaded[0].completed == True

        # Toggle back to incomplete
        tasks_loaded[0].completed = False
        save_tasks(tasks_loaded)

        # Restart and verify again
        tasks_loaded2, _ = initialize_persistence()
        assert tasks_loaded2[0].completed == False

    def test_multiple_operations_persist_correctly(self, tmp_path, monkeypatch):
        """Test complex sequence of operations persists correctly"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        # Add 3 tasks
        tasks, next_id = initialize_persistence()
        for i in range(1, 4):
            task = Task(id=i, title=f"Task {i}", description=None, completed=False)
            tasks.append(task)
        save_tasks(tasks)

        # Update task 2
        tasks[1].title = "Updated Task 2"
        save_tasks(tasks)

        # Toggle task 3
        tasks[2].completed = True
        save_tasks(tasks)

        # Delete task 1
        tasks = tasks[1:]
        save_tasks(tasks)

        # Restart and verify all changes
        tasks_loaded, next_id_loaded = initialize_persistence()
        assert len(tasks_loaded) == 2
        assert tasks_loaded[0].id == 2
        assert tasks_loaded[0].title == "Updated Task 2"
        assert tasks_loaded[1].id == 3
        assert tasks_loaded[1].completed == True
        assert next_id_loaded == 4


class TestAtomicWrites:
    """Tests specifically for atomic write behavior"""

    def test_atomic_write_verified_with_tmp_file(self, tmp_path, monkeypatch):
        """Test that atomic write uses .tmp file during operation"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        tasks, _ = initialize_persistence()
        task = Task(id=1, title="Test", description=None, completed=False)
        tasks.append(task)

        # Save should complete successfully
        save_tasks(tasks)

        # .tmp file should not exist after save
        tmp_file = Path(str(test_data_file) + '.tmp')
        assert not tmp_file.exists()

        # Target file should exist
        assert test_data_file.exists()

    def test_rapid_successive_saves(self, tmp_path, monkeypatch):
        """Test that rapid saves don't corrupt data"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        tasks, next_id = initialize_persistence()

        # Rapid successive saves
        for i in range(10):
            task = Task(id=next_id + i, title=f"Task {i}", description=None, completed=False)
            tasks.append(task)
            save_tasks(tasks)

        # File should be valid JSON
        with open(test_data_file, 'r') as f:
            data = json.load(f)

        assert len(data["tasks"]) == 10

    def test_file_always_in_consistent_state(self, tmp_path, monkeypatch):
        """Test that file is always either old state or new state, never partial"""
        test_data_dir = tmp_path / "data"
        test_data_file = test_data_dir / "todo_data.json"
        monkeypatch.setattr('src.persistence.DATA_DIR', test_data_dir)
        monkeypatch.setattr('src.persistence.DATA_FILE', test_data_file)

        # Initial state
        tasks, _ = initialize_persistence()
        task1 = Task(id=1, title="Task 1", description=None, completed=False)
        tasks.append(task1)
        save_tasks(tasks)

        # Read initial state
        with open(test_data_file, 'r') as f:
            initial_content = f.read()

        # Update state
        task2 = Task(id=2, title="Task 2", description=None, completed=False)
        tasks.append(task2)
        save_tasks(tasks)

        # Read updated state
        with open(test_data_file, 'r') as f:
            updated_content = f.read()

        # Both should be valid JSON (not partial)
        json.loads(initial_content)  # Should not raise
        json.loads(updated_content)  # Should not raise

        # Content should have changed
        assert initial_content != updated_content
