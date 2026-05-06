import { test, expect } from '@playwright/test';

test('dashboard loads without infinite loading', async ({ page }) => {
  // Navigate to dashboard
  await page.goto('http://localhost:5174/');
  
  // Wait for page to load (max 10 seconds)
  await page.waitForLoadState('networkidle', { timeout: 10000 });
  
  // Check if we're on login page or dashboard
  const url = page.url();
  
  if (url.includes('/login')) {
    console.log('Redirected to login page - expected behavior');
    // Login with demo credentials
    await page.fill('input[name="email"]', 'manager@demo.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Wait for navigation after login
    await page.waitForLoadState('networkidle', { timeout: 10000 });
  }
  
  // Check that loading spinner is not stuck
  const spinner = page.locator('.animate-spin');
  await expect(spinner).toHaveCount(0, { timeout: 10000 });
  
  // Check that dashboard content is visible or error message is shown
  const dashboardContent = page.locator('h1:has-text("Dashboard")');
  const errorMessage = page.locator('text=/failed to load/i');
  
  const hasDashboard = await dashboardContent.count() > 0;
  const hasError = await errorMessage.count() > 0;
  
  expect(hasDashboard || hasError).toBeTruthy();
  
  if (hasError) {
    console.log('Error state displayed (expected when backend is down)');
  } else {
    console.log('Dashboard loaded successfully');
  }
});
