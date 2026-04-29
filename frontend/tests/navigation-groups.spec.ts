import { test, expect, type Page } from '@playwright/test';

type Role = 'manager' | 'supervisor' | 'assistant_manager' | 'member';

function userFor(role: Role) {
	return {
		id: role === 'manager' ? 1 : role === 'supervisor' ? 2 : role === 'assistant_manager' ? 3 : 4,
		email: `${role}@example.com`,
		username: role,
		full_name: role.replace('_', ' '),
		role,
		avatar_url: null,
		is_active: true,
		created_at: '2026-04-29T00:00:00Z'
	};
}

async function mockSession(page: Page, role: Role) {
	await page.route('**/api/auth/me', (route) => route.fulfill({ json: userFor(role) }));
	await page.route('**/api/notifications/pending', (route) => route.fulfill({ json: [] }));
}

test.describe('Desktop grouped navigation', () => {
	test.use({ viewport: { width: 1280, height: 720 } });

	test.beforeEach(async ({ page }) => {
		await mockSession(page, 'manager');
	});

	test('all five parent groups are visible', async ({ page }) => {
		await page.goto('/');

		// Verify all parent groups are present
		await expect(page.getByRole('button', { name: 'Dashboard' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Work' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Planning' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Team', exact: true })).toBeVisible();
		await expect(page.getByRole('button', { name: 'AI' })).toBeVisible();
	});

	test('parent group expansion toggles without navigation', async ({ page }) => {
		await page.goto('/');

		// Tap Work parent group
		const workGroup = page.getByRole('button', { name: 'Work' });
		await workGroup.click();

		// Should show child links (Projects, Tasks)
		await expect(page.getByRole('link', { name: 'Projects' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Tasks' })).toBeVisible();

		// URL should not change (parent rows are non-navigating)
		await expect(page).toHaveURL('/');

		// Tap again to collapse
		await workGroup.click();
		await expect(page.getByRole('link', { name: 'Projects' })).not.toBeVisible();
	});

	test('active parent auto-expands on page load', async ({ page }) => {
		await page.goto('/tasks');

		// Work group should be auto-expanded since /tasks is under Work
		await expect(page.getByRole('link', { name: 'Projects' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Tasks' })).toBeVisible();
	});

	test('active child has stronger highlight than active parent', async ({ page }) => {
		await page.goto('/tasks');

		// Both parent and child should have active styling
		const workGroup = page.getByRole('button', { name: 'Work' });
		const tasksLink = page.getByRole('link', { name: 'Tasks' });

		// Verify both are visible and have active classes
		await expect(workGroup).toHaveClass(/bg-primary-600\/10/); // Lighter parent highlight
		await expect(tasksLink).toHaveClass(/bg-primary-600\/20/); // Stronger child highlight
	});

	test('child navigation preserves URLs', async ({ page }) => {
		await page.goto('/');

		// Navigate through various child routes
		await page.getByRole('button', { name: 'Work' }).click();
		await page.getByRole('link', { name: 'Projects' }).click();
		await expect(page).toHaveURL('/projects');

		await page.getByRole('button', { name: 'Planning' }).click();
		await page.getByRole('link', { name: 'Timeline' }).click();
		await expect(page).toHaveURL('/timeline');

		await page.getByRole('button', { name: 'Team', exact: true }).click();
		await page.getByRole('link', { name: 'Performance' }).click();
		await expect(page).toHaveURL(/\/performance(\/overview)?$/);
	});

	test('nested route matching works for dynamic paths', async ({ page }) => {
		await page.goto('/performance/123');

		// Performance under Team should be active and parent auto-expanded
		await expect(page.getByRole('button', { name: 'Team', exact: true })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Performance' })).toBeVisible();
	});

	test('Performance is visible to manager', async ({ page }) => {
		await page.goto('/');

		// Expand Team group
		await page.getByRole('button', { name: 'Team', exact: true }).click();

		// Performance should be visible for managers and scoped leaders
		await expect(page.getByRole('link', { name: 'Performance' })).toBeVisible();
	});
});

test.describe('Desktop grouped navigation - scoped leader visibility', () => {
	test.use({ viewport: { width: 1280, height: 720 } });

	for (const role of ['supervisor', 'assistant_manager'] as const) {
		test(`Performance is visible to ${role}`, async ({ page }) => {
			await mockSession(page, role);
			await page.goto('/');
			await page.getByRole('button', { name: 'Team', exact: true }).click();
			await expect(page.getByRole('link', { name: 'Performance' })).toBeVisible();
		});
	}
});

test.describe('Desktop grouped navigation - Member role visibility', () => {
	test.use({ viewport: { width: 1280, height: 720 } });

	test.beforeEach(async ({ page }) => {
		await mockSession(page, 'member');
	});

	test('Performance is hidden for members', async ({ page }) => {
		await page.goto('/');

		// Expand Team group
		await page.getByRole('button', { name: 'Team', exact: true }).click();

		// Performance should not be visible for members
		await expect(page.getByRole('link', { name: 'Performance' })).not.toBeVisible();

		// Other Team children should still be visible
		await expect(page.getByRole('link', { name: 'Team' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Updates' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Weekly Board' })).toBeVisible();
	});

	test('attempting to access /performance redirects for members', async ({ page }) => {
		await page.goto('/performance');

		// Should redirect to dashboard
		await expect(page).toHaveURL('/');
	});
});
