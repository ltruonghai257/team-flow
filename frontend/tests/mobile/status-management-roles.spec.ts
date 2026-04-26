import { test, expect, type Page } from '@playwright/test';

// ---------------------------------------------------------------------------
// Shared fixtures
// ---------------------------------------------------------------------------

const baseTask = {
	id: 1,
	title: 'Sample task',
	description: null,
	status: 'todo',
	custom_status_id: 1,
	custom_status: { id: 1, name: 'To Do', slug: 'todo', color: '#64748b', is_done: false, is_archived: false, position: 0 },
	priority: 'medium',
	type: 'task',
	due_date: null,
	completed_at: null,
	estimated_hours: null,
	tags: null,
	project_id: 1,
	milestone_id: null,
	assignee_id: null,
	creator_id: 1,
	sprint_id: null,
	created_at: '2026-04-26T00:00:00Z',
	updated_at: '2026-04-26T00:00:00Z',
	assignee: null
};

const defaultStatusSet = {
	id: 1,
	scope: 'sub_team_default',
	project_id: null,
	sub_team_id: 1,
	statuses: [
		{ id: 1, name: 'To Do',      slug: 'todo',        color: '#64748b', is_done: false, is_archived: false, position: 0, status_set_id: 1 },
		{ id: 2, name: 'In Progress',slug: 'in_progress', color: '#3b82f6', is_done: false, is_archived: false, position: 1, status_set_id: 1 },
		{ id: 3, name: 'Done',       slug: 'done',        color: '#22c55e', is_done: true,  is_archived: false, position: 2, status_set_id: 1 }
	]
};

const project = { id: 1, name: 'Alpha', description: null, color: '#6366f1', sub_team_id: 1, created_at: '2026-04-26T00:00:00Z' };

function makeUser(role: 'admin' | 'supervisor' | 'member') {
	return {
		id: role === 'admin' ? 1 : role === 'supervisor' ? 2 : 3,
		email: `${role}@example.com`,
		username: role,
		full_name: `${role.charAt(0).toUpperCase() + role.slice(1)} User`,
		role,
		avatar_url: null,
		is_active: true,
		created_at: '2026-04-26T00:00:00Z'
	};
}

async function mockCommonRoutes(page: Page, role: 'admin' | 'supervisor' | 'member') {
	const user = makeUser(role);

	await page.route('/api/auth/me', (r) => r.fulfill({ json: user }));
	await page.route('/api/notifications/pending', (r) => r.fulfill({ json: [] }));
	await page.route('/api/users/', (r) => r.fulfill({ json: [user] }));
	await page.route('/api/projects/', (r) => r.fulfill({ json: [project] }));
	await page.route('/api/milestones/', (r) => r.fulfill({ json: [] }));
	await page.route('/api/sprints/', (r) => r.fulfill({ json: [] }));
	await page.route('**/api/tasks/**', (r) => r.fulfill({ json: [baseTask] }));
	await page.route('/api/status-sets/effective**', (r) => r.fulfill({ json: defaultStatusSet }));
	await page.route('/api/status-sets/default/statuses', (r) =>
		r.fulfill({ status: 201, json: { id: 99, name: 'New Status', slug: 'new-status', color: '#f59e0b', is_done: false, is_archived: false, position: 3, status_set_id: 1 } })
	);
}

async function mockProjectsRoutes(page: Page, role: 'admin' | 'supervisor' | 'member') {
	const user = makeUser(role);

	await page.route('/api/auth/me', (r) => r.fulfill({ json: user }));
	await page.route('/api/notifications/pending', (r) => r.fulfill({ json: [] }));
	await page.route('/api/projects/', (r) => r.fulfill({ json: [project] }));
	await page.route('/api/status-sets/effective**', (r) => r.fulfill({ json: defaultStatusSet }));
}

// ---------------------------------------------------------------------------
// /tasks — Manage Statuses visibility
// ---------------------------------------------------------------------------

test.describe('Status management — /tasks page', () => {

	test('admin: Manage Statuses button is visible', async ({ page }) => {
		await mockCommonRoutes(page, 'admin');
		await page.goto('/tasks');
		const btn = page.getByRole('button', { name: /manage statuses/i });
		await expect(btn).toBeVisible();
		await page.screenshot({ path: 'test-results/evidence/admin-tasks-manage-statuses-visible.png', fullPage: false });
	});

	test('supervisor: Manage Statuses button is visible', async ({ page }) => {
		await mockCommonRoutes(page, 'supervisor');
		await page.goto('/tasks');
		const btn = page.getByRole('button', { name: /manage statuses/i });
		await expect(btn).toBeVisible();
		await page.screenshot({ path: 'test-results/evidence/supervisor-tasks-manage-statuses-visible.png', fullPage: false });
	});

	test('member: Manage Statuses button is NOT visible', async ({ page }) => {
		await mockCommonRoutes(page, 'member');
		await page.goto('/tasks');
		const btn = page.getByRole('button', { name: /manage statuses/i });
		await expect(btn).not.toBeVisible();
		await page.screenshot({ path: 'test-results/evidence/member-tasks-manage-statuses-hidden.png', fullPage: false });
	});

});

// ---------------------------------------------------------------------------
// /tasks — StatusSetManager edit controls inside panel
// ---------------------------------------------------------------------------

test.describe('Status management — panel controls', () => {

	test('admin: can see Create status button inside panel', async ({ page }) => {
		await mockCommonRoutes(page, 'admin');
		await page.goto('/tasks');
		await page.getByRole('button', { name: /manage statuses/i }).click();
		await expect(page.getByRole('button', { name: /create status/i })).toBeVisible();
		await page.screenshot({ path: 'test-results/evidence/admin-tasks-panel-create-button.png', fullPage: false });
	});

	test('supervisor: can see Create status button inside panel', async ({ page }) => {
		await mockCommonRoutes(page, 'supervisor');
		await page.goto('/tasks');
		await page.getByRole('button', { name: /manage statuses/i }).click();
		await expect(page.getByRole('button', { name: /create status/i })).toBeVisible();
		await page.screenshot({ path: 'test-results/evidence/supervisor-tasks-panel-create-button.png', fullPage: false });
	});

	test('member: panel is not accessible (button hidden)', async ({ page }) => {
		await mockCommonRoutes(page, 'member');
		await page.goto('/tasks');
		// Manage Statuses button is hidden — panel cannot be opened
		await expect(page.getByRole('button', { name: /manage statuses/i })).not.toBeVisible();
		// Create status must also be absent
		await expect(page.getByRole('button', { name: /create status/i })).not.toBeVisible();
		await page.screenshot({ path: 'test-results/evidence/member-tasks-panel-no-edit-controls.png', fullPage: false });
	});

});

// ---------------------------------------------------------------------------
// /tasks — Kanban board renders DB statuses for all roles
// ---------------------------------------------------------------------------

test.describe('Kanban board — DB statuses visible to all roles', () => {

	for (const role of ['admin', 'supervisor', 'member'] as const) {
		test(`${role}: kanban shows DB status columns`, async ({ page }) => {
			await mockCommonRoutes(page, role);
			await page.goto('/tasks');
			await page.getByRole('button', { name: /kanban/i }).click();
			// All three DB status columns should be visible (scope to headings to avoid filter dropdown collision)
			await expect(page.getByRole('heading', { name: 'To Do', exact: true })).toBeVisible();
			await expect(page.getByRole('heading', { name: 'In Progress', exact: true })).toBeVisible();
			await expect(page.getByRole('heading', { name: 'Done', exact: true })).toBeVisible();
			await page.screenshot({ path: `test-results/evidence/${role}-kanban-db-status-columns.png`, fullPage: false });
		});
	}

});

// ---------------------------------------------------------------------------
// /projects — Statuses panel visibility and edit controls
// ---------------------------------------------------------------------------

test.describe('Status management — /projects page', () => {

	test('admin: Statuses button visible and shows Create project override', async ({ page }) => {
		await mockProjectsRoutes(page, 'admin');
		await page.goto('/projects');
		const statusBtn = page.getByRole('button', { name: /statuses/i }).first();
		await expect(statusBtn).toBeVisible();
		await statusBtn.click();
		// Panel should show Create project override (canManage=true)
		await expect(page.getByRole('button', { name: /create project override/i })).toBeVisible();
		await page.screenshot({ path: 'test-results/evidence/admin-projects-statuses-panel-override-button.png', fullPage: false });
	});

	test('supervisor: Statuses button visible and shows Create project override', async ({ page }) => {
		await mockProjectsRoutes(page, 'supervisor');
		await page.goto('/projects');
		const statusBtn = page.getByRole('button', { name: /statuses/i }).first();
		await expect(statusBtn).toBeVisible();
		await statusBtn.click();
		await expect(page.getByRole('button', { name: /create project override/i })).toBeVisible();
		await page.screenshot({ path: 'test-results/evidence/supervisor-projects-statuses-panel-override-button.png', fullPage: false });
	});

	test('member: Statuses button visible but no edit controls inside panel', async ({ page }) => {
		await mockProjectsRoutes(page, 'member');
		await page.goto('/projects');
		const statusBtn = page.getByRole('button', { name: /statuses/i }).first();
		await expect(statusBtn).toBeVisible();
		await statusBtn.click();
		// Panel opens (members can view) but no override button
		await expect(page.getByRole('button', { name: /create project override/i })).not.toBeVisible();
		await expect(page.getByRole('button', { name: /revert to defaults/i })).not.toBeVisible();
		await page.screenshot({ path: 'test-results/evidence/member-projects-statuses-panel-read-only.png', fullPage: false });
	});

});
