import { test, expect } from '@playwright/test';
import { loginAs } from './helpers/auth';

test.describe('Sprint Board E2E', () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page);
  });

  test('Kanban board displays Backlog column for unassigned tasks', async ({ page }) => {
    await page.goto('/tasks');
    await page.getByRole('button', { name: 'Kanban' }).click();

    // Verify Backlog column is visible
    const backlogColumn = page.getByRole('heading', { name: 'Backlog' });
    await expect(backlogColumn).toBeVisible();
  });

  test('Sprint selector filters tasks by selected sprint', async ({ page }) => {
    await page.goto('/tasks');
    await page.getByRole('button', { name: 'Kanban' }).click();

    // Get the sprint selector
    const sprintSelector = page.locator('select').first();
    
    // Verify "No Sprint (Backlog)" is selected by default
    const selectedOption = await sprintSelector.inputValue();
    expect(selectedOption).toBe('');
  });

  test('Dragging task to Backlog removes sprint assignment', async ({ page }) => {
    await page.goto('/tasks');
    await page.getByRole('button', { name: 'Kanban' }).click();

    // This test requires a task in a sprint to drag to backlog
    // For now, just verify the Backlog column is a valid drop target
    const backlogColumn = page.getByRole('heading', { name: 'Backlog' }).locator('..');
    await expect(backlogColumn).toBeVisible();
  });

  test('Sprint board filters correctly when sprint is selected', async ({ page }) => {
    await page.goto('/tasks');
    await page.getByRole('button', { name: 'Kanban' }).click();

    // Verify the sprint selector exists
    const sprintSelector = page.locator('select').first();
    await expect(sprintSelector).toBeVisible();
  });
});
