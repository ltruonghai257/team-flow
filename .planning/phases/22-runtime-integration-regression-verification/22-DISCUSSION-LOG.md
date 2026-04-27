# Phase 22: Runtime Integration & Regression Verification — Discussion Log

**Date:** 2026-04-27
**Mode:** Resume from checkpoint (2 of 4 areas previously completed)

This log captures the questions asked, options presented, and selections made during `/gsd-discuss-phase 22`. Decisions are persisted in `22-CONTEXT.md` (D-01..D-14). This file is for human audit only and is not consumed by downstream agents.

---

## Areas Already Completed (from checkpoint)

1. **Runtime Entrypoint Policy** → D-01..D-03 (see `22-CONTEXT.md`)
2. **Verification Command Floor** → D-06..D-08 (see `22-CONTEXT.md`)

Decision-by-decision log for these areas is preserved in the original `22-DISCUSS-CHECKPOINT.json` archived from this session (deleted post-merge per workflow).

---

## Area 3 — Smoke Test Evidence

### Q1. What evidence format should each smoke check produce so the phase is verifiably complete?

**Options presented:**
1. Playwright covers it, manual = checklist+notes
2. Screenshots + curl/log snippets per item
3. Pass/fail checklist only
4. Promote critical gaps to Playwright

**User selected:** Option 1 — Playwright covers it, manual = checklist+notes
**→ Locked as D-09**

### Q2. Where should the smoke evidence live?

**Options presented:**
1. Single `22-VERIFICATION.md`
2. Per-plan verification sections
3. `22-VERIFICATION.md` + raw artifacts dir

**User response:** "give recommendation"
**Claude's recommendation (accepted):** Option 1 — single `22-VERIFICATION.md`. Reasons: matches existing GSD pattern in repo, single point of audit for milestone close-out, Playwright HTML report can be referenced by path rather than duplicated.
**→ Locked as D-10**

### Q3. If a smoke check fails or is blocked by local environment, what's the rule?

**Options presented:**
1. Fallback allowed, mirroring Phase 19
2. Hard block — must pass locally
3. Hard block on prod-critical, fallback OK on dev-only

**User selected:** Option 1 — Fallback allowed, mirroring Phase 19
**→ Locked as D-11**

---

## Area 4 — Migration Notes & Shim Cleanup

### Q4. What should the migration/dev-notes deliverable contain?

**Options presented:**
1. Path table + shim ledger + runbook
2. Path table only
3. Aggregate from Phase 19/20/21 docs

**User selected:** Option 1 — Path table + shim ledger + runbook
**→ Locked as D-12**

### Q5. Where should this dev-notes doc live and where should top-level pointers update?

**Options presented:**
1. `docs/MIGRATION-V2.1.md` + README link
2. Phase-only: `22-MIGRATION-NOTES.md`
3. Update `README/CLAUDE.md` inline + 22 summary

**User response:** "you decide"
**Claude's selection (accepted):** Option 1 — `docs/MIGRATION-V2.1.md` + one-line pointer in `README.md` and `backend/CLAUDE.md`. Reasons: matches existing `docs/` pattern (`docs/KPI_SCORE_GUIDE.md`), persists past milestone archival, single source of truth, minimal sprawl into top-level files.
**→ Locked as D-13**

### Q6. Shim ledger removal trigger — how do we mark when each shim is safe to delete?

**Options presented:**
1. Per-shim removal trigger + grep gate
2. Time-boxed: "remove next milestone"
3. No removal commitment

**User response:** "you decide all remaining"
**Claude's selection (accepted):** Option 1 — Per-shim removal trigger + grep gate. Reasons: lightweight, objective, complements existing "removal deferred to cleanup milestone" deferred-idea note by adding a *verifiable* trigger; calendar-only triggers tend to slip silently.
**→ Locked as D-14**

---

## Deferred Ideas Captured

(no new deferred ideas in this resume session — pre-existing deferreds in `22-CONTEXT.md` retained as-is)

---

## Outcome

All 4 gray areas closed. `22-CONTEXT.md` updated with D-09..D-14. Checkpoint deleted. Phase 22 ready for `/gsd-plan-phase 22`.
