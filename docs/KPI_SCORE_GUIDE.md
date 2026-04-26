# KPI Score Guide

This document explains how every number on the **Performance Dashboard → Overview** tab is calculated, what the bands mean, and how to interpret a member's scorecard.

---

## Overall KPI Score (0–100)

The KPI score is a **weighted average** of five dimension scores.
Default weights (configurable in the **Settings** tab):

| Dimension | Default Weight |
|---|---|
| Workload | 20% |
| Velocity | 25% |
| Cycle Time | 20% |
| On-Time Rate | 20% |
| Defects / Quality | 15% |

**Formula:**

```
KPI Score = (Workload × 0.20) + (Velocity × 0.25) + (Cycle Time × 0.20)
          + (On-Time × 0.20) + (Defects × 0.15)
```

Weights can be changed in **Settings → KPI Weight Settings**. They must always sum to **100%**.

---

## Score Bands

| Band | Range | Colour | Meaning |
|---|---|---|---|
| **Good** | 80–100 | 🟢 Green | Member is performing well across all dimensions |
| **Fair** | 60–79 | 🟡 Yellow | Some dimensions need attention |
| **At Risk** | 0–59 | 🔴 Red | Multiple dimensions are underperforming |

---

## Dimension Scores

Each dimension returns a score between **0 and 100**. Hover over the `ⓘ` icon on any scorecard row to see the bands inline.

---

### 1. Workload (active task count)

Measures how many tasks are currently assigned and **not yet completed**.

| Active Tasks | Score |
|---|---|
| ≤ 7 | **100** — healthy bandwidth |
| 8–10 | **70** — approaching capacity |
| > 10 | **40** — overloaded |

> **Why this matters:** Too many open tasks increases context-switching, raises cycle time, and is a leading indicator of upcoming overdue items.

---

### 2. Velocity (tasks completed in 30 days)

Measures output volume over the last 30 days. Completion is determined by `CustomStatus.is_done = true` (not the legacy `done` enum).

| Tasks Completed | Score |
|---|---|
| 0 | 0 |
| 1 | 10 |
| 5 | 50 |
| 10+ | **100** (capped) |

**Formula:** `min(100, completed_30d × 10)`

> **Why this matters:** Velocity reflects sustained delivery. High velocity with low quality (many bugs) shows up in the Defects dimension.

---

### 3. Cycle Time (average hours from creation → completion)

Measures how long it takes to move a task from **created** to **done** on average.

| Avg Hours | Score |
|---|---|
| ≤ 48 h (≤ 2 days) | **100** — fast delivery |
| 49–120 h (2–5 days) | **70** — acceptable |
| > 120 h (> 5 days) | **40** — slow |
| No completed tasks | **40** — conservative default |

> **Why this matters:** Long cycle times signal blockers, unclear requirements, or inadequate capacity. Pair with Workload to distinguish "busy" from "blocked".

---

### 4. On-Time Rate (%)

Percentage of completed tasks that were finished **on or before their due date**, among tasks that have a due date set.

| On-Time % | Score |
|---|---|
| 100% | **100** |
| 80% | **80** |
| 60% | **60** |
| 0% | **0** |

**Formula:** `score = round(on_time_count / total_with_due_date × 100)`  
Tasks without a due date are excluded (neither penalised nor rewarded).

> **Why this matters:** On-time rate directly measures promise-keeping. A member with high velocity but low on-time rate is completing work but not the right work at the right time.

---

### 5. Defects / Quality (bug MTTR)

Mean Time to Resolve (MTTR) for **bug-type tasks** assigned to this member. Measured from bug creation to completion.

| Avg MTTR | Score |
|---|---|
| ≤ 72 h (≤ 3 days) | **100** — fast resolution |
| 73–168 h (3–7 days) | **70** — acceptable |
| > 168 h (> 7 days) | **40** — slow |
| No bugs assigned | **100** — best case |

> **Why this matters:** Slow bug resolution drags quality and blocks other team members. Members with no bugs are not penalised.

---

## Trend Indicator

The trend arrow on the scorecard is derived from the **current KPI score band** (not a historical comparison, which requires time-series data):

| Arrow | Score | Meaning |
|---|---|---|
| ↑ Up | ≥ 80 | Good standing |
| → Stable | 60–79 | Acceptable, monitor |
| ↓ Down | < 60 | Needs attention |

---

## Alert Reasons

When a dimension score falls below 70, an alert reason appears on the scorecard:

| Reason Label | Trigger |
|---|---|
| High workload | Workload score < 70 |
| Low velocity | Velocity score < 70 |
| Slow cycle time | Cycle time score < 70 |
| Low on-time rate | On-time score < 70 |
| High bug MTTR | Defects score < 70 |

Severity:
- **Critical** (red) — score = 40 (worst band)
- **Warning** (yellow) — score = 70 (middle band)

---

## "Needs Attention" Section

A member appears in **Needs Attention** if either:
- Their overall KPI score is **below 70**, OR
- They have at least one **critical** alert reason

---

## Adjusting Weights

Supervisors can re-weight dimensions in **Settings → KPI Weight Settings**.

Rules:
1. All five weights must sum to exactly **100**.
2. Changes take effect immediately on the next Overview load.
3. Weights are stored per sub-team — different teams can have different priorities.

**Example** — a team focused on bug-free releases might use:

| Dimension | Custom Weight |
|---|---|
| Workload | 15% |
| Velocity | 20% |
| Cycle Time | 15% |
| On-Time Rate | 20% |
| Defects | **30%** |

---

## Data Freshness

All KPI data is **computed live** on each page load — there is no caching layer. The timestamp shown under the page title reflects when the last request completed.
