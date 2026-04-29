import { expect, test, type Page } from '@playwright/test';

type Role = 'manager' | 'supervisor' | 'assistant_manager' | 'member';

function makeUser(id: number, role: Role) {
	return {
		id,
		email: `${role}@example.com`,
		username: role,
		full_name: role.replace('_', ' '),
		role,
		avatar_url: null,
		is_active: true,
		sub_team_id: role === 'manager' ? null : 10,
		created_at: '2026-04-29T00:00:00Z'
	};
}

const users = [
	makeUser(1, 'manager'),
	makeUser(2, 'supervisor'),
	makeUser(3, 'assistant_manager'),
	makeUser(4, 'member')
];

async function mockTeamApi(page: Page, role: Role) {
	await page.route('**/api/auth/me', (route) => route.fulfill({ json: makeUser(99, role) }));
	await page.route('**/api/notifications/pending', (route) => route.fulfill({ json: [] }));
	await page.route('**/api/users/', (route) => route.fulfill({ json: users }));
	await page.route('**/api/tasks/**', (route) => route.fulfill({ json: [] }));
	await page.route('**/api/invites/pending', (route) => route.fulfill({ json: [] }));
	await page.route('**/api/sub-teams/', (route) =>
		route.fulfill({
			json: [{ id: 10, name: 'Alpha', supervisor_id: 2 }]
		})
	);
	await page.route('**/api/sub-teams/reminder-settings/current', (route) =>
		route.fulfill({
			json: {
				id: 1,
				sub_team_id: 10,
				lead_time_days: 2,
				sprint_reminders_enabled: true,
				milestone_reminders_enabled: true,
				updated_at: '2026-04-29T00:00:00Z'
			}
		})
	);
	await page.route('**/api/sub-teams/reminder-settings/proposals', (route) =>
		route.fulfill({ json: [] })
	);
}

test.describe('Team role visibility', () => {
	test.use({ viewport: { width: 1280, height: 720 } });

	test('manager can assign leadership roles', async ({ page }) => {
		await mockTeamApi(page, 'manager');
		await page.goto('/team');

		await page.getByRole('button', { name: 'Invite Member' }).click();
		const inviteRole = page.locator('#inviteRole');
		await expect(inviteRole.getByRole('option', { name: 'Member' })).toBeAttached();
		await expect(inviteRole.getByRole('option', { name: 'Supervisor' })).toBeAttached();
		await expect(inviteRole.getByRole('option', { name: 'Assistant Manager' })).toBeAttached();
		await expect(inviteRole.getByRole('option', { name: 'Manager', exact: true })).toBeAttached();
		await expect(page.getByText('Admin')).toHaveCount(0);
	});

	for (const role of ['supervisor', 'assistant_manager'] as const) {
		test(`${role} can manage members without leadership assignment options`, async ({ page }) => {
			await mockTeamApi(page, role);
			await page.goto('/team');

			await expect(page.getByRole('button', { name: 'Invite Member' })).toBeVisible();
			await page.getByRole('button', { name: 'Invite Member' }).click();
			const inviteRole = page.locator('#inviteRole');
			await expect(inviteRole.getByRole('option', { name: 'Member' })).toBeAttached();
			await expect(inviteRole.getByRole('option', { name: 'Supervisor' })).toHaveCount(0);
			await expect(inviteRole.getByRole('option', { name: 'Assistant Manager' })).toHaveCount(0);
			await expect(inviteRole.getByRole('option', { name: 'Manager', exact: true })).toHaveCount(0);
		});
	}

	test('member does not see management controls', async ({ page }) => {
		await mockTeamApi(page, 'member');
		await page.goto('/team');

		await expect(page.getByRole('button', { name: 'Invite Member' })).toHaveCount(0);
		await expect(page.getByRole('button', { name: 'Add Member' })).toHaveCount(0);
		await expect(page.getByRole('button', { name: 'Sub-Teams' })).toHaveCount(0);
		await expect(page.getByText('Read-only view for your team.')).toBeVisible();
	});
});
