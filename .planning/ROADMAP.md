# Roadmap: TeamFlow

_Updated: 2026-04-24_

---

## Milestone 1 History: Production-Ready Team Management Platform

**Status:** Complete ✓ (Phases 1–11)
**Completed:** 2026-04-24

| Phase | Name                             | Requirements | Status |
| ----- | -------------------------------- | ------------ | ------ |
| 1     | Production Hardening             | REQ-01       | ✓ Done |
| 2     | RBAC & Role Model                | REQ-07       | ✓ Done |
| 3     | Supervisor Performance Dashboard | REQ-02       | ✓ Done |
| 4     | Team Timeline View               | REQ-03       | ✓ Done |
| 5     | Enhanced AI Features             | REQ-04       | ✓ Done |
| 6     | Mobile-Responsive UI             | REQ-06       | ✓ Done |
| 7     | Azure Deployment & CI/CD         | REQ-05       | ✓ Done |
| 8     | User Invite & Team Management    | —            | ✓ Done |
| 9     | Verification Docs (Phases 1–3)   | —            | ✓ Done |
| 10    | Verification Docs (Phases 4–5)   | —            | ✓ Done |
| 11    | Verification Docs (Phases 6–8)   | —            | ✓ Done |

---

## Milestone 2: Team Hierarchy, Sprints & Advanced Analytics

**Goal:** Transform TeamFlow from a single-team tool into a multi-team platform with sprint-driven project management, Trello-style customizable boards, and data-grounded KPI analytics.

**Definition of Done:** Admin can create sub-teams and assign supervisors; supervisors see only their sub-team's data (API-enforced); sprints exist within milestones; Kanban board columns driven from DB statuses; performance dashboard shows velocity, burndown, cycle time, throughput, and defect metrics; in-app reminders fire before sprint end and milestone due dates; all existing data migrated without loss.

---

## Phases

-   [ ] **Phase 12: Task Types** — Add task type field (feature/bug/task/improvement) to every task; visible on cards, filterable on board; backfill existing tasks to `task` type
-   [ ] **Phase 13: Multi-Team Hierarchy + Timeline Visibility** — Introduce SubTeam model, scope all data access by sub-team, enforce role-aware timeline visibility for members, supervisors, and admins
-   [ ] **Phase 14: Sprint Model** — Sprints as time-boxed iterations within milestones; tasks assigned to sprints; sprint board filters by sprint; sprint close flow
-   [ ] **Phase 15: Custom Kanban Statuses** — Migrate hardcoded enum to DB-driven statuses; supervisor-managed team-wide and per-project status sets; `is_done` flag replaces hardcoded done slug
-   [ ] **Phase 16: Advanced KPI Dashboard** — Velocity per sprint, burndown chart, cycle time by type, throughput by member, defect metrics and MTTR; all queries use `is_done` and task types
-   [ ] **Phase 17: Sprint & Release Reminders** — In-app notifications N days before sprint end and milestone due dates; configurable offset; deduplication via EventNotification rows

---

## Phase Details

### Phase 12: Task Types

**Goal**: Every task has a type (feature/bug/task/improvement) that is visible on the board and usable as a filter
**Depends on**: Nothing (fully isolated column addition)
**Requirements**: TYPE-01, TYPE-02, TYPE-03
**Success Criteria** (what must be TRUE):

1. User can set task type when creating or editing a task; type defaults to `task` if not selected
2. Task type is visible as an icon or badge on every Kanban card
3. User can filter the Kanban board to show only tasks of a specific type
4. All existing tasks show type `task` after migration with no null values
   **Plans**: TBD
   **UI hint**: yes

### Phase 13: Multi-Team Hierarchy + Timeline Visibility

**Goal**: The app is organized into sub-teams; every user, project, and task is scoped to a sub-team; the timeline shows only what each role is permitted to see
**Depends on**: Phase 12 (parallel is acceptable; 13 requires nothing from 12)
**Requirements**: TEAM-01, TEAM-02, TEAM-03, TEAM-04, TEAM-05, VIS-01, VIS-02, VIS-03
**Success Criteria** (what must be TRUE):

1. Admin can create a sub-team, assign a supervisor, rename it, and reassign its supervisor from the settings page
2. A supervisor's dashboard, performance page, and timeline show only their sub-team's members and projects — cross-team data is inaccessible even via direct API calls
3. A member sees only projects where they have at least one assigned task on the timeline
4. Admin can view all sub-teams, switch between them, and see org-wide aggregates on the dashboard
5. All existing users and projects are migrated to a default sub-team with zero data loss
   **Plans**: 5 plans

-   [ ] 13-01-PLAN.md — Database migration (SubTeam model, FK columns, default sub-team)
-   [ ] 13-02-PLAN.md — Backend sub-team scoping (get_sub_team dependency, SubTeam CRUD router)
-   [ ] 13-03-PLAN.md — Frontend sub-team switcher and team page extension
-   [ ] 13-04-PLAN.md — Timeline visibility and invite flow updates
-   [ ] 13-05-PLAN.md — Wave 0 test stubs and schema push
        **UI hint**: yes

### Phase 14: Sprint Model

**Goal**: Supervisors can create time-boxed sprints within milestones; team members can assign tasks to sprints; the board can be filtered to show a single sprint's work
**Depends on**: Phase 13 (sprint scoping requires sub-team context)
**Requirements**: SPRINT-01, SPRINT-02, SPRINT-03, SPRINT-04
**Success Criteria** (what must be TRUE):

1. Supervisor can create, edit, and close a sprint with a name, start date, and end date within a milestone
2. Task creation and edit forms include a sprint selector; selecting a sprint associates the task with that sprint
3. Sprint board view filters to tasks in the selected sprint; unassigned tasks are visible in a Backlog column
4. Closing a sprint prompts the user to move incomplete tasks to backlog or next sprint before closing
   **Plans**: TBD
   **UI hint**: yes

### Phase 15: Custom Kanban Statuses

**Goal**: Kanban columns are driven from database-stored statuses instead of hardcoded enum values; supervisors can create, reorder, and manage statuses; task completion is determined by the `is_done` flag
**Depends on**: Phase 14 (sprint burndown and `is_done` logic must be written correctly from the start, not retrofitted)
**Requirements**: STATUS-01, STATUS-02, STATUS-03, STATUS-04
**Success Criteria** (what must be TRUE):

1. Supervisor can create a custom status with a name and color, reorder statuses via drag-and-drop, and set one as the completion status (`is_done`)
2. Kanban board columns reflect the current DB-stored status list, not hardcoded values; changes take effect immediately without a deploy
3. A project can define its own status set; projects with no custom statuses inherit the team-wide defaults
4. All existing tasks are migrated from the enum to the new DB-backed statuses with zero data loss; task completion timestamps (`completed_at`) are preserved correctly
5. Moving a task to any status marked `is_done` sets its completion timestamp; moving it back clears the timestamp
   **Plans**: TBD
   **UI hint**: yes

### Phase 16: Advanced KPI Dashboard

**Goal**: The supervisor performance dashboard exposes data-grounded sprint and team metrics — velocity, burndown, cycle time, throughput, and defect metrics — all computed from real sprint and task type data
**Depends on**: Phase 13 (team scoping), Phase 14 (sprint data), Phase 15 (is_done flag and task types from Phase 12)
**Requirements**: KPI-01, KPI-02, KPI-03, KPI-04, KPI-05
**Success Criteria** (what must be TRUE):

1. Supervisor can view a velocity chart showing tasks completed per sprint per member over the last 6 sprints
2. Supervisor can view a burndown chart for the active sprint and any closed sprint, showing remaining tasks vs elapsed time
3. Performance dashboard shows average cycle time broken down by task type (feature/bug/task/improvement) over the last 3 months
4. Performance dashboard shows tasks completed per week per member grouped by type as a stacked bar chart over the last 8 weeks
5. Performance dashboard shows bugs reported vs bugs resolved per period, and MTTR per member for the last 30 days
   **Plans**: TBD
   **UI hint**: yes

### Phase 17: Sprint & Release Reminders

**Goal**: Team members and supervisors receive in-app notifications before sprint end dates and milestone due dates, with configurable lead time and no duplicate reminders
**Depends on**: Phase 13 (team membership for fanout), Phase 14 (sprint model for trigger events)
**Requirements**: REMIND-01, REMIND-02
**Success Criteria** (what must be TRUE):

1. All sprint participants receive an in-app notification N days before the sprint end date (default: 2 days); N is configurable per team by the supervisor or admin
2. Supervisor and admin receive an in-app notification N days before a milestone due date (default: 3 days); N is configurable per team
3. Reminders are not duplicated if the sprint or milestone date is unchanged; a reminder is re-created if the date is moved
4. Reminders persist across app restarts and Azure deploys (stored as EventNotification rows, not in-memory scheduler jobs)
   **Plans**: TBD

---

## Progress Table

| Phase                                          | Plans Complete | Status      | Completed |
| ---------------------------------------------- | -------------- | ----------- | --------- |
| 12. Task Types                                 | 0/?            | Not started | -         |
| 13. Multi-Team Hierarchy + Timeline Visibility | 5/5            | Planned     | -         |
| 14. Sprint Model                               | 0/?            | Not started | -         |
| 15. Custom Kanban Statuses                     | 0/?            | Not started | -         |
| 16. Advanced KPI Dashboard                     | 0/?            | Not started | -         |
| 17. Sprint & Release Reminders                 | 0/?            | Not started | -         |

---

## Phase Sequencing

```
Phase 12 - Task Types               [Isolated; can run parallel to 13]
Phase 13 - Multi-Team Hierarchy     [Gates all scoping; includes timeline visibility]
  └─ Phase 14 - Sprint Model        [Requires team context for scoping]
       └─ Phase 15 - Custom Statuses [Riskiest migration; burndown written once against is_done]
            └─ Phase 16 - KPI Dashboard [Requires 12+13+14+15 all complete]
Phase 13+14 → Phase 17 - Reminders  [Parallel workstream to 16; requires only hierarchy + sprints]
```

---

## Coverage

| Requirement | Phase    | Status  |
| ----------- | -------- | ------- |
| TYPE-01     | Phase 12 | Pending |
| TYPE-02     | Phase 12 | Pending |
| TYPE-03     | Phase 12 | Pending |
| TEAM-01     | Phase 13 | Pending |
| TEAM-02     | Phase 13 | Pending |
| TEAM-03     | Phase 13 | Pending |
| TEAM-04     | Phase 13 | Pending |
| TEAM-05     | Phase 13 | Pending |
| VIS-01      | Phase 13 | Pending |
| VIS-02      | Phase 13 | Pending |
| VIS-03      | Phase 13 | Pending |
| SPRINT-01   | Phase 14 | Pending |
| SPRINT-02   | Phase 14 | Pending |
| SPRINT-03   | Phase 14 | Pending |
| SPRINT-04   | Phase 14 | Pending |
| STATUS-01   | Phase 15 | Pending |
| STATUS-02   | Phase 15 | Pending |
| STATUS-03   | Phase 15 | Pending |
| STATUS-04   | Phase 15 | Pending |
| KPI-01      | Phase 16 | Pending |
| KPI-02      | Phase 16 | Pending |
| KPI-03      | Phase 16 | Pending |
| KPI-04      | Phase 16 | Pending |
| KPI-05      | Phase 16 | Pending |
| REMIND-01   | Phase 17 | Pending |
| REMIND-02   | Phase 17 | Pending |

**Coverage: 26/26 requirements mapped ✓**
