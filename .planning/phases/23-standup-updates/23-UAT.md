---
status: testing
phase: 23-standup-updates
source: [23-01-SUMMARY.md, 23-02-SUMMARY.md, 23-03-SUMMARY.md, 23-04-SUMMARY.md]
started: 2026-04-28T14:08:00.000Z
updated: 2026-04-28T14:08:00.000Z
---

## Current Test
<!-- OVERWRITE each test - shows where we are -->

number: 1
name: Cold Start Smoke Test
expected: |
  Kill any running server/service. Clear ephemeral state (temp DBs, caches, lock files). Start the application from scratch. Server boots without errors, any seed/migration completes, and a primary query (health check, homepage load, or basic API call) returns live data.
awaiting: user response

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running server/service. Clear ephemeral state (temp DBs, caches, lock files). Start the application from scratch. Server boots without errors, any seed/migration completes, and a primary query (health check, homepage load, or basic API call) returns live data.
result: pending

### 2. Navigate to /updates
expected: Clicking Updates in the sidebar opens the /updates route. The page displays "Updates" header with "Team standup feed" subtitle. The Updates nav item is highlighted as active.
result: pending

### 3. StandupForm collapsed by default
expected: The "Post a standup update" button is visible at the top of the page. The form is collapsed (not expanded) by default.
result: pending

### 4. Expand StandupForm
expected: Clicking "Post a standup update" expands the form to show template-driven textareas (one per field from the template). The button changes to "Hide form" with a chevron-up icon.
result: pending

### 5. Submit a standup post
expected: Fill out the template fields and click "Post Update". The form submits, shows a success toast "Standup posted", and the new post appears at the top of the feed. The form collapses and fields are cleared.
result: pending

### 6. Post shows task snapshot
expected: The newly created post displays a "Task snapshot (X tasks)" button at the bottom, collapsed by default. The snapshot is not visible until clicked.
result: pending

### 7. Expand task snapshot
expected: Clicking the task snapshot button expands to show the list of tasks assigned to the user at post time. Each task shows status dot, priority badge, and due date.
result: pending

### 8. Edit button ownership check
expected: On your own post, the "Edit post" and "Delete post" buttons are visible. On another user's post, these buttons are not visible.
result: pending

### 9. Edit a post
expected: Clicking "Edit post" opens inline editing mode with one textarea per field. Changing values and clicking "Save changes" updates the post and shows "Update saved" toast. The mode returns to read.
result: pending

### 10. Delete a post
expected: Clicking "Delete post" shows inline confirmation "Delete this post?" with "Yes, delete" and "Keep post" buttons. Clicking "Yes, delete" removes the post from the feed and shows "Post deleted" toast.
result: pending

### 11. Supervisor template editor
expected: When logged in as supervisor or admin, a "Configure standup template" card is visible above the feed. When logged in as a member, this card is not visible.
result: pending

### 12. Update template fields
expected: In the template editor, you can add new fields, remove existing fields, and rename fields. Clicking "Save template" saves the changes and shows "Template saved" toast.
result: pending

### 13. Filter by author
expected: Selecting a team member from the author dropdown filters the feed to show only posts by that member. Clicking "Clear filters" resets to show all posts.
result: pending

### 14. Filter by date
expected: Selecting a date from the date picker filters the feed to show only posts from that day. Clicking "Clear filters" resets to show all posts.
result: pending

### 15. Load more pagination
expected: When there are more than 20 posts, a "Load more" button appears at the bottom. Clicking it loads the next page of posts (cursor-based pagination) and appends them to the feed.
result: pending

## Summary

total: 15
passed: 0
issues: 0
pending: 15
skipped: 0

## Gaps

[none yet]
