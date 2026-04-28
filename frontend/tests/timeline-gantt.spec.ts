import { expect, test } from '@playwright/test';

const TIMELINE_FIXTURE = [
	{
		id: 1,
		name: 'Project Atlas',
		color: '#6366f1',
		milestones: [
			{
				id: 101,
				title: 'M1 Launch Readiness',
				description: null,
				status: 'in_progress',
				start_date: '2026-03-01T00:00:00.000Z',
				due_date: '2026-03-25T00:00:00.000Z',
				completed_at: null,
				tasks: [
					{
						id: 1001,
						title: 'Prepare go-live checklist',
						description: null,
						tags: null,
						status: 'in_progress',
						priority: 'high',
						due_date: '2026-03-18T00:00:00.000Z',
						created_at: '2026-03-03T00:00:00.000Z',
						milestone_id: 101,
						project_id: 1,
						assignee_id: 30,
						custom_status_id: null,
						custom_status: null,
						assignee: {
							id: 30,
							email: 'ada@example.com',
							username: 'ada',
							full_name: 'Ada Lovelace',
							role: 'member',
							avatar_url: null,
							is_active: true,
							sub_team_id: 1,
							created_at: '2026-01-01T00:00:00.000Z'
						}
					}
				]
			}
		],
		unassigned_tasks: []
	}
];

test.describe('Timeline Gantt milestone-first regressions', () => {
	test.beforeEach(async ({ page }) => {
		await page.route('**/api/auth/me', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 30,
					email: 'ada@example.com',
					username: 'ada',
					full_name: 'Ada Lovelace',
					role: 'member',
					avatar_url: null,
					is_active: true,
					created_at: '2026-01-01T00:00:00.000Z'
				})
			});
		});
		await page.route('**/api/notifications/unread', async (route) => {
			await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
		});
		await page.route('**/api/timeline/', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(TIMELINE_FIXTURE)
			});
		});
		await page.route('**/api/tasks/*', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ ok: true })
			});
		});
	});

	test('timeline renders project-scoped task rows for milestone planning context', async ({ page }) => {
		await page.goto('/timeline');
		await expect(page.getByRole('button', { name: 'By Project' })).toHaveClass(/bg-indigo-600/);
		await expect(page.getByText('Prepare go-live checklist')).toBeVisible();
	});

	test('preserves selected custom date range when switching between By Project and By Member', async ({ page }) => {
		await page.goto('/timeline');
		await page.getByRole('combobox').selectOption('custom');

		const dateInputs = page.locator('input[type="date"]');
		await expect(dateInputs).toHaveCount(2);
		await dateInputs.nth(0).fill('2026-02-10');
		await dateInputs.nth(1).fill('2026-04-30');

		await page.getByRole('button', { name: 'By Member' }).click();
		await expect(dateInputs.nth(0)).toHaveValue('2026-02-10');
		await expect(dateInputs.nth(1)).toHaveValue('2026-04-30');

		await page.getByRole('button', { name: 'By Project' }).click();
		await expect(dateInputs.nth(0)).toHaveValue('2026-02-10');
		await expect(dateInputs.nth(1)).toHaveValue('2026-04-30');
	});

	test('member view keeps milestone/task context understandable after switching views', async ({ page }) => {
		await page.goto('/timeline');
		await page.getByRole('button', { name: 'By Member' }).click();
		await expect(page.getByText('Ada Lovelace')).toBeVisible();
		await expect(page.getByText('Prepare go-live checklist')).toBeVisible();
	});
});
