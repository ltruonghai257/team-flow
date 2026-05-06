# Requirements: TeamFlow v2.4

**Milestone:** v2.4 — Professional Role-Aware Dashboard
**Created:** 2026-05-06
**Status:** Active

---

## Milestone Requirements

### Dashboard UI & Layout (DASH)

-   [ ] **DASH-01**: User sees a professional dashboard layout with visual hierarchy, clear section groupings, and data visualizations instead of raw-number-only stat cards
-   [ ] **DASH-02**: Dashboard renders role-appropriate sections based on the logged-in user's role without exposing supervisor-only panels to members
-   [ ] **DASH-03**: Dashboard is responsive on mobile with the same role-conditional section structure as desktop

### My Tasks & Deadlines (TASKS)

-   [ ] **TASKS-01**: User sees their own assigned tasks sorted by urgency (overdue first, then ascending due date) on the dashboard
-   [ ] **TASKS-02**: Overdue tasks are visually flagged in red; tasks due within 48 hours are highlighted as due soon
-   [ ] **TASKS-03**: User can navigate from a dashboard task card directly to the full task view at `/tasks`

### Team Health Panel (HEALTH)

-   [ ] **HEALTH-01**: Supervisor, assistant manager, and manager see each team member's workload status (overloaded / healthy / underloaded) on the dashboard
-   [ ] **HEALTH-02**: At-risk members (overdue tasks or high active-task load) are visually distinguished from healthy members in the team health panel
-   [ ] **HEALTH-03**: Supervisor/manager can navigate to the full performance page from the team health panel

### KPI Summary Strip (KPI)

-   [ ] **KPI-01**: Supervisor, assistant manager, and manager see the team's average KPI score, task completion rate, and needs-attention count on the dashboard
-   [ ] **KPI-02**: Members flagged as needing attention (KPI score < 70) are surfaced as a count or compact list in the KPI strip
-   [ ] **KPI-03**: Dashboard KPI summary links to `/performance` for full drill-down

### Activity Feed (FEED)

-   [ ] **FEED-01**: All roles see a scoped activity feed of recent standup posts on the dashboard
-   [ ] **FEED-02**: Activity feed is scoped to the user's visibility rules (member sees own sub-team, supervisor sees their scope, manager sees all)
-   [ ] **FEED-03**: Activity items show author name, post summary, and relative time; clicking links to `/updates`

### Backend API (API)

-   [ ] **API-01**: `/api/dashboard/` returns role-aware data in one call: `my_tasks`, `team_health` (supervisor+), `kpi_summary` (supervisor+), `recent_activity`
-   [ ] **API-02**: `my_tasks` returns the current user's assigned tasks sorted by urgency with overdue and due-soon flags
-   [ ] **API-03**: `team_health` returns per-member workload status derived from existing performance data; only present for supervisor / assistant manager / manager roles
-   [ ] **API-04**: `kpi_summary` returns avg score, completion rate, and needs-attention member list; only present for supervisor / assistant manager / manager roles
-   [ ] **API-05**: `recent_activity` returns the 5 most recent standup posts scoped to the user's visibility rules

---

## Future Requirements (Deferred)

-   Real-time dashboard refresh (WebSocket push instead of on-load fetch)
-   Pinnable or customizable dashboard sections per user
-   Dashboard widgets for projects without milestones
-   Embedded mini-Gantt or sprint burndown on the dashboard

---

## Out of Scope

| Item                                 | Reason                                                             |
| ------------------------------------ | ------------------------------------------------------------------ |
| New `/dashboard` route               | Dashboard stays at `/`; no route change needed                     |
| New database tables                  | All data derived from existing Task, User, StandupPost, KPI models |
| Dashboard for unauthenticated users  | Dashboard requires login; no public variant                        |
| Full performance charts on dashboard | KPI strip links to `/performance` for charts; no duplication       |

---

## Traceability

| REQ-ID    | Phase    | Notes                                   |
| --------- | -------- | --------------------------------------- |
| API-01    | Phase 31 | Role-aware dashboard endpoint           |
| API-02    | Phase 31 | My tasks payload                        |
| API-03    | Phase 31 | Team health payload                     |
| API-04    | Phase 31 | KPI summary payload                     |
| API-05    | Phase 31 | Activity feed payload                   |
| DASH-01   | Phase 32 | Professional UI layout                  |
| DASH-02   | Phase 32 | Role-conditional section rendering      |
| DASH-03   | Phase 32 | Mobile responsiveness                   |
| TASKS-01  | Phase 32 | My tasks sorted by urgency              |
| TASKS-02  | Phase 32 | Overdue/due-soon visual flags           |
| TASKS-03  | Phase 32 | Navigate to /tasks from dashboard       |
| HEALTH-01 | Phase 32 | Team health panel (supervisor+)         |
| HEALTH-02 | Phase 32 | At-risk member highlighting             |
| HEALTH-03 | Phase 32 | Link to /performance from health panel  |
| KPI-01    | Phase 32 | KPI summary strip (supervisor+)         |
| KPI-02    | Phase 32 | Needs-attention count/list              |
| KPI-03    | Phase 32 | Link to /performance KPI view           |
| FEED-01   | Phase 32 | Activity feed for all roles             |
| FEED-02   | Phase 32 | Visibility-scoped feed                  |
| FEED-03   | Phase 32 | Author, summary, time, link to /updates |
