import { type Page } from '@playwright/test';

/**
 * Login helper for Playwright tests.
 * Set credentials via env vars:
 *   TEST_USERNAME=your_username TEST_PASSWORD=your_password bun run test:mobile
 * Defaults to the values below if env vars are not set.
 */
export async function loginAs(page: Page, username?: string, password?: string) {
	const user = username ?? process.env.TEST_USERNAME ?? 'testuser';
	const pass = password ?? process.env.TEST_PASSWORD ?? 'testpass';

	await page.goto('/login');
	await page.locator('#username').fill(user);
	await page.locator('#password').fill(pass);
	await page.getByRole('button', { name: 'Sign In' }).click();
	// Wait for client-side navigation away from /login
	await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 15000 });
}
