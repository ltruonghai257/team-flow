import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
	testDir: './tests',
	fullyParallel: true,
	retries: 0,
	reporter: 'list',
	timeout: 600000,
	use: {
		baseURL: 'http://127.0.0.1:5173',
		trace: 'on-first-retry',
		video: 'on',
	},
	projects: [
		{
			name: 'desktop-chrome',
			use: { ...devices['Desktop Chrome'], channel: 'chrome' },
		},
	],
	...(process.env.PLAYWRIGHT_SKIP_WEBSERVER === '1'
		? {}
		: {
				webServer: {
					command: 'bun run dev -- --host 127.0.0.1 --port 5173',
					url: 'http://127.0.0.1:5173',
					reuseExistingServer: true,
					timeout: 30000,
				},
			}),
});
