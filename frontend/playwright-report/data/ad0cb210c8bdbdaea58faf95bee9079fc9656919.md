# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: mobile/task-types.spec.ts >> Task types >> filters by multiple task types across views
- Location: tests/mobile/task-types.spec.ts:161:2

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('Bug task', { exact: true })
Expected: visible
Error: strict mode violation: getByText('Bug task', { exact: true }) resolved to 2 elements:
    1) <p class="text-sm font-medium text-gray-100 leading-snug flex-1">Bug task</p> aka getByText('Bug task').nth(1)
    2) <p class="text-sm font-medium text-gray-100 leading-snug flex-1">Bug task</p> aka getByText('Bug task').nth(2)

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText('Bug task', { exact: true })

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - alert
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
              - paragraph [ref=e59]: 2 tasks
            - generic [ref=e60]:
              - generic [ref=e61]:
                - button "List" [ref=e62] [cursor=pointer]:
                  - img [ref=e63]
                  - text: List
                - button "Kanban" [active] [ref=e64] [cursor=pointer]:
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
                - option "No Sprint (Backlog)" [selected]
            - generic [ref=e74]:
              - img [ref=e75]
              - combobox [ref=e76]:
                - option "All Status" [selected]
                - option "To Do"
                - option "In Progress"
                - option "Review"
                - option "Done"
                - option "Blocked"
            - button "Manage Statuses" [ref=e77] [cursor=pointer]
            - generic [ref=e78] [cursor=pointer]:
              - checkbox "My tasks only" [ref=e79]
              - text: My tasks only
            - generic [ref=e80]:
              - generic [ref=e81]: Type
              - button "Feature" [ref=e82] [cursor=pointer]:
                - img [ref=e83]
                - text: Feature
              - button "Bug" [ref=e84] [cursor=pointer]:
                - img [ref=e85]
                - text: Bug
              - button "Task" [ref=e86] [cursor=pointer]:
                - img [ref=e87]
                - text: Task
              - button "Improve" [ref=e88] [cursor=pointer]:
                - img [ref=e89]
                - text: Improve
          - generic [ref=e90]:
            - generic [ref=e91]:
              - generic [ref=e92]:
                - heading "Backlog" [level=3] [ref=e94]
                - generic [ref=e95]: "3"
              - list [ref=e96]:
                - listitem [ref=e97]:
                  - generic [ref=e98]:
                    - generic [ref=e99]:
                      - paragraph [ref=e100]: Feature task
                      - button "Edit task" [ref=e101] [cursor=pointer]:
                        - img [ref=e102]
                    - paragraph [ref=e103]: Build the thing
                    - generic [ref=e104]:
                      - generic [ref=e105]:
                        - img [ref=e106]
                        - text: Feature
                      - generic [ref=e107]: medium
                    - generic [ref=e108]:
                      - generic [ref=e109]: TU
                      - generic [ref=e110]: Test User
                - listitem [ref=e111]:
                  - generic [ref=e112]:
                    - generic [ref=e113]:
                      - paragraph [ref=e114]: Bug task
                      - button "Edit task" [ref=e115] [cursor=pointer]:
                        - img [ref=e116]
                    - paragraph [ref=e117]: Fix the thing
                    - generic [ref=e118]:
                      - generic [ref=e119]:
                        - img [ref=e120]
                        - text: Bug
                      - generic [ref=e121]: high
                    - generic [ref=e122]:
                      - generic [ref=e123]: TU
                      - generic [ref=e124]: Test User
                - listitem [ref=e125]:
                  - generic [ref=e126]:
                    - generic [ref=e127]:
                      - paragraph [ref=e128]: Chore task
                      - button "Edit task" [ref=e129] [cursor=pointer]:
                        - img [ref=e130]
                    - paragraph [ref=e131]: Do the thing
                    - generic [ref=e132]:
                      - generic [ref=e133]:
                        - img [ref=e134]
                        - text: Task
                      - generic [ref=e135]: low
            - generic [ref=e136]:
              - generic [ref=e137]:
                - heading "To Do" [level=3] [ref=e140]
                - generic [ref=e141]: "1"
              - list [ref=e142]:
                - listitem [ref=e143]:
                  - generic [ref=e144]:
                    - generic [ref=e145]:
                      - paragraph [ref=e146]: Feature task
                      - button "Edit task" [ref=e147] [cursor=pointer]:
                        - img [ref=e148]
                    - paragraph [ref=e149]: Build the thing
                    - generic [ref=e150]:
                      - generic [ref=e151]:
                        - img [ref=e152]
                        - text: Feature
                      - generic [ref=e153]: medium
                    - generic [ref=e154]:
                      - generic [ref=e155]: TU
                      - generic [ref=e156]: Test User
            - generic [ref=e157]:
              - generic [ref=e158]:
                - heading "In Progress" [level=3] [ref=e161]
                - generic [ref=e162]: "1"
              - list [ref=e163]:
                - listitem [ref=e164]:
                  - generic [ref=e165]:
                    - generic [ref=e166]:
                      - paragraph [ref=e167]: Bug task
                      - button "Edit task" [ref=e168] [cursor=pointer]:
                        - img [ref=e169]
                    - paragraph [ref=e170]: Fix the thing
                    - generic [ref=e171]:
                      - generic [ref=e172]:
                        - img [ref=e173]
                        - text: Bug
                      - generic [ref=e174]: high
                    - generic [ref=e175]:
                      - generic [ref=e176]: TU
                      - generic [ref=e177]: Test User
            - generic [ref=e178]:
              - generic [ref=e179]:
                - heading "Review" [level=3] [ref=e182]
                - generic [ref=e183]: "0"
              - list [ref=e184]:
                - listitem [ref=e185]: No tasks in this status
            - generic [ref=e186]:
              - generic [ref=e187]:
                - generic [ref=e188]:
                  - heading "Done" [level=3] [ref=e190]
                  - generic [ref=e191]: Done
                - generic [ref=e192]: "0"
              - list [ref=e193]:
                - listitem [ref=e194]: No tasks in this status
            - generic [ref=e195]:
              - generic [ref=e196]:
                - heading "Blocked" [level=3] [ref=e199]
                - generic [ref=e200]: "0"
              - list [ref=e201]:
                - listitem [ref=e202]: No tasks in this status
```

# Test source

```ts
  73  | 
  74  | async function mockApi(page: Page) {
  75  | 	await page.route('/api/auth/me', (route) => route.fulfill({ json: user }));
  76  | 	await page.route('/api/notifications/pending', (route) => route.fulfill({ json: [] }));
  77  | 	await page.route('/api/users/', (route) => route.fulfill({ json: [user] }));
  78  | 	await page.route('/api/projects/', (route) =>
  79  | 		route.fulfill({ json: [{ id: 1, name: 'Project', description: null, color: '#6366f1', created_at: '2026-04-24T00:00:00Z' }] })
  80  | 	);
  81  | 	await page.route('/api/milestones/', (route) =>
  82  | 		route.fulfill({
  83  | 			json: [
  84  | 				{
  85  | 					id: 1,
  86  | 					title: 'Milestone',
  87  | 					description: null,
  88  | 					status: 'planned',
  89  | 					start_date: null,
  90  | 					due_date: '2026-05-01T00:00:00Z',
  91  | 					completed_at: null,
  92  | 					project_id: 1,
  93  | 					created_at: '2026-04-24T00:00:00Z'
  94  | 				}
  95  | 			]
  96  | 		})
  97  | 	);
  98  | 	await page.route('**/api/tasks/**', async (route) => {
  99  | 		const request = route.request();
  100 | 		const url = new URL(request.url());
  101 | 		if (request.method() === 'POST') {
  102 | 			const body = JSON.parse(request.postData() || '{}');
  103 | 			return route.fulfill({ status: 201, json: { ...tasks[0], ...body, id: 99, assignee: user } });
  104 | 		}
  105 | 
  106 | 		const selectedTypes = (url.searchParams.get('types') || '').split(',').filter(Boolean);
  107 | 		const filtered = selectedTypes.length ? tasks.filter((task) => selectedTypes.includes(task.type)) : tasks;
  108 | 		return route.fulfill({ json: filtered });
  109 | 	});
  110 | 	await page.route('/api/tasks/ai-parse', (route) =>
  111 | 		route.fulfill({
  112 | 			json: {
  113 | 				title: 'Investigate login crash',
  114 | 				description: null,
  115 | 				status: 'todo',
  116 | 				priority: 'high',
  117 | 				type: 'bug',
  118 | 				due_date: null,
  119 | 				estimated_hours: null,
  120 | 				tags: null,
  121 | 				assignee_name: null
  122 | 			}
  123 | 		})
  124 | 	);
  125 | 	await page.route('/api/tasks/ai-breakdown', (route) =>
  126 | 		route.fulfill({
  127 | 			json: {
  128 | 				subtasks: [
  129 | 					{ title: 'Design flow', priority: 'medium', type: 'feature', estimated_hours: 2, description: 'Draft the flow.' },
  130 | 					{ title: 'Fix edge case', priority: 'high', type: 'task', estimated_hours: 1, description: 'Handle the edge case.' }
  131 | 				]
  132 | 			}
  133 | 		})
  134 | 	);
  135 | }
  136 | 
  137 | test.describe('Task types', () => {
  138 | 	test.beforeEach(async ({ page }) => {
  139 | 		await mockApi(page);
  140 | 	});
  141 | 
  142 | 	test('shows type badges in list, kanban, and agile views', async ({ page }) => {
  143 | 		await page.goto('/tasks');
  144 | 
  145 | 		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
  146 | 		await expect(page.getByText('Feature').first()).toBeVisible();
  147 | 		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
  148 | 		await expect(page.getByText('Bug').first()).toBeVisible();
  149 | 		await expect(page.getByText('Chore task', { exact: true })).toBeVisible();
  150 | 		await expect(page.getByText('Task').first()).toBeVisible();
  151 | 
  152 | 		await page.getByRole('button', { name: /kanban/i }).click();
  153 | 		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
  154 | 		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
  155 | 
  156 | 		await page.getByRole('button', { name: /agile/i }).click();
  157 | 		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
  158 | 		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
  159 | 	});
  160 | 
  161 | 	test('filters by multiple task types across views', async ({ page }) => {
  162 | 		await page.goto('/tasks');
  163 | 
  164 | 		await page.getByRole('button', { name: /^Feature$/ }).click();
  165 | 		await page.getByRole('button', { name: /^Bug$/ }).click();
  166 | 
  167 | 		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
  168 | 		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
  169 | 		await expect(page.getByText('Chore task', { exact: true })).toBeHidden();
  170 | 
  171 | 		await page.getByRole('button', { name: /kanban/i }).click();
  172 | 		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
> 173 | 		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
      |                                                             ^ Error: expect(locator).toBeVisible() failed
  174 | 		await expect(page.getByText('Chore task', { exact: true })).toBeHidden();
  175 | 
  176 | 		await page.getByRole('button', { name: /^Feature$/ }).click();
  177 | 		await page.getByRole('button', { name: /^Bug$/ }).click();
  178 | 		await expect(page.getByText('Chore task', { exact: true })).toBeVisible();
  179 | 	});
  180 | 
  181 | 	test('defaults create form to Task and applies AI type suggestions', async ({ page }) => {
  182 | 		await page.goto('/tasks');
  183 | 		await page.getByRole('button', { name: /new task/i }).click();
  184 | 
  185 | 		await expect(page.locator('#t-type')).toHaveValue('task');
  186 | 
  187 | 		await page.getByRole('button', { name: /nlp/i }).click();
  188 | 		await page.locator('#ai-nlp').fill('Bug: investigate login crash');
  189 | 		await page.getByRole('button', { name: /parse with ai/i }).click();
  190 | 
  191 | 		await expect(page.locator('#t-type')).toHaveValue('bug');
  192 | 	});
  193 | 
  194 | 	test('lets AI breakdown subtasks keep editable task types', async ({ page }) => {
  195 | 		await page.goto('/tasks');
  196 | 		await page.getByRole('button', { name: /new task/i }).click();
  197 | 		await page.getByRole('button', { name: /breakdown/i }).click();
  198 | 
  199 | 		await page.locator('#bd-project').selectOption('1');
  200 | 		await page.locator('#bd-desc').fill('Build task types');
  201 | 		await page.getByRole('button', { name: /break down with ai/i }).click();
  202 | 
  203 | 		await expect(page.getByLabel('Subtask title').first()).toHaveValue('Design flow');
  204 | 		await expect(page.locator('select[id^="st-type-"]').first()).toHaveValue('feature');
  205 | 		await page.locator('select[id^="st-type-"]').first().selectOption('improvement');
  206 | 		await expect(page.locator('select[id^="st-type-"]').first()).toHaveValue('improvement');
  207 | 	});
  208 | });
  209 | 
```