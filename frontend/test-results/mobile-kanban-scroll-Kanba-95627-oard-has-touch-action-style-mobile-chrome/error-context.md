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
      - link "Dashboard" [ref=e13] [cursor=pointer]:
        - /url: /
        - img [ref=e14]
        - text: Dashboard
      - link "Performance" [ref=e15] [cursor=pointer]:
        - /url: /performance
        - img [ref=e16]
        - text: Performance
      - link "Projects" [ref=e17] [cursor=pointer]:
        - /url: /projects
        - img [ref=e18]
        - text: Projects
      - link "Tasks" [ref=e19] [cursor=pointer]:
        - /url: /tasks
        - img [ref=e20]
        - text: Tasks
        - img [ref=e21]
      - link "Milestones" [ref=e22] [cursor=pointer]:
        - /url: /milestones
        - img [ref=e23]
        - text: Milestones
      - link "Timeline" [ref=e24] [cursor=pointer]:
        - /url: /timeline
        - img [ref=e25]
        - text: Timeline
      - link "Team" [ref=e26] [cursor=pointer]:
        - /url: /team
        - img [ref=e27]
        - text: Team
      - link "Scheduler" [ref=e28] [cursor=pointer]:
        - /url: /schedule
        - img [ref=e29]
        - text: Scheduler
      - link "AI Assistant" [ref=e30] [cursor=pointer]:
        - /url: /ai
        - img [ref=e31]
        - text: AI Assistant
    - generic [ref=e33]:
      - generic [ref=e34]: SA
      - generic [ref=e35]:
        - paragraph [ref=e36]: Sam Supervisor
        - paragraph [ref=e37]: supervisor
      - button "Logout" [ref=e38] [cursor=pointer]:
        - img [ref=e39]
  - generic [ref=e40]:
    - banner [ref=e41]:
      - button "Open menu" [ref=e42] [cursor=pointer]:
        - img [ref=e43]
      - generic [ref=e44]:
        - generic [ref=e45]: T
        - generic [ref=e46]: TeamFlow
      - button "Notifications" [ref=e48] [cursor=pointer]:
        - img [ref=e49]
        - generic [ref=e50]: Notifications
    - main [ref=e51]:
      - generic [ref=e52]:
        - generic [ref=e53]:
          - generic [ref=e54]:
            - heading "Tasks" [level=1] [ref=e55]
            - paragraph [ref=e56]: 16 tasks
          - generic [ref=e57]:
            - generic [ref=e58]:
              - button "List" [ref=e59] [cursor=pointer]:
                - img [ref=e60]
                - text: List
              - button "Kanban" [ref=e61] [cursor=pointer]:
                - img [ref=e62]
                - text: Kanban
              - button "Agile" [ref=e63] [cursor=pointer]:
                - img [ref=e64]
                - text: Agile
            - button "New Task" [ref=e65] [cursor=pointer]:
              - img [ref=e66]
              - text: New Task
        - generic [ref=e67]:
          - generic [ref=e68]:
            - img [ref=e69]
            - combobox [ref=e70]:
              - option "All Status" [selected]
              - option "To Do"
              - option "In Progress"
              - option "Review"
              - option "Done"
              - option "Blocked"
          - generic [ref=e71] [cursor=pointer]:
            - checkbox "My tasks only" [ref=e72]
            - text: My tasks only
        - generic [ref=e73]:
          - generic [ref=e74]:
            - button [ref=e75] [cursor=pointer]
            - generic [ref=e78]:
              - generic [ref=e79]:
                - paragraph [ref=e80]: "Spike: offline mode feasibility"
                - generic [ref=e81]:
                  - generic [ref=e82]: To Do
                  - generic [ref=e83]: medium
                  - generic [ref=e84]: → Bob Kim
              - generic [ref=e85]:
                - button [ref=e86] [cursor=pointer]:
                  - img [ref=e87]
                - button [ref=e88] [cursor=pointer]:
                  - img [ref=e89]
          - generic [ref=e90]:
            - button [ref=e91] [cursor=pointer]
            - generic [ref=e94]:
              - generic [ref=e95]:
                - paragraph [ref=e96]: "Backlog: API versioning research"
                - generic [ref=e97]:
                  - generic [ref=e98]: To Do
                  - generic [ref=e99]: low
              - generic [ref=e100]:
                - button [ref=e101] [cursor=pointer]:
                  - img [ref=e102]
                - button [ref=e103] [cursor=pointer]:
                  - img [ref=e104]
          - generic [ref=e105]:
            - button [ref=e106] [cursor=pointer]
            - generic [ref=e109]:
              - generic [ref=e110]:
                - paragraph [ref=e111]: Icon library integration
                - generic [ref=e112]:
                  - generic [ref=e113]: In Progress
                  - generic [ref=e114]: low
                  - generic [ref=e115]: Due Apr 28, 2026
                  - generic [ref=e116]: → Bob Kim
              - generic [ref=e117]:
                - button [ref=e118] [cursor=pointer]:
                  - img [ref=e119]
                - button [ref=e120] [cursor=pointer]:
                  - img [ref=e121]
          - generic [ref=e122]:
            - button [ref=e123] [cursor=pointer]
            - generic [ref=e126]:
              - generic [ref=e127]:
                - paragraph [ref=e128]: Color palette finalization
                - generic [ref=e129]:
                  - generic [ref=e130]: Review
                  - generic [ref=e131]: medium
                  - generic [ref=e132]: Due Apr 27, 2026
                  - generic [ref=e133]: → Alice Chen
              - generic [ref=e134]:
                - button [ref=e135] [cursor=pointer]:
                  - img [ref=e136]
                - button [ref=e137] [cursor=pointer]:
                  - img [ref=e138]
          - generic [ref=e139]:
            - button "✓" [ref=e140] [cursor=pointer]:
              - generic [ref=e142]: ✓
            - generic [ref=e144]:
              - generic [ref=e145]:
                - paragraph [ref=e146]: Typography tokens
                - generic [ref=e147]:
                  - generic [ref=e148]: Done
                  - generic [ref=e149]: medium
                  - generic [ref=e150]: Due Apr 20, 2026
                  - generic [ref=e151]: → Carol Davis
              - generic [ref=e152]:
                - button [ref=e153] [cursor=pointer]:
                  - img [ref=e154]
                - button [ref=e155] [cursor=pointer]:
                  - img [ref=e156]
          - generic [ref=e157]:
            - button [ref=e158] [cursor=pointer]
            - generic [ref=e161]:
              - generic [ref=e162]:
                - paragraph [ref=e163]: App store listing copy
                - generic [ref=e164]:
                  - generic [ref=e165]: To Do
                  - generic [ref=e166]: low
                  - generic [ref=e167]: Due May 20, 2026
                  - generic [ref=e168]: → Carol Davis
              - generic [ref=e169]:
                - button [ref=e170] [cursor=pointer]:
                  - img [ref=e171]
                - button [ref=e172] [cursor=pointer]:
                  - img [ref=e173]
          - generic [ref=e174]:
            - button [ref=e175] [cursor=pointer]
            - generic [ref=e178]:
              - generic [ref=e179]:
                - paragraph [ref=e180]: Push notification setup
                - generic [ref=e181]:
                  - generic [ref=e182]: To Do
                  - generic [ref=e183]: medium
                  - generic [ref=e184]: Due May 17, 2026
                  - generic [ref=e185]: → Bob Kim
              - generic [ref=e186]:
                - button [ref=e187] [cursor=pointer]:
                  - img [ref=e188]
                - button [ref=e189] [cursor=pointer]:
                  - img [ref=e190]
          - generic [ref=e191]:
            - button [ref=e192] [cursor=pointer]
            - generic [ref=e195]:
              - generic [ref=e196]:
                - paragraph [ref=e197]: Login screen UI
                - generic [ref=e198]:
                  - generic [ref=e199]: In Progress
                  - generic [ref=e200]: high
                  - generic [ref=e201]: Due May 12, 2026
                  - generic [ref=e202]: → Alice Chen
              - generic [ref=e203]:
                - button [ref=e204] [cursor=pointer]:
                  - img [ref=e205]
                - button [ref=e206] [cursor=pointer]:
                  - img [ref=e207]
          - generic [ref=e208]:
            - button "✓" [ref=e209] [cursor=pointer]:
              - generic [ref=e211]: ✓
            - generic [ref=e213]:
              - generic [ref=e214]:
                - paragraph [ref=e215]: Role-based route guards
                - generic [ref=e216]:
                  - generic [ref=e217]: Done
                  - generic [ref=e218]: medium
                  - generic [ref=e219]: Due Apr 11, 2026
                  - generic [ref=e220]: → Carol Davis
              - generic [ref=e221]:
                - button [ref=e222] [cursor=pointer]:
                  - img [ref=e223]
                - button [ref=e224] [cursor=pointer]:
                  - img [ref=e225]
          - generic [ref=e226]:
            - button "✓" [ref=e227] [cursor=pointer]:
              - generic [ref=e229]: ✓
            - generic [ref=e231]:
              - generic [ref=e232]:
                - paragraph [ref=e233]: Implement JWT refresh tokens
                - generic [ref=e234]:
                  - generic [ref=e235]: Done
                  - generic [ref=e236]: high
                  - generic [ref=e237]: Due Apr 10, 2026
                  - generic [ref=e238]: → Bob Kim
              - generic [ref=e239]:
                - button [ref=e240] [cursor=pointer]:
                  - img [ref=e241]
                - button [ref=e242] [cursor=pointer]:
                  - img [ref=e243]
          - generic [ref=e244]:
            - button [ref=e245] [cursor=pointer]
            - generic [ref=e248]:
              - generic [ref=e249]:
                - paragraph [ref=e250]: Fix overdue bug in scheduler
                - generic [ref=e251]:
                  - generic [ref=e252]: Blocked
                  - generic [ref=e253]: critical
                  - generic [ref=e254]: Due Apr 19, 2026
                  - generic [ref=e255]: → Alice Chen
              - generic [ref=e256]:
                - button [ref=e257] [cursor=pointer]:
                  - img [ref=e258]
                - button [ref=e259] [cursor=pointer]:
                  - img [ref=e260]
          - generic [ref=e261]:
            - button [ref=e262] [cursor=pointer]
            - generic [ref=e265]:
              - generic [ref=e266]:
                - paragraph [ref=e267]: Performance load testing
                - generic [ref=e268]:
                  - generic [ref=e269]: To Do
                  - generic [ref=e270]: high
                  - generic [ref=e271]: Due Apr 25, 2026
                  - generic [ref=e272]: → Carol Davis
              - generic [ref=e273]:
                - button [ref=e274] [cursor=pointer]:
                  - img [ref=e275]
                - button [ref=e276] [cursor=pointer]:
                  - img [ref=e277]
          - generic [ref=e278]:
            - button [ref=e279] [cursor=pointer]
            - generic [ref=e282]:
              - generic [ref=e283]:
                - paragraph [ref=e284]: Write API documentation
                - generic [ref=e285]:
                  - generic [ref=e286]: To Do
                  - generic [ref=e287]: medium
                  - generic [ref=e288]: Due May 4, 2026
                  - generic [ref=e289]: → Bob Kim
              - generic [ref=e290]:
                - button [ref=e291] [cursor=pointer]:
                  - img [ref=e292]
                - button [ref=e293] [cursor=pointer]:
                  - img [ref=e294]
          - generic [ref=e295]:
            - button [ref=e296] [cursor=pointer]
            - generic [ref=e299]:
              - generic [ref=e300]:
                - paragraph [ref=e301]: Set up CI/CD pipeline
                - generic [ref=e302]:
                  - generic [ref=e303]: In Progress
                  - generic [ref=e304]: high
                  - generic [ref=e305]: Due May 2, 2026
                  - generic [ref=e306]: → Alice Chen
              - generic [ref=e307]:
                - button [ref=e308] [cursor=pointer]:
                  - img [ref=e309]
                - button [ref=e310] [cursor=pointer]:
                  - img [ref=e311]
          - generic [ref=e312]:
            - button "✓" [ref=e313] [cursor=pointer]:
              - generic [ref=e315]: ✓
            - generic [ref=e317]:
              - generic [ref=e318]:
                - paragraph [ref=e319]: Deploy new logging service
                - generic [ref=e320]:
                  - generic [ref=e321]: Done
                  - generic [ref=e322]: medium
                  - generic [ref=e323]: Due Apr 21, 2026
                  - generic [ref=e324]: → Hai La
                  - generic [ref=e325]: fe
              - generic [ref=e326]:
                - button [ref=e327] [cursor=pointer]:
                  - img [ref=e328]
                - button [ref=e329] [cursor=pointer]:
                  - img [ref=e330]
          - generic [ref=e331]:
            - button "✓" [ref=e332] [cursor=pointer]:
              - generic [ref=e334]: ✓
            - generic [ref=e336]:
              - generic [ref=e337]:
                - paragraph [ref=e338]: Testing
                - generic [ref=e339]:
                  - generic [ref=e340]: Done
                  - generic [ref=e341]: medium
              - generic [ref=e342]:
                - button [ref=e343] [cursor=pointer]:
                  - img [ref=e344]
                - button [ref=e345] [cursor=pointer]:
                  - img [ref=e346]
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