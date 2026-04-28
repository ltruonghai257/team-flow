import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
	testDir: './tests',
	fullyParallel: true,
	retries: 0,
	reporter: 'list',
	timeout: 600000,
	use: {
		baseURL: 'http://localhost:5173',
		trace: 'on-first-retry',
		video: 'on',
	},
	projects: [
		{
			name: 'desktop-chrome',
			use: { ...devices['Desktop Chrome'] },
		},
	],
	webServer: {
		command: 'bun run dev',
		url: 'http://localhost:5173',
		reuseExistingServer: true,
		timeout: 30000,
	},
});
