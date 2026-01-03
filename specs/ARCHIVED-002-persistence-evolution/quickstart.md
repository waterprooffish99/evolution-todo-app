# Quickstart: Persistence Evolution Implementation

**Feature**: 002-persistence-evolution
**Audience**: Developers implementing Phase II
**Date**: 2026-01-01

## Overview

This guide walks you through implementing JSON persistence for the Phase I todo application. You'll add file storage while keeping all Phase I skills unchanged.

**Time Estimate**: 2-4 hours (including testing)

---

## Prerequisites

- [ ] Phase I implementation complete and tested (branch: `001-in-memory-todo`)
- [ ] All Phase I tests passing
- [ ] Python 3.13+ installed
- [ ] pytest installed (or virtual environment activated)
- [ ] Git branch `002-persistence-evolution` checked out

**Verify Prerequisites**:
```bash
# Check Python version
python3 --version  # Should be 3.13 or higher

# Verify Phase I tests pass
pytest tests/  # All tests should pass

# Confirm correct branch
git branch  # Should show * 002-persistence-evolution
```

---

## Step-by-Step Implementation

### Step 1: Create Data Directory Structure

**Goal**: Set up the directory for storing JSON files

**Commands**:
```bash
# Create data directory
mkdir -p data

# Add .gitignore to exclude user data
echo "data/
!data/.gitkeep" >> .gitignore

# Create .gitkeep to track directory in git
touch data/.gitkeep
```

**Verify**:
```bash
ls -la data/  # Should see .gitkeep
cat .gitignore  # Should include data/ exclusion
```

**Why**: User data shouldn't be committed to version control, but we need the directory structure in git.

---

### Step 2: Create Persistence Module

**Goal**: Implement the persistence layer

**File**: `src/persistence.py`

**Implementation Order**:
1. Import required modules (`json`, `os`, `pathlib`, `datetime`)
2. Define constants (`DATA_DIR`, `DATA_FILE`)
3. Implement `ensure_atomic_write()` (atomic file writing)
4. Implement `load_tasks()` (read and parse JSON)
5. Implement `handle_corrupted_file()` (error recovery)
6. Implement `save_tasks()` (serialize and save)
7. Implement `initialize_persistence()` (startup initialization)

**Key Functions** (see `contracts/persistence-api.md` for full signatures):
- `initialize_persistence()`: Called once at startup
- `save_tasks()`: Called after every mutation
- `load_tasks()`: Internal, called by initialize
- `handle_corrupted_file()`: Internal, called on JSON errors
- `ensure_atomic_write()`: Internal, implements atomic writes

**Code Template**:
```python
# src/persistence.py
import json
import os
from pathlib import Path
from datetime import datetime

# Constants
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_FILE = DATA_DIR / 'todo_data.json'

def ensure_atomic_write(data, filepath):
    """Write data atomically to prevent corruption"""
    # TODO: Implement write-then-rename strategy
    pass

def load_tasks():
    """Load tasks from JSON file"""
    # TODO: Implement file reading with error handling
    pass

def handle_corrupted_file(filepath):
    """Handle corrupted JSON with backup and recovery"""
    # TODO: Implement backup and user prompts
    pass

def save_tasks():
    """Save current task state to JSON file"""
    # TODO: Implement serialization and atomic write
    pass

def initialize_persistence():
    """Initialize persistence layer at startup"""
    # TODO: Implement directory creation, file loading, ID setup
    pass
```

**Reference**: See `research.md` for detailed implementation patterns and `contracts/persistence-api.md` for function contracts.

---

### Step 3: Integrate with Phase I Skills

**Goal**: Make persistence transparent to Phase I skills

**File**: `src/main.py` (or wherever your CLI logic lives)

**Changes Required**:

1. **Import persistence module**:
```python
from persistence import initialize_persistence, save_tasks
```

2. **Initialize at startup** (before menu loop):
```python
if __name__ == "__main__":
    initialize_persistence()  # Load existing data
    # ... rest of startup code
```

3. **Add save calls after mutations**:
```python
# Example: After AddTask
task = AddTask(title, description)
save_tasks()  # Persist immediately

# Example: After UpdateTask
UpdateTask(task_id, new_title, new_description)
save_tasks()  # Persist immediately

# Example: After DeleteTask
DeleteTask(task_id)
save_tasks()  # Persist immediately

# Example: After ToggleTaskStatus
ToggleTaskStatus(task_id)
save_tasks()  # Persist immediately
```

4. **No saves for read operations**:
```python
# Example: GetTasks (no save needed)
tasks = GetTasks()
display_tasks(tasks)  # Just display, don't save
```

**Why**: This keeps Phase I skills unchanged (they don't know about persistence). The CLI layer handles save calls.

---

### Step 4: Write Tests

**Goal**: Verify persistence works correctly

**Test Categories**:

**A. Unit Tests** (`tests/test_persistence.py`):
```python
import pytest
from src.persistence import (
    initialize_persistence,
    save_tasks,
    load_tasks,
    handle_corrupted_file
)

def test_initialize_creates_directory(tmp_path):
    """Test that initialize creates data directory"""
    # TODO: Implement

def test_save_tasks_writes_valid_json(tmp_path):
    """Test that save creates valid JSON file"""
    # TODO: Implement

def test_load_tasks_returns_empty_on_missing_file(tmp_path):
    """Test graceful handling of missing file"""
    # TODO: Implement

def test_load_tasks_handles_corrupted_json(tmp_path):
    """Test corruption recovery flow"""
    # TODO: Implement

# ... more tests (see contracts/persistence-api.md for full list)
```

**B. Integration Tests** (`tests/test_persistence_integration.py`):
```python
def test_add_task_persists_immediately():
    """Test that adding a task saves to file"""
    # TODO: Implement

def test_restart_loads_previous_session():
    """Test that restarting app loads previous tasks"""
    # TODO: Implement

def test_task_id_continuity_after_restart():
    """Test that IDs continue correctly after restart"""
    # TODO: Implement
```

**Run Tests**:
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_persistence.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**Success Criteria**:
- [ ] All new persistence tests pass
- [ ] All Phase I tests still pass (backward compatibility)
- [ ] Code coverage > 90% for persistence.py

---

### Step 5: Manual Testing

**Goal**: Verify real-world usage scenarios

**Test Scenario 1: Fresh Start**
```bash
# Delete any existing data
rm -rf data/todo_data.json

# Run application
python3 src/main.py

# Add a few tasks
# Exit application
# Verify data/todo_data.json exists and contains tasks
cat data/todo_data.json
```

**Expected Result**: JSON file created with tasks

**Test Scenario 2: Persistence Across Restarts**
```bash
# Start application (should load previous tasks)
python3 src/main.py

# Verify tasks from previous session are visible
# Add more tasks
# Toggle some task statuses
# Exit and restart again
# Verify all changes persisted
```

**Expected Result**: All changes preserved across restarts

**Test Scenario 3: Corruption Recovery**
```bash
# Corrupt the JSON file intentionally
echo "{invalid json" > data/todo_data.json

# Start application
python3 src/main.py

# Should see corruption error message
# Choose option to create fresh file
# Verify backup file created (todo_data.json.corrupt.*)
ls -la data/
```

**Expected Result**: Backup created, fresh file initialized, app continues

**Test Scenario 4: Task ID Continuity**
```bash
# Add 3 tasks (IDs: 1, 2, 3)
# Delete task 2
# Exit and restart
# Add a new task
# Verify new task has ID 4 (not 2)
```

**Expected Result**: IDs never reused, continue from max + 1

---

### Step 6: Verify Phase I Compatibility

**Goal**: Ensure Phase I skills remain unchanged

**Verification Checklist**:
- [ ] No changes to Phase I skill function signatures
- [ ] No changes to Phase I skill behavior (input/output unchanged)
- [ ] All Phase I tests pass without modification
- [ ] Phase I skills have no knowledge of persistence (no imports of persistence module)

**Run Phase I Test Suite**:
```bash
# Run original Phase I tests
pytest tests/test_skills.py -v

# All should pass without changes
```

**Code Review**:
- Inspect `src/skills.py` (or wherever Phase I skills are defined)
- Confirm no new imports, no file I/O code, no persistence logic
- Skills should still operate only on in-memory `tasks` list

---

## Common Issues & Solutions

### Issue 1: Permission Denied Error

**Symptom**: `PermissionError` when accessing `data/` directory

**Solution**:
```bash
# Fix directory permissions
chmod 755 data/
chmod 644 data/todo_data.json
```

### Issue 2: JSON File Not Created

**Symptom**: `data/todo_data.json` doesn't exist after running app

**Debug**:
- Check that `initialize_persistence()` is called at startup
- Verify `DATA_DIR.mkdir(parents=True, exist_ok=True)` is executed
- Add print statements to confirm execution flow

### Issue 3: Tests Fail with "File Not Found"

**Symptom**: Tests can't find data file

**Solution**: Use `tmp_path` fixture in tests to avoid polluting real data directory:
```python
def test_example(tmp_path, monkeypatch):
    # Override DATA_DIR to use temp directory
    monkeypatch.setattr('src.persistence.DATA_DIR', tmp_path)
    # ... test code
```

### Issue 4: Corrupted File Not Backed Up

**Symptom**: Corruption recovery doesn't create backup

**Debug**:
- Verify `handle_corrupted_file()` is called when `JSONDecodeError` occurs
- Check file permissions (need write access to create backup)
- Add logging to confirm backup creation

### Issue 5: Task IDs Reset After Restart

**Symptom**: New tasks after restart have low IDs (e.g., 1, 2)

**Debug**:
- Check `initialize_persistence()` sets `next_task_id` correctly
- Verify: `next_task_id = max(task['id'] for task in tasks) + 1`
- Ensure this runs AFTER loading tasks from file

---

## Performance Validation

### Load Time Test

**Goal**: Verify startup performance meets target (< 1s for 1,000 tasks)

**Test Script**:
```python
import time
import json
from pathlib import Path

# Create test file with 1,000 tasks
test_data = {
    'version': '1.0',
    'tasks': [
        {'id': i, 'title': f'Task {i}', 'description': '', 'completed': False}
        for i in range(1, 1001)
    ]
}

with open('data/todo_data.json', 'w') as f:
    json.dump(test_data, f)

# Measure load time
start = time.time()
from src.persistence import initialize_persistence
initialize_persistence()
elapsed = time.time() - start

print(f"Load time for 1,000 tasks: {elapsed:.3f}s")
assert elapsed < 1.0, f"Load time {elapsed}s exceeds 1s target"
```

### Save Time Test

**Goal**: Verify save performance meets target (< 100ms)

**Test Script**:
```python
import time
from src.persistence import save_tasks
from src.skills import AddTask

# Add some tasks
for i in range(100):
    AddTask(f'Task {i}', '')

# Measure save time
start = time.time()
save_tasks()
elapsed = time.time() - start

print(f"Save time for 100 tasks: {elapsed*1000:.1f}ms")
assert elapsed < 0.1, f"Save time {elapsed}s exceeds 100ms target"
```

---

## Completion Checklist

Before marking Phase II complete, verify:

- [ ] `src/persistence.py` implements all functions from contract
- [ ] `data/` directory structure created
- [ ] `.gitignore` excludes `data/` (except `.gitkeep`)
- [ ] Persistence integrated into CLI layer (save calls after mutations)
- [ ] Phase I skills unchanged (no imports, no file I/O)
- [ ] All Phase I tests pass without modification
- [ ] All Phase II persistence tests pass
- [ ] Code coverage > 90% for persistence module
- [ ] Manual testing scenarios completed successfully
- [ ] Performance targets met (load < 1s, save < 100ms)
- [ ] Error handling tested (corruption, permissions, disk full)
- [ ] Documentation updated (README, if applicable)

---

## Next Steps After Completion

**Phase II Complete**: JSON persistence working, all tests passing

**Phase III Options** (for future):
1. Add timestamps (created_at, updated_at) to tasks
2. Implement task filtering/search
3. Add tags or categories
4. Migrate to SQLite for better performance
5. Add cloud sync capabilities
6. Implement undo/redo functionality

**Immediate Next**:
- Create pull request for review
- Merge to main branch
- Tag release: `v0.2.0-persistence`

---

## Resources

- **Spec**: `specs/002-persistence-evolution/spec.md`
- **Research**: `specs/002-persistence-evolution/research.md`
- **Data Model**: `specs/002-persistence-evolution/data-model.md`
- **Contracts**: `specs/002-persistence-evolution/contracts/persistence-api.md`
- **Constitution**: `.specify/memory/constitution.md` (Amendment I)

**Python Documentation**:
- JSON module: https://docs.python.org/3/library/json.html
- os.replace(): https://docs.python.org/3/library/os.html#os.replace
- pathlib: https://docs.python.org/3/library/pathlib.html

**Testing**:
- pytest: https://docs.pytest.org/
- pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
- mocking: https://docs.python.org/3/library/unittest.mock.html

---

## Questions?

If you encounter issues not covered in this guide:
1. Check the contracts (`contracts/persistence-api.md`)
2. Review research decisions (`research.md`)
3. Verify constitution compliance (`.specify/memory/constitution.md`)
4. Consult Phase I implementation for patterns

**Happy coding!**
