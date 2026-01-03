"""Integration tests for the CLI layer.

These tests verify end-to-end workflows through the CLI menu system,
testing the interaction between the CLI orchestrator and the skills layer.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from src.models.task import Task
from src.cli.todo_menu import (
    collect_task_input,
    collect_task_id,
    collect_update_input,
    display_tasks,
    handle_add_task,
    handle_view_tasks,
    handle_update_task,
    handle_delete_task,
    handle_toggle_task,
)


class TestCollectTaskInput:
    """Tests for task input collection."""

    def test_collect_valid_input(self):
        """Should return title and description when valid input is provided."""
        with patch('builtins.input', side_effect=['Buy groceries', 'Milk and eggs']):
            title, description = collect_task_input()
            assert title == "Buy groceries"
            assert description == "Milk and eggs"

    def test_collect_empty_title_rejected(self):
        """Empty title should be rejected and re-prompted."""
        inputs = iter(['', 'Valid title', 'Optional desc'])
        with patch('builtins.input', side_effect=inputs):
            title, description = collect_task_input()
            assert title == "Valid title"

    def test_collect_empty_description_becomes_none(self):
        """Empty description should be converted to None."""
        with patch('builtins.input', side_effect=['Title', '']):
            title, description = collect_task_input()
            assert description is None


class TestDisplayTasks:
    """Tests for task display formatting."""

    def test_display_empty_list(self):
        """Should show 'No tasks yet' for empty list."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_tasks([])
            output = fake_out.getvalue()
            assert "No tasks yet" in output

    def test_display_single_task(self):
        """Should display task with correct format."""
        task = Task(id=1, title="Test task", description="Test desc", completed=False)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_tasks([task])
            output = fake_out.getvalue()
            assert "1." in output
            assert "[ ]" in output
            assert "Test task" in output
            assert "Test desc" in output

    def test_display_completed_task(self):
        """Should show [X] for completed tasks."""
        task = Task(id=1, title="Done task", completed=True)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_tasks([task])
            output = fake_out.getvalue()
            assert "[X]" in output

    def test_display_multiple_tasks(self):
        """Should display all tasks in order."""
        tasks = [
            Task(id=1, title="Task 1"),
            Task(id=2, title="Task 2"),
            Task(id=3, title="Task 3"),
        ]
        with patch('sys.stdout', new=StringIO()) as fake_out:
            display_tasks(tasks)
            output = fake_out.getvalue()
            assert "1." in output
            assert "2." in output
            assert "3." in output
            assert "Task 1" in output
            assert "Task 2" in output
            assert "Task 3" in output


class TestHandleAddTask:
    """Tests for the Add Task workflow."""

    def test_add_task_success(self):
        """Adding a task should create it and return updated state."""
        with patch('builtins.input', side_effect=['New task', 'Description']):
            tasks, next_id = handle_add_task([], 1)

        assert len(tasks) == 1
        assert tasks[0].title == "New task"
        assert tasks[0].description == "Description"
        assert tasks[0].id == 1
        assert next_id == 2

    def test_add_multiple_tasks_increment_ids(self):
        """Each task should get a unique ID."""
        with patch('builtins.input', side_effect=['Task 1', '']):
            tasks1, next_id1 = handle_add_task([], 1)

        with patch('builtins.input', side_effect=['Task 2', '']):
            tasks2, next_id2 = handle_add_task(tasks1, next_id1)

        assert tasks1[0].id == 1
        assert tasks2[1].id == 2


class TestHandleUpdateTask:
    """Tests for the Update Task workflow."""

    def test_update_existing_task(self):
        """Updating an existing task should modify it."""
        existing = [Task(id=1, title="Original", description="Desc")]

        with patch('builtins.input', side_effect=['1', 'Updated', 'New desc']):
            tasks, was_updated = handle_update_task(existing)

        assert was_updated is True
        assert tasks[0].title == "Updated"
        assert tasks[0].description == "New desc"
        assert tasks[0].id == 1  # ID should not change

    def test_update_nonexistent_task(self):
        """Updating a nonexistent task should not modify the list."""
        tasks = [Task(id=1, title="Task")]

        with patch('builtins.input', side_effect=['999', 'New', '']):
            result, was_updated = handle_update_task(tasks)

        assert result == tasks
        assert was_updated is False

    def test_update_empty_list(self):
        """Updating when no tasks exist should return unchanged."""
        with patch('builtins.input', side_effect=[1, 'New', '']):
            result, was_updated = handle_update_task([])

        assert result == []
        assert was_updated is False


class TestHandleDeleteTask:
    """Tests for the Delete Task workflow."""

    def test_delete_existing_task(self):
        """Deleting an existing task should remove it."""
        tasks = [Task(id=1, title="To delete")]

        with patch('builtins.input', side_effect=['1']):
            result, deleted = handle_delete_task(tasks)

        assert deleted is True
        assert len(result) == 0

    def test_delete_nonexistent_task(self):
        """Deleting a nonexistent task should return unchanged list."""
        tasks = [Task(id=1, title="Task")]

        with patch('builtins.input', side_effect=['999']):
            result, deleted = handle_delete_task(tasks)

        assert deleted is False
        assert result == tasks

    def test_delete_preserves_other_tasks(self):
        """Deleting one task should not affect others."""
        tasks = [
            Task(id=1, title="Keep 1"),
            Task(id=2, title="Delete"),
            Task(id=3, title="Keep 2"),
        ]

        with patch('builtins.input', side_effect=['2']):
            result, deleted = handle_delete_task(tasks)

        assert deleted is True
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 3

    def test_delete_empty_list(self):
        """Deleting from empty list should return unchanged."""
        with patch('builtins.input', side_effect=[1]):
            result, deleted = handle_delete_task([])

        assert result == []
        assert deleted is False


class TestHandleToggleTask:
    """Tests for the Toggle Task workflow."""

    def test_toggle_incomplete_to_complete(self):
        """Toggling should change completion status."""
        tasks = [Task(id=1, title="Task", completed=False)]

        with patch('builtins.input', side_effect=['1']):
            result, toggled = handle_toggle_task(tasks)

        assert toggled is True
        assert result[0].completed is True

    def test_toggle_complete_to_incomplete(self):
        """Toggling should work in both directions."""
        tasks = [Task(id=1, title="Task", completed=True)]

        with patch('builtins.input', side_effect=['1']):
            result, toggled = handle_toggle_task(tasks)

        assert toggled is True
        assert result[0].completed is False

    def test_toggle_nonexistent_task(self):
        """Toggling a nonexistent task should not modify the list."""
        tasks = [Task(id=1, title="Task", completed=False)]

        with patch('builtins.input', side_effect=['999']):
            result, toggled = handle_toggle_task(tasks)

        assert toggled is False
        assert result[0].completed is False

    def test_toggle_empty_list(self):
        """Toggling from empty list should return unchanged."""
        with patch('builtins.input', side_effect=[1]):
            result, toggled = handle_toggle_task([])

        assert result == []
        assert toggled is False


class TestFullWorkflows:
    """Integration tests for complete user workflows."""

    def test_add_and_view_workflow(self):
        """Test adding tasks and viewing them."""
        # Add tasks
        with patch('builtins.input', side_effect=['Task 1', 'Desc 1']):
            tasks, next_id = handle_add_task([], 1)

        with patch('builtins.input', side_effect=['Task 2', '']):
            tasks, next_id = handle_add_task(tasks, next_id)

        assert len(tasks) == 2
        assert tasks[0].id == 1
        assert tasks[1].id == 2

        # View tasks
        with patch('sys.stdout', new=StringIO()) as fake_out:
            handle_view_tasks(tasks)
            output = fake_out.getvalue()
            assert "Task 1" in output
            assert "Task 2" in output

    def test_crud_workflow(self):
        """Test complete Create, Read, Update, Delete workflow."""
        # Create
        with patch('builtins.input', side_effect=['Task', 'Description']):
            tasks, next_id = handle_add_task([], 1)

        assert len(tasks) == 1

        # Read (View)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            handle_view_tasks(tasks)
            assert "Task" in fake_out.getvalue()

        # Update
        with patch('builtins.input', side_effect=['1', 'Updated', '']):
            tasks, _ = handle_update_task(tasks)

        assert tasks[0].title == "Updated"

        # Delete
        with patch('builtins.input', side_effect=['1']):
            tasks, _ = handle_delete_task(tasks)

        assert len(tasks) == 0

    def test_toggle_and_view_completion(self):
        """Test toggling completion and verifying view shows status."""
        # Add task
        with patch('builtins.input', side_effect=['Task', '']):
            tasks, _ = handle_add_task([], 1)

        # View incomplete
        with patch('sys.stdout', new=StringIO()) as fake_out:
            handle_view_tasks(tasks)
            assert "[ ]" in fake_out.getvalue()

        # Toggle to complete
        with patch('builtins.input', side_effect=['1']):
            tasks, _ = handle_toggle_task(tasks)

        # View complete
        with patch('sys.stdout', new=StringIO()) as fake_out:
            handle_view_tasks(tasks)
            assert "[X]" in fake_out.getvalue()
