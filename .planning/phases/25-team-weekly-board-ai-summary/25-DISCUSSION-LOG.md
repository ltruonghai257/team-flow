# Phase 25: Team Weekly Board & AI Summary - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-28T14:45:02+07:00
**Phase:** 25-team-weekly-board-ai-summary
**Areas discussed:** Posting model, Board layout, Week navigation, Summary experience, Markdown authoring

---

## Posting Model

| Option | Description | Selected |
|--------|-------------|----------|
| One post per member per week, editable in place | Clean weekly board, simpler summary input, and aligned with "your weekly update". | |
| Multiple posts per member per week | Flexible incremental updates, but noisier and harder to summarize cleanly. | |
| One primary weekly post, plus optional short follow-up append entries | Structured weekly anchor with lightweight incremental additions. | yes |
| You decide | Let the agent lock the recommendation from existing `/updates` and v2.2 patterns. | |

**User's choice:** One primary weekly post, plus optional short follow-up append entries.
**Notes:** This shaped the board as a digest, not a chat-style feed.

---

## Board Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Summary-first week view | Week header and AI summary at top, followed by member posts and follow-up entries. | yes |
| Feed-first card layout | Reuse `/updates` style with composer then reverse-chronological cards. | |
| Two-column desktop board, stacked mobile | More editorial, but a newer layout pattern. | |
| You decide | Let the agent pick from current `/updates` and `/schedule` patterns. | yes |

**User's choice:** You decide.
**Notes:** Locked as summary-first week view because it best matches the chosen posting model and the phase's AI summary goal.

---

## Week Navigation

| Option | Description | Selected |
|--------|-------------|----------|
| Previous / Current / Next controls only | Cleanest current-week browsing. | |
| Previous / Current / Next plus a compact week picker | Balance between easy current-week use and archive access. | yes |
| Archive sidebar of past weeks | Stronger history surface, but heavier UI. | |
| You decide | Let the agent choose the best fit for the summary-first board. | yes |

**User's choice:** You decide.
**Notes:** Locked as previous/current/next controls plus a compact week picker.

---

## Summary Experience

| Option | Description | Selected |
|--------|-------------|----------|
| Summary panel always at the top of the selected week | Stored summary visible immediately; empty state and cooldown behavior are clear. | yes |
| Summary starts collapsed, user expands when needed | Keeps posts dominant, but makes summary less central. | |
| Summary appears only after the user clicks summarize | Minimal, but hides stored summaries for past weeks. | |
| You decide | Let the agent choose the most useful behavior for a weekly digest board. | yes |

**User's choice:** You decide.
**Notes:** Locked as a persistent top summary panel with stored result visibility and cooldown-aware regenerate behavior.

---

## Markdown Authoring

| Option | Description | Selected |
|--------|-------------|----------|
| Textarea with sanitized preview toggle | Good balance of simple authoring, safe rendering, and formatting verification. | yes |
| Live split preview while typing | Richer, but heavier and more fragile on mobile. | |
| Textarea only, rendered after save | Fastest, but weak for markdown confidence. | |
| You decide | Let the agent pick the fit for the digest workflow. | yes |

**User's choice:** User asked to continue after raising management comments.
**Notes:** Interpreted as approval to lock the recommended sanitized preview toggle. The management comments request was captured as a deferred future phase because board post comments/threading are out of scope for v2.2.

---

## Codex's Discretion

- Exact naming for append-entry tables/schemas/endpoints.
- Exact empty summary and cooldown copy.
- Exact compact week-picker UI.
- Exact digest ordering of members/posts.

## Deferred Ideas

- Management comments on another member's board post - future phase. This is a comments/threading capability and remains out of scope for Phase 25.
