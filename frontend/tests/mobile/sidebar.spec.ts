import { test, expect } from '@playwright/test';

test.describe('Mobile sidebar (375px)', () => {
	test.use({ viewport: { width: 375, height: 812 } });

	test.beforeEach(async ({ page }) => {
		// Go to login page and authenticate
		await page.goto('/login');
	});

	test('hamburger button is visible and sidebar is hidden on load', async ({ page }) => {
		await page.goto('/');
		const hamburger = page.getByRole('button', { name: 'Open menu' });
		await expect(hamburger).toBeVisible();

		// Sidebar should be translated off-screen (has -translate-x-full class)
		const sidebar = page.locator('aside');
		await expect(sidebar).toHaveClass(/-translate-x-full/);
	});

	test('tapping hamburger opens sidebar', async ({ page }) => {
		await page.goto('/');
		await page.getByRole('button', { name: 'Open menu' }).click();

		const sidebar = page.locator('aside');
		await expect(sidebar).not.toHaveClass(/-translate-x-full/);

		// Backdrop visible
		await expect(page.locator('.fixed.inset-0.bg-black\\/60')).toBeVisible();
	});

	test('tapping backdrop closes sidebar', async ({ page }) => {
		await page.goto('/');
		await page.getByRole('button', { name: 'Open menu' }).click();
		await page.locator('.fixed.inset-0.bg-black\\/60').click();

		const sidebar = page.locator('aside');
		await expect(sidebar).toHaveClass(/-translate-x-full/);
	});

	test('nav link closes sidebar and navigates', async ({ page }) => {
		await page.goto('/');
		await page.getByRole('button', { name: 'Open menu' }).click();
		await page.getByRole('link', { name: 'Tasks' }).click();

		await expect(page).toHaveURL('/tasks');
		const sidebar = page.locator('aside');
		await expect(sidebar).toHaveClass(/-translate-x-full/);
	});

	test('hamburger is hidden at md breakpoint (768px)', async ({ page }) => {
		await page.setViewportSize({ width: 768, height: 1024 });
		await page.goto('/');
		const hamburger = page.locator('header.md\\:hidden');
		await expect(hamburger).toBeHidden();
	});
});
