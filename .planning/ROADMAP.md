# Roadmap: TeamFlow

_Updated: 2026-04-30_

---

## Milestones

-   ✅ **v1.0** — Production-Ready Team Management Platform (Phases 1-11) — shipped 2026-04-24
-   ✅ **v2.0** — Team Hierarchy, Sprints & Advanced Analytics (Phases 12-18) — shipped 2026-04-28
-   ✅ **v2.1** — Open WebUI-Style Project Structure Refactor (Phases 19-22) — shipped 2026-04-28
-   ✅ **v2.2** — Team Updates, Knowledge Sharing & Weekly Board (Phases 23-25) — shipped 2026-04-28
-   🔄 **v2.3** — Timeline Clarity, Navigation IA & Scoped Visibility (Phases 26-30) — in progress

---

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-11) — SHIPPED 2026-04-24</summary>

-   [x] Phase 1: Production Hardening (2/2 plans) — completed 2026-04-23
-   [x] Phase 2: RBAC & Role Model (2/2 plans) — completed 2026-04-23
-   [x] Phase 3: Supervisor Performance Dashboard (2/2 plans) — completed 2026-04-23
-   [x] Phase 4: Team Timeline View (2/2 plans) — completed 2026-04-23
-   [x] Phase 5: Enhanced AI Features (2/2 plans) — completed 2026-04-23
-   [x] Phase 6: Mobile-Responsive UI (2/2 plans) — completed 2026-04-23
-   [x] Phase 7: Azure Deployment & CI/CD (2/2 plans) — completed 2026-04-23
-   [x] Phase 8: User Invite & Team Management (2/2 plans) — completed 2026-04-24
-   [x] Phase 9: Verification Docs (Phases 1-3) (1/1 plan) — completed 2026-04-24
-   [x] Phase 10: Verification Docs (Phases 4-5) (1/1 plan) — completed 2026-04-24
-   [x] Phase 11: Verification Docs (Phases 6-8) (1/1 plan) — completed 2026-04-24

</details>

<details>
<summary>✅ v2.0 Team Hierarchy, Sprints & Advanced Analytics (Phases 12-18) — SHIPPED 2026-04-28</summary>

-   [x] Phase 12: Task Types (5/5 plans) — completed 2026-04-26
-   [x] Phase 13: Multi-team Hierarchy & Timeline Visibility (5/5 plans) — completed 2026-04-26
-   [x] Phase 14: Sprint Model (5/5 plans) — completed 2026-04-26
-   [x] Phase 15: Custom Kanban Statuses (5/5 plans) — completed 2026-04-26
-   [x] Phase 16: Advanced KPI Dashboard (5/5 plans) — completed 2026-04-27
-   [x] Phase 17: Sprint & Release Reminders (5/5 plans) — completed 2026-04-28
-   [x] Phase 18: Status Transition Graph (Workflow Rules) (4/4 plans) — completed 2026-04-27

</details>

<details>
<summary>✅ v2.1 Open WebUI-Style Project Structure Refactor (Phases 19-22) — SHIPPED 2026-04-28</summary>

-   [x] Phase 19: Refactor Map & Safety Baseline (4/4 plans) — completed 2026-04-27
-   [x] Phase 20: Backend Package Restructure (5/5 plans) — completed 2026-04-27
-   [x] Phase 21: Frontend SvelteKit Structure (4/4 plans) — completed 2026-04-27
-   [x] Phase 22: Runtime Integration & Regression Verification (4/4 plans) — completed 2026-04-27

</details>

### v2.2 — Team Updates, Knowledge Sharing & Weekly Board

-   [x] **Phase 23: Standup Updates** — Template-driven standup posts with task snapshot, team feed, and author-owned edits — completed 2026-04-28
-   [x] **Phase 24: Knowledge Sharing Scheduler** — Scoped Knowledge Sessions inside `/schedule`, with notifications and reminders — completed 2026-04-28
-   [x] **Phase 25: Team Weekly Board & AI Summary** — Weekly markdown board with on-demand and scheduled AI summaries — completed 2026-04-28

### v2.3 — Timeline Clarity, Navigation IA & Scoped Visibility

-   [x] **Phase 26: Navigation Information Architecture** — Reorganize the sidebar and mobile navigation into workflow-based groups with nested items and role-aware visibility (completed 2026-04-28)
-   [x] **Phase 27: Timeline & Gantt Clarity** — Make `/timeline` milestone-first, clearer to scan, and richer in planning and decision signal (completed 2026-04-28)
-   [x] **Phase 28: Milestone Planning & Decisions** — Improve `/milestones` so planning state, decisions, and related tasks are visible together (completed 2026-04-30)
-   [x] **Phase 29: Scoped Team Visibility & Leadership RBAC** — Enforce the new member / supervisor / assistant manager / manager visibility rules across the product (completed 2026-04-29)

---

**Known deferred items at close: 4 (see STATE.md Deferred Items)**

---

For detailed historical milestone information, see archived files in `.planning/milestones/`.

---

## Phase Details

### Phase 26: Navigation Information Architecture

**Goal**: Make navigation easier to understand by grouping pages into workflow-based parent and child sections across desktop and mobile
**Depends on**: Phase 25
**Requirements**: NAV-01, NAV-02, NAV-03, NAV-04, NAV-05
**Success Criteria** (what must be TRUE):

1. The sidebar is grouped into logical parent sections with nested child items rather than a flat list
2. Opening any child page clearly shows both the active route and the active parent section
3. Mobile navigation uses the same groups and expansion rules as desktop
4. Users do not lose access to existing pages or route URLs after the information architecture change
   **Plans**: 3 plans
   Plans:
   **Wave 1**

-   [x] 26-01-PLAN.md — Define grouped navigation metadata, active-route matching, and role-aware filtering

**Wave 2** _(blocked on Wave 1 completion)_

-   [x] 26-02-PLAN.md — Refactor the shared desktop/mobile layout to render grouped navigation behavior

**Wave 3** _(blocked on Wave 2 completion)_

-   [x] 26-03-PLAN.md — Add grouped-navigation regression coverage and final verification
        **UI hint**: yes

### Phase 27: Timeline & Gantt Clarity

**Goal**: Turn `/timeline` into a milestone-first planning surface with clearer Gantt signals, linked tasks, and better risk scanning
**Depends on**: Phase 26
**Requirements**: TL-01, TL-02, TL-03, TL-04, TL-05
**Success Criteria** (what must be TRUE):

1. A user can open `/timeline` and immediately distinguish milestones from task bars
2. Milestone rows or panels expose the tasks that belong to each milestone without forcing a full context switch
3. Planning windows, milestone risk, and decision points are visually distinct from normal tasks
4. Switching between project and people-oriented views preserves the chosen time range and keeps the view understandable
   **Plans**: 3 plans
   Plans:
   **Wave 1**

-   [x] 27-01-PLAN.md — Expand the timeline API contract and typed frontend timeline models for milestone summaries, risk inputs, and decision markers

**Wave 2** _(blocked on Wave 1 completion)_

-   [x] 27-02-PLAN.md — Rebuild `/timeline` as a milestone-first gantt with expandable milestone rows, focus continuity, and member-view context cues

**Wave 3** _(blocked on Wave 2 completion)_

-   [x] 27-03-PLAN.md — Add targeted timeline regression coverage and final release verification
        **Cross-cutting constraints:**
-   Existing `/timeline` route URL, task edit modal, and task drag-to-reschedule behavior stay intact.
-   Risk and decision signals are derived from existing milestone/task/custom-status data; no new persistence is introduced in Phase 27.
-   By Member view stays people-first while preserving the selected date range and focused milestone/task context.
    **UI hint**: yes

### Phase 28: Milestone Planning & Decisions

**Goal**: Make `/milestones` a clearer command view for milestone status, decisions, and linked work
**Depends on**: Phase 27
**Requirements**: ML-01, ML-02, ML-03, ML-04
**Success Criteria** (what must be TRUE):

1. A supervisor can scan the milestone page and distinguish planned, committed, active, and completed work
2. Milestone detail shows related tasks in context rather than forcing users to mentally join separate screens
3. Key milestone decisions are visible on the product surface, not only in planning files
4. Any new persistence introduced for decisions or planning state is clearly justified by a gap in the current schema
   **Plans**: 4 plans
   Plans:
   **Wave 1**

-   [ ] 28-01-PLAN.md — Add milestone decision persistence, scoped decision CRUD, and backend coverage

**Wave 2** _(blocked on Wave 1 completion)_

-   [ ] 28-02-PLAN.md — Add the derived milestone command-view API, summary metrics, and typed frontend contract

**Wave 3** _(blocked on Wave 2 completion)_

-   [x] 28-03-PLAN.md — Rebuild `/milestones` into a lane-based command view with linked-task detail and decision CRUD

**Wave 4** _(blocked on Wave 3 completion)_

-   [ ] 28-04-PLAN.md — Add milestone command-view regression coverage and final release verification
        **Cross-cutting constraints:**
-   Existing `/milestones` route URL and the basic milestone create/edit modal stay intact while the page is upgraded into a richer command view.
-   Planning state is derived from existing milestone and task data; no manual planning-state override is introduced in Phase 28.
-   Structured decision persistence is limited to milestone-owned decision records, and task rows hand off to the existing `/tasks?task_id=` flow instead of adding inline task editing.
    **UI hint**: yes

### Phase 29: Scoped Team Visibility & Leadership RBAC

**Goal**: Enforce the new visibility model so members, supervisors, assistant managers, and managers each see the right people and data
**Depends on**: Phase 28
**Requirements**: VIS-01, VIS-02, VIS-03, VIS-04, VIS-05, VIS-06, VIS-07
**Success Criteria** (what must be TRUE):

1. A member can only see users and team data from their own sub-team across team, timeline, milestones, updates, board, and schedule surfaces
2. Supervisors and assistant managers can see same-level leaders in their allowed parent scope plus the members they are meant to oversee
3. A manager can see all teams and users across the organization
4. Invite and team-management flows support the role and scope data needed by the new visibility rules
5. Existing user and sub-team records survive the migration or mapping cleanly
   **Plans**: 0 plans
   **UI hint**: yes

---

## Progress Table

| Phase                                              | Plans Complete | Status      | Completed  |
| -------------------------------------------------- | -------------- | ----------- | ---------- |
| 26. Navigation Information Architecture            | 3/3            | Complete    | 2026-04-28 |
| 27. Timeline & Gantt Clarity                       | 3/3            | Complete    | 2026-04-28 |
| 28. Milestone Planning & Decisions                 | 4/4            | Complete    | 2026-04-30 |
| 29. Scoped Team Visibility & Leadership RBAC       | 4/4            | Complete    | 2026-04-29 |
| 30. Phase 18 status-transition follow-up hardening | 2/2 | Complete    | 2026-05-06 |

### Phase 30: Phase 18 status-transition follow-up hardening

**Goal:** Harden and verify the shipped Phase 18 status-transition workflow rules after the refactor, with a focus on status-set scoping, workflow feedback, and regression coverage.
**Requirements**: TBD
**Depends on:** Phase 29
**Plans:** 2/2 plans complete

Plans:
**Wave 1**

-   [x] 30-01-PLAN.md — Fix `_require_status_write_scope` RBAC bug, regression audit, and backend test coverage for Phase 29 role set

**Wave 2** _(blocked on Wave 1 completion)_

-   [x] 30-02-PLAN.md — Automate Phase 18 UAT #2 and #4 as Playwright tests, update 18-UAT.md with full results
