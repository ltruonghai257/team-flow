---
phase: 19
slug: refactor-map-safety-baseline
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-27
---

# Phase 19 - Validation Strategy

> Documentation-phase validation contract for the refactor map and safety baseline.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Markdown artifact checks plus existing backend/frontend command capture |
| **Config file** | `.planning/phases/19-refactor-map-safety-baseline/19-RESEARCH.md` |
| **Quick run command** | `rtk proxy rg "STRUCT-01|STRUCT-02|STRUCT-03|D-01|D-16" .planning/phases/19-refactor-map-safety-baseline` |
| **Full suite command** | `rtk proxy node .codex/get-shit-done/bin/gsd-tools.cjs verify references .planning/phases/19-refactor-map-safety-baseline/19-REFACTOR-PLAYBOOK.md` |
| **Estimated runtime** | ~10 seconds for docs checks, excluding app baseline commands |

---

## Sampling Rate

- **After every task commit:** Run the quick artifact grep for requirement and decision coverage.
- **After every plan wave:** Verify the relevant Markdown artifact contains concrete source paths, target paths, and protected behavior.
- **Before `$gsd-verify-work`:** Run reference verification on `19-REFACTOR-PLAYBOOK.md` and confirm all baseline commands are either run or documented with failure reason and fallback.
- **Max feedback latency:** 60 seconds for documentation checks.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | STRUCT-02 | T-19-01 | Protected behavior inventory cannot omit auth/runtime surfaces silently | docs | `rtk proxy rg "/api/auth|/ws/chat|/health|app.main:app|alembic" .planning/phases/19-refactor-map-safety-baseline/19-SAFETY-BASELINE.md` | Yes | pending |
| 19-01-02 | 01 | 1 | STRUCT-02 | T-19-02 | Blocked checks require explicit fallback | docs | `rtk proxy rg "failure reason|fallback|blocked" .planning/phases/19-refactor-map-safety-baseline/19-SAFETY-BASELINE.md` | Yes | pending |
| 19-02-01 | 02 | 2 | STRUCT-01, STRUCT-03 | T-19-03 | Backend map names runtime and migration import targets | docs | `rtk proxy rg "backend/app/main.py|backend/alembic/env.py|backend/tests|app.main:app" .planning/phases/19-refactor-map-safety-baseline/19-BACKEND-MAP.md` | Yes | pending |
| 19-03-01 | 03 | 2 | STRUCT-01, STRUCT-03 | T-19-04 | Frontend map preserves route URLs and request behavior | docs | `rtk proxy rg "frontend/src/lib/api.ts|frontend/src/lib/apis|/tasks|/invite/accept|credentials" .planning/phases/19-refactor-map-safety-baseline/19-FRONTEND-MAP.md` | Yes | pending |
| 19-04-01 | 04 | 3 | STRUCT-01, STRUCT-02, STRUCT-03 | T-19-05 | Final playbook keeps downstream phases surgical | docs | `rtk proxy rg "Phase 20|Phase 21|Phase 22|temporary shim|removal" .planning/phases/19-refactor-map-safety-baseline/19-REFACTOR-PLAYBOOK.md` | Yes | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

Existing documentation and file inventory are enough for Phase 19. No new test framework or package install is required.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Target structure is understandable | STRUCT-01 | Readability and architectural fit are subjective | Review `19-REFACTOR-PLAYBOOK.md` and confirm backend/frontend target trees are concrete enough for Phase 20/21 |
| Protected behavior list is complete | STRUCT-02 | Critical flows span runtime, API, frontend, scheduler, and manual smoke checks | Compare playbook list against ROADMAP Phase 19 success criteria and CONTEXT D-11 through D-13 |
| Migration slices are small | STRUCT-03 | Plan sequencing needs engineering judgment | Confirm Phase 20/21 handoff lists migration slices, dependencies, and verification after each slice |

---

## Validation Sign-Off

- [x] All tasks have automated documentation verification or explicit manual review.
- [x] Sampling continuity: every plan has at least one artifact check.
- [x] Wave 0 covers all missing infrastructure references.
- [x] No watch-mode flags.
- [x] Feedback latency < 60s for docs checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** pending

