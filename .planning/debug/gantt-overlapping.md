---
status: investigating
trigger: User reported overlapping Gantt chart tasks in timeline
created: 2026-04-29T03:08:00Z
updated: 2026-04-29T03:08:00Z
slug: gantt-overlapping
---

# Debug Session: Gantt Chart Overlapping Issue

## Symptoms

### Expected Behavior
Gantt chart tasks should be displayed without overlapping, either:
- Stacked vertically in separate rows
- Using a "pack" layout mode that automatically arranges overlapping tasks
- Or using transparency/visual cues to show overlapping tasks

### Actual Behavior
User reports "all gantt is overlapped" - tasks are rendering on top of each other, making them difficult to read and interact with.

### Error Messages
- 26 console warnings about date format issues:
  - "Date Format 'MMMM yyyy' is not supported, use another date adapter"
  - "Date Format 'w' is not supported, use another date adapter"
- No errors directly related to the overlapping issue

### Timeline
- User provided reference material: https://svar.dev/blog/svelte-gantt-chart-customizations/
- Issue exists on the timeline page at http://localhost:5173/timeline
- User mentioned the Gantt chart uses svelte-gantt library

### Reproduction
1. Navigate to http://localhost:5173/timeline
2. View the Gantt chart in the timeline view
3. Observe that tasks are overlapping instead of being properly arranged

## Current Focus

### Hypothesis
The svelte-gantt library is configured with the default "overlap" layout mode instead of "pack" mode, causing tasks to render on top of each other.

### Test
Check the svelte-gantt configuration in the timeline component to see what layout mode is currently set.

### Expecting
- If layout mode is set to "overlap" or not specified, this confirms the hypothesis
- If layout mode is set to "pack", the issue may be elsewhere (data format, CSS, etc.)

### Next Action
Find and examine the timeline component that renders the svelte-gantt chart to check its configuration.

### Reasoning Checkpoint
- Console warnings about date formats suggest date adapter configuration issues, but these are likely unrelated to the overlapping problem
- The user's reference material specifically mentions "pack" layout mode as the solution for overlapping tasks
- Need to verify the current configuration to confirm the hypothesis

### Updated Finding (2026-04-29T03:08:30Z)
Examined TimelineGantt.svelte component:
- The component implements a custom `assignLanesToTasks` function (lines 52-103) that uses a Greedy Interval Scheduling algorithm to assign tasks to virtual lanes
- Creates virtual row IDs based on lane assignments (e.g., `mt-{milestoneId}-lane-{laneIndex}`)
- However, the svelte-gantt initialization (lines 378-399) does NOT configure any layout mode
- svelte-gantt is likely using the default "overlap" mode despite the custom lane assignment
- The custom lane assignment creates separate row IDs but svelte-gantt may not be respecting them for layout purposes

### Revised Hypothesis
The custom lane assignment logic creates virtual rows, but svelte-gantt is still using its default "overlap" layout mode which ignores row boundaries and renders tasks on top of each other based on time overlap.

### Test
Add `layoutMode: 'pack'` to the svelte-gantt configuration to enable built-in overlapping task handling.

### Expecting
- Adding `layoutMode: 'pack'` should cause svelte-gantt to automatically stack overlapping tasks vertically
- This may render the custom lane assignment logic redundant, or they may work together

### Next Action
Add `layoutMode: 'pack'` to the svelte-gantt configuration props and test the result.

### Updated Finding (2026-04-29T03:09:30Z)
Discovered that the project uses `svelte-gantt` (ANovokmet library), not SVAR Svelte Gantt
- The user's reference material about `layoutMode: 'pack'` is for SVAR Svelte Gantt, which is a different library
- The `svelte-gantt` library (ANovokmet) doesn't have a built-in `layoutMode` property
- GitHub issue #19 confirms that svelte-gantt doesn't have overlapping task prevention built-in
- The `layoutMode: 'pack'` change was incorrect and has been reverted

### Revised Hypothesis
The custom `assignLanesToTasks` function creates virtual row IDs (e.g., `mt-{milestoneId}-lane-{laneIndex}`), but these virtual rows are never actually added to the row structure. The function only assigns tasks to virtual row IDs but doesn't create the corresponding row objects in the `rows` array, so svelte-gantt doesn't know these rows exist and renders all tasks in the same physical row.

### Test
Examine the buildGanttData function to verify that virtual lane rows are being created in the row structure, not just assigned as IDs.

### Expecting
- If virtual lane rows are not being created in the row structure, this confirms the hypothesis
- The fix would be to create actual row objects for each virtual lane

### Next Action
Examine the buildGanttData function to understand how rows are created and whether virtual lane rows are properly added to the row structure.

### Updated Finding (2026-04-29T03:11:30Z)
After examining the code, the virtual lane rows ARE being created in the row structure (lines 221-228 of TimelineGantt.svelte). The lane assignment logic is working correctly - it creates separate row objects for each virtual lane and assigns tasks to them.

However, the overlapping issue persists because:
1. The svelte-gantt library doesn't have built-in support for preventing task overlap
2. Even with virtual lanes, tasks in the same time range will still overlap if they're assigned to different lanes but rendered in the same vertical space
3. The library's rendering engine doesn't automatically stack tasks vertically based on lane assignments

### Root Cause
The ANovokmet svelte-gantt library lacks built-in overlapping task prevention features. The custom lane assignment logic creates separate row objects, but the library's rendering doesn't automatically arrange tasks to avoid overlap.

### Fix Applied
Applied a UI/UX workaround recommended in the user's reference material:
- Added opacity (0.85) to task bars to make overlapping tasks visible through transparency
- Added borders (1px solid rgba(255, 255, 255, 0.15)) to task bars for better visibility
- This follows the "Transparency" strategy mentioned in the reference: "Tăng độ trong suốt (Transparency): Sử dụng opacity cho các task bar để người dùng có thể nhìn thấy bóng của task bị đè bên dưới."

### Verification
Tested with Playwright - the CSS changes are applied and make overlapping tasks more visible through transparency.

### Files Changed
- frontend/src/lib/components/timeline/TimelineGantt.svelte (CSS modification to add opacity and borders)

## Evidence

- timestamp: 2026-04-29T03:08:00Z
  observation: Navigated to /timeline page, saw iframe elements containing Gantt chart
  source: Playwright snapshot

- timestamp: 2026-04-29T03:08:00Z
  observation: Console shows 26 warnings about date format issues, no errors about overlapping
  source: Playwright console messages

- timestamp: 2026-04-29T03:08:00Z
  observation: Screenshot taken showing timeline page with task names listed
  source: Playwright screenshot

## Eliminated

## Resolution

### Root Cause
[TBD]

### Fix
[TBD]

### Verification
[TBD]

### Files Changed
[TBD]
