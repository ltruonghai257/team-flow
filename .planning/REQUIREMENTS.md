# Requirements: TeamFlow v2.2

**Milestone:** v2.2 — Team Updates, Knowledge Sharing & Weekly Board
**Created:** 2026-04-28
**Status:** Active

---

## Milestone Requirements

### Standup Updates (UPD)

- [ ] **UPD-01**: Member fills out a standup post using the configured template fields
- [ ] **UPD-02**: Default template includes: Pending Tasks, Future Tasks, Blockers, Need Help From, Critical Timeline, Release Date
- [ ] **UPD-03**: Supervisor can customize the standup template (add, remove, or rename fields)
- [ ] **UPD-04**: Standup post captures a frozen snapshot of the member's task statuses at submit time (stored as JSONB, not a live query)
- [ ] **UPD-05**: Standup posts are visible to all team members and the supervisor in a team feed
- [ ] **UPD-06**: Team feed can be filtered by member and date
- [ ] **UPD-07**: Member can edit their own standup post
- [ ] **UPD-08**: Member can delete their own standup post

### Knowledge Sharing (KS)

- [ ] **KS-01**: Manager (admin) can create a KS session scoped to all team members, with fields: topic, description, references, presenter (user), session type (presentation/demo/workshop/Q&A), duration, date/time, tags
- [ ] **KS-02**: Supervisor can create a KS session scoped to their sub-team only (same fields as KS-01)
- [ ] **KS-03**: Knowledge Sessions appear as a dedicated tab inside the existing /schedule page (no new top-level route)
- [ ] **KS-04**: Members see only KS sessions in their scope (org-wide sessions + their sub-team's sessions)
- [ ] **KS-05**: Team members receive an in-app reminder before a session they are scoped to
- [ ] **KS-06**: Team members receive an in-app notification when a new session in their scope is created

### Weekly Board (BOARD)

- [ ] **BOARD-01**: Any team member can post a weekly markdown update to the Team Weekly Board
- [ ] **BOARD-02**: Board organizes posts by ISO week; members can navigate to past weeks
- [ ] **BOARD-03**: Markdown content is rendered safely (marked + DOMPurify — XSS protection required)
- [ ] **BOARD-04**: Any member can trigger an on-demand AI summary for the current week
- [ ] **BOARD-05**: AI weekly summary is generated automatically at end of week (Sunday 23:00 via APScheduler CronTrigger)
- [ ] **BOARD-06**: AI summary is stored/cached; re-generation overwrites the stored result for that week (30-min cooldown on on-demand trigger)
- [ ] **BOARD-07**: Member can edit their own weekly post
- [ ] **BOARD-08**: Member can delete their own weekly post

---

## Future Requirements (Deferred)

These were considered but deferred beyond v2.2:

- Scheduled standup bot reminders — causes notification fatigue; defer to v2.3+
- Mandatory standup gate (block app use until post submitted) — adoption risk; defer
- KS session recurring series (repeat weekly/monthly) — complexity; defer
- KS RSVP / attendance tracking — surveillance concern; defer
- Video link auto-generation for KS sessions — external integration; defer
- Cross-week AI summaries (monthly digest) — defer to v2.3+
- Per-post AI analysis or reactions — defer
- Board post comments / threading — duplicates chat; defer
- Email digests for any feature — out of scope for v1 (in-app only)

---

## Out of Scope

| Item | Reason |
|------|--------|
| Scheduled standup reminders | Notification fatigue; Geekbot-style bot reminders harm adoption |
| Attendance tracking on KS sessions | Surveillance anxiety; not aligned with tool's trust model |
| Threaded comments on board posts | Duplicates existing WebSocket chat |
| Mandatory standup enforcement | Kills voluntary adoption |
| Email notifications | In-app and push reminders are sufficient; email was excluded in v1 |
| Multi-org KS sessions | Single-org deployment; no cross-org scheduling |

---

## Traceability

_Filled by roadmapper when phases are assigned._

| REQ-ID | Phase | Notes |
|--------|-------|-------|
| UPD-01 | — | — |
| UPD-02 | — | — |
| UPD-03 | — | — |
| UPD-04 | — | — |
| UPD-05 | — | — |
| UPD-06 | — | — |
| UPD-07 | — | — |
| UPD-08 | — | — |
| KS-01  | — | — |
| KS-02  | — | — |
| KS-03  | — | — |
| KS-04  | — | — |
| KS-05  | — | — |
| KS-06  | — | — |
| BOARD-01 | — | — |
| BOARD-02 | — | — |
| BOARD-03 | — | — |
| BOARD-04 | — | — |
| BOARD-05 | — | — |
| BOARD-06 | — | — |
| BOARD-07 | — | — |
| BOARD-08 | — | — |
