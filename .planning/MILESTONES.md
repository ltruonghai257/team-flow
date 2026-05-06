# Milestones: TeamFlow

## v2.4 Professional Role-Aware Dashboard (Started: 2026-05-06)

**Status:** Planning

### Goals

-   Redesign the dashboard (`/`) with professional visual hierarchy, clear section groupings, and data visualizations
-   Add a personalized My Tasks panel (all roles): assigned tasks sorted by urgency, overdue flagged red, due-soon highlighted
-   Add a Team Health panel (supervisor+): per-member workload status with at-risk signals from existing performance data
-   Add a KPI Summary strip (supervisor+): avg KPI score, completion rate, needs-attention count — linked to `/performance`
-   Add an Activity Feed (all roles): recent standup posts scoped by visibility rules

---

## v2.3 Timeline Clarity, Navigation IA & Scoped Visibility (Shipped: 2026-05-06)

**Status:** Complete
**Phases completed:** 5 phases (26-30)

### What Shipped

-   Grouped sidebar navigation with parent/child sections and role-aware visibility
-   Milestone-first Gantt timeline with expandable task rollups and planning/decision signal
-   Milestone command view with planning state, decisions, and linked task detail
-   Scoped visibility RBAC enforced across team, timeline, milestones, updates, board, and schedule screens

### Exit Criteria Met

-   ✓ `/timeline` delivered with milestone-first Gantt and planning signal
-   ✓ `/milestones` upgraded to command view with decision CRUD
-   ✓ Visibility rules enforced for member / supervisor / assistant manager / manager roles
-   ✓ Sidebar navigation restructured into workflow-based groups

---

## v2.2 Team Updates, Knowledge Sharing & Weekly Board (Shipped: 2026-04-28)

**Phases completed:** 3 phases (23-25)

### What Shipped

-   Structured standup updates with frozen task snapshots and a team feed
-   Knowledge Sharing sessions embedded into `/schedule` with scoped visibility and reminders
-   Weekly markdown board with per-week navigation plus on-demand and scheduled AI summaries

### Exit Criteria Met

-   ✓ `/updates` delivered with template-driven standup posts
-   ✓ `/schedule` includes scoped Knowledge Sessions
-   ✓ `/board` delivered with markdown posts and AI summaries

---

## v2.1 Open WebUI-Style Project Structure Refactor (Shipped: 2026-04-27)

**Status:** Complete
**Phases completed:** 4 phases (19-22)

### What Shipped

-   Open WebUI-inspired backend package groups with compatibility preserved
-   Frontend SvelteKit structure reorganized into cleaner route and lib groups
-   Runtime, Docker, Alembic, tests, and smoke checks verified after the move

---

## v2.0 Team Hierarchy, Sprints & Advanced Analytics (Shipped: 2026-04-28)

**Status:** Complete
**Phases completed:** 7 phases (12-18)

### What Shipped

-   Multi-team hierarchy and timeline visibility
-   Sprint model and sprint reminders
-   Custom Kanban statuses
-   Advanced KPI dashboard
-   Status transition graph and workflow rules

---

## v1.0 Production-Ready Team Management Platform (Shipped: 2026-04-24)

**Status:** Complete
**Phases completed:** 11 phases (1-11)

### What Shipped

-   Production hardening and RBAC baseline
-   Supervisor performance dashboard
-   Timeline view
-   AI task features
-   Mobile responsiveness
-   Azure deployment and CI/CD
-   User invite and team management
