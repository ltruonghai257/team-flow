import { test, expect } from '@playwright/test';
import { loginAs } from '../helpers/auth';

test.describe('Mobile sidebar (375px) - Grouped Navigation', () => {
	test.use({ viewport: { width: 375, height: 812 } });

	test.beforeEach(async ({ page }) => {
		await loginAs(page);
	});

	test('hamburger button is visible and sidebar is hidden on load', async ({ page }) => {
		await page.goto('/');
		const hamburger = page.getByRole('button', { name: 'Open menu' });
		await expect(hamburger).toBeVisible();

		// Sidebar should be translated off-screen (has -translate-x-full class)
		const sidebar = page.locator('aside');
		await expect(sidebar).toHaveClass(/-translate-x-full/);
	});

	test('tapping hamburger opens sidebar with grouped navigation', async ({ page }) => {
		await page.goto('/');
		await page.getByRole('button', { name: 'Open menu' }).click();

		const sidebar = page.locator('aside');
		await expect(sidebar).not.toHaveClass(/-translate-x-full/);

		// Backdrop visible
		await expect(page.locator('.fixed.inset-0.bg-black\\/60')).toBeVisible();

		// Verify parent groups are visible
		await expect(page.getByRole('button', { name: 'Dashboard' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Work' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Planning' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'Team' })).toBeVisible();
		await expect(page.getByRole('button', { name: 'AI' })).toBeVisible();
	});

	test('tapping backdrop closes sidebar', async ({ page }) => {
		await page.goto('/');
		await page.getByRole('button', { name: 'Open menu' }).click();
		await page.locator('.fixed.inset-0.bg-black\\/60').click();

		const sidebar = page.locator('aside');
		await expect(sidebar).toHaveClass(/-translate-x-full/);
	});

	test('parent group expansion toggles without navigation', async ({ page }) => {
		await page.goto('/');
		await page.getByRole('button', { name: 'Open menu' }).click();

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

	test('child link closes sidebar and navigates', async ({ page }) => {
		await page.goto('/');
		await page.getByRole('button', { name: 'Open menu' }).click();

		// Expand Work group
		await page.getByRole('button', { name: 'Work' }).click();
		await page.getByRole('link', { name: 'Tasks' }).click();

		await expect(page).toHaveURL('/tasks');
		const sidebar = page.locator('aside');
		await expect(sidebar).toHaveClass(/-translate-x-full/);
	});

	test('active parent auto-expands on page load', async ({ page }) => {
		await page.goto('/tasks');
		await page.getByRole('button', { name: 'Open menu' }).click();

		// Work group should be auto-expanded since /tasks is under Work
		await expect(page.getByRole('link', { name: 'Projects' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Tasks' })).toBeVisible();
	});

	test('hamburger is hidden at md breakpoint (768px)', async ({ page }) => {
		await page.setViewportSize({ width: 768, height: 1024 });
		await page.goto('/');
		const hamburger = page.locator('header.md\\:hidden');
		await expect(hamburger).toBeHidden();
	});
});
