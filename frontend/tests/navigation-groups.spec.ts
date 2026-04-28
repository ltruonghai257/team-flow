import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.describe('Desktop grouped navigation', () => {
	test.use({ viewport: { width: 1280, height: 720 } });

	test.beforeEach(async ({ page }) => {
		await loginAs(page);
	});

	test('all five parent groups are visible', async ({ page }) => {
		await page.goto('/');

		// Verify all parent groups are present
		await expect(page.getByRole('button', { name: 'Dashboard' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Work' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Planning' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Team' })).toBeVisible();
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

		await page.getByRole('button', { name: 'Team' }).click();
		await page.getByRole('link', { name: 'Performance' }).click();
		await expect(page).toHaveURL('/performance');
	});

	test('nested route matching works for dynamic paths', async ({ page }) => {
		await page.goto('/performance/123');

		// Performance under Team should be active and parent auto-expanded
		await expect(page.getByRole('button', { name: 'Team' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Performance' })).toBeVisible();
	});

	test('Performance is visible to supervisor', async ({ page }) => {
		await page.goto('/');

		// Expand Team group
		await page.getByRole('button', { name: 'Team' }).click();

		// Performance should be visible for supervisor
		await expect(page.getByRole('link', { name: 'Performance' })).toBeVisible();
	});
});

test.describe('Desktop grouped navigation - Member role visibility', () => {
	test.use({ viewport: { width: 1280, height: 720 } });

	test.beforeEach(async ({ page }) => {
		// Login as member (non-supervisor)
		await page.goto('/login');
		await page.fill('input[name="username"]', 'member');
		await page.fill('input[name="password"]', 'password');
		await page.click('button[type="submit"]');
		await page.waitForURL('/');
	});

	test('Performance is hidden for non-supervisor', async ({ page }) => {
		await page.goto('/');

		// Expand Team group
		await page.getByRole('button', { name: 'Team' }).click();

		// Performance should not be visible for members
		await expect(page.getByRole('link', { name: 'Performance' })).not.toBeVisible();

		// Other Team children should still be visible
		await expect(page.getByRole('link', { name: 'Team' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Updates' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Weekly Board' })).toBeVisible();
	});

	test('attempting to access /performance redirects for non-supervisor', async ({ page }) => {
		await page.goto('/performance');

		// Should redirect to dashboard
		await expect(page).toHaveURL('/');
	});
});
