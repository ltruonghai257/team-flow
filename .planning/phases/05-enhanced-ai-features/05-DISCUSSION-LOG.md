# Phase 5: Enhanced AI Features - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-23
**Phase:** 05-enhanced-ai-features
**Areas discussed:** Task Breakdown UX, Project Summary Entry Point, AI Chat Intent Routing, Subtask Fields & Scope

---

## Task Breakdown UX

| Option | Description | Selected |
|--------|-------------|----------|
| New tab in AiTaskInput | 4th tab alongside NLP/JSON/Form | ✓ |
| Separate button outside modal | Standalone drawer/panel | |
| Replace current NLP tab | Upgrade NLP to handle both | |

**Review flow:**
| Option | Description | Selected |
|--------|-------------|----------|
| Inline card list in modal | Editable cards, per-card milestone, delete + Create All | ✓ |
| Checklist with edit-on-click | Compact checklist, expandable | |
| Replace task form | Breakdown mode replaces form entirely | |

**Context timing:**
| Option | Description | Selected |
|--------|-------------|----------|
| Before — required inputs first | Project + milestone + assignee before description | ✓ |
| After — description first | Scratchpad style | |

---

## Project Summary Entry Point

| Option | Description | Selected |
|--------|-------------|----------|
| Add /projects/[id] detail route | New page with Summarize button | |
| Inline on project card in list | Button on existing card | ✓ |
| Inside existing project modal | Summarize tab in modal | |

**Summary content:**
| Option | Description | Selected |
|--------|-------------|----------|
| Short paragraph (3-5 sentences) | Health-check style | |
| Structured report with sections | Milestone / Overdue / Completions / At-Risk | ✓ |
| One-liner status + expand | Compact with expand | |

**Display:**
| Option | Description | Selected |
|--------|-------------|----------|
| Expandable section below card | Slides open, cached in state | ✓ |
| Modal/dialog | Summary in modal | |

---

## AI Chat Intent Routing

| Option | Description | Selected |
|--------|-------------|----------|
| Backend keyword detection + data injection | Regex match → fetch project → inject context | ✓ |
| LiteLLM function/tool calling | Tool call API, LLM decides when to call | |
| Enriched system prompt | Project list in every system prompt | |

**Name matching:**
| Option | Description | Selected |
|--------|-------------|----------|
| Case-insensitive partial match | Substring match, clarify on ambiguity | ✓ |
| Exact match only | Fail gracefully if not found | |

---

## Subtask Fields & Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Title + priority + estimated_hours only | Lean output | |
| Include brief description | title + priority + hours + 1-2 sentence desc | ✓ (user: "both of above") |

**Milestone:**
| Option | Description | Selected |
|--------|-------------|----------|
| Default + per-subtask override | User sets default, can override per card | ✓ (user: "Hybrid") |
| Default + AI suggests per-subtask | AI assigns milestones based on names | |

**Count:**
| Option | Description | Selected |
|--------|-------------|----------|
| 3–8 subtasks, prompt-guided | AI decides based on complexity | ✓ |
| Fixed 5 tasks | Always exactly 5 | |

---

## Claude's Discretion

- Loading state treatment on Summarize button
- Exact regex patterns for chat intent
- Error handling for AI timeout / malformed JSON
- Icon choice for Summarize button
- Assignee field label wording in breakdown tab
