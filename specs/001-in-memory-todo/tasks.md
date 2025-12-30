---

description: "Task list for in-memory console Todo application"
---

# Tasks: In-Memory Console Todo Application

**Input**: Design documents from `/specs/001-in-memory-todo/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/skills.md

**Tests**: Tests are OPTIONAL for this feature - not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per implementation plan in `src/`, `src/models/`, `src/skills/`, `src/cli/`, `tests/unit/`, `tests/integration/`
- [x] T002 [P] Create Task dataclass in `src/models/task.py` with id, title, description, completed fields
- [x] T003 [P] Create empty `__init__.py` files in `src/models/`, `src/skills/`, `src/cli/`, `tests/unit/`, `tests/integration/`

**Checkpoint**: Project structure ready - foundational phase can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement AddTask skill in `src/skills/task_skills.py` per contract in `contracts/skills.md`
- [x] T005 [P] Implement GetTasks skill in `src/skills/task_skills.py` per contract
- [x] T006 [P] Implement UpdateTask skill in `src/skills/task_skills.py` per contract
- [x] T007 [P] Implement DeleteTask skill in `src/skills/task_skills.py` per contract
- [x] T008 [P] Implement ToggleTaskStatus skill in `src/skills/task_skills.py` per contract
- [x] T009 [P] Create unit tests for all skills in `tests/unit/test_skills.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add New Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks with title and optional description

**Independent Test**: Run application, select "Add task", verify task appears in list with correct ID, title, description, and incomplete status

- [x] T010 [P] [US1] Implement CLI menu display function in `src/cli/todo_menu.py`
- [x] T011 [P] [US1] Implement task input collector in `src/cli/todo_menu.py`
- [x] T012 [US1] Implement menu option 1 (Add Task) handler in `src/cli/todo_menu.py`
- [x] T013 [US1] Integrate AddTask skill with CLI input in `src/cli/todo_menu.py`
- [x] T014 [US1] Create integration test for adding tasks in `tests/integration/test_cli.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can see all tasks with their completion status

**Independent Test**: Add multiple tasks (some completed), run "View tasks", verify all tasks display with correct details

- [x] T015 [P] [US2] Implement GetTasks skill integration in `src/cli/todo_menu.py`
- [x] T016 [US2] Implement CLI task display formatter in `src/cli/todo_menu.py`
- [x] T017 [US2] Implement menu option 2 (View Tasks) handler in `src/cli/todo_menu.py`
- [x] T018 [US2] Create integration test for viewing tasks in `tests/integration/test_cli.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Existing Tasks (Priority: P1)

**Goal**: Users can modify task title and/or description by ID

**Independent Test**: Add a task, update its title/description, verify changes applied and ID unchanged

- [x] T019 [P] [US3] Implement task ID input collector in `src/cli/todo_menu.py`
- [x] T020 [P] [US3] Implement update input collector in `src/cli/todo_menu.py`
- [x] T021 [US3] Implement UpdateTask skill integration in `src/cli/todo_menu.py`
- [x] T022 [US3] Implement menu option 3 (Update Task) handler in `src/cli/todo_menu.py`
- [x] T023 [US3] Create integration test for updating tasks in `tests/integration/test_cli.py`

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P1)

**Goal**: Users can remove tasks by ID

**Independent Test**: Add multiple tasks, delete one, verify it no longer appears in list

- [x] T024 [P] [US4] Implement DeleteTask skill integration in `src/cli/todo_menu.py`
- [x] T025 [US4] Implement menu option 4 (Delete Task) handler in `src/cli/todo_menu.py`
- [x] T026 [US4] Create integration test for deleting tasks in `tests/integration/test_cli.py`

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Toggle Task Status (Priority: P1)

**Goal**: Users can mark tasks as complete or incomplete

**Independent Test**: Add tasks, toggle completion, verify status changes in both directions

- [x] T027 [P] [US5] Implement ToggleTaskStatus skill integration in `src/cli/todo_menu.py`
- [x] T028 [US5] Implement menu option 5 (Toggle Status) handler in `src/cli/todo_menu.py`
- [x] T029 [US5] Create integration test for toggling status in `tests/integration/test_cli.py`

**Checkpoint**: At this point, ALL user stories should be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T030 [P] Implement application entry point in `src/app.py`
- [x] T031 [P] Implement main menu loop in `src/cli/todo_menu.py`
- [x] T032 [P] Implement exit option (menu option 6) in `src/cli/todo_menu.py`
- [x] T033 Add input validation for non-existent task IDs across all handlers in `src/cli/todo_menu.py`
- [x] T034 Add input validation for empty/whitespace titles in `src/cli/todo_menu.py`
- [x] T035 Run full integration test suite in `tests/integration/test_cli.py`
- [x] T036 Update quickstart.md if any running instructions changed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) since they all use the same skills layer
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (Add)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (View)**: Can start after Foundational - Can work with just AddTask skill
- **User Story 3 (Update)**: Can start after Foundational - Depends on skills layer
- **User Story 4 (Delete)**: Can start after Foundational - Depends on skills layer
- **User Story 5 (Toggle)**: Can start after Foundational - Depends on skills layer

All user stories are **independent** - they can be implemented in parallel after the Foundational phase.

### Within Each User Story

- Models before skills (already done in Setup/Foundational)
- Skills before CLI integration (already done in Foundational)
- CLI integration before testing
- Story complete before moving to next story or Polish

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel
- All tasks within a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all CLI tasks for User Story 1 together:
Task: "T010 [P] [US1] Implement CLI menu display function in src/cli/todo_menu.py"
Task: "T011 [P] [US1] Implement task input collector in src/cli/todo_menu.py"

# These can run in parallel since they modify different functions in the same file
# They depend only on the Foundational phase (skills) being complete
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test adding tasks independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Complete Phase 8: Polish
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
3. Stories complete and integrate independently

---

## Task Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 36 |
| Setup Phase | 3 tasks |
| Foundational Phase | 6 tasks |
| User Story 1 | 5 tasks |
| User Story 2 | 4 tasks |
| User Story 3 | 5 tasks |
| User Story 4 | 3 tasks |
| User Story 5 | 3 tasks |
| Polish Phase | 7 tasks |
| Parallelizable Tasks | 16 tasks |

### Independent Test Criteria per Story

| Story | Test | Expected Result |
|-------|------|-----------------|
| US1: Add | Run app, select "1", enter title/description | Task created with unique ID |
| US2: View | Run app with tasks, select "2" | All tasks displayed with status |
| US3: Update | Run app with task, select "3", enter ID and new title | Title updated, ID unchanged |
| US4: Delete | Run app with tasks, select "4", enter ID | Task removed from list |
| US5: Toggle | Run app with task, select "5", enter ID | Task status flips |

---

## Notes

- [P] tasks = different files or independent functions, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
