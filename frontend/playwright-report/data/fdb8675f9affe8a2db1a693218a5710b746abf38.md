# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: mobile/kanban-scroll.spec.ts >> Kanban horizontal scroll on mobile (375px) >> kanban board has touch-action style
- Location: tests/mobile/kanban-scroll.spec.ts:28:2

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('[style*="touch-action"]').first()
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('[style*="touch-action"]').first()

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - complementary [ref=e4]:
    - generic [ref=e6]:
      - generic [ref=e7]: T
      - generic [ref=e8]: TeamFlow
    - navigation [ref=e9]:
      - button "Notifications" [ref=e10] [cursor=pointer]:
        - img [ref=e11]
        - generic [ref=e12]: Notifications
      - button "All Teams" [ref=e14] [cursor=pointer]:
        - text: All Teams
        - img [ref=e15]
      - link "Dashboard" [ref=e16] [cursor=pointer]:
        - /url: /
        - img [ref=e17]
        - text: Dashboard
      - link "Performance" [ref=e18] [cursor=pointer]:
        - /url: /performance
        - img [ref=e19]
        - text: Performance
      - link "Projects" [ref=e20] [cursor=pointer]:
        - /url: /projects
        - img [ref=e21]
        - text: Projects
      - link "Tasks" [ref=e22] [cursor=pointer]:
        - /url: /tasks
        - img [ref=e23]
        - text: Tasks
        - img [ref=e24]
      - link "Milestones" [ref=e25] [cursor=pointer]:
        - /url: /milestones
        - img [ref=e26]
        - text: Milestones
      - link "Timeline" [ref=e27] [cursor=pointer]:
        - /url: /timeline
        - img [ref=e28]
        - text: Timeline
      - link "Team" [ref=e29] [cursor=pointer]:
        - /url: /team
        - img [ref=e30]
        - text: Team
      - link "Scheduler" [ref=e31] [cursor=pointer]:
        - /url: /schedule
        - img [ref=e32]
        - text: Scheduler
      - link "AI Assistant" [ref=e33] [cursor=pointer]:
        - /url: /ai
        - img [ref=e34]
        - text: AI Assistant
    - generic [ref=e36]:
      - generic [ref=e37]: TE
      - generic [ref=e38]:
        - paragraph [ref=e39]: Test User
        - paragraph [ref=e40]: admin
      - button "Logout" [ref=e41] [cursor=pointer]:
        - img [ref=e42]
  - generic [ref=e43]:
    - banner [ref=e44]:
      - button "Open menu" [ref=e45] [cursor=pointer]:
        - img [ref=e46]
      - generic [ref=e47]:
        - generic [ref=e48]: T
        - generic [ref=e49]: TeamFlow
      - button "Notifications" [ref=e51] [cursor=pointer]:
        - img [ref=e52]
        - generic [ref=e53]: Notifications
    - main [ref=e54]:
      - generic [ref=e55]:
        - generic [ref=e56]:
          - generic [ref=e57]:
            - heading "Tasks" [level=1] [ref=e58]
            - paragraph [ref=e59]: 3 tasks
          - generic [ref=e60]:
            - generic [ref=e61]:
              - button "List" [ref=e62] [cursor=pointer]:
                - img [ref=e63]
                - text: List
              - button "Kanban" [ref=e64] [cursor=pointer]:
                - img [ref=e65]
                - text: Kanban
              - button "Agile" [ref=e66] [cursor=pointer]:
                - img [ref=e67]
                - text: Agile
            - button "New Task" [ref=e68] [cursor=pointer]:
              - img [ref=e69]
              - text: New Task
        - generic [ref=e70]:
          - generic [ref=e71]:
            - img [ref=e72]
            - combobox [ref=e73]:
              - option "No Sprint (Backlog)"
              - option "Mobile Sprint (active)" [selected]
              - option "Release Sprint (active)"
            - button "Close Sprint" [ref=e74] [cursor=pointer]
          - generic [ref=e75]:
            - img [ref=e76]
            - combobox [ref=e77]:
              - option "All Status" [selected]
              - option "To Do"
              - option "In Progress"
              - option "Review"
              - option "Done"
              - option "Blocked"
          - button "Manage Statuses" [ref=e78] [cursor=pointer]
          - generic [ref=e79] [cursor=pointer]:
            - checkbox "My tasks only" [ref=e80]
            - text: My tasks only
          - generic [ref=e81]:
            - generic [ref=e82]: Type
            - button "Feature" [ref=e83] [cursor=pointer]:
              - img [ref=e84]
              - text: Feature
            - button "Bug" [ref=e85] [cursor=pointer]:
              - img [ref=e86]
              - text: Bug
            - button "Task" [ref=e87] [cursor=pointer]:
              - img [ref=e88]
              - text: Task
            - button "Improve" [ref=e89] [cursor=pointer]:
              - img [ref=e90]
              - text: Improve
        - generic [ref=e91]:
          - generic [ref=e92]:
            - button [ref=e93] [cursor=pointer]
            - generic [ref=e96]:
              - generic [ref=e97]:
                - paragraph [ref=e98]: Login screen UI
                - paragraph [ref=e99]: sahfuhqwjrhqjwfhjlwq
                - generic [ref=e100]:
                  - generic [ref=e101]: In Review
                  - generic [ref=e102]:
                    - img [ref=e103]
                    - text: Task
                  - generic [ref=e104]: high
                  - generic [ref=e105]: Due May 16, 2026
                  - generic [ref=e106]: → Alice Chen
              - generic [ref=e107]:
                - button [ref=e108] [cursor=pointer]:
                  - img [ref=e109]
                - button [ref=e110] [cursor=pointer]:
                  - img [ref=e111]
          - generic [ref=e112]:
            - button [ref=e113] [cursor=pointer]
            - generic [ref=e116]:
              - generic [ref=e117]:
                - paragraph [ref=e118]: Onboarding flow wireframes
                - generic [ref=e119]:
                  - generic [ref=e120]: In Progress
                  - generic [ref=e121]:
                    - img [ref=e122]
                    - text: Task
                  - generic [ref=e123]: medium
                  - generic [ref=e124]: Due May 4, 2026
                  - generic [ref=e125]: → Carol Davis
              - generic [ref=e126]:
                - button [ref=e127] [cursor=pointer]:
                  - img [ref=e128]
                - button [ref=e129] [cursor=pointer]:
                  - img [ref=e130]
          - generic [ref=e131]:
            - button [ref=e132] [cursor=pointer]
            - generic [ref=e135]:
              - generic [ref=e136]:
                - paragraph [ref=e137]: Push notification setup
                - generic [ref=e138]:
                  - generic [ref=e139]: Blocked
                  - generic [ref=e140]:
                    - img [ref=e141]
                    - text: Task
                  - generic [ref=e142]: medium
                  - generic [ref=e143]: Due May 21, 2026
                  - generic [ref=e144]: → Bob Kim
              - generic [ref=e145]:
                - button [ref=e146] [cursor=pointer]:
                  - img [ref=e147]
                - button [ref=e148] [cursor=pointer]:
                  - img [ref=e149]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | import { loginAs } from '../helpers/auth';
  3  | 
  4  | test.describe('Kanban horizontal scroll on mobile (375px)', () => {
  5  | 	test.use({ viewport: { width: 375, height: 812 } });
  6  | 
  7  | 	test.beforeEach(async ({ page }) => {
  8  | 		await loginAs(page);
  9  | 	});
  10 | 
  11 | 	test('kanban board scrolls horizontally', async ({ page }) => {
  12 | 		await page.goto('/tasks');
  13 | 
  14 | 		// Switch to Kanban view
  15 | 		const kanbanBtn = page.getByRole('button', { name: /kanban/i });
  16 | 		if (await kanbanBtn.isVisible()) {
  17 | 			await kanbanBtn.click();
  18 | 		}
  19 | 
  20 | 		const board = page.locator('.overflow-x-auto').first();
  21 | 		await expect(board).toBeVisible();
  22 | 
  23 | 		const scrollWidth = await board.evaluate((el) => el.scrollWidth);
  24 | 		const clientWidth = await board.evaluate((el) => el.clientWidth);
  25 | 		expect(scrollWidth).toBeGreaterThan(clientWidth);
  26 | 	});
  27 | 
  28 | 	test('kanban board has touch-action style', async ({ page }) => {
  29 | 		await page.goto('/tasks');
  30 | 
  31 | 		const kanbanBtn = page.getByRole('button', { name: /kanban/i });
  32 | 		if (await kanbanBtn.isVisible()) {
  33 | 			await kanbanBtn.click();
  34 | 		}
  35 | 
  36 | 		const board = page.locator('[style*="touch-action"]').first();
> 37 | 		await expect(board).toBeVisible();
     |                       ^ Error: expect(locator).toBeVisible() failed
  38 | 		const touchAction = await board.evaluate((el) => (el as HTMLElement).style.touchAction);
  39 | 		expect(touchAction).toContain('pan-x');
  40 | 	});
  41 | });
  42 | 
```