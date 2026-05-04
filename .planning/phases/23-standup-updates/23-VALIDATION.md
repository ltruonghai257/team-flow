---
phase: 23
slug: standup-updates
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-28
---

# Phase 23 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none — project uses manual browser/curl smoke testing; no automated test suite |
| **Config file** | none |
| **Quick run command** | `curl -s http://localhost:8000/api/updates/ -H "Authorization: Bearer $TOKEN" | python3 -m json.tool` |
| **Full suite command** | Manual browser walkthrough of /updates page smoke tests (see Per-Task map below) |
| **Estimated runtime** | ~5 minutes for full manual walkthrough |

---

## Sampling Rate

- **After every task commit:** Verify backend endpoint responds (curl) OR SvelteKit build compiles without errors
- **After every plan wave:** Full manual smoke test of /updates page
- **Before `/gsd-verify-work`:** All Manual-Only Verifications completed
- **Max feedback latency:** 120 seconds per task

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Secure Behavior | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------------|-----------|-------------------|--------|
| 23-migration | 01 | 1 | UPD-04 | JSONB snapshot stored server-side, not client-side | manual | `alembic upgrade head` exits 0 | ⬜ pending |
| 23-models | 01 | 1 | UPD-01, UPD-04 | StandupPost.author_id enforced server-side | manual | `python3 -c "from app.models.updates import StandupPost, StandupTemplate; print('OK')"` | ⬜ pending |
| 23-router-post | 02 | 1 | UPD-01, UPD-04, UPD-05 | POST /api/updates/ freezes snapshot at submit time | manual | `curl -s -X POST http://localhost:8000/api/updates/ ...` | ⬜ pending |
| 23-router-get | 02 | 1 | UPD-05, UPD-06 | GET /api/updates/ returns only sub-team posts | manual | `curl -s http://localhost:8000/api/updates/?cursor=&author_id=&date=` | ⬜ pending |
| 23-router-put | 02 | 1 | UPD-07 | PUT /api/updates/{id} rejects edits by non-author (403) | manual | `curl -s -X PUT ... (different user token)` returns 403 | ⬜ pending |
| 23-router-delete | 02 | 1 | UPD-08 | DELETE /api/updates/{id} rejects non-author (403) | manual | `curl -s -X DELETE ... (different user token)` returns 403 | ⬜ pending |
| 23-template-api | 02 | 1 | UPD-02, UPD-03 | GET /api/updates/template returns default; supervisor PATCH updates team template | manual | `curl -s http://localhost:8000/api/updates/template` returns 6-field default | ⬜ pending |
| 23-frontend-page | 03 | 2 | UPD-01, UPD-05 | /updates route loads; form panel collapses by default | manual | Browser: navigate to /updates, verify page loads and form is collapsed | ⬜ pending |
| 23-frontend-submit | 03 | 2 | UPD-01, UPD-04 | Submit creates post; snapshot visible in card | manual | Browser: fill form, submit, verify card appears with snapshot | ⬜ pending |
| 23-frontend-filter | 03 | 2 | UPD-06 | Filter by author or date fetches fresh results | manual | Browser: apply author filter, verify feed updates | ⬜ pending |
| 23-frontend-edit | 03 | 2 | UPD-07 | Inline edit shows only on own posts; saves correctly | manual | Browser: edit own post, verify inline form; verify no edit button on other's post | ⬜ pending |
| 23-frontend-delete | 03 | 2 | UPD-08 | Inline delete confirm; removes card on success | manual | Browser: delete own post, verify card removed | ⬜ pending |
| 23-template-mgmt | 04 | 2 | UPD-03 | Supervisor sees template editor; member does not | manual | Browser: login as supervisor, verify template section visible; login as member, verify hidden | ⬜ pending |
| 23-nav | 04 | 2 | UPD-05 | /updates appears in nav for all authenticated users | manual | Browser: verify "Updates" nav link present | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

None — no automated test framework to install. All verification is manual smoke testing.

*Existing infrastructure covers all phase requirements (no test framework needed; manual verification documented in Per-Task map above).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Frozen snapshot doesn't change after task status update | UPD-04 | Requires two-step state change in browser | 1. Submit standup. 2. Change a task's status. 3. Reload /updates. 4. Verify post snapshot shows original status. |
| Non-author cannot edit/delete others' posts | UPD-07, UPD-08 | Requires multi-user session test | 1. Login as user A, submit post. 2. Login as user B, navigate to /updates. 3. Verify no Edit/Delete buttons on user A's card. |
| Template field changes affect new posts only | UPD-03 | Requires sequential test with existing data | 1. Submit a post. 2. Supervisor removes a field from template. 3. Verify existing post still shows old field. 4. Submit new post — verify removed field absent. |
| Supervisor template editor not visible to regular member | UPD-03 | Role-gated UI check | 1. Login as member. 2. Navigate to /updates. 3. Verify "Configure standup template" section is NOT visible. |
| Cursor pagination appends posts (no duplicate/missing) | UPD-05, UPD-06 | Requires >20 posts in feed | 1. Create 21+ posts. 2. Load page. 3. Click "Load more". 4. Verify 21st post appears; no duplicates. |

---

## Validation Sign-Off

- [ ] All tasks have manual verification steps documented
- [ ] Security behaviors (403 on non-author edit/delete) verified via curl
- [ ] Snapshot immutability verified manually (two-step test)
- [ ] Role-gate (supervisor template editor) verified manually
- [ ] `nyquist_compliant: true` set in frontmatter after all checks pass

**Approval:** pending
