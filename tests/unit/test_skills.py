"""Unit tests for the skills layer.

Tests verify that all skills (AddTask, GetTasks, UpdateTask, DeleteTask, ToggleTaskStatus)
behave according to their contracts in /specs/001-in-memory-todo/contracts/skills.md
"""

import pytest

from src.models.task import Task
from src.skills.task_skills import (
    AddTask,
    GetTasks,
    UpdateTask,
    DeleteTask,
    ToggleTaskStatus
)


class TestAddTask:
    """Tests for the AddTask skill."""

    def test_add_single_task(self):
        """Adding a task should create it with the correct ID and default values."""
        tasks = []
        new_task, updated_tasks, next_id = AddTask("Buy milk", "2% preferred", tasks, 1)

        assert new_task.id == 1
        assert new_task.title == "Buy milk"
        assert new_task.description == "2% preferred"
        assert new_task.completed is False
        assert len(updated_tasks) == 1
        assert next_id == 2

    def test_add_multiple_tasks(self):
        """Each new task should get a unique sequential ID."""
        task1, tasks1, next_id1 = AddTask("Task 1", None, [], 1)
        task2, tasks2, next_id2 = AddTask("Task 2", None, tasks1, next_id1)
        task3, tasks3, next_id3 = AddTask("Task 3", None, tasks2, next_id2)

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3
        assert len(tasks3) == 3
        assert next_id3 == 4

    def test_add_task_with_none_description(self):
        """Description can be None."""
        task, tasks, next_id = AddTask("Simple task", None, [], 1)

        assert task.description is None
        assert len(tasks) == 1

    def test_returns_new_list_instance(self):
        """AddTask should return a new list, not modify the original."""
        original = []
        _, new_list, _ = AddTask("Task", None, original, 1)

        assert original == []
        assert new_list != original
        assert len(new_list) == 1


class TestGetTasks:
    """Tests for the GetTasks skill."""

    def test_get_empty_list(self):
        """Getting tasks from empty list should return empty list."""
        result = GetTasks([])
        assert result == []

    def test_get_all_tasks(self):
        """GetTasks should return all tasks."""
        tasks = [
            Task(id=1, title="Task 1"),
            Task(id=2, title="Task 2"),
        ]
        result = GetTasks(tasks)

        assert len(result) == 2
        assert result[0].title == "Task 1"
        assert result[1].title == "Task 2"

    def test_returns_copy(self):
        """GetTasks should return a copy, not the original list."""
        original = [Task(id=1, title="Task")]
        result = GetTasks(original)

        # Modifying the result should not affect original
        result.append(Task(id=2, title="Task 2"))
        assert len(original) == 1
        assert len(result) == 2


class TestUpdateTask:
    """Tests for the UpdateTask skill."""

    def test_update_title_only(self):
        """UpdateTask should update only the title when description is None."""
        task = Task(id=1, title="Old title", description="Old desc")
        updated, new_list = UpdateTask(1, "New title", None, [task])

        assert updated.title == "New title"
        assert updated.description == "Old desc"
        assert updated.id == 1
        assert updated.completed is False

    def test_update_description_only(self):
        """UpdateTask should update only the description when title is None."""
        task = Task(id=1, title="Title", description="Old desc")
        updated, new_list = UpdateTask(1, None, "New desc", [task])

        assert updated.title == "Title"
        assert updated.description == "New desc"

    def test_update_both_fields(self):
        """UpdateTask should update both title and description."""
        task = Task(id=1, title="Old", description="Old")
        updated, new_list = UpdateTask(1, "New", "New", [task])

        assert updated.title == "New"
        assert updated.description == "New"

    def test_update_nonexistent_task(self):
        """Updating a nonexistent task should return None and original list."""
        task = Task(id=1, title="Task")
        updated, new_list = UpdateTask(999, "New", None, [task])

        assert updated is None
        assert new_list == [task]

    def test_preserves_completion_status(self):
        """UpdateTask should not change the completion status."""
        task = Task(id=1, title="Task", completed=True)
        updated, _ = UpdateTask(1, "New title", None, [task])

        assert updated.completed is True


class TestDeleteTask:
    """Tests for the DeleteTask skill."""

    def test_delete_existing_task(self):
        """Deleting an existing task should return True and updated list."""
        task = Task(id=1, title="Task")
        deleted, new_list = DeleteTask(1, [task])

        assert deleted is True
        assert len(new_list) == 0

    def test_delete_nonexistent_task(self):
        """Deleting a nonexistent task should return False and original list."""
        task = Task(id=1, title="Task")
        deleted, new_list = DeleteTask(999, [task])

        assert deleted is False
        assert len(new_list) == 1
        assert new_list[0] == task

    def test_delete_from_multiple_tasks(self):
        """Deleting one task should keep others intact."""
        tasks = [
            Task(id=1, title="Task 1"),
            Task(id=2, title="Task 2"),
            Task(id=3, title="Task 3"),
        ]
        deleted, new_list = DeleteTask(2, tasks)

        assert deleted is True
        assert len(new_list) == 2
        assert new_list[0].id == 1
        assert new_list[1].id == 3


class TestToggleTaskStatus:
    """Tests for the ToggleTaskStatus skill."""

    def test_toggle_incomplete_to_complete(self):
        """Toggling an incomplete task should mark it as complete."""
        task = Task(id=1, title="Task", completed=False)
        toggled, new_list = ToggleTaskStatus(1, [task])

        assert toggled.completed is True
        assert new_list[0].completed is True

    def test_toggle_complete_to_incomplete(self):
        """Toggling a complete task should mark it as incomplete."""
        task = Task(id=1, title="Task", completed=True)
        toggled, new_list = ToggleTaskStatus(1, [task])

        assert toggled.completed is False
        assert new_list[0].completed is False

    def test_toggle_nonexistent_task(self):
        """Toggling a nonexistent task should return None."""
        task = Task(id=1, title="Task")
        toggled, new_list = ToggleTaskStatus(999, [task])

        assert toggled is None
        assert new_list[0].completed is False

    def test_preserves_other_fields(self):
        """Toggling should not change title or description."""
        task = Task(id=1, title="Task", description="Desc", completed=False)
        toggled, _ = ToggleTaskStatus(1, [task])

        assert toggled.title == "Task"
        assert toggled.description == "Desc"

    def test_double_toggle_returns_to_original(self):
        """Toggling twice should return to the original state."""
        task = Task(id=1, title="Task", completed=False)
        _, list1 = ToggleTaskStatus(1, [task])
        _, list2 = ToggleTaskStatus(1, list1)

        assert list2[0].completed is False
