import { test, expect } from '@playwright/test';

test.describe('Kanban horizontal scroll on mobile (375px)', () => {
	test.use({ viewport: { width: 375, height: 812 } });

	test('kanban board scrolls horizontally', async ({ page }) => {
		await page.goto('/tasks');

		// Switch to Kanban view
		const kanbanBtn = page.getByRole('button', { name: /kanban/i });
		if (await kanbanBtn.isVisible()) {
			await kanbanBtn.click();
		}

		const board = page.locator('.overflow-x-auto').first();
		await expect(board).toBeVisible();

		const scrollWidth = await board.evaluate((el) => el.scrollWidth);
		const clientWidth = await board.evaluate((el) => el.clientWidth);
		expect(scrollWidth).toBeGreaterThan(clientWidth);
	});

	test('kanban board has touch-action style', async ({ page }) => {
		await page.goto('/tasks');

		const kanbanBtn = page.getByRole('button', { name: /kanban/i });
		if (await kanbanBtn.isVisible()) {
			await kanbanBtn.click();
		}

		const board = page.locator('[style*="touch-action"]').first();
		await expect(board).toBeVisible();
		const touchAction = await board.evaluate((el) => (el as HTMLElement).style.touchAction);
		expect(touchAction).toContain('pan-x');
	});
});
