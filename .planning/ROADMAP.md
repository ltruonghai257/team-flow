# Roadmap: TeamFlow

_Updated: 2026-04-28_

---

## Milestones

- ✅ **v1.0** — Production-Ready Team Management Platform (Phases 1-11) — shipped 2026-04-24
- ✅ **v2.0** — Team Hierarchy, Sprints & Advanced Analytics (Phases 12-18) — shipped 2026-04-28
- ✅ **v2.1** — Open WebUI-Style Project Structure Refactor (Phases 19-22) — shipped 2026-04-28
- 🔄 **v2.2** — Team Updates, Knowledge Sharing & Weekly Board (Phases 23-25) — in progress

---

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-11) — SHIPPED 2026-04-24</summary>

- [x] Phase 1: Production Hardening (2/2 plans) — completed 2026-04-23
- [x] Phase 2: RBAC & Role Model (2/2 plans) — completed 2026-04-23
- [x] Phase 3: Supervisor Performance Dashboard (2/2 plans) — completed 2026-04-23
- [x] Phase 4: Team Timeline View (2/2 plans) — completed 2026-04-23
- [x] Phase 5: Enhanced AI Features (2/2 plans) — completed 2026-04-23
- [x] Phase 6: Mobile-Responsive UI (2/2 plans) — completed 2026-04-23
- [x] Phase 7: Azure Deployment & CI/CD (2/2 plans) — completed 2026-04-23
- [x] Phase 8: User Invite & Team Management (2/2 plans) — completed 2026-04-24
- [x] Phase 9: Verification Docs (Phases 1-3) (1/1 plan) — completed 2026-04-24
- [x] Phase 10: Verification Docs (Phases 4-5) (1/1 plan) — completed 2026-04-24
- [x] Phase 11: Verification Docs (Phases 6-8) (1/1 plan) — completed 2026-04-24

</details>

<details>
<summary>✅ v2.0 Team Hierarchy, Sprints & Advanced Analytics (Phases 12-18) — SHIPPED 2026-04-28</summary>

- [x] Phase 12: Task Types (5/5 plans) — completed 2026-04-26
- [x] Phase 13: Multi-team Hierarchy & Timeline Visibility (5/5 plans) — completed 2026-04-26
- [x] Phase 14: Sprint Model (5/5 plans) — completed 2026-04-26
- [x] Phase 15: Custom Kanban Statuses (5/5 plans) — completed 2026-04-26
- [x] Phase 16: Advanced KPI Dashboard (5/5 plans) — completed 2026-04-27
- [x] Phase 17: Sprint & Release Reminders (5/5 plans) — completed 2026-04-28
- [x] Phase 18: Status Transition Graph (Workflow Rules) (4/4 plans) — completed 2026-04-27

</details>

<details>
<summary>✅ v2.1 Open WebUI-Style Project Structure Refactor (Phases 19-22) — SHIPPED 2026-04-28</summary>

- [x] Phase 19: Refactor Map & Safety Baseline (4/4 plans) — completed 2026-04-27
- [x] Phase 20: Backend Package Restructure (5/5 plans) — completed 2026-04-27
- [x] Phase 21: Frontend SvelteKit Structure (4/4 plans) — completed 2026-04-27
- [x] Phase 22: Runtime Integration & Regression Verification (4/4 plans) — completed 2026-04-27

</details>

### v2.2 — Team Updates, Knowledge Sharing & Weekly Board

- [ ] **Phase 23: Standup Updates** — Template-driven standup posts with task snapshot, team feed, edit/delete
- [ ] **Phase 24: Knowledge Sharing Scheduler** — Admin/supervisor-scoped KS sessions as a tab in /schedule, with notifications
- [ ] **Phase 25: Team Weekly Board & AI Summary** — Markdown board organized by ISO week, on-demand and scheduled AI summary

---

**Known deferred items at close: 4 (see STATE.md Deferred Items)**

---

For detailed phase information, see archived milestone files in `.planning/milestones/`.

---

## Phase Details

### Phase 23: Standup Updates
**Goal**: Members can post structured daily/weekly standups with a frozen task snapshot, and the whole team can browse and filter the feed
**Depends on**: Phase 22 (v2.1 structure baseline)
**Requirements**: UPD-01, UPD-02, UPD-03, UPD-04, UPD-05, UPD-06, UPD-07, UPD-08
**Success Criteria** (what must be TRUE):
  1. A member can open /updates, fill out the configured template fields, submit a standup post, and see it appear in the team feed immediately
  2. The submitted post displays a frozen snapshot of the member's tasks at submit time — refreshing the page or changing task statuses later does not alter the snapshot
  3. The supervisor can add, remove, or rename fields in the standup template and the change is reflected for the next post submission
  4. Any team member can filter the feed by author or by date to narrow results
  5. A member can edit or delete their own standup post; they cannot edit or delete another member's post
**Plans**: 4 plans
Plans:
- [ ] 23-01-PLAN.md — SQLAlchemy models, Pydantic schemas, Alembic migration (Wave 1)
- [ ] 23-02-PLAN.md — Frontend packages, updates API module, updates store (Wave 1)
- [ ] 23-03-PLAN.md — Backend router: all 6 endpoints + main.py registration (Wave 2)
- [ ] 23-04-PLAN.md — Frontend UI: page, form, card, snapshot panel, nav item (Wave 2)
**UI hint**: yes

### Phase 24: Knowledge Sharing Scheduler
**Goal**: Admins and supervisors can schedule Knowledge Sharing sessions scoped to their team, and members receive notifications for sessions in their scope
**Depends on**: Phase 23
**Requirements**: KS-01, KS-02, KS-03, KS-04, KS-05, KS-06
**Success Criteria** (what must be TRUE):
  1. An admin can create a KS session (topic, description, references, presenter, session type, duration, date/time, tags) that is visible to all org members; a supervisor can create a session visible only to their sub-team
  2. The /schedule page shows a "Knowledge Sessions" tab; no new top-level route is added
  3. A team member sees only sessions scoped to them (org-wide sessions plus their sub-team's sessions); sessions outside their scope are not visible
  4. A member receives an in-app notification when a new session in their scope is created
  5. A member receives an in-app reminder before a session in their scope begins
**Plans**: TBD
**UI hint**: yes

### Phase 25: Team Weekly Board & AI Summary
**Goal**: Any member can post markdown updates to a shared weekly board, and an AI summary is available both on demand and automatically at end of week
**Depends on**: Phase 24
**Requirements**: BOARD-01, BOARD-02, BOARD-03, BOARD-04, BOARD-05, BOARD-06, BOARD-07, BOARD-08
**Success Criteria** (what must be TRUE):
  1. Any member can open /board, write a markdown post for the current week, submit it, and see the rendered (XSS-safe) content appear on the board
  2. The board groups posts by ISO week; members can navigate to any past week and see that week's posts and its stored AI summary
  3. A member can click "Summarize this week" to trigger an on-demand AI summary; the result is stored and re-clicking within 30 minutes returns the cached result without calling the AI again
  4. At Sunday 23:00 the system automatically generates a weekly summary via APScheduler CronTrigger; if no posts exist for the week the summary is "no updates this week" (no AI call made)
  5. A member can edit or delete their own weekly post; another member's post cannot be modified
**Plans**: TBD
**UI hint**: yes

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 23. Standup Updates | 0/4 | In planning | - |
| 24. Knowledge Sharing Scheduler | 0/? | Not started | - |
| 25. Team Weekly Board & AI Summary | 0/? | Not started | - |
