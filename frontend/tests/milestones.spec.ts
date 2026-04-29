import { expect, test } from '@playwright/test';

const MILESTONE_COMMAND_VIEW_FIXTURE = {
	metrics: {
		active_milestones: 2,
		risky_milestones: 1,
		proposed_decisions: 3,
		blocked_tasks: 1
	},
	lanes: {
		planned: [
			{
				id: 1,
				title: 'Future Milestone',
				project_name: 'Project Alpha',
				due_date: '2026-12-01T00:00:00.000Z',
				planning_state: 'planned',
				risk: null,
				progress: { total: 5, done: 0, blocked: 0, completion_percent: 0 },
				decision_summary: { proposed: 1, approved: 0 },
				tasks: [],
				decisions: []
			}
		],
		committed: [
			{
				id: 2,
				title: 'Committed Milestone',
				project_name: 'Project Beta',
				due_date: '2026-06-01T00:00:00.000Z',
				planning_state: 'committed',
				risk: 'watch',
				progress: { total: 10, done: 2, blocked: 0, completion_percent: 20 },
				decision_summary: { proposed: 0, approved: 1 },
				tasks: [],
				decisions: []
			}
		],
		active: [
			{
				id: 3,
				title: 'Active Milestone',
				project_name: 'Project Alpha',
				due_date: '2026-04-15T00:00:00.000Z',
				planning_state: 'active',
				risk: null,
				progress: { total: 8, done: 4, blocked: 1, completion_percent: 50 },
				decision_summary: { proposed: 2, approved: 1 },
				tasks: [
					{ id: 101, title: 'Critical Task', status: 'in_progress', priority: 'high', due_date: '2026-04-10T00:00:00.000Z' },
					{ id: 102, title: 'Blocked Task', status: 'blocked', priority: 'medium', due_date: '2026-04-12T00:00:00.000Z' }
				],
				decisions: [
					{ id: 1, title: 'Choose API Provider', note: 'Considering Stripe vs Braintree', status: 'proposed', created_at: '2026-03-20T10:00:00.000Z' }
				]
			}
		],
		completed: [
			{
				id: 4,
				title: 'Completed Milestone',
				project_name: 'Project Gamma',
				due_date: '2026-02-01T00:00:00.000Z',
				planning_state: 'completed',
				risk: null,
				progress: { total: 4, done: 4, blocked: 0, completion_percent: 100 },
				decision_summary: { proposed: 0, approved: 2 },
				tasks: [],
				decisions: []
			}
		]
	}
};

const RISKY_MILESTONE_FIXTURE = {
	...MILESTONE_COMMAND_VIEW_FIXTURE,
	lanes: {
		...MILESTONE_COMMAND_VIEW_FIXTURE.lanes,
		planned: [
			{
				id: 5,
				title: 'Risky Planned Milestone',
				project_name: 'Project Delta',
				due_date: '2026-05-01T00:00:00.000Z',
				planning_state: 'planned',
				risk: 'at_risk',
				progress: { total: 3, done: 0, blocked: 2, completion_percent: 0 },
				decision_summary: { proposed: 1, approved: 0 },
				tasks: [{ id: 103, title: 'Delayed Task', status: 'todo', priority: 'high', due_date: '2026-04-01T00:00:00.000Z' }],
				decisions: []
			}
		]
	}
};

test.describe('Milestone Command View', () => {
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
					is_active: true
				})
			});
		});
		await page.route('**/api/notifications/unread', async (route) => {
			await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
		});
		await page.route('**/api/projects/', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{ id: 1, name: 'Project Alpha' },
					{ id: 2, name: 'Project Beta' },
					{ id: 3, name: 'Project Gamma' },
					{ id: 4, name: 'Project Delta' }
				])
			});
		});
	});

	test('renders all four lanes and summary metrics', async ({ page }) => {
		await page.route('**/api/milestones/command-view', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(MILESTONE_COMMAND_VIEW_FIXTURE)
			});
		});

		await page.goto('/milestones');

		// Check metrics
		await expect(page.getByText('2', { exact: true }).first()).toBeVisible(); // Active
		await expect(page.getByText('1', { exact: true }).first()).toBeVisible(); // Risky
		await expect(page.getByText('3', { exact: true }).first()).toBeVisible(); // Proposed Decisions
		await expect(page.getByText('1', { exact: true }).nth(1)).toBeVisible(); // Blocked Tasks (nth because metrics row has multiple '1's potentially)

		// Check lanes
		await expect(page.getByText('Planned', { exact: true })).toBeVisible();
		await expect(page.getByText('Committed', { exact: true })).toBeVisible();
		await expect(page.getByText('Active', { exact: true })).toBeVisible();
		await expect(page.getByText('Completed', { exact: true })).toBeVisible();

		// Check milestone presence in lanes
		await expect(page.getByText('Future Milestone')).toBeVisible();
		await expect(page.getByText('Committed Milestone')).toBeVisible();
		await expect(page.getByText('Active Milestone')).toBeVisible();
		await expect(page.getByText('Completed Milestone')).toBeVisible();
	});

	test('auto-expands active milestones and shows details', async ({ page }) => {
		await page.route('**/api/milestones/command-view', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(MILESTONE_COMMAND_VIEW_FIXTURE)
			});
		});

		await page.goto('/milestones');

		// Active Milestone (ID 3) should be expanded by default
		await expect(page.getByText('Critical Task')).toBeVisible();
		await expect(page.getByText('Choose API Provider')).toBeVisible();
		
		// Planned Milestone (ID 1) should NOT be expanded by default
		await expect(page.getByText('No tasks linked to this milestone.')).not.toBeVisible();
	});

	test('auto-expands risky milestones even if not active', async ({ page }) => {
		await page.route('**/api/milestones/command-view', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(RISKY_MILESTONE_FIXTURE)
			});
		});

		await page.goto('/milestones');

		// Risky Planned Milestone (ID 5) should be expanded
		await expect(page.getByText('Delayed Task')).toBeVisible();
		await expect(page.getByText('Risky Planned Milestone').locator('xpath=..').getByText('AT RISK')).toBeVisible();
	});

	test('decision CRUD interaction', async ({ page }) => {
		await page.route('**/api/milestones/command-view', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(MILESTONE_COMMAND_VIEW_FIXTURE)
			});
		});

		let createCalled = false;
		await page.route('**/api/milestones/3/decisions', async (route) => {
			if (route.request().method() === 'POST') {
				createCalled = true;
				await route.fulfill({ status: 201, body: JSON.stringify({ id: 99, title: 'New Decision' }) });
			}
		});

		await page.goto('/milestones');

		// Find the 'Add Decision' button in the expanded Active Milestone card
		const activeCard = page.locator('#milestone-3');
		await activeCard.getByRole('button', { name: 'Add Decision' }).click();

		await page.getByPlaceholder('Decision title *').fill('New Test Decision');
		await page.getByPlaceholder('Notes (optional)').fill('Some details');
		await page.locator('#milestone-3').getByRole('button').filter({ hasText: '' }).last().click(); // The Check button

		expect(createCalled).toBe(true);
	});

	test('mobile layout stacks lanes', async ({ page }) => {
		await page.setViewportSize({ width: 375, height: 667 });
		
		await page.route('**/api/milestones/command-view', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(MILESTONE_COMMAND_VIEW_FIXTURE)
			});
		});

		await page.goto('/milestones');

		// In mobile, lanes are stacked vertically. 
		// We verify they all exist and are visible.
		await expect(page.getByText('Planned')).toBeVisible();
		await expect(page.getByText('Committed')).toBeVisible();
		await expect(page.getByText('Active')).toBeVisible();
		await expect(page.getByText('Completed')).toBeVisible();
		
		// Verify metrics are also visible in mobile (grid-cols-2)
		await expect(page.getByText('Active', { exact: true })).toBeVisible();
		await expect(page.getByText('Risky', { exact: true })).toBeVisible();
	});
});
