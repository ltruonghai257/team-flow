import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

(async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    const imagesDir = path.join(__dirname, '../docs/images');

    try {
        console.log('Capturing screenshots...');

        // Login page
        await page.goto('http://localhost:5175/login');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '01-login-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured login page');

        // Register page
        await page.goto('http://localhost:5175/register');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '02-register-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured register page');

        // Login with demo credentials
        await page.goto('http://localhost:5175/login');
        await page.fill('input[name="username"]', 'supervisor');
        await page.fill('input[name="password"]', 'password123');
        await page.click('button[type="submit"]');
        await page.waitForNavigation();
        console.log('✓ Logged in as supervisor');

        // Dashboard
        await page.goto('http://localhost:5175/');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '03-dashboard.png'),
            fullPage: true,
        });
        console.log('✓ Captured dashboard');

        // Tasks page
        await page.goto('http://localhost:5175/tasks');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '04-tasks-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured tasks page');

        // Projects page
        await page.goto('http://localhost:5175/projects');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '05-projects-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured projects page');

        // Milestones page
        await page.goto('http://localhost:5175/milestones');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '06-milestones-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured milestones page');

        // Timeline page
        await page.goto('http://localhost:5175/timeline');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '07-timeline-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured timeline page');

        // Performance page
        await page.goto('http://localhost:5175/performance');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '08-performance-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured performance page');

        // Schedule page
        await page.goto('http://localhost:5175/schedule');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '09-schedule-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured schedule page');

        // Team page
        await page.goto('http://localhost:5175/team');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '10-team-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured team page');

        // Updates page
        await page.goto('http://localhost:5175/updates');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '11-updates-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured updates page');

        // Board page
        await page.goto('http://localhost:5175/board');
        await page.waitForLoadState('networkidle');
        await page.screenshot({
            path: path.join(imagesDir, '12-board-page.png'),
            fullPage: true,
        });
        console.log('✓ Captured board page');

        console.log('All screenshots captured successfully');
    } catch (error) {
        console.error('Error capturing screenshots:', error.message);
    } finally {
        await browser.close();
    }
})();
