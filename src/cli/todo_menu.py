"""CLI menu orchestrator for the in-memory Todo application.

This module handles all user interaction, input validation, and delegates
to the skills layer for business logic. It follows the architecture
specified in /specs/001-in-memory-todo/plan.md

CLI as Orchestrator Principle:
- Display menus and collect user input
- Validate basic input (non-empty titles, valid IDs)
- Delegate business logic to skills layer
- Display results to user
"""

import sys
from typing import List, Optional

from src.models.task import Task
from src.skills.task_skills import (
    AddTask,
    GetTasks,
    UpdateTask,
    DeleteTask,
    ToggleTaskStatus
)


def display_menu() -> None:
    """Display the main menu options to the user."""
    print("\n=== Todo Application ===")
    print("1. Add a new task")
    print("2. View all tasks")
    print("3. Update a task")
    print("4. Delete a task")
    print("5. Toggle task completion")
    print("6. Exit")


def get_menu_choice() -> int:
    """Get and validate the user's menu choice.

    Returns:
        int: Valid menu choice (1-6)

    Raises:
        ValueError: If input is not a valid integer in range.
    """
    while True:
        try:
            choice = int(input("\nEnter your choice (1-6): ").strip())
            if 1 <= choice <= 6:
                return choice
            else:
                print("Please enter a number between 1 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def collect_task_input() -> tuple[str, Optional[str]]:
    """Collect task title and optional description from user.

    Returns:
        tuple: (title, description)
        - title: Non-empty task title
        - description: Optional description (None if empty)
    """
    # Collect title with validation
    while True:
        title = input("Enter task title: ").strip()
        if title:
            break
        print("Title cannot be empty. Please try again.")

    # Collect optional description
    description = input("Enter description (optional): ").strip()
    if not description:
        description = None

    return title, description


def collect_task_id(prompt: str) -> int:
    """Collect and validate a task ID from user.

    Args:
        prompt: Custom prompt message for the input.

    Returns:
        int: Valid task ID.

    Raises:
        ValueError: If input is not a valid integer.
    """
    while True:
        try:
            task_id = int(input(f"\n{prompt}").strip())
            if task_id > 0:
                return task_id
            else:
                print("Task ID must be a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def collect_update_input() -> tuple[Optional[str], Optional[str]]:
    """Collect optional update fields from user.

    Returns:
        tuple: (new_title, new_description)
        - new_title: New title or None to keep current
        - new_description: New description or None to keep current
    """
    new_title = input("Enter new title (leave empty to keep current): ").strip()
    if not new_title:
        new_title = None

    new_description = input("Enter new description (leave empty to keep current): ").strip()
    if not new_description:
        new_description = None

    return new_title, new_description


def display_tasks(tasks: List[Task]) -> None:
    """Display all tasks in a formatted way.

    Args:
        tasks: List of Task objects to display.
    """
    if not tasks:
        print("\nNo tasks yet.")
        return

    print("\n=== Tasks ===")
    for task in tasks:
        # Status indicator
        status = "[X]" if task.completed else "[ ]"
        print(f"{task.id}. {status} {task.title}")

        # Show description if present
        if task.description:
            print(f"   Description: {task.description}")


def handle_add_task(tasks: List[Task], next_id: int) -> tuple[List[Task], int]:
    """Handle the Add Task menu option.

    Args:
        tasks: Current list of tasks.
        next_id: Next available task ID.

    Returns:
        tuple: (updated_tasks, updated_next_id)
    """
    title, description = collect_task_input()

    # Call the AddTask skill
    new_task, updated_tasks, updated_next_id = AddTask(
        title=title,
        description=description,
        tasks=tasks,
        next_id=next_id
    )

    print(f"Task added successfully! (ID: {new_task.id})")
    return updated_tasks, updated_next_id


def handle_view_tasks(tasks: List[Task]) -> None:
    """Handle the View Tasks menu option.

    Args:
        tasks: Current list of tasks.
    """
    all_tasks = GetTasks(tasks)
    display_tasks(all_tasks)


def handle_update_task(tasks: List[Task]) -> tuple[List[Task], bool]:
    """Handle the Update Task menu option.

    Args:
        tasks: Current list of tasks.

    Returns:
        tuple: (updated_tasks, was_updated)
    """
    if not tasks:
        print("No tasks to update.")
        return tasks, False

    # Get task ID
    task_id = collect_task_id("Enter task ID to update: ")

    # Verify task exists
    all_tasks = GetTasks(tasks)
    task_ids = [t.id for t in all_tasks]
    if task_id not in task_ids:
        print(f"Task with ID {task_id} not found.")
        return tasks, False

    # Collect new values
    new_title, new_description = collect_update_input()

    # Call UpdateTask skill
    updated_task, updated_tasks = UpdateTask(
        task_id=task_id,
        title=new_title,
        description=new_description,
        tasks=tasks
    )

    if updated_task:
        print("Task updated successfully!")
        return updated_tasks, True
    else:
        print("Failed to update task.")
        return tasks, False


def handle_delete_task(tasks: List[Task]) -> tuple[List[Task], bool]:
    """Handle the Delete Task menu option.

    Args:
        tasks: Current list of tasks.

    Returns:
        tuple: (updated_tasks, was_deleted)
    """
    if not tasks:
        print("No tasks to delete.")
        return tasks, False

    # Get task ID
    task_id = collect_task_id("Enter task ID to delete: ")

    # Call DeleteTask skill
    deleted, updated_tasks = DeleteTask(task_id=task_id, tasks=tasks)

    if deleted:
        print("Task deleted successfully!")
        return updated_tasks, True
    else:
        print(f"Task with ID {task_id} not found.")
        return tasks, False


def handle_toggle_task(tasks: List[Task]) -> tuple[List[Task], bool]:
    """Handle the Toggle Task Status menu option.

    Args:
        tasks: Current list of tasks.

    Returns:
        tuple: (updated_tasks, was_toggled)
    """
    if not tasks:
        print("No tasks to toggle.")
        return tasks, False

    # Get task ID
    task_id = collect_task_id("Enter task ID to toggle: ")

    # Call ToggleTaskStatus skill
    toggled_task, updated_tasks = ToggleTaskStatus(task_id=task_id, tasks=tasks)

    if toggled_task:
        status = "complete" if toggled_task.completed else "incomplete"
        print(f"Task marked as {status}!")
        return updated_tasks, True
    else:
        print(f"Task with ID {task_id} not found.")
        return tasks, False


def run_menu_loop() -> None:
    """Run the main menu loop.

    This function initializes the in-memory state and processes
    user input until they choose to exit.
    """
    # Initialize in-memory state
    tasks: List[Task] = []
    next_id: int = 1

    while True:
        # Display menu and get choice
        display_menu()
        choice = get_menu_choice()

        # Handle each menu option
        if choice == 1:
            # Add Task
            tasks, next_id = handle_add_task(tasks, next_id)
        elif choice == 2:
            # View Tasks
            handle_view_tasks(tasks)
        elif choice == 3:
            # Update Task
            tasks, _ = handle_update_task(tasks)
        elif choice == 4:
            # Delete Task
            tasks, _ = handle_delete_task(tasks)
        elif choice == 5:
            # Toggle Task Status
            tasks, _ = handle_toggle_task(tasks)
        elif choice == 6:
            # Exit
            print("\nGoodbye!")
            break
