# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: mobile/task-types.spec.ts >> Task types >> lets AI breakdown subtasks keep editable task types
- Location: tests/mobile/task-types.spec.ts:194:2

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.selectOption: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('#bd-project')
    - locator resolved to <select required="" class="input" id="bd-project">…</select>
  - attempting select option action
    2 × waiting for element to be visible and enabled
      - did not find some options
    - retrying select option action
    - waiting 20ms
    2 × waiting for element to be visible and enabled
      - did not find some options
    - retrying select option action
      - waiting 100ms
    57 × waiting for element to be visible and enabled
       - did not find some options
     - retrying select option action
       - waiting 500ms

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
            - button [ref=e92] [cursor=pointer]
            - generic [ref=e95]:
              - generic [ref=e96]:
                - paragraph [ref=e97]: Feature task
                - paragraph [ref=e98]: Build the thing
                - generic [ref=e99]:
                  - generic [ref=e100]: To Do
                  - generic [ref=e101]:
                    - img [ref=e102]
                    - text: Feature
                  - generic [ref=e103]: medium
                  - generic [ref=e104]: → Test User
              - generic [ref=e105]:
                - button [ref=e106] [cursor=pointer]:
                  - img [ref=e107]
                - button [ref=e108] [cursor=pointer]:
                  - img [ref=e109]
          - generic [ref=e110]:
            - button [ref=e111] [cursor=pointer]
            - generic [ref=e114]:
              - generic [ref=e115]:
                - paragraph [ref=e116]: Bug task
                - paragraph [ref=e117]: Fix the thing
                - generic [ref=e118]:
                  - generic [ref=e119]: In Progress
                  - generic [ref=e120]:
                    - img [ref=e121]
                    - text: Bug
                  - generic [ref=e122]: high
                  - generic [ref=e123]: → Test User
              - generic [ref=e124]:
                - button [ref=e125] [cursor=pointer]:
                  - img [ref=e126]
                - button [ref=e127] [cursor=pointer]:
                  - img [ref=e128]
          - generic [ref=e129]:
            - button [ref=e130] [cursor=pointer]
            - generic [ref=e133]:
              - generic [ref=e134]:
                - paragraph [ref=e135]: Chore task
                - paragraph [ref=e136]: Do the thing
                - generic [ref=e137]:
                  - generic [ref=e138]: Review
                  - generic [ref=e139]:
                    - img [ref=e140]
                    - text: Task
                  - generic [ref=e141]: low
              - generic [ref=e142]:
                - button [ref=e143] [cursor=pointer]:
                  - img [ref=e144]
                - button [ref=e145] [cursor=pointer]:
                  - img [ref=e146]
      - generic [ref=e148]:
        - generic [ref=e149]:
          - heading "New Task" [level=2] [ref=e150]
          - button [ref=e151] [cursor=pointer]:
            - img [ref=e152]
        - generic [ref=e153]:
          - generic [ref=e155]:
            - button "Form" [ref=e156] [cursor=pointer]:
              - img [ref=e157]
              - text: Form
            - button "NLP" [ref=e158] [cursor=pointer]:
              - img [ref=e159]
              - text: NLP
            - button "JSON" [ref=e160] [cursor=pointer]:
              - img [ref=e161]
              - text: JSON
            - button "Breakdown" [active] [ref=e162] [cursor=pointer]:
              - img [ref=e163]
              - text: Breakdown
          - generic [ref=e164]:
            - generic [ref=e165]:
              - generic [ref=e166]: Project
              - combobox "Project" [ref=e167]:
                - option "Select a project" [selected]
            - generic [ref=e168]:
              - generic [ref=e169]: Default Milestone
              - combobox "Default Milestone" [ref=e170]:
                - option "No milestone" [selected]
            - generic [ref=e171]:
              - generic [ref=e172]: Assign all to
              - combobox "Assign all to" [ref=e173]:
                - option "Unassigned" [selected]
            - generic [ref=e174]:
              - generic [ref=e175]: What do you want to build?
              - textbox "What do you want to build?" [ref=e176]:
                - /placeholder: Describe the feature or work to break down into tasks...
            - button "Break down with AI" [disabled] [ref=e177]
```

# Test source

```ts
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
  173 | 		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
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
> 199 | 		await page.locator('#bd-project').selectOption('1');
      |                                     ^ Error: locator.selectOption: Test timeout of 30000ms exceeded.
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