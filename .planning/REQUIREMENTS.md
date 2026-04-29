# Requirements: TeamFlow v2.3

**Milestone:** v2.3 — Timeline Clarity, Navigation IA & Scoped Visibility
**Created:** 2026-04-29
**Status:** Active

---

## Milestone Requirements

### Navigation Information Architecture (NAV)

- [x] **NAV-01**: Sidebar groups related pages into parent sections with nested sub-items instead of one flat route list
- [x] **NAV-02**: Current route highlight also shows the active parent section so users can tell which feature area they are inside
- [x] **NAV-03**: Grouping uses existing page URLs; the redesign does not require changing public routes
- [x] **NAV-04**: Desktop sidebar and mobile drawer use the same grouped navigation structure and expand/collapse behavior
- [x] **NAV-05**: Navigation visibility respects role and scope so users only see sections they are allowed to open

### Timeline & Gantt Clarity (TL)

- [x] **TL-01**: `/timeline` presents milestones as visually distinct planning objects, not only as implied collections of task bars
- [x] **TL-02**: Each milestone view in the timeline includes its related tasks so milestone progress can be understood without leaving the screen
- [x] **TL-03**: Timeline highlights milestone risk, current planning windows, and explicit decision points
- [x] **TL-04**: Users can switch between project-oriented and people-oriented timeline views without losing the selected date range
- [x] **TL-05**: Timeline shows milestone progress labels or badges in addition to raw Gantt bars

### Milestone Planning & Decisions (ML)

- [x] **ML-01**: `/milestones` gives a clearer overview of milestone status with separate signals for committed work, planned work, and completed work
- [x] **ML-02**: A milestone detail view shows the tasks that belong to that milestone directly in context
- [x] **ML-03**: Milestone decisions are captured and visible in the milestone experience, not only in planning docs
- [x] **ML-04**: Planning and decision markers reuse existing data where possible and introduce new persistence only when current models cannot express the workflow

### Scoped Team Visibility & RBAC (VIS)

- [x] **VIS-01**: Members can only see other users and team data inside their own sub-team
- [x] **VIS-02**: Supervisors can see members in their allowed scope plus peer leaders at the same level in the relevant parent-team scope
- [x] **VIS-03**: Assistant managers follow the same peer-visibility model as supervisors unless a later planning phase narrows it
- [x] **VIS-04**: Managers can see all teams, members, and leadership groups
- [ ] **VIS-05**: Team, timeline, milestones, updates, board, and schedule views enforce the same visibility rules
- [ ] **VIS-06**: Invite and team-management flows can assign or represent the leadership scopes required by the new visibility model
- [x] **VIS-07**: Existing `admin` / `supervisor` / `member` data is migrated or mapped safely into the new visibility model without orphaning users or sub-teams

---

## Future Requirements (Deferred)

These were considered but deferred beyond v2.3:

- Custom sidebar layouts per user or per role
- Cross-team exceptions where an individual can belong to multiple visibility scopes
- Dedicated org-chart or people directory views
- Timeline dependency lines or auto-scheduling logic
- Decision approval workflows with explicit sign-off states

---

## Out of Scope

| Item | Reason |
|------|--------|
| Route URL redesign | The milestone should improve information architecture without breaking existing links and habits |
| Public org directory | Visibility changes are for internal work scopes, not a company-wide people browser |
| Matrix management and many-to-many reporting lines | Too large for this milestone; start with the stated manager / supervisor / assistant manager / member model |
| External identity or HR sync | Scope is internal RBAC behavior, not enterprise directory integration |
| Full portfolio planning suite | Milestone planning clarity should stay inside existing TeamFlow milestones and timeline surfaces |

---

## Traceability

| REQ-ID | Phase | Notes |
|--------|-------|-------|
| NAV-01 | Phase 26 | Parent/child sidebar structure |
| NAV-02 | Phase 26 | Active-section affordance |
| NAV-03 | Phase 26 | Stable route URLs |
| NAV-04 | Phase 26 | Shared desktop/mobile grouping behavior |
| NAV-05 | Phase 26 | Navigation-level permission visibility |
| TL-01 | Phase 27 | Milestone-first timeline treatment |
| TL-02 | Phase 27 | Milestone-linked task rollups |
| TL-03 | Phase 27 | Risk / planning / decision highlights |
| TL-04 | Phase 27 | Preserve date context across views |
| TL-05 | Phase 27 | Milestone progress labels |
| ML-01 | Phase 28 | Milestone overview clarity |
| ML-02 | Phase 28 | Linked tasks in milestone detail |
| ML-03 | Phase 28 | Visible milestone decisions |
| ML-04 | Phase 28 | Minimal persistence changes |
| VIS-01 | Phase 29 | Member sub-team-only visibility |
| VIS-02 | Phase 29 | Supervisor peer and scoped-member visibility |
| VIS-03 | Phase 29 | Assistant manager visibility rule |
| VIS-04 | Phase 29 | Manager org-wide visibility |
| VIS-05 | Phase 29 | Cross-surface enforcement |
| VIS-06 | Phase 29 | Team/invite flow support |
| VIS-07 | Phase 29 | Safe role/scope migration |
