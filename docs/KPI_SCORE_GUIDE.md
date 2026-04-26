# KPI Score Guide

This document explains how every number on the **Performance Dashboard → Overview** tab is calculated, what the bands mean, and how to interpret a member's scorecard — with real scenarios throughout.

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

### 📖 Worked example — Alice's score of 88

Alice has the following raw dimension scores this month:

| Dimension | Raw Score | Weight | Contribution |
|---|---|---|---|
| Workload | 100 | 20% | 20.0 |
| Velocity | 90 | 25% | 22.5 |
| Cycle Time | 100 | 20% | 20.0 |
| On-Time Rate | 85 | 20% | 17.0 |
| Defects | 100 | 15% | 15.0 |
| **Total** | — | **100%** | **94.5 → rounded to 88** |

> Her weakest point is On-Time Rate (85), which pulls the overall score down slightly. Everything else is in the top band.

---

## Score Bands

| Band | Range | Colour | Meaning |
|---|---|---|---|
| **Good** | 80–100 | 🟢 Green | Member is performing well across all dimensions |
| **Fair** | 60–79 | 🟡 Yellow | Some dimensions need attention |
| **At Risk** | 0–59 | 🔴 Red | Multiple dimensions are underperforming |

### 📖 Scenario — Reading a scorecard at a glance

You open the dashboard on a Monday morning and see three cards:

- **David Park — 93 🟢** → Ship it. Everything green, no action needed.
- **Eva Rossi — 63 🟡** → Two yellow alerts. Schedule a 1:1 to understand what's blocking her on-time delivery.
- **Carla Müller — 55 🔴** → Appears in "Needs Attention". Two critical alerts (overloaded + slow cycle time). Reassign tasks today before sprint planning.

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

#### 📖 Scenario — Spot the overload before it becomes a miss

Ben has 11 active tasks → Workload score **40** → alert "High workload" (critical).  
His cycle time is also rising (72 h average). This combination tells you: he is not blocked, he is just handling too much. Before the next sprint, move 3–4 tasks to another member.

Compare: Alice has 6 active tasks → Workload **100**. She has room for 1–2 more items if the sprint backlog is large.

---

### 2. Velocity (tasks completed in 30 days)

Measures output volume over the last 30 days. Completion is determined by `CustomStatus.is_done = true`.

| Tasks Completed | Score |
|---|---|
| 0 | 0 |
| 3 | 30 |
| 5 | 50 |
| 10+ | **100** (capped) |

**Formula:** `min(100, completed_30d × 10)`

> **Why this matters:** Velocity reflects sustained delivery. High velocity with low quality (many bugs) shows up in the Defects dimension.

#### 📖 Scenario — Low velocity isn't always bad performance

Ben completed 5 tasks last month → Velocity **50** → alert "Low velocity" (warning).  
But: his 5 tasks were all large features. Check the Cycle Time and On-Time dimensions. If both are green, Ben is working on bigger scope, not slacking. Consider splitting large tasks so the dashboard reflects real throughput.

Contrast: Eva completed 6 tasks → Velocity **60**. She's hitting the middle band. If she was completing 10 last quarter, that drop is worth a conversation.

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

#### 📖 Scenario — Busy vs blocked

**Case A:** Carla has 12 active tasks and a 130 h average cycle time → Workload **40**, Cycle Time **40**.  
Both are critical. Diagnosis: **overloaded**. Solution: reduce her queue.

**Case B:** David has 5 active tasks and a 145 h average cycle time → Workload **100**, Cycle Time **40**.  
Workload is fine but cycle time is bad. Diagnosis: **blocked** (waiting on review, dependencies, or unclear requirements). Solution: remove the blocker, not reassign tasks.

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

#### 📖 Scenario — High velocity, low on-time

Eva completed 6 tasks but only 3 of her 6 tasks with due dates were on time → On-Time **50** → alert "Low on-time rate".  
She is productive but finishing the wrong tasks first. In your next 1:1, review how she prioritises her queue. Her cycle time (70) is fine, so the issue is priority, not speed.

**Case B — legitimate lateness:** Alice had 1 task delayed by a third-party API outage → On-Time **90**. The drop is minor (1 late task out of 10) and clearly external. No action needed; the score self-corrects next cycle.

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

#### 📖 Scenario — MTTR spike after a release

After the v2.3 release, your team gets 5 new bugs. Eva is assigned 4 of them. She resolves 2 within 24 h but the other 2 take 10 days each (blocked by a missing vendor fix). Her MTTR climbs to 180 h → Defects score **40** → alert "High bug MTTR".

The score is technically correct, but the context matters. Add a note in the bug task that 2 issues are vendor-blocked. When they're resolved, her MTTR resets to normal next month.

David has no bugs this sprint → Defects **100** automatically. He is not rewarded beyond the cap — the score simply reflects no quality debt.

---

## Trend Indicator

| Arrow | Score | Meaning |
|---|---|---|
| ↑ Up | ≥ 80 | Good standing |
| → Stable | 60–79 | Acceptable, monitor |
| ↓ Down | < 60 | Needs attention |

#### 📖 Scenario — Using trend to prioritise your week

On Monday you see:
- Alice ↑ 88 → No meeting needed. Send a quick kudos.
- Ben → 72 → Check in on his Velocity warning mid-week.
- Carla ↓ 55 → Block 30 min today. Review her task queue together and reassign before things slip further.

---

## Alert Reasons

When a dimension score falls below 70, an alert reason appears on the scorecard:

| Reason Label | Trigger | Severity |
|---|---|---|
| High workload | Workload score = 40 | 🔴 Critical |
| Low velocity | Velocity score < 70 | depends on band |
| Slow cycle time | Cycle time score = 40 | 🔴 Critical |
| Low on-time rate | On-time score < 70 | depends on band |
| High bug MTTR | Defects score = 40 | 🔴 Critical |

- **Critical** (red `⚠`) — score = 40 (worst band). Act this week.
- **Warning** (yellow `!`) — score = 70 (middle band). Monitor and discuss.

#### 📖 Scenario — Two alerts vs one alert

**Carla** has two critical alerts (High workload + Slow cycle time) → these always go together when someone is overloaded. One action (reduce queue) fixes both.

**Eva** has two warning alerts (Low on-time rate + High bug MTTR) → these are independent problems. On-time is a prioritisation issue; bug MTTR is a resolution-speed issue. They need separate conversations.

---

## "Needs Attention" Section

A member appears here if either:
- Their overall KPI score is **below 70**, OR
- They have at least one **critical** alert reason

#### 📖 Scenario — Who belongs here?

| Member | Score | Alerts | In "Needs Attention"? |
|---|---|---|---|
| Alice | 88 | none | ❌ No |
| Ben | 72 | 1 warning | ❌ No (score ≥ 70, no critical) |
| Eva | 63 | 2 warnings | ✅ Yes (score < 70) |
| Carla | 55 | 2 critical | ✅ Yes (score < 70 AND critical alerts) |

Ben sits just above the threshold. If he misses one more delivery this month, his score will cross below 70 and he'll appear here too — use the "Stable →" trend as an early warning.

---

## Adjusting Weights

Supervisors can re-weight dimensions in **Settings → KPI Weight Settings**.

Rules:
1. All five weights must sum to exactly **100**.
2. Changes take effect on the next Overview load.
3. Weights are stored **per sub-team** — different teams can prioritise differently.

### 📖 Scenario A — Quality-focused team (QA / release team)

This team ships to production and bug escapes are very costly:

| Dimension | Custom Weight | Reason |
|---|---|---|
| Workload | 15% | Less critical — team size is stable |
| Velocity | 15% | Speed matters less than correctness |
| Cycle Time | 15% | Reviews take longer intentionally |
| On-Time Rate | 25% | Release dates are hard commitments |
| Defects | **30%** | Bug MTTR is the top priority |

With these weights, a member who resolves bugs slowly will drop much faster even if they're completing many tasks.

### 📖 Scenario B — Sprint delivery team (feature team)

This team needs high throughput to hit quarterly OKRs:

| Dimension | Custom Weight | Reason |
|---|---|---|
| Workload | 15% | Some overload is acceptable near deadlines |
| Velocity | **35%** | Task throughput is the primary goal |
| Cycle Time | 25% | Fast iteration is valued |
| On-Time Rate | 20% | Commitments still matter |
| Defects | 5% | Bugs routed to a separate QA sub-team |

Here Ben's Velocity score of 50 would pull his overall score down much harder than in the default config, giving you an earlier signal that he needs help unblocking.

---

## Data Freshness

All KPI data is **computed live** on each page load — there is no caching layer. The timestamp shown under the page title reflects when the last request completed.

#### 📖 Scenario — Score changed overnight

Carla resolved two bugs yesterday evening. She marked them done at 11 pm. When you open the dashboard at 9 am, her Defects score has already updated from 40 → 100 because MTTR is recalculated fresh on every load. Her overall score rises from 55 → 68, crossing from At Risk into Fair. The "High bug MTTR" critical alert disappears automatically.
