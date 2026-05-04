---
phase: 5
slug: enhanced-ai-features
wave: 1
status: pending
created: 2026-04-23
---

# Phase 5 Plan: Enhanced AI Features

## Wave 1

### Plan 01: Backend AI Endpoints
**Wave:** 1
**Objective:** Add `POST /api/tasks/ai-breakdown` and `POST /api/ai/project-summary` endpoints with shared data-fetch helper and chat intent routing.

**Files modified:**
- `backend/app/schemas.py`
- `backend/app/routers/tasks.py`
- `backend/app/routers/ai.py`

**Tasks:**
1. **schemas.py** — Add `AiBreakdownRequest`, `AiBreakdownSubtask`, `AiBreakdownResponse`, `ProjectSummaryRequest`, `ProjectSummarySections`, `ProjectSummaryResponse`
2. **tasks.py** — Add `_coerce_ai_breakdown()` defensive parser and `POST /api/tasks/ai-breakdown` endpoint with rate limiter
3. **ai.py** — Add missing imports (`re`, `Project`, `MilestoneStatus`, `TaskStatus`), `_fetch_project_summary_data()` shared helper, `POST /api/ai/project-summary` endpoint
4. **ai.py** — Add chat intent routing in `send_message()`: `INTENT_PATTERNS`, `_extract_project_name()`, data-injection logic before LiteLLM call
5. **Validation** — Verify endpoints return correct schemas with curl or test script

---

## Wave 2

### Plan 02: Breakdown Tab UI
**Wave:** 2
**Depends on:** Plan 01 (ai-breakdown endpoint)
**Objective:** Add 4th "Breakdown" tab to AiTaskInput.svelte with SubtaskCard inline editing and batch-create flow.

**Files modified:**
- `frontend/src/lib/components/tasks/SubtaskCard.svelte` (new)
- `frontend/src/lib/components/tasks/AiTaskInput.svelte`
- `frontend/src/routes/tasks/+page.svelte`
- `frontend/src/lib/api.ts`

**Tasks:**
1. **api.ts** — Add `aiBreakdown(description, projectId)` to tasks object
2. **SubtaskCard.svelte** — New component: editable card with title, priority, hours, description, milestone select, delete button. Emits `update` and `remove` events.
3. **AiTaskInput.svelte** — Extend Mode type to include `'breakdown'`, add `projectList`/`milestoneList`/`userList` props, add Layers icon import, add Breakdown tab button, add breakdown tab UI (context selects + description textarea + "Break down with AI" button + subtask card list + "Create All" button + progress indicator + empty state)
4. **tasks/+page.svelte** — Pass `{projectList}`, `{milestoneList}`, `{userList}` props to `<AiTaskInput>`
5. **Validation** — Verify Breakdown tab renders, submits to API, cards are editable, Create All posts tasks sequentially

---

### Plan 03: Project Summary UI
**Wave:** 2
**Depends on:** Plan 01 (project-summary endpoint)
**Objective:** Add "Summarize" button and expandable summary panel to each project card in /projects.

**Files modified:**
- `frontend/src/routes/projects/+page.svelte`
- `frontend/src/lib/api.ts`

**Tasks:**
1. **api.ts** — Add `projectSummary(projectId)` to ai object
2. **projects/+page.svelte** — Add `summaryMap`, `loadingMap`, `expandedMap` state, `summarizeProject()` and `toggleSummary()` functions, Sparkles icon import, slide transition import
3. **projects/+page.svelte** — Add Summarize button to each project card footer (separator + button with loading/expanded states)
4. **projects/+page.svelte** — Add expandable summary panel with 4 sections (Milestone Progress, Recent Completions, Overdue, At-Risk) with slide transition
5. **Validation** — Verify Summarize button calls API, panel slides open, toggle works, button label changes per state
