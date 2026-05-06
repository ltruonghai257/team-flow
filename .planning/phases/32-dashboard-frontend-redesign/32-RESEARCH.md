# Phase 32: Dashboard Frontend Redesign — Research

**Phase:** 32  
**Researched:** 2026-05-07  
**Status:** Complete

---

## 1. Phase Goal & Scope

Rebuild `frontend/src/routes/+page.svelte` into a professional role-aware dashboard consuming the Phase 31 `GET /api/dashboard/` endpoint. No backend changes. No route changes.

**Files to modify:**
- `frontend/src/routes/+page.svelte` — full rebuild
- `frontend/src/lib/apis/dashboard.ts` — add typed `get()` wrapper

---

## 2. API Contract (Phase 31 — Confirmed Live)

`GET /api/dashboard/` returns `DashboardPayload` with `response_model_exclude_none=True`:

```
DashboardPayload
  my_tasks: DashboardTaskItem[]          -- all roles, max 20, sorted by urgency
  team_health?: DashboardTeamHealthMember[]  -- absent for member role (key not present)
  kpi_summary?: DashboardKpiSummary       -- absent for member role (key not present)
  recent_activity: DashboardActivityItem[] -- all roles, max 5
```

### DashboardTaskItem
```ts
{ id, title, project_name: string|null, status: TaskStatus, priority: TaskPriority|null,
  due_date: string|null, is_overdue: bool, is_due_soon: bool }
```

### DashboardTeamHealthMember
```ts
{ user_id, full_name, avatar_url: string|null,
  status: "green"|"yellow"|"red",   // ← ACTUAL API VALUES
  active_tasks, completed_30d, overdue_tasks }
```

**⚠ IMPORTANT DISCREPANCY:** UI-SPEC lists status dot values as `"healthy"`, `"moderate"`, `"at_risk"`. The actual API (`schemas/dashboard.py:26`) returns `"green"`, `"yellow"`, `"red"`. Planner MUST use the actual API values in the status dot mapping.

### DashboardKpiSummary
```ts
{ avg_score: int, completion_rate: float,  // 0.0–1.0, NOT a percentage
  needs_attention_count: int }
```

**⚠ conversion needed:** `completion_rate` is `0.0–1.0`. Display as `Math.round(stats.kpi_summary.completion_rate * 100) + '%'`.

### DashboardActivityItem
```ts
{ post_id, author_id, author_name, created_at: datetime, field_values: dict }
```

---

## 3. Frontend API Client

**Current state** (`dashboard.ts` — 6 lines):
```ts
export const dashboard = {
    stats: () => request('/dashboard/'),
};
```

**Required change:** Add `get()` that calls the same endpoint but returns a typed `DashboardPayload`. The simplest approach — rename `stats` to `get` with a typed return, or add `get` alongside `stats` and update the page to use `get`.

**Decision:** Add `get` as the primary method (keep `stats` if there are any other callers — confirmed no other callers exist since only `+page.svelte` calls `dashboard.stats()`). Safe to rename.

---

## 4. Auth Store — Role Gate

`isManagerOrLeader` derived store (`frontend/src/lib/stores/auth.ts:68-74`):
```ts
export const isManagerOrLeader = derived(authStore,
  ($a) => $a.user?.role === 'manager' || $a.user?.role === 'supervisor'
         || $a.user?.role === 'assistant_manager'
);
```
Use `{#if $isManagerOrLeader}` to gate KPI strip and Team Health Panel. ✓

---

## 5. Reusable Utilities

All in `frontend/src/lib/utils.ts`:

| Utility | Signature | Use |
|---------|-----------|-----|
| `timeAgo(date)` | `(string|Date|null) → string` | Activity feed timestamps ("2h ago") |
| `priorityColors` | `Record<string,string>` | My Tasks priority badge |
| `statusColors` | `Record<string,string>` | My Tasks status badge (legacy enum values) |
| `statusLabels` | `Record<string,string>` | My Tasks status badge text |
| `initials(name)` | `(string) → string` | Team health member avatar initials |

**Note:** `statusColors` maps legacy enum keys: `todo`, `in_progress`, `review`, `done`, `blocked`. The `DashboardTaskItem.status` field is `TaskStatus` enum which uses these same values — no mapping needed.

---

## 6. Reusable Patterns (read before implementing)

### Avatar/initials (KpiScoreCard.svelte:82–97)
```html
{#if member.avatar_url}
  <img src={member.avatar_url} alt={member.full_name}
       class="w-10 h-10 rounded-full object-cover shrink-0" />
{:else}
  <div class="w-10 h-10 rounded-full bg-primary-700 flex items-center justify-center
              text-white font-semibold text-sm shrink-0">
    {initials(member.full_name)}
  </div>
{/if}
```

### Activity feed row (StandupCard.svelte:72–79)
```html
<div class="flex items-start gap-3">
  <div class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center
              text-xs font-semibold text-gray-300 flex-shrink-0">
    {(author_name).charAt(0).toUpperCase()}
  </div>
  <div class="flex-1 min-w-0">
    <p class="text-sm font-semibold text-gray-200">{author_name}</p>
    <p class="text-xs text-gray-500">{timeAgo(created_at)}</p>
  </div>
</div>
```

### Task list row (+page.svelte:103–119)
```html
<a href="/tasks" class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-800 transition-colors group">
```

### Panel header (+page.svelte:71–73)
```html
<div class="flex items-center gap-2 mb-4">
  <Icon class="text-primary-400" size={18} />
  <h2 class="font-semibold text-white">{heading}</h2>
</div>
```

### Empty state (+page.svelte:76,99)
```html
<p class="text-gray-500 text-sm py-4 text-center">{message}</p>
```

---

## 7. Activity Feed — field_values Rendering

`field_values` is a plain dict (`{ fieldName: string, ... }`). The design calls for "first non-empty field value, plain text, truncated to ~120 chars":

```ts
function activityPreview(fv: Record<string, string>): string {
  const first = Object.values(fv).find(v => v?.trim());
  return first ? first.substring(0, 120) : '';
}
```

---

## 8. Sub-Team Header — No Action Needed

`request.ts` automatically injects `X-SubTeam-ID` from `subTeamStore` on every API call. Dashboard visibility scoping is handled transparently. The frontend page does not need to pass any extra header.

---

## 9. Component Scoping Strategy

Per UI-SPEC ("No external component registry calls in this phase. All components are inline in `+page.svelte`"), keep all new markup inline in `+page.svelte`. The component is a single-owner page; extraction adds no reuse value for this phase.

---

## 10. TypeScript Types

Define lightweight TypeScript interfaces at the top of `+page.svelte` `<script>` block:

```ts
interface DashboardTaskItem {
  id: number; title: string; project_name: string | null;
  status: string; priority: string | null;
  due_date: string | null; is_overdue: boolean; is_due_soon: boolean;
}
interface DashboardTeamHealthMember {
  user_id: number; full_name: string; avatar_url: string | null;
  status: 'green' | 'yellow' | 'red';
  active_tasks: number; completed_30d: number; overdue_tasks: number;
}
interface DashboardKpiSummary {
  avg_score: number; completion_rate: number; needs_attention_count: number;
}
interface DashboardActivityItem {
  post_id: number; author_id: number; author_name: string;
  created_at: string; field_values: Record<string, string>;
}
interface DashboardPayload {
  my_tasks: DashboardTaskItem[];
  team_health?: DashboardTeamHealthMember[];
  kpi_summary?: DashboardKpiSummary;
  recent_activity: DashboardActivityItem[];
}
```

---

## 11. Wave Strategy

**Wave 1 (unblocked):** Update `dashboard.ts` — rename `stats` to `get`, add `DashboardPayload` import type or inline return type annotation.

**Wave 2 (depends on Wave 1):** Full `+page.svelte` rebuild:
1. TypeScript interfaces for all API types
2. Import `isManagerOrLeader` from auth store  
3. `onMount` calls `dashboard.get()` into typed `stats: DashboardPayload | null`
4. Supervisor layout: KPI strip → two-col row (My Tasks + Activity Feed) → Team Health
5. Member layout: two-col row (My Tasks + Activity Feed)
6. All empty states, loading spinner, footer CTA links

---

## 12. Requirements Traceability

| REQ-ID | How covered |
|--------|-------------|
| DASH-01 | Full layout rebuild with visual hierarchy, role-conditional sections |
| DASH-02 | `{#if $isManagerOrLeader}` gates KPI strip + Team Health |
| DASH-03 | `grid-cols-1 sm:grid-cols-3` for KPI strip; `grid-cols-1 lg:grid-cols-2` for panel row |
| TASKS-01 | API already sorts by urgency; render `my_tasks` as-is |
| TASKS-02 | `is_overdue → bg-red-950/40`, `is_due_soon → bg-yellow-950/40` row tints |
| TASKS-03 | Each task row is `<a href="/tasks">` |
| HEALTH-01 | Team health panel renders per-member card grid |
| HEALTH-02 | `status === "red"` → `border-red-500/50` on card |
| HEALTH-03 | "View full performance →" footer link to `/performance` |
| KPI-01 | 3-card KPI strip: avg_score, completion_rate, needs_attention_count |
| KPI-02 | `needs_attention_count` shown as number in third KPI card |
| KPI-03 | Needs Attention card links to `/performance` |
| FEED-01 | Activity feed section for all roles |
| FEED-02 | Scoped at backend via `X-SubTeam-ID` — no frontend work |
| FEED-03 | Author name + `timeAgo()` + field preview + footer link to `/updates` |

---

## RESEARCH COMPLETE
