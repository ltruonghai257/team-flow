---
phase: 14
slug: sprint-model
status: verified
threats_open: 0
asvs_level: 1
created: 2026-04-26T07:57:00.000Z
---

# Phase 14 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| DB schema | Model structures and migrations do not process untrusted input directly, but establish valid constraints | Sprint data, task relationships |
| API Router | Validates incoming payloads to ensure correct typing and format | Sprint CRUD, task reassignment |
| Client UI | User inputs are processed by UI components before API transmission | Sprint creation, task mapping |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-14-01 | Tampering | DB Migration | mitigate | Use autogenerate and review; named foreign keys; checkfirst=True for enum | closed |
| T-14-02 | Information Disclosure | Sprints Router | mitigate | get_sub_team dependency filters by sub_team_id | closed |
| T-14-03 | Denial of Service | Sprint Close | mitigate | Pydantic Dict[int, Optional[int]] schema limits payload size | closed |
| T-14-04 | Spoofing | Sprint Close Modal | mitigate | API sub-team checks prevent unauthorized task mapping | closed |
| T-14-05 | Tampering | Kanban Board | mitigate | Backend task API validates write permissions | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-04-26 | 5 | 5 | 0 | gsd-secure-phase workflow |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-04-26
