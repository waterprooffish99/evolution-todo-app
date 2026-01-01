"""
Persistence Layer for Evolution Todo Application (Phase II)

This module handles loading and saving task data to/from data/todo_data.json
with error handling, atomic writes, and corruption recovery.

All functions are designed to be transparent to Phase I skills - the persistence
layer wraps the existing skills without modifying them.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import asdict

from src.models.task import Task

# Constants
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_FILE = DATA_DIR / 'todo_data.json'


def ensure_data_directory() -> None:
    """
    Create data directory if it doesn't exist.

    Side Effects:
        - Creates DATA_DIR directory (filesystem operation)

    Exceptions:
        - PermissionError: Cannot create directory (permissions issue)
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def ensure_atomic_write(data: Dict[str, Any], filepath: Path) -> None:
    """
    Write data to file atomically to prevent corruption.

    Strategy:
    1. Serialize data to JSON string with indentation
    2. Write to temporary file (filepath.tmp)
    3. Atomically rename temp to target (os.replace)

    Args:
        data: Dictionary to serialize and write
        filepath: Target file path

    Side Effects:
        - Writes temporary file (filepath.tmp)
        - Replaces target file atomically

    Exceptions:
        - OSError: Disk full, permission denied, filesystem error

    Guarantees:
        - Target file is either fully updated or unchanged
        - No partial writes (atomic rename ensures this)
    """
    tmp_path = str(filepath) + '.tmp'

    # Write to temporary file
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Atomic rename (POSIX + Windows guarantee)
    os.replace(tmp_path, filepath)


def load_tasks() -> List[Dict[str, Any]]:
    """
    Load tasks from JSON file.

    Returns:
        List of task dictionaries. Empty list if file doesn't exist.

    Side Effects:
        - None (read-only operation)

    Exceptions:
        - json.JSONDecodeError: File is corrupted (triggers recovery flow)
        - ValueError: Schema validation failed (treated as corruption)

    Postconditions:
        - Returned list contains only valid Task dictionaries
        - No duplicate task IDs in returned list
    """
    try:
        # Check if file exists
        if not DATA_FILE.exists():
            return []

        # Read and parse JSON
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate schema
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
        if 'version' not in data:
            raise ValueError("Missing version field")
        if 'tasks' not in data:
            raise ValueError("Missing tasks field")
        if not isinstance(data['tasks'], list):
            raise ValueError("tasks must be a list")

        return data['tasks']

    except FileNotFoundError:
        # First run, no file exists yet
        return []
    except (json.JSONDecodeError, ValueError) as e:
        # File is corrupted, trigger recovery
        return handle_corrupted_file(DATA_FILE)


def handle_corrupted_file(filepath: Path) -> List[Dict[str, Any]]:
    """
    Handle corrupted JSON file with user recovery options.

    Behavior:
    1. Backup corrupted file with timestamp
    2. Display error message to user
    3. Prompt for action: (1) Create fresh file or (2) Exit
    4. Execute user choice

    Args:
        filepath: Path to corrupted file

    Returns:
        Empty list if user chooses fresh start

    Side Effects:
        - Creates backup file (filesystem)
        - May create fresh empty JSON file
        - May exit application

    Exceptions:
        - PermissionError: Cannot create backup
        - SystemExit: User chose to exit (code 1)
    """
    # Create backup with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    backup_path = Path(str(filepath) + f'.corrupt.{timestamp}')

    # Backup the corrupted file
    if filepath.exists():
        filepath.rename(backup_path)

    # Display error to user
    print(f"\nERROR: {filepath} is corrupted (backed up to {backup_path.name})")
    print("\nOptions:")
    print("1. Create fresh empty file (you will lose corrupted data)")
    print("2. Exit and manually fix the backup file")

    # Get user choice
    while True:
        choice = input("\nChoose (1/2): ").strip()
        if choice == "1":
            print("\nFresh file will be created. Starting with empty task list.")
            return []
        elif choice == "2":
            print("\nExiting. Please fix the backup file manually.")
            sys.exit(1)
        else:
            print("Invalid choice. Please enter 1 or 2.")


def save_tasks(tasks: List[Task]) -> None:
    """
    Atomically save current task state to JSON file.

    Args:
        tasks: Current list of Task objects to save

    Behavior:
    1. Serialize current tasks list to JSON
    2. Write to temporary file
    3. Atomically rename to target file

    Side Effects:
        - Writes to filesystem (data/todo_data.json.tmp)
        - Replaces data/todo_data.json

    Exceptions:
        - PermissionError: Cannot write to data directory
        - OSError: Disk full, filesystem read-only

    Preconditions:
        - tasks list must be valid (not None)
        - All tasks must have required fields

    Postconditions:
        - data/todo_data.json reflects current tasks state
        - File contains valid JSON with correct schema version
    """
    # Ensure directory exists
    ensure_data_directory()

    # Convert Task objects to dictionaries
    task_dicts = [asdict(task) for task in tasks]

    # Create JSON structure with version
    data = {
        "version": "1.0",
        "tasks": task_dicts
    }

    # Write atomically
    ensure_atomic_write(data, DATA_FILE)


def initialize_persistence() -> tuple[List[Task], int]:
    """
    Initialize persistence layer, load existing data, setup in-memory state.

    Returns:
        tuple: (loaded_tasks, next_task_id)
            - loaded_tasks: List of Task objects loaded from file
            - next_task_id: Next available ID (max ID + 1 or 1 if empty)

    Behavior:
    1. Create data/ directory if missing
    2. Check for data/todo_data.json
    3. If file exists: Load and parse JSON
    4. If file missing: Create empty file
    5. If file corrupted: Backup and handle recovery
    6. Calculate next_task_id from loaded data

    Side Effects:
        - Creates data/ directory (filesystem)
        - Creates data/todo_data.json if missing
        - May create backup files if corruption detected

    Exceptions:
        - PermissionError: Cannot read/write data directory
        - OSError: Disk full or other filesystem error
        - SystemExit: User chose to exit during corruption recovery

    Postconditions:
        - tasks list is populated from file (or empty if no data)
        - next_task_id is set correctly (max ID + 1 or 1 if empty)
        - data/todo_data.json exists and is valid JSON
    """
    # Ensure directory exists
    ensure_data_directory()

    # Load task dictionaries from file
    task_dicts = load_tasks()

    # Convert dictionaries to Task objects
    tasks = [Task(**task_dict) for task_dict in task_dicts]

    # Calculate next_task_id
    if tasks:
        next_id = max(task.id for task in tasks) + 1
    else:
        next_id = 1

    # Create empty file if it doesn't exist
    if not DATA_FILE.exists():
        save_tasks(tasks)

    return tasks, next_id
