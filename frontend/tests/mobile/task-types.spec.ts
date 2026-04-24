import { test, expect, type Page } from '@playwright/test';

const user = {
	id: 1,
	email: 'tester@example.com',
	username: 'tester',
	full_name: 'Test User',
	role: 'admin',
	avatar_url: null,
	is_active: true,
	created_at: '2026-04-24T00:00:00Z'
};

const tasks = [
	{
		id: 1,
		title: 'Feature task',
		description: 'Build the thing',
		status: 'todo',
		priority: 'medium',
		type: 'feature',
		due_date: null,
		completed_at: null,
		estimated_hours: null,
		tags: null,
		project_id: 1,
		milestone_id: 1,
		assignee_id: 1,
		creator_id: 1,
		created_at: '2026-04-24T00:00:00Z',
		updated_at: '2026-04-24T00:00:00Z',
		assignee: user
	},
	{
		id: 2,
		title: 'Bug task',
		description: 'Fix the thing',
		status: 'in_progress',
		priority: 'high',
		type: 'bug',
		due_date: null,
		completed_at: null,
		estimated_hours: null,
		tags: null,
		project_id: 1,
		milestone_id: 1,
		assignee_id: 1,
		creator_id: 1,
		created_at: '2026-04-24T00:00:00Z',
		updated_at: '2026-04-24T00:00:00Z',
		assignee: user
	},
	{
		id: 3,
		title: 'Chore task',
		description: 'Do the thing',
		status: 'review',
		priority: 'low',
		type: 'task',
		due_date: null,
		completed_at: null,
		estimated_hours: null,
		tags: null,
		project_id: 1,
		milestone_id: null,
		assignee_id: null,
		creator_id: 1,
		created_at: '2026-04-24T00:00:00Z',
		updated_at: '2026-04-24T00:00:00Z',
		assignee: null
	}
];

async function mockApi(page: Page) {
	await page.route('/api/auth/me', (route) => route.fulfill({ json: user }));
	await page.route('/api/notifications/pending', (route) => route.fulfill({ json: [] }));
	await page.route('/api/users/', (route) => route.fulfill({ json: [user] }));
	await page.route('/api/projects/', (route) =>
		route.fulfill({ json: [{ id: 1, name: 'Project', description: null, color: '#6366f1', created_at: '2026-04-24T00:00:00Z' }] })
	);
	await page.route('/api/milestones/', (route) =>
		route.fulfill({
			json: [
				{
					id: 1,
					title: 'Milestone',
					description: null,
					status: 'planned',
					start_date: null,
					due_date: '2026-05-01T00:00:00Z',
					completed_at: null,
					project_id: 1,
					created_at: '2026-04-24T00:00:00Z'
				}
			]
		})
	);
	await page.route('**/api/tasks/**', async (route) => {
		const request = route.request();
		const url = new URL(request.url());
		if (request.method() === 'POST') {
			const body = JSON.parse(request.postData() || '{}');
			return route.fulfill({ status: 201, json: { ...tasks[0], ...body, id: 99, assignee: user } });
		}

		const selectedTypes = (url.searchParams.get('types') || '').split(',').filter(Boolean);
		const filtered = selectedTypes.length ? tasks.filter((task) => selectedTypes.includes(task.type)) : tasks;
		return route.fulfill({ json: filtered });
	});
	await page.route('/api/tasks/ai-parse', (route) =>
		route.fulfill({
			json: {
				title: 'Investigate login crash',
				description: null,
				status: 'todo',
				priority: 'high',
				type: 'bug',
				due_date: null,
				estimated_hours: null,
				tags: null,
				assignee_name: null
			}
		})
	);
	await page.route('/api/tasks/ai-breakdown', (route) =>
		route.fulfill({
			json: {
				subtasks: [
					{ title: 'Design flow', priority: 'medium', type: 'feature', estimated_hours: 2, description: 'Draft the flow.' },
					{ title: 'Fix edge case', priority: 'high', type: 'task', estimated_hours: 1, description: 'Handle the edge case.' }
				]
			}
		})
	);
}

test.describe('Task types', () => {
	test.beforeEach(async ({ page }) => {
		await mockApi(page);
	});

	test('shows type badges in list, kanban, and agile views', async ({ page }) => {
		await page.goto('/tasks');

		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
		await expect(page.getByText('Feature').first()).toBeVisible();
		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
		await expect(page.getByText('Bug').first()).toBeVisible();
		await expect(page.getByText('Chore task', { exact: true })).toBeVisible();
		await expect(page.getByText('Task').first()).toBeVisible();

		await page.getByRole('button', { name: /kanban/i }).click();
		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();

		await page.getByRole('button', { name: /agile/i }).click();
		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
	});

	test('filters by multiple task types across views', async ({ page }) => {
		await page.goto('/tasks');

		await page.getByRole('button', { name: /^Feature$/ }).click();
		await page.getByRole('button', { name: /^Bug$/ }).click();

		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
		await expect(page.getByText('Chore task', { exact: true })).toBeHidden();

		await page.getByRole('button', { name: /kanban/i }).click();
		await expect(page.getByText('Feature task', { exact: true })).toBeVisible();
		await expect(page.getByText('Bug task', { exact: true })).toBeVisible();
		await expect(page.getByText('Chore task', { exact: true })).toBeHidden();

		await page.getByRole('button', { name: /^Feature$/ }).click();
		await page.getByRole('button', { name: /^Bug$/ }).click();
		await expect(page.getByText('Chore task', { exact: true })).toBeVisible();
	});

	test('defaults create form to Task and applies AI type suggestions', async ({ page }) => {
		await page.goto('/tasks');
		await page.getByRole('button', { name: /new task/i }).click();

		await expect(page.locator('#t-type')).toHaveValue('task');

		await page.getByRole('button', { name: /nlp/i }).click();
		await page.locator('#ai-nlp').fill('Bug: investigate login crash');
		await page.getByRole('button', { name: /parse with ai/i }).click();

		await expect(page.locator('#t-type')).toHaveValue('bug');
	});

	test('lets AI breakdown subtasks keep editable task types', async ({ page }) => {
		await page.goto('/tasks');
		await page.getByRole('button', { name: /new task/i }).click();
		await page.getByRole('button', { name: /breakdown/i }).click();

		await page.locator('#bd-project').selectOption('1');
		await page.locator('#bd-desc').fill('Build task types');
		await page.getByRole('button', { name: /break down with ai/i }).click();

		await expect(page.getByLabel('Subtask title').first()).toHaveValue('Design flow');
		await expect(page.locator('select[id^="st-type-"]').first()).toHaveValue('feature');
		await page.locator('select[id^="st-type-"]').first().selectOption('improvement');
		await expect(page.locator('select[id^="st-type-"]').first()).toHaveValue('improvement');
	});
});
