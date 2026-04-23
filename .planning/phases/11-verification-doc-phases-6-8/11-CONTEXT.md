# Phase 11: Generate Verification Documentation (Phases 6-8) - Context

**Gathered:** 2026-04-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Create VERIFICATION.md files for Phases 6, 7, and 8 to enable requirement verification, create missing VALIDATION.md files, and fix VALIDATION.md for Phase 6 (set nyquist_compliant: true).

This is a documentation-only phase — no code changes.

### Phase 6 — Mobile Responsive UI
- Requirement: REQ-06
- Delivers: Mobile sidebar, responsive routes, Kanban scroll, task forms

### Phase 7 — Azure Deployment & CI/CD
- Requirement: REQ-05
- Delivers: Azure App Service deployment, CI/CD pipeline, deploy scripts

### Phase 8 — User Invite & Team Management
- Requirement: (invitation flow, no specific REQ number)
- Delivers: Email invites, validation codes, team add/invite endpoints, invite acceptance UI
</domain>

<decisions>
## Locked Decisions

1. **Phase 11 will generate 3 VERIFICATION.md files** — one per phase, following the same format as Phases 1-5
2. **VALIDATION.md files for Phases 6, 7, and 8 will be created** — Phase 6 needs nyquist fix, Phases 7 and 8 don't exist yet
3. **Evidence standards:** code snippets, API response samples, terminal logs, plan summaries, screenshot descriptions
4. **Status values:** "✅ Verified", "⚠️ Partial", "❌ Not Verified"
5. **Frontmatter format:**
   ```yaml
   ---
   phase: "NN"
   status: verified
   verified_date: "YYYY-MM-DD"
   ---
   ```
6. **VALIDATION.md frontmatter:**
   ```yaml
   ---
   phase: "NN"
   slug: "phase-slug"
   status: complete
   nyquist_compliant: true
   wave_0_complete: true
   created: "YYYY-MM-DD"
   ---
   ```
7. **Nyquist compliance:** All verification docs must have Requirements Coverage tables with acceptance criteria from REQUIREMENTS.md
8. **Phase 6 VALIDATION.md** must have `nyquist_compliant: true` (fixing any existing `false`)
</decisions>

<specifics>
## Implementation Details

### Files to read for Phase 6 evidence:
- `frontend/src/routes/+layout.svelte` (sidebar, mobile responsive)
- `frontend/src/lib/components/tasks/KanbanBoard.svelte` (mobile touch)
- `frontend/src/routes/performance/+page.svelte` (responsive table)
- `frontend/tests/mobile/sidebar.spec.ts` (Playwright mobile tests)
- `frontend/playwright.config.ts` (mobile test config)
- Phase 6 plan summaries (if any)

### Files to read for Phase 7 evidence:
- `scripts/setup-azure.sh`
- `scripts/deploy.sh`
- `.github/workflows/deploy.yml`
- `backend/.env.azure.example`
- `Dockerfile` (monolith)
- `docker-compose.yml`
- `backend/Dockerfile`, `frontend/Dockerfile`
- `.gitlab-ci.yml`
- Phase 7 plan summaries (if any)

### Files to read for Phase 8 evidence:
- `backend/app/routers/invites.py` (invite endpoints)
- `backend/app/models.py` (Invite model)
- `frontend/src/routes/invite/accept/+page.svelte` (invite acceptance)
- `backend/app/scripts/` (email templates)
- Phase 8 plan summaries (if any)

### Requirements to verify:
- Phase 6 / REQ-06: Mobile sidebar (hamburger), all routes responsive, Kanban scroll, performance table scroll, task forms mobile-friendly
- Phase 7 / REQ-05: Azure scripts, CI/CD pipeline, env template, startup command, README docs, deployed URLs
- Phase 8: Invite email with token/code, validate endpoint, accept endpoint, frontend invite modal, invite acceptance page, pending invites list, role guards
</specifics>

<deferred>
## Deferred Ideas

None — phase scope is strictly documentation generation.
</deferred>
