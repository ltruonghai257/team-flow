import { test, expect } from '@playwright/test';

test.describe('Member Dashboard', () => {
  test('member sees tasks and activity feed, but not team health or KPI', async ({ page }) => {
    // Authenticate as member user
    await page.goto('/login');
    await page.fill('input[name="email"]', 'member@example.com');
    await page.fill('input[name="password"]', 'testpassword');
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('/');

    // Verify task section is visible
    const taskSection = page.locator('[data-testid="my-tasks-section"]');
    await expect(taskSection).toBeVisible();

    // Verify activity feed is visible
    const activityFeed = page.locator('[data-testid="activity-feed-section"]');
    await expect(activityFeed).toBeVisible();

    // Verify team health section is NOT visible (member-only view)
    const teamHealth = page.locator('[data-testid="team-health-section"]');
    await expect(teamHealth).not.toBeVisible();

    // Verify KPI summary section is NOT visible (member-only view)
    const kpiSummary = page.locator('[data-testid="kpi-summary-section"]');
    await expect(kpiSummary).not.toBeVisible();

    // Verify overdue tasks have red styling
    const overdueTasks = page.locator('[data-testid="task-card"][data-overdue="true"]');
    if (await overdueTasks.count() > 0) {
      const firstOverdue = overdueTasks.first();
      await expect(firstOverdue).toHaveCSS('background-color', /rgba\(153,\s*0,\s*0/i);
    }

    // Verify due-soon tasks have indicator
    const dueSoonTasks = page.locator('[data-testid="task-card"][data-due-soon="true"]');
    if (await dueSoonTasks.count() > 0) {
      const firstDueSoon = dueSoonTasks.first();
      await expect(firstDueSoon).toHaveCSS('background-color', /rgba\(234,\s*179,\s*8/i);
    }

    // Verify task navigation
    const firstTask = page.locator('[data-testid="task-card"]').first();
    await firstTask.click();
    await page.waitForURL(/\/tasks/);
  });
});
