# Phase 5: Enhanced AI Features — Research

*Researched: 2026-04-23*
*Source files reviewed: ai.py, tasks.py, schemas.py, models.py, AiTaskInput.svelte, tasks/+page.svelte, projects/+page.svelte, api.ts*

---

## 1. Current AI Infrastructure

### Backend: LiteLLM call pattern (ai.py:120)
```python
response = await litellm.acompletion(
    model=settings.AI_MODEL,
    messages=history,
)
ai_content = response.choices[0].message.content
model_used = response.model
```
All AI endpoints use `@limiter.limit("30/minute")` decorator with `request: Request` as first param.

### Backend: Defensive JSON parsing (_coerce_ai_parse in tasks.py:36)
```python
def _coerce_ai_parse(data: dict) -> AiParseResponse:
    valid_status = {s.value for s in TaskStatus}
    valid_priority = {p.value for p in TaskPriority}
    # normalize fields, validate enums, parse dates, truncate strings
```
Code-fence stripping pattern (tasks.py:198–209): regex strips ```` ```json ... ``` ```` or extracts bare `{...}` if model wraps output.

### Important: ai-parse endpoint missing rate limiter (tasks.py:162)
The existing `/ai-parse` endpoint does NOT have `@limiter.limit("30/minute")` or `request: Request`. The new `/api/tasks/ai-breakdown` endpoint should add rate limiting to be consistent with all other AI endpoints.

### NLP parse system prompt pattern (tasks.py:20-33)
Prompt instructs model to return ONLY valid JSON, no markdown, no prose. Uses `temperature=0.2` for deterministic output. Injection of `{today}` for date context.

---

## 2. New Backend Endpoints

### 2a. POST /api/tasks/ai-breakdown (in tasks.py)

**New schemas needed in schemas.py:**
```python
class AiBreakdownRequest(BaseModel):
    description: str
    project_id: int

class AiBreakdownSubtask(BaseModel):
    title: str
    priority: str        # low|medium|high|critical
    estimated_hours: int
    description: str

class AiBreakdownResponse(BaseModel):
    subtasks: List[AiBreakdownSubtask]
```

**System prompt pattern (follow _AI_PARSE_SYSTEM_PROMPT style):**
```
You are a task breakdown assistant. The user describes a feature or work item.
Decompose it into 3–8 concrete subtasks. Respond with ONLY a valid JSON array (no markdown, no prose):
[{"title":"...", "priority":"low|medium|high|critical", "estimated_hours": integer, "description":"1-2 sentences"}]
Return between 3 and 8 items. No code fences. No explanations.
```

**Defensive parsing — new `_coerce_ai_breakdown(data)` helper:**
- Strip code fences (reuse existing regex pattern from tasks.py:198)
- Parse JSON — expect array not object
- Validate each subtask: title required, priority in valid_priority set, estimated_hours must be int >= 0, description optional
- Drop invalid items, clamp to 3–8 range if needed

**Endpoint signature:**
```python
@router.post("/ai-breakdown", response_model=AiBreakdownResponse)
@limiter.limit("30/minute")
async def ai_breakdown(
    request: Request,
    payload: AiBreakdownRequest,
    _: User = Depends(get_current_user),
):
```

### 2b. POST /api/ai/project-summary (in ai.py)

**New schemas needed in schemas.py:**
```python
class ProjectSummaryRequest(BaseModel):
    project_id: int

class ProjectSummarySections(BaseModel):
    milestone_progress: str
    recent_completions: str
    overdue: str
    at_risk: str

class ProjectSummaryResponse(BaseModel):
    summary: str
    sections: ProjectSummarySections
```

**Shared data-fetch helper (async def _fetch_project_summary_data):**
Reused by both the endpoint AND the chat intent handler (D-16). Query pattern:
```python
from datetime import timedelta

async def _fetch_project_summary_data(db: AsyncSession, project_id: int) -> dict:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    seven_days_ago = now - timedelta(days=7)
    forty_eight_hours = now + timedelta(hours=48)

    # Project + milestones
    project = await db.get(Project, project_id)
    milestones_result = await db.execute(
        select(Milestone).where(Milestone.project_id == project_id)
    )
    milestones = milestones_result.scalars().all()
    total_milestones = len(milestones)
    completed_milestones = sum(1 for m in milestones if m.status == MilestoneStatus.completed)
    active_milestone = next((m.title for m in milestones if m.status == MilestoneStatus.in_progress), None)

    # Tasks queries
    tasks_result = await db.execute(
        select(Task).where(Task.project_id == project_id)
    )
    all_tasks = tasks_result.scalars().all()

    recently_completed = [t for t in all_tasks
                          if t.completed_at and t.completed_at >= seven_days_ago]
    overdue = [t for t in all_tasks
               if t.due_date and t.due_date < now
               and t.status not in (TaskStatus.done,)]
    at_risk = [t for t in all_tasks
               if t.due_date and now <= t.due_date <= forty_eight_hours
               and t.status not in (TaskStatus.done,)]

    return {
        "project_name": project.name,
        "milestones_total": total_milestones,
        "milestones_completed": completed_milestones,
        "active_milestone": active_milestone,
        "recently_completed": [t.title for t in recently_completed],
        "overdue": [{"title": t.title, "due": t.due_date.strftime("%Y-%m-%d")} for t in overdue],
        "at_risk": [{"title": t.title, "due": t.due_date.strftime("%Y-%m-%d")} for t in at_risk],
    }
```

**Prompt injection format (from CONTEXT.md specifics):**
```
Project: {name} | Milestones: {completed}/{total} complete{, active: {milestone} if exists} |
Overdue tasks: {count} ({title} due {date}, ...) | Completed this week: {count} tasks |
Due within 48h: {title}, {title}
```

**Missing import in ai.py:** `Project` and `MilestoneStatus` are NOT currently imported. ai.py currently imports only `AIConversation, AIMessage, Task, Milestone, User`. Must add `Project, MilestoneStatus, TaskStatus`.

### 2c. Chat Intent Routing (modify send_message in ai.py:92)

**Import needed:** `import re` — already imported in tasks.py but NOT in ai.py.

**Intent pattern matching — insert BEFORE the LiteLLM call (after user message saved, before history built):**
```python
INTENT_PATTERNS = [
    r"summarize project",
    r"project status",
    r"how is (?:project )?(.+?)(?:\?|$)",
    r"project (.+?) summary",
]

def _extract_project_name(content: str) -> str | None:
    for pattern in INTENT_PATTERNS:
        m = re.search(pattern, content, re.IGNORECASE)
        if m:
            # Return named group if available, else try group(1), else return sentinel
            return m.group(1).strip() if m.lastindex else ""
    return None
```

**Resolution strategy (D-15):** Case-insensitive partial match on `Project.name`. If exactly 1 match → inject data. If 0 or 2+ → skip injection, let AI ask for clarification. Use `ilike` or Python-side filter after loading all projects (small dataset).

**Data injection:** Prepend the text block from `_fetch_project_summary_data()` as a system context block before the user message in `history`. Do not replace the user message — prepend as a separate system message or prefix the user message content.

---

## 3. Frontend Changes

### 3a. AiTaskInput.svelte — Add Breakdown Tab

**Current props (line 6–9):**
```svelte
export let onParsed: (fields: Record<string, any>) => void = () => {};
type Mode = 'form' | 'nlp' | 'json';
export let mode: Mode = 'form';
```

**New props to add:**
```svelte
export let projectList: any[] = [];
export let milestoneList: any[] = [];
export let userList: any[] = [];
```

**Type union extends to:** `'form' | 'nlp' | 'json' | 'breakdown'`

**New Lucide icon import:** `GitBranch` or `Layers` (per D-01). CONTEXT.md mentions `Layers` — use it.

**Breakdown tab local state:**
```svelte
let breakdownProject = '';
let breakdownMilestone = '';
let breakdownAssignee = '';
let breakdownDescription = '';
let breakdownLoading = false;
let subtasks: SubtaskDraft[] = [];
let batchProgress = { current: 0, total: 0, running: false };

type SubtaskDraft = {
  title: string;
  priority: string;
  estimated_hours: number;
  description: string;
  milestone_id: string;  // per-card override, pre-set to breakdownMilestone
};
```

**Breakdown function — calls new API:**
```typescript
async function breakdown() {
    if (!breakdownProject || !breakdownDescription.trim()) return;
    breakdownLoading = true;
    try {
        const result = await tasksApi.aiBreakdown(breakdownDescription, Number(breakdownProject));
        subtasks = result.subtasks.map(s => ({
            ...s,
            milestone_id: breakdownMilestone
        }));
    } catch (e: any) {
        toast.error('AI breakdown failed — please try again');
    } finally {
        breakdownLoading = false;
    }
}
```

**Batch create — sequential POSTs (D-06, CONTEXT specifics):**
```typescript
async function createAll() {
    batchProgress = { current: 0, total: subtasks.length, running: true };
    let successCount = 0;
    for (let i = 0; i < subtasks.length; i++) {
        batchProgress.current = i + 1;
        try {
            await tasksApi.create({
                title: subtasks[i].title,
                description: subtasks[i].description,
                priority: subtasks[i].priority,
                estimated_hours: subtasks[i].estimated_hours || null,
                project_id: Number(breakdownProject),
                milestone_id: subtasks[i].milestone_id ? Number(subtasks[i].milestone_id) : null,
                assignee_id: breakdownAssignee ? Number(breakdownAssignee) : null,
            });
            successCount++;
        } catch {
            // continue on individual failure
        }
    }
    batchProgress = { current: 0, total: 0, running: false };
    if (successCount < subtasks.length) {
        toast.error("Some tasks couldn't be created — check project settings");
    } else {
        toast.success(`Created ${successCount} tasks successfully`);
    }
    subtasks = [];
    // Reset inputs
    breakdownDescription = '';
}
```

**tasks/+page.svelte changes — pass lists as props:**
```svelte
<AiTaskInput 
    bind:mode={aiMode} 
    onParsed={applyParsed}
    {projectList}
    {milestoneList}
    {userList}
>
```
All three lists already loaded in `loadAll()` — no new API calls needed.

### 3b. SubtaskCard.svelte — New Component

**Location:** `frontend/src/lib/components/tasks/SubtaskCard.svelte`

**Props and events:**
```svelte
export let subtask: { title: string; priority: string; estimated_hours: number; description: string; milestone_id: string };
export let milestoneList: any[] = [];
import { createEventDispatcher } from 'svelte';
const dispatch = createEventDispatcher();
// dispatch('update', updatedSubtask) on each field change
// dispatch('remove') on delete click
```

**Layout order per UI-SPEC:**
1. Title input (full width)
2. Priority select + Estimated hours input (flex row, gap-3)
3. Description textarea (rows="2")
4. Milestone select + Delete button (flex row, items-center)

### 3c. projects/+page.svelte — Summarize Button

**New state variables:**
```svelte
let summaryMap: Record<number, { summary: string; sections: any } | null> = {};
let loadingMap: Record<number, boolean> = {};
let expandedMap: Record<number, boolean> = {};
```

**Summarize function:**
```typescript
async function summarizeProject(projectId: number) {
    loadingMap[projectId] = true;
    loadingMap = loadingMap; // trigger reactivity
    try {
        const result = await ai.projectSummary(projectId);
        summaryMap[projectId] = result;
        expandedMap[projectId] = true;
    } catch {
        toast.error("Couldn't summarize project — please try again");
    } finally {
        loadingMap[projectId] = false;
        loadingMap = loadingMap;
    }
}

function toggleSummary(projectId: number) {
    expandedMap[projectId] = !expandedMap[projectId];
    expandedMap = expandedMap;
}
```

**Import additions:** `Sparkles` from lucide-svelte, `slide` from `svelte/transition`, `ai` from `$lib/api`.

### 3d. api.ts — New Methods

```typescript
// In tasks object:
aiBreakdown: (description: string, projectId: number) =>
    request('/tasks/ai-breakdown', {
        method: 'POST',
        body: JSON.stringify({ description, project_id: projectId })
    }),

// In ai object:
projectSummary: (projectId: number) =>
    request('/ai/project-summary', {
        method: 'POST',
        body: JSON.stringify({ project_id: projectId })
    }),
```

---

## 4. No Schema Migration Required

Phase 5 adds NO new database models. All new endpoints operate on existing `Project`, `Milestone`, `Task`, and `User` tables. No Alembic migration needed.

---

## 5. Milestone Filtering Note (Claude's Discretion)

The `milestoneList` passed to `AiTaskInput` from `tasks/+page.svelte` contains ALL milestones for ALL projects. When the user selects a project in the breakdown tab, the milestone dropdown ideally filters to show only that project's milestones. This filtering should be reactive:
```svelte
$: filteredMilestones = breakdownProject
    ? milestoneList.filter(m => m.project_id === Number(breakdownProject))
    : milestoneList;
```

---

## 6. Plan Structure Recommendation

Phase 5 work separates cleanly into 3 plans:

| Plan | Wave | Scope |
|------|------|-------|
| Plan 01: Backend AI Endpoints | 1 | schemas.py additions, tasks.py ai-breakdown endpoint, ai.py project-summary endpoint + chat intent routing |
| Plan 02: Breakdown Tab UI | 2 | SubtaskCard.svelte (new), AiTaskInput.svelte (4th tab), tasks/+page.svelte (pass props + milestone_id in form), api.ts additions |
| Plan 03: Project Summary UI | 2 (parallel with Plan 02) | projects/+page.svelte (summarize button + expandable panel), api.ts (ai.projectSummary) |

Plans 02 and 03 can run in parallel (wave 2) after Plan 01 (wave 1) completes. Plan 02 depends on the aiBreakdown API; Plan 03 depends on the projectSummary API.

---

## 7. Validation Architecture

### Key Integration Points to Verify

1. `POST /api/tasks/ai-breakdown` — returns valid `AiBreakdownResponse` with `subtasks` array, each item has `title`, `priority`, `estimated_hours`, `description`
2. `POST /api/ai/project-summary` — returns `summary` string + `sections` with 4 keys
3. Chat intent: message "summarize project TeamFlow" → project data injected into LiteLLM context
4. Batch-create: 5 subtasks POST sequentially, all use correct `project_id` and `milestone_id`
5. Summarize toggle: cached summary shown/hidden on click without API call

### Rate Limiting Consistency
- `/api/tasks/ai-breakdown`: must have `@limiter.limit("30/minute")` + `request: Request`
- `/api/ai/project-summary`: must have `@limiter.limit("30/minute")` + `request: Request`
- Note: existing `/ai-parse` endpoint is missing these — not in scope to fix, but document

### Auth
All new endpoints use `Depends(get_current_user)`. The project-summary endpoint should also verify the project exists (404 if not).

## RESEARCH COMPLETE
