---
id: 0007
title: Global Project Cleanup Non-Official Artifacts
stage: green
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5
feature: 002-web-evolution
branch: main
user: waterprooffish99
command: /sp.implement
labels: ["cleanup", "git", "project-structure", "phase-ii"]
links:
  spec: specs/002-web-evolution/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - evolution_history/ (deleted)
  - history/prompts/002-persistence-evolution/ (deleted)
  - specs/ARCHIVED-001-console-tests/ (deleted)
  - specs/ARCHIVED-002-persistence-evolution/ (deleted)
  - history/prompts/002-web-evolution/0006-push-phase-ii-web-evolution-to-github.green.prompt.md (added)
tests:
  - None (cleanup operation only)
---

## Prompt

"Global Project Scrub: Remove All Non-Official Artifacts"

Instructions for Claude Code:

DELETED FOLDERS (Permanent Removal):

evolution_history/ (All archived content)

data/ (Old JSON persistence)

history/prompts/002-persistence-evolution/ (Mistaken persistence prompts)

specs/ARCHIVED-*/ (All archived specification folders)

DELETED FILES (Permanent Removal):

PHASE-II-COMPLETE.md (Persistence milestone)

persistence.py (Old persistence logic)

PRESERVE ONLY:

backend/ (Phase 2 official)

frontend/ (Phase 2 official)

history/prompts/001-in-memory-todo/ (Phase 1 history)

history/prompts/002-web-evolution/ (Phase 2 history)

specs/002-web-evolution/ (Phase 2 official specs)

.specify/ and root configuration files

GIT SYNC: After deleting, stage all changes and commit with: "build: global cleanup - removed all non-official artifacts".

## Response snapshot

Successfully executed global project cleanup:

**Deleted (26 files, 5,296 deletions):**
- evolution_history/ (9 files: archived Phase I/II code, PHASE-II-COMPLETE.md, persistence.py)
- history/prompts/002-persistence-evolution/ (3 files: mistaken persistence prompts)
- specs/ARCHIVED-001-console-tests/ (6 files: archived Phase I tests)
- specs/ARCHIVED-002-persistence-evolution/ (7 files: archived persistence specs)

**Preserved:**
- backend/ (Phase II FastAPI application)
- frontend/ (Phase II Next.js application)
- history/prompts/001-in-memory-todo/ (Phase I history)
- history/prompts/002-web-evolution/ (Phase II history + 1 new PHR)
- specs/002-web-evolution/ (Phase II official specification)
- .specify/, CLAUDE.md, PHASE-II-WEB-MIGRATION-COMPLETE.md

**Git Operations:**
- All deletions staged using git rm -rf
- Empty directories removed (evolution_history/, 002-persistence-evolution/)
- Committed: "build: global cleanup - removed all non-official artifacts" (6149352)
- Repository now contains only official Phase II artifacts

## Outcome

- ✅ Impact: Clean project structure with only official Phase II artifacts; removed 5,296 lines of archived/obsolete code
- 🧪 Tests: None (cleanup operation only)
- 📁 Files: 26 files deleted; project reduced to essential Phase II structure
- 🔁 Next prompts: Ready to push cleanup commit to GitHub
- 🧠 Reflection: Successful cleanup operation; repository now maintains clear separation between Phase I history and Phase II official code

## Evaluation notes (flywheel)

- Failure modes observed: None; all deletions executed successfully
- Graders run and results (PASS/FAIL): PASS (all preserved folders verified intact)
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Verify GitHub repository structure after push
