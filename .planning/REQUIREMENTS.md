# Requirements: TeamFlow

*Updated: 2026-04-24*
*Stack: FastAPI (Python 3.13) + SvelteKit 5 + PostgreSQL 16 + TailwindCSS*
*Deployment: Azure App Service (Linux) + Azure Database for PostgreSQL Flexible Server*

---

## Requirements Traceability Table

| REQ-ID | Description | Priority | Phase | Status |
|--------|-------------|----------|-------|--------|
| REQ-01 | Production Hardening | Critical | 1 | ✓ Done |
| REQ-02 | Supervisor Performance Dashboard | High | 3 | ✓ Done |
| REQ-03 | Team Timeline / Project Overview | High | 4 | ✓ Done |
| REQ-04 | Enhanced AI Capabilities | Medium | 5 | ✓ Done |
| REQ-05 | Azure Deployment | Critical | 7 | ✓ Done |
| REQ-06 | Mobile-Responsive UI | Medium | 6 | ✓ Done |
| REQ-07 | Role-Based Access Control | Medium | 2 | ✓ Done |
| TEAM-01 | Admin creates/manages sub-teams | High | 13 | Pending |
| TEAM-02 | Member belongs to one sub-team | High | 13 | Pending |
| TEAM-03 | Projects scoped to sub-team | High | 13 | Pending |
| TEAM-04 | Supervisor sees only their sub-team | High | 13 | Pending |
| TEAM-05 | Admin sees all teams org-wide | High | 13 | Pending |
| VIS-01 | Members see only assigned projects on timeline | Medium | 13 | Pending |
| VIS-02 | Supervisors see sub-team projects on timeline | Medium | 13 | Pending |
| VIS-03 | Admin sees all projects on timeline | Medium | 13 | Pending |
| SPRINT-01 | Sprints as time-boxed iterations within milestone | High | 14 | Pending |
| SPRINT-02 | Milestones belong to one project | High | 14 | Pending |
| SPRINT-03 | Task create/edit includes sprint selector | High | 14 | Pending |
| SPRINT-04 | Sprint board filters tasks by sprint | High | 14 | Pending |
| STATUS-01 | Supervisor/admin manages team-wide statuses | High | 15 | Pending |
| STATUS-02 | Per-project status override | Medium | 15 | Pending |
| STATUS-03 | Existing statuses migrated to DB records | Critical | 15 | Pending |
| STATUS-04 | Status has is_done flag (replaces hardcoded done slug) | Critical | 15 | Pending |
| TYPE-01 | Task type field: feature/bug/task/improvement | High | 12 | Pending |
| TYPE-02 | Type visible on cards, filterable on board | Medium | 12 | Pending |
| TYPE-03 | Existing tasks default to task type on migration | High | 12 | Pending |
| KPI-01 | Velocity per sprint (task count + story points) | High | 16 | Pending |
| KPI-02 | Sprint burndown chart | High | 16 | Pending |
| KPI-03 | Cycle time per task type | Medium | 16 | Pending |
| KPI-04 | Throughput by member and type | Medium | 16 | Pending |
| KPI-05 | Defect metrics: bugs reported/resolved, MTTR | Medium | 16 | Pending |
| REMIND-01 | In-app reminder N days before sprint end | Medium | 17 | Pending |
| REMIND-02 | In-app reminder N days before milestone due date | Medium | 17 | Pending |

---

## Milestone 1: Production-Ready Team Management Platform (Complete ✓)

All REQ-01 through REQ-07 satisfied. See MILESTONES.md for full exit criteria.

---

## Milestone 2: Team Hierarchy, Sprints & Advanced Analytics

### Goal
Transform TeamFlow from a single-team tool into a multi-team platform with sprint-driven project management, Trello-style customizable boards, and data-grounded KPI analytics.

---

## TEAM-01: Admin Creates/Manages Sub-Teams

**Priority:** High

### Acceptance Criteria
- [ ] Admin can create a sub-team with a name and assign exactly one supervisor
- [ ] Admin can rename a sub-team and reassign its supervisor
- [ ] Admin can delete a sub-team (only if no members or projects are attached)
- [ ] Sub-team management UI accessible from admin settings page

---

## TEAM-02: Member Belongs to One Sub-Team

**Priority:** High

### Acceptance Criteria
- [ ] Every user (member role) belongs to exactly one sub-team
- [ ] Admin can reassign a member from one sub-team to another
- [ ] A member cannot exist without a sub-team after migration (nullable during transition)
- [ ] Existing users assigned to a default sub-team on migration

---

## TEAM-03: Projects Scoped to Sub-Team

**Priority:** High

### Acceptance Criteria
- [ ] Every project has a sub-team association
- [ ] Admin and the sub-team's supervisor can create projects for that sub-team
- [ ] Members can only see and interact with projects in their sub-team
- [ ] Existing projects assigned to a default sub-team on migration

---

## TEAM-04: Supervisor Sees Only Their Sub-Team

**Priority:** High

### Acceptance Criteria
- [ ] Supervisor's dashboard, performance page, and timeline show only their sub-team's members and projects
- [ ] All API endpoints filter results by the requesting user's sub-team (not just frontend routing)
- [ ] Supervisor cannot access members, tasks, or projects from other sub-teams via API

---

## TEAM-05: Admin Sees All Teams Org-Wide

**Priority:** High

### Acceptance Criteria
- [ ] Admin can view all sub-teams and switch between them in dashboard/timeline/performance views
- [ ] Admin performance dashboard shows org-wide aggregates and per-sub-team breakdown

---

## VIS-01: Members See Only Assigned Projects on Timeline

**Priority:** Medium

### Acceptance Criteria
- [ ] Timeline `/timeline` filters to projects where the member has at least one assigned task
- [ ] Filter applied server-side (not just frontend)

---

## VIS-02: Supervisors See Sub-Team Projects on Timeline

**Priority:** Medium

### Acceptance Criteria
- [ ] Supervisor sees all projects belonging to their sub-team on the timeline
- [ ] Cross-team projects not visible unless admin

---

## VIS-03: Admin Sees All Projects on Timeline

**Priority:** Medium

### Acceptance Criteria
- [ ] Admin sees all projects from all sub-teams on the timeline
- [ ] Admin can filter timeline by sub-team

---

## SPRINT-01: Sprints as Time-Boxed Iterations

**Priority:** High

### Acceptance Criteria
- [ ] Sprint model: `name`, `start_date`, `end_date`, `milestone_id` (FK), `status` (planning/active/closed)
- [ ] Supervisor/admin can create, edit, and close sprints within a milestone
- [ ] Sprint list view shows all sprints for a project with status and date range
- [ ] Closing a sprint moves incomplete tasks to backlog or next sprint (user chooses)

---

## SPRINT-02: Milestones Belong to One Project

**Priority:** High

### Acceptance Criteria
- [ ] Milestone model has a required `project_id` FK
- [ ] Existing milestones without a project association assigned to a default project on migration
- [ ] Milestone creation UI requires selecting a project

---

## SPRINT-03: Task Create/Edit Includes Sprint Selector

**Priority:** High

### Acceptance Criteria
- [ ] Task creation form includes a sprint dropdown (filtered to active/planning sprints for the task's project)
- [ ] Task edit form allows reassigning to a different sprint or removing sprint association
- [ ] Sprint assignment stored as nullable `sprint_id` FK on Task

---

## SPRINT-04: Sprint Board Filters Tasks by Sprint

**Priority:** High

### Acceptance Criteria
- [ ] Sprint board view shows only tasks assigned to the selected sprint
- [ ] Sprint selector at top of board; defaults to the active sprint
- [ ] Unassigned tasks visible in a "Backlog" column alongside sprint board

---

## STATUS-01: Supervisor/Admin Manages Team-Wide Statuses

**Priority:** High

### Acceptance Criteria
- [ ] Supervisor/admin can create custom statuses with name, color, and order
- [ ] Statuses can be reordered via drag-and-drop
- [ ] Each status has an `is_done` boolean flag (marks task as complete for KPI calculations)
- [ ] A status cannot be deleted if tasks are currently assigned to it

---

## STATUS-02: Per-Project Status Override

**Priority:** Medium

### Acceptance Criteria
- [ ] A project can define its own status set (create/reorder/delete per-project statuses)
- [ ] If a project has no custom statuses, it inherits the team-wide default set
- [ ] Switching from per-project statuses back to team default migrates tasks to matching team statuses

---

## STATUS-03: Existing Statuses Migrated to DB Records

**Priority:** Critical

### Acceptance Criteria
- [ ] Existing `TaskStatus` enum values (todo/in_progress/review/done/blocked) created as DB records in the team-wide default set
- [ ] All existing tasks migrated from enum value to FK reference in a single Alembic migration
- [ ] Zero data loss during migration (verified by row count check)

---

## STATUS-04: Status `is_done` Flag Drives Completion Logic

**Priority:** Critical

### Acceptance Criteria
- [ ] `Task.completed_at` is set when task moves to any status with `is_done = true`
- [ ] `Task.completed_at` is cleared when task moves from a done status back to a non-done status
- [ ] All KPI queries and cycle time calculations use `is_done` flag, not hardcoded status slug

---

## TYPE-01: Task Type Field

**Priority:** High

### Acceptance Criteria
- [ ] Task has a `type` field with values: `feature / bug / task / improvement`
- [ ] Type is required on task creation (defaults to `task` if not selected)
- [ ] Type is included in all task API responses

---

## TYPE-02: Type Visible on Cards and Filterable

**Priority:** Medium

### Acceptance Criteria
- [ ] Task type displayed as an icon or badge on Kanban cards
- [ ] Kanban board has a filter by type (show all / feature / bug / task / improvement)
- [ ] Task list view sortable and filterable by type

---

## TYPE-03: Existing Tasks Default to `task` Type

**Priority:** High

### Acceptance Criteria
- [ ] Migration sets `type = 'task'` for all existing tasks with no type set
- [ ] No null values for `type` after migration

---

## KPI-01: Velocity per Sprint

**Priority:** High

### Acceptance Criteria
- [ ] Performance dashboard shows velocity chart: tasks completed per sprint per member
- [ ] Velocity displayed as task count (story points shown if field is populated)
- [ ] Chart covers last 6 sprints

---

## KPI-02: Sprint Burndown Chart

**Priority:** High

### Acceptance Criteria
- [ ] Burndown chart shows remaining tasks vs elapsed sprint time for the active sprint
- [ ] Computed on-the-fly from task completion dates within the sprint window
- [ ] Supervisor can view burndown for any closed sprint

---

## KPI-03: Cycle Time per Task Type

**Priority:** Medium

### Acceptance Criteria
- [ ] Performance dashboard shows average cycle time broken down by task type
- [ ] Cycle time = `completed_at - created_at` (only completed tasks with both dates set)
- [ ] Trend line over last 3 months

---

## KPI-04: Throughput by Member and Type

**Priority:** Medium

### Acceptance Criteria
- [ ] Performance dashboard shows tasks completed per week per member, grouped by type
- [ ] Stacked bar chart: feature / bug / task / improvement per member per week
- [ ] Covers last 8 weeks

---

## KPI-05: Defect Metrics

**Priority:** Medium

### Acceptance Criteria
- [ ] Performance dashboard shows: bugs reported (created with type=bug) vs bugs resolved (completed) per period
- [ ] MTTR per member: average time from bug creation to completion (type=bug only)
- [ ] Covers last 30 days

---

## REMIND-01: Sprint End Reminders

**Priority:** Medium

### Acceptance Criteria
- [ ] In-app notification sent to all sprint participants N days before sprint end date (default: 2 days)
- [ ] N is configurable per team (supervisor/admin setting)
- [ ] Reminder stored as `EventNotification` row (persists across restarts)
- [ ] No duplicate reminders if sprint date is unchanged

---

## REMIND-02: Milestone Due Date Reminders

**Priority:** Medium

### Acceptance Criteria
- [ ] In-app notification sent to supervisor/admin N days before a milestone due date (default: 3 days)
- [ ] N is configurable per team (supervisor/admin setting)
- [ ] Reminder stored as `EventNotification` row

---

## Non-Requirements (Out of Scope for Milestone 2)

- Cross-sub-team project collaboration (projects belong to exactly one sub-team)
- Git/CI integration for code-quality KPIs (Code Coverage, Code Stability, MTTR from CI)
- Historical burndown snapshots (on-the-fly computation is sufficient for v2.0)
- Story points estimation enforcement (nullable, not required)
- Email notifications for reminders (in-app only)
- Extensible/custom task types (fixed four values)

---

## Constraints

- No framework changes — FastAPI + SvelteKit 5 + PostgreSQL 16 only
- Zero new npm or Python packages (all needed libs already installed)
- All schema changes via Alembic migrations only
- Task.status enum→FK migration must use dual-write strategy (no single-shot ALTER TYPE)
- All API endpoints must enforce sub-team scoping server-side (not just frontend routing)

---

## Definition of Done (Milestone 2)

- [ ] Admin can create sub-teams and assign supervisors
- [ ] Supervisors see only their sub-team's data across all views (API-enforced)
- [ ] Sprints exist within milestones; tasks can be assigned to a sprint
- [ ] Kanban board columns are driven from DB statuses, not hardcoded enum
- [ ] Performance dashboard shows velocity, burndown, cycle time by type, throughput, and defect metrics
- [ ] In-app reminders fire before sprint end and milestone due dates
- [ ] All existing data migrated without loss (zero data loss verified)
