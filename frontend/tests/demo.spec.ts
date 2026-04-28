import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.use({
	video: 'on',
	viewport: { width: 1920, height: 1080 },
});

test.describe('TeamFlow Detailed Feature Demo', () => {
	test('Detailed scenarios for each phase (excluding refactor)', async ({ page }) => {
		// ========== PHASE 1: Production Hardening ==========
		// Login flow with detailed steps
		await page.goto('/login');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 1: Production Hardening - Secure Login Flow';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(2000);
		
		await page.locator('#username').fill('testuser');
		await page.locator('#password').fill('testpass');
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});
		await page.getByRole('button', { name: 'Sign In' }).click();
		await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 15000 });
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,100,0,0.9); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = '✓ Login Successful - Auth Token Stored';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(2000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 2: RBAC & Role Model ==========
		// Dashboard shows role-based information
		await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 2: RBAC - Role-Based Dashboard View';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 3: Supervisor Performance Dashboard ==========
		await page.getByRole('link', { name: 'Performance', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 3: Supervisor Dashboard - Team KPI Metrics';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 4: Team Timeline View ==========
		await page.getByRole('link', { name: 'Timeline', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 4: Timeline - Visual Project Gantt Chart';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 5: Enhanced AI Features ==========
		await page.getByRole('link', { name: 'AI Assistant', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 5: AI Assistant - Persistent Chat Context';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 6: Mobile-Responsive UI ==========
		// Resize to mobile and show responsive design
		await page.setViewportSize({ width: 375, height: 667 });
		await page.waitForTimeout(1000);
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 6: Mobile Responsive - Collapsible Sidebar';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});
		
		await page.setViewportSize({ width: 1920, height: 1080 });
		await page.waitForTimeout(1000);

		// ========== PHASE 8: User Invite & Team Management ==========
		await page.getByRole('link', { name: 'Team', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 8: Team Management - Viewing Team Members';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 12: Task Types ==========
		await page.getByRole('link', { name: 'Tasks', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 12: Task Types - Viewing Different Task Categories';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 14: Sprint Model ==========
		await page.getByRole('button', { name: 'Kanban' }).click();
		await page.waitForTimeout(1500);
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 14: Sprint Model - Kanban Board with Sprint Organization';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 15: Custom Kanban Statuses ==========
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 15: Custom Statuses - Custom Workflow Columns in Kanban';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 16: Advanced KPI Dashboard ==========
		await page.getByRole('link', { name: 'Performance', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 16: Advanced KPI - Velocity, Burndown, Completion Rates';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 17: Sprint & Release Reminders ==========
		await page.getByRole('link', { name: 'Scheduler', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 17: Reminders - Event Notifications & Alerts';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 18: Status Transition Graph ==========
		await page.getByRole('link', { name: 'Tasks', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 18: Status Transitions - Role-Based Workflow Rules';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== PHASE 23: Standup Updates ==========
		await page.getByRole('link', { name: 'Updates', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: white; padding: 15px 30px; border-radius: 10px; font-size: 24px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif;';
			annotation.textContent = 'PHASE 23: Standup Updates - Viewing Team Standup Feed';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(3000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});

		// ========== SUMMARY ==========
		await page.getByRole('link', { name: 'Dashboard', exact: true }).click();
		await page.waitForLoadState('networkidle');
		
		await page.evaluate(() => {
			const annotation = document.createElement('div');
			annotation.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.9); color: white; padding: 30px 50px; border-radius: 15px; font-size: 32px; font-weight: bold; z-index: 10000; font-family: Arial, sans-serif; text-align: center;';
			annotation.innerHTML = 'TeamFlow Detailed Feature Demo<br><span style="font-size: 20px; font-weight: normal;">Phases 1-18 & 23 with Scenarios<br>Phases 19-22: Refactor (Excluded)<br>Phases 24-25: In Development</span>';
			annotation.id = 'demo-annotation';
			document.body.appendChild(annotation);
		});
		await page.waitForTimeout(5000);
		await page.evaluate(() => {
			const el = document.getElementById('demo-annotation');
			if (el) el.remove();
		});
	});
});
