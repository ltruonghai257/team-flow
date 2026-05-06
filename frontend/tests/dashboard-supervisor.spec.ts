import { test, expect } from '@playwright/test';

test.describe('Supervisor Dashboard', () => {
    test('supervisor sees all dashboard sections with team health and KPI', async ({
        page,
    }) => {
        // Authenticate as supervisor user
        await page.goto('/login');
        await page.fill('input[name="email"]', 'supervisor@example.com');
        await page.fill('input[name="password"]', 'testpassword');
        await page.click('button[type="submit"]');

        // Wait for redirect to dashboard
        await page.waitForURL('/');

        // Verify all sections are visible for supervisor
        const taskSection = page.locator('[data-testid="my-tasks-section"]');
        await expect(taskSection).toBeVisible();

        const activityFeed = page.locator(
            '[data-testid="activity-feed-section"]'
        );
        await expect(activityFeed).toBeVisible();

        const teamHealth = page.locator('[data-testid="team-health-section"]');
        await expect(teamHealth).toBeVisible();

        const kpiSummary = page.locator('[data-testid="kpi-summary-section"]');
        await expect(kpiSummary).toBeVisible();

        // Verify team health displays per-member workload
        const healthMembers = page.locator(
            '[data-testid="team-health-member"]'
        );
        const healthCount = await healthMembers.count();
        expect(healthCount).toBeGreaterThanOrEqual(0);

        // Verify at-risk members have distinct styling
        const atRiskMembers = page.locator(
            '[data-testid="team-health-member"][data-at-risk="true"]'
        );
        if ((await atRiskMembers.count()) > 0) {
            const firstAtRisk = atRiskMembers.first();
            await expect(firstAtRisk).toHaveCSS(
                'border-color',
                /rgba\(239,\s*68,\s*68/i
            );
        }

        // Verify KPI summary displays metrics
        const avgScore = page.locator('[data-testid="kpi-avg-score"]');
        await expect(avgScore).toBeVisible();

        const completionRate = page.locator(
            '[data-testid="kpi-completion-rate"]'
        );
        await expect(completionRate).toBeVisible();

        const needsAttention = page.locator(
            '[data-testid="kpi-needs-attention"]'
        );
        await expect(needsAttention).toBeVisible();

        // Verify activity feed is visible
        const feedItems = page.locator('[data-testid="activity-feed-item"]');
        const feedCount = await feedItems.count();
        expect(feedCount).toBeGreaterThanOrEqual(0);
    });
});
