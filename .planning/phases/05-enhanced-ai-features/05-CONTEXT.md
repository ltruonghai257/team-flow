# Phase 5: Enhanced AI Features - Context

**Gathered:** 2026-04-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Add two AI capabilities to TeamFlow:
1. **AI Task Breakdown** — User describes a feature/project, AI returns 3–8 subtask drafts (title, priority, estimated_hours, brief description). User reviews and edits inline before batch-creating.
2. **AI Project Status Summary** — Grounded natural-language summary of a project's real data (milestone progress, overdue tasks, recent completions, at-risk items). Accessible via project card button + AI chat intent.

No new project detail route. No new AI chat UI. Both features extend existing pages/components.

</domain>

<decisions>
## Implementation Decisions

### Task Breakdown — Integration Point
- **D-01:** "Break down with AI" lives as a **new 4th tab** in `AiTaskInput.svelte` (alongside existing Form / NLP / JSON tabs). Tab label: "Breakdown" with a `GitBranch` or `Layers` icon.
- **D-02:** Endpoint: `POST /api/tasks/ai-breakdown` — accepts `{"description": "...", "project_id": N}` and returns `{"subtasks": [{"title": "...", "priority": "...", "estimated_hours": N, "description": "..."}]}`.

### Task Breakdown — Form Inputs (before description)
- **D-03:** Before entering description, user selects: **project** (required) + **default milestone** (optional, "None" is valid) + **default assignee** (optional). These are the same dropdowns used in the normal task creation form — reuse the same `projectList`, `milestoneList`, `userList` state.
- **D-04:** User then types description and clicks "Break down" → shows loading spinner → renders subtask card list.

### Task Breakdown — Review UX
- **D-05:** Subtask list renders as **inline card list** inside the modal (same modal as normal task creation). Each card shows:
  - Editable `title` (text input)
  - Editable `priority` (select: low/medium/high/critical)
  - Editable `estimated_hours` (number input)
  - Editable `description` (1-2 line textarea)
  - **Per-card milestone dropdown** — pre-set to the default milestone chosen before breakdown, user can override each card individually
  - Delete button (removes that subtask from list)
- **D-06:** "Create All" button at the bottom batch-POSTs each subtask to `POST /api/tasks/` with `project_id` + `milestone_id` (per-card) + `assignee_id` (default). Shows success toast per batch completion.

### Task Breakdown — Subtask content
- **D-07:** AI returns: `title`, `priority` (low/medium/high/critical), `estimated_hours` (integer), `description` (1-2 sentences). No milestone or assignee from AI — those are user-controlled.
- **D-08:** Prompt instructs AI to return **3–8 subtasks** (prompt-guided, not fixed). Output must be valid JSON array — same defensive `_coerce_ai_parse`-style parsing pattern.

### Project Summary — Entry Point
- **D-09:** "Summarize" button appears **inline on each project card** in the existing `/projects` list view. No new `/projects/[id]` route in this phase.
- **D-10:** Click "Summarize" → button shows loading spinner → **expandable section slides open below the card** with the structured summary. Click again to collapse. Summary is cached in component state (not persisted — clears on page refresh).

### Project Summary — Structure
- **D-11:** Summary is **structured with 4 sections**, each a short paragraph (not bullets):
  - **Milestone Progress** — X of Y milestones complete, current active milestone
  - **Recent Completions** — tasks completed in the last 7 days
  - **Overdue** — count and names of overdue tasks
  - **At-Risk** — tasks due within 48h that are not done
- **D-12:** Backend fetches real project data (milestones, tasks, completion dates, due dates) and injects it into the LiteLLM prompt as structured context. AI writes the narrative — it does NOT invent data.
- **D-13:** Endpoint: `POST /api/ai/project-summary` — accepts `{"project_id": N}`, returns `{"summary": "...", "sections": {"milestone_progress": "...", "recent_completions": "...", "overdue": "...", "at_risk": "..."}}`.

### AI Chat Intent Routing
- **D-14:** In `send_message` handler (`POST /api/ai/conversations/{conv_id}/messages`), **before** calling LiteLLM, check the user message against intent patterns:
  - Regex patterns: `summarize project`, `project status`, `how is (?:project )?`, `project.*summary`
  - If matched: extract project name from message, look up project by case-insensitive partial match, fetch project data, prepend structured data block to user message as context.
- **D-15:** **Project name resolution**: case-insensitive partial match against `Project.name`. If 1 match → use it. If 0 or 2+ matches → skip data injection, AI responds with clarification ("I couldn't find a project named X. Available projects: [list]").
- **D-16:** When injecting project data into chat, prepend the same structured data block used by `project-summary` endpoint — reuse that helper function. No separate data-fetching path.

### Claude's Discretion
- Loading state treatment on the "Summarize" button (spinner vs skeleton vs disabled state)
- Exact regex patterns for chat intent matching
- Error handling for AI timeout or malformed subtask JSON (toast error, clear loading state)
- Whether to use `Sparkles` or another lucide icon for the Summarize button on project cards
- Assignee field label in breakdown tab ("Default assignee" vs "Assign all to")

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` § REQ-04a — AI Task Breakdown (acceptance criteria)
- `.planning/REQUIREMENTS.md` § REQ-04b — AI Project Status Summary (acceptance criteria)

### Existing AI Patterns
- `backend/app/routers/ai.py` — `litellm.acompletion()` pattern, `@limiter.limit("30/minute")`, `get_current_user` + `get_db` deps, system prompt structure, `AIMessageOut` response schema
- `backend/app/routers/tasks.py` — `/ai-parse` endpoint: `_coerce_ai_parse()` for defensive JSON parsing, `AiParseRequest`/`AiParseResponse` schemas — follow this pattern for breakdown endpoint

### Frontend AI Component
- `frontend/src/lib/components/tasks/AiTaskInput.svelte` — existing 3-tab component; add 4th "Breakdown" tab here
- `frontend/src/routes/tasks/+page.svelte` — task creation modal with `form` state, `projectList`/`milestoneList`/`userList` — reuse these lists in breakdown tab

### Frontend Project Page
- `frontend/src/routes/projects/+page.svelte` — add Summarize button + expandable section to each project card here

### Backend Data Models
- `backend/app/models.py` — `Project`, `Milestone` (start_date, due_date, status), `Task` (status, due_date, completed_at, assignee_id) — all fields needed for summary data injection

### Schemas
- `backend/app/schemas.py` — existing `TaskCreate`, `TaskOut`, `AiParseRequest`, `AiParseResponse` — extend here

### Prior Phase Context
- `.planning/phases/04-team-timeline-view/04-CONTEXT.md` — dark theme, component directory conventions
- `.planning/phases/03-supervisor-performance-dashboard/03-CONTEXT.md` — SQL aggregation patterns for task metrics (reuse for at-risk/overdue counts)

### Config
- `backend/app/config.py` — `settings.AI_MODEL` — never hardcode model names

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `litellm.acompletion(model=settings.AI_MODEL, messages=[...])` — exact call pattern in `ai.py:120`
- `@limiter.limit("30/minute")` + `request: Request` parameter — required on all AI endpoints
- `_coerce_ai_parse()` in `tasks.py` — defensive JSON parsing with enum validation; replicate for breakdown response
- `AiTaskInput.svelte` tab system — existing `mode` prop + tab button pattern; add "Breakdown" alongside NLP/JSON/Form
- `projectList`, `milestoneList`, `userList` already loaded in `tasks/+page.svelte` — pass to AiTaskInput as props
- `svelte-sonner` toast — existing success/error feedback pattern
- `btn-primary` CSS class — existing button style

### Established Patterns
- Backend router files in `backend/app/routers/` registered in `backend/app/main.py`
- New schemas added to `backend/app/schemas.py`
- Frontend components in `frontend/src/lib/components/{domain}/`
- API client methods added to `frontend/src/lib/api.ts`
- All routes use `get_current_user` dependency (no public endpoints)

### Integration Points
- `POST /api/tasks/ai-breakdown` → new endpoint in `tasks.py` (same router prefix `/api/tasks`)
- `POST /api/ai/project-summary` → new endpoint in `ai.py` (same router prefix `/api/ai`)
- Chat intent: modify `send_message()` in `ai.py` to add pre-call intent check
- `AiTaskInput.svelte` receives `projectList`/`milestoneList`/`userList` as props from parent `tasks/+page.svelte`

</code_context>

<specifics>
## Specific Ideas

- "Break down with AI" tab should follow the exact same tab button styling as existing NLP/JSON tabs in AiTaskInput.svelte (border-b-2, primary-500 active state)
- Batch-create should POST tasks sequentially (not parallel) to avoid overwhelming the DB with concurrent inserts, show a progress indicator ("Creating 1 of 5...")
- Project summary data injection: build a text block like "Project: X | Milestones: 2/4 complete | Overdue tasks: 3 (Task A due 2 days ago, ...) | Completed this week: 5 tasks | Due within 48h: Task B, Task C" — inject before user message

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-enhanced-ai-features*
*Context gathered: 2026-04-23*
