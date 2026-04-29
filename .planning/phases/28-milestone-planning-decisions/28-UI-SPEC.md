---
phase: 28
slug: milestone-planning-decisions
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-29
---

# Phase 28 - UI Design Contract

> Visual and interaction contract for the `/milestones` planning command view. Generated inline from Phase 28 context, research, and existing TeamFlow UI patterns.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none |
| Icon library | `lucide-svelte` |
| Font | Existing TeamFlow sans stack (`Inter`, `system-ui`, `sans-serif` from `frontend/tailwind.config.js`; do not introduce a new font family in this phase) |

Design rules:
- Keep the existing TeamFlow shell, dark surfaces, button primitives, badges, and modal language.
- Extend the current milestone page rather than creating a new dashboard pattern.
- Preserve existing route query highlight behavior for `milestone_id`.

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, dense badge padding, chip separators |
| sm | 8px | Inline metadata spacing, compact controls, decision row internals |
| md | 16px | Default card padding blocks, lane header spacing, form control rhythm |
| lg | 24px | Header sections, expanded card panels, modal sections |
| xl | 32px | Gap between summary row and planning lanes |
| 2xl | 48px | Empty-state and mobile section separation |
| 3xl | 64px | Not required on the core milestone surface |

Exceptions: existing `card`, `btn-*`, and modal primitives may keep their current rounded/padding values where they already align closely with this scale.

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 14px | 400 | 1.5 |
| Label | 12px | 500 | 1.4 |
| Heading | 16px | 600 | 1.35 |
| Display | 24px | 700 | 1.2 |

Rules:
- Page title uses `Display`; lane titles use `Heading`.
- Milestone card titles use `Heading`; collapsed metric labels and decision counts use `Label`.
- Expanded task rows and decision notes use `Body`.
- Do not use oversized hero typography anywhere on `/milestones`.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#111827` / `#0f172a` family | Page shell and background surfaces |
| Secondary (30%) | `#1f2937` / `#111827` family | Cards, lane surfaces, modal panels, grouped detail sections |
| Accent (10%) | `#4f46e5` | Active lane emphasis, expanded-card focus, summary metrics emphasis, interactive focus rings |
| Destructive | `#dc2626` / `#ef4444` | Delete decision, delete milestone, high-risk warnings |

Accent reserved for:
- Expanded or route-highlighted milestone cards
- Summary metrics with actionable attention value
- Interactive focus states
- Positive planning emphasis such as committed/active lane affordances

Color behavior:
- Planning-state lanes are distinguished by header treatment and badges, not by filling each whole lane with a strong color.
- Risk remains an overlay signal and should use amber/red badges on top of the card, not its own lane background.
- Decision statuses use compact chips with distinct but muted status colors:
  - `proposed`: neutral/indigo-tinted
  - `approved`: green-tinted
  - `rejected`: red-tinted
  - `superseded`: slate-tinted

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | `New Milestone` |
| Empty state heading | `No milestones yet` |
| Empty state body | `Create a milestone to start tracking planning, linked work, and key decisions.` |
| Error state | `Milestones unavailable. Refresh the page or try again after your connection recovers.` |
| Destructive confirmation | `Delete milestone`: `Delete this milestone?` |

Microcopy rules:
- Use planning language, not release-marketing language.
- Lane names remain exactly `Planned`, `Committed`, `Active`, and `Completed`.
- Risk labels should be short and operational: `At risk`, `Delayed`, `Blocked`, `Watch`.
- Decision labels should use the exact decision states from context: `Proposed`, `Approved`, `Rejected`, `Superseded`.
- Task-link affordances should point users to the existing task flow with language like `Open task`, not `Edit here`.

---

## Layout Contract

### Primary Surface

- `/milestones` remains a single route with four vertical bands:
  1. Page header and primary action row
  2. Compact summary metrics row
  3. Planning-state lane area
  4. Modal layer for milestone and decision forms
- The page should feel like a command view, not a gallery. Prioritize scan speed and dense but readable signal over decorative framing.

### Summary Metrics Row

- Place the summary row directly below the page header.
- Show compact cards or segmented panels for:
  - active milestones
  - risky milestones
  - proposed decisions
  - blocked tasks
- Metrics must be glanceable without opening any milestone card.

### Planning-State Lanes

- Render four lanes in this order:
  1. `Planned`
  2. `Committed`
  3. `Active`
  4. `Completed`
- Desktop may use a multi-column lane layout; mobile must stack the same four lanes as collapsible sections.
- Do not introduce a fifth `Risk` lane. Risk is shown within cards and lane summaries only.

### Milestone Cards

- Each milestone is represented by a single card inside its derived lane.
- Collapsed card header must show:
  - title
  - project name
  - planning-state badge
  - risk overlay badge when applicable
  - due date and optional start date span
  - task progress summary
  - decision counts by status
- Expanded cards may reveal:
  - grouped linked task list
  - structured milestone decisions list
  - milestone-level actions for edit/delete
  - decision CRUD controls

---

## Interaction Contract

- Milestone cards are expandable in place; expansion does not navigate away.
- Active and risky milestones are expanded by default.
- Quiet planned or completed milestones may start collapsed.
- Task rows inside an expanded milestone must link to or open the existing task flow via `/tasks?task_id={id}` behavior.
- Do not add inline task status editing inside milestone cards in this phase.
- Decision CRUD is allowed inside expanded milestone cards only.
- Manual override of derived planning state is not allowed.
- The existing milestone create/edit modal remains valid, but the design should accommodate a richer detail surface around it.

---

## Task Detail Contract

- Expanded task lists show only tasks already linked to the milestone.
- Group tasks by status first, then due date within each group.
- Each task row should show:
  - title
  - status
  - assignee when present
  - due date
  - priority or blocked signal when meaningful
- Collapsed milestone cards still show aggregate task counts:
  - total
  - done
  - blocked
  - completion percentage

---

## Decision Contract

- Decision entries are a first-class UI block within expanded milestone cards.
- Each entry should show:
  - title
  - decision status
  - note
  - created date
  - linked task affordance when present
- Collapsed cards must show decision counts by status without exposing full notes.
- Decision controls should be compact and embedded in the detail panel, not placed as a separate global dashboard.
- The surface should make it visually obvious that decisions are informational records, not approvals workflow steps.

---

## State And Feedback

- Loading state: centered spinner inside the content area.
- Empty state: reuse the existing milestone empty-state mood, but mention planning and decision visibility.
- Error state: one concise recovery sentence; no verbose exception text in the layout.
- Highlighted state: route-selected or recently focused milestone uses accent ring treatment consistent with current page behavior.
- Expanded state: use subtle border and surface elevation, not bright panel color changes.
- Hover state: cards and compact action buttons may slightly tint or raise, but the page should remain calm and operational.

---

## Mobile Contract

- Lanes stack vertically as collapsible sections in the same order as desktop.
- Summary metrics can wrap to two rows, but each metric remains readable without horizontal scrolling.
- Expanded milestone cards should reveal tasks and decisions in a single-column flow.
- Dense badge/count clusters may wrap, but must not overflow card edges.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party | none required for this phase | no new registry additions allowed in this UI contract |

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-29
