# Implementation Plan: In-Memory Console Todo

**Branch**: `001-in-memory-todo` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-in-memory-todo/spec.md`

## Summary

Implement a menu-driven console Todo application using Python 3.13+ with in-memory data storage. The application provides five core operations: Add, View, Update, Delete, and Toggle task status. Core business logic is implemented as reusable, deterministic skills independent of the CLI layer, following the spec-driven development methodology outlined in the constitution.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python Standard Library Only (no external dependencies)
**Storage**: In-memory dictionary/list data structure (session-scoped, no persistence)
**Testing**: pytest (for unit/integration tests)
**Target Platform**: Linux/Windows/macOS via Python interpreter
**Project Type**: Single project (console application)
**Performance Goals**: All operations complete within 1 second (SC-002)
**Constraints**: No file I/O, no external services, no database, no web interface
**Scale/Scope**: Single user, session-scoped, task count limited by memory

### MCP Readiness Constraint

All core skills defined in this phase must remain Model Context Protocol (MCP) ready.
This means each skill must:
- Be deterministic
- Accept explicit inputs and return explicit outputs
- Avoid direct user input/output
- Remain independently callable without CLI dependency

These constraints ensure that Phase I skills can be safely exposed to AI agents in later phases without refactoring.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven First | PASS | Feature spec at `specs/001-in-memory-todo/spec.md` created via `/sp.specify` |
| II. Reusable Intelligence | PASS | Skills (AddTask, GetTasks, UpdateTask, DeleteTask, ToggleTaskStatus) specified in FR-010 |
| III. Human-Readable Design | PASS | Clear naming, simple flows, docstrings required (FR-011) |
| IV. Clean Phase Boundaries | PASS | No web/database/AI logic - console only, in-memory only |

**Technical Guardrails Compliance**:
- Language: Python 3.13+ ✅
- Runtime: Console/CLI only ✅
- Persistence: In-memory only ✅
- No file system usage ✅
- No external services/databases ✅

**Gate Status**: ✅ PASS - All constitution requirements satisfied. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-in-memory-todo/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (minimal - all decisions specified)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── skills.md        # Skill contracts for reusable intelligence
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── skills/
│   └── task_skills.py   # Core reusable skills (AddTask, GetTasks, etc.)
├── cli/
│   └── todo_menu.py     # Menu-driven CLI orchestrator
├── models/
│   └── task.py          # Task data class
└── app.py               # Application entry point

tests/
├── unit/
│   └── test_skills.py   # Tests for core skills
└── integration/
    └── test_cli.py      # End-to-end CLI tests
```

**Structure Decision**: Single project structure with clear separation between skills (business logic) and CLI (orchestration). This enforces the "CLI as orchestrator" principle and ensures skills remain independently testable.

## Phase 0: Outline & Research

All technical decisions are already specified in the constitution and feature spec. No additional research required.

**Research Summary**: Not applicable - all technology choices explicitly defined in constitution:
- Python 3.13+ (explicit)
- In-memory storage (explicit)
- Console/CLI only (explicit)
- No external dependencies (explicit)

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for complete entity definitions and validation rules.

### Skills Contracts

See `contracts/skills.md` for detailed skill interfaces with inputs, outputs, and side effects.

### Quickstart Guide

See `quickstart.md` for instructions on running and testing the application.

### Agent Context Update

Agent context file updated via `.specify/scripts/bash/update-agent-context.sh`.

## Complexity Tracking

No constitution violations requiring justification. The implementation follows all constitution principles with no deviations.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | - | - |

---
*Plan created via `/sp.plan` command following spec-driven development methodology.*
