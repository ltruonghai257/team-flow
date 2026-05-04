import { expect, test } from '@playwright/test';

const COMMAND_VIEW_FIXTURE = {
    metrics: {
        active_milestones: 1,
        risky_milestones: 1,
        proposed_decisions: 1,
        blocked_tasks: 1
    },
    lanes: {
        planned: [
            {
                id: 1,
                title: 'Phase 1: Foundation',
                description: 'Initial setup and base architecture',
                status: 'planned',
                planning_state: 'planned',
                risk: null,
                start_date: '2026-05-01T00:00:00.000Z',
                due_date: '2026-05-15T00:00:00.000Z',
                completed_at: null,
                project_id: 1,
                project_name: 'Core System',
                project_color: '#6366f1',
                progress: { total: 5, done: 0, blocked: 0, completion_percent: 0 },
                decision_summary: { proposed: 0, approved: 0, rejected: 0, superseded: 0 },
                tasks: [],
                decisions: []
            }
        ],
        committed: [
            {
                id: 2,
                title: 'Phase 2: Security',
                description: 'OAuth and RBAC implementation',
                status: 'in_progress',
                planning_state: 'committed',
                risk: 'watch',
                start_date: '2026-05-10T00:00:00.000Z',
                due_date: '2026-05-25T00:00:00.000Z',
                completed_at: null,
                project_id: 1,
                project_name: 'Core System',
                project_color: '#6366f1',
                progress: { total: 10, done: 2, blocked: 0, completion_percent: 20 },
                decision_summary: { proposed: 1, approved: 0, rejected: 0, superseded: 0 },
                tasks: [
                    { id: 101, title: 'Define scope', status: 'Done', due_date: '2026-05-12' },
                    { id: 102, title: 'Mock implementation', status: 'In Progress', due_date: '2026-05-15' }
                ],
                decisions: [
                    {
                        id: 201,
                        milestone_id: 2,
                        task_id: null,
                        title: 'Auth provider choice',
                        status: 'proposed',
                        note: 'Considering Auth0 or custom JWT',
                        created_at: '2026-05-11T10:00:00Z',
                        updated_at: '2026-05-11T10:00:00Z'
                    }
                ]
            }
        ],
        active: [
            {
                id: 3,
                title: 'Phase 3: Integration',
                description: 'External API connectors',
                status: 'in_progress',
                planning_state: 'active',
                risk: 'at_risk',
                start_date: '2026-04-15T00:00:00.000Z',
                due_date: '2026-05-05T00:00:00.000Z',
                completed_at: null,
                project_id: 1,
                project_name: 'Core System',
                project_color: '#6366f1',
                progress: { total: 8, done: 4, blocked: 1, completion_percent: 50 },
                decision_summary: { proposed: 0, approved: 1, rejected: 0, superseded: 0 },
                tasks: [
                    { id: 103, title: 'Slack integration', status: 'Blocked', due_date: '2026-04-20' },
                    { id: 104, title: 'Email service', status: 'In Progress', due_date: '2026-04-25' }
                ],
                decisions: [
                    {
                        id: 202,
                        milestone_id: 3,
                        task_id: 103,
                        title: 'Slack API Tier',
                        status: 'approved',
                        note: 'Going with Pro tier for better rate limits',
                        created_at: '2026-04-18T10:00:00Z',
                        updated_at: '2026-04-18T10:00:00Z'
                    }
                ]
            }
        ],
        completed: [
            {
                id: 4,
                title: 'Phase 0: Planning',
                description: 'Project discovery and scoping',
                status: 'completed',
                planning_state: 'completed',
                risk: null,
                start_date: '2026-03-01T00:00:00.000Z',
                due_date: '2026-03-15T00:00:00.000Z',
                completed_at: '2026-03-14T10:00:00.000Z',
                project_id: 1,
                project_name: 'Core System',
                project_color: '#6366f1',
                progress: { total: 3, done: 3, blocked: 0, completion_percent: 100 },
                decision_summary: { proposed: 0, approved: 2, rejected: 0, superseded: 0 },
                tasks: [],
                decisions: []
            }
        ]
    }
};

const PROJECTS_FIXTURE = [
    { id: 1, name: 'Core System', color: '#6366f1' }
];

test.describe('Milestones Command View', () => {
	test.beforeEach(async ({ page }) => {
		await page.route('**/api/auth/me', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({
					id: 30,
					email: 'ada@example.com',
					username: 'ada',
					full_name: 'Ada Lovelace',
					role: 'member',
					avatar_url: null,
					is_active: true,
					created_at: '2026-01-01T00:00:00.000Z'
				})
			});
		});
		await page.route('**/api/notifications/unread', async (route) => {
			await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
		});
		await page.route('**/api/milestones/command-view/', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(COMMAND_VIEW_FIXTURE)
			});
		});
		await page.route('**/api/projects/', async (route) => {
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(PROJECTS_FIXTURE)
			});
		});
	});

	test('renders summary metrics', async ({ page }) => {
		await page.goto('/milestones');
		await expect(page.getByText('1', { exact: true }).first()).toBeVisible(); // Active
		await expect(page.getByText('Active', { exact: true }).first()).toBeVisible();
		await expect(page.getByText('Risky', { exact: true })).toBeVisible();
		await expect(page.getByText('Proposed Decisions', { exact: true })).toBeVisible();
		await expect(page.getByText('Blocked Tasks', { exact: true })).toBeVisible();
	});

	test('renders all four lanes', async ({ page }) => {
		await page.goto('/milestones');
		await expect(page.getByRole('heading', { name: /^Planned$/ }).first()).toBeVisible();
		await expect(page.getByRole('heading', { name: /^Committed$/ }).first()).toBeVisible();
		await expect(page.getByRole('heading', { name: /^Active$/ }).first()).toBeVisible();
		await expect(page.getByRole('heading', { name: /^Completed$/ }).first()).toBeVisible();
	});

	test('active milestones are expanded by default', async ({ page }) => {
		await page.goto('/milestones');
		// Phase 3 is active and risky, should be expanded
		const card = page.locator('#milestone-3');
		await expect(card.getByText('Phase 3: Integration')).toBeVisible();
		await expect(card.getByText('Linked Tasks')).toBeVisible();
		await expect(card.getByText('Slack integration')).toBeVisible();
		await expect(card.getByText('Email service')).toBeVisible();
        await expect(card.getByText('Slack API Tier')).toBeVisible();
	});

    test('risky milestones (watch) are NOT expanded by default unless active', async ({ page }) => {
		await page.goto('/milestones');
		// Phase 2 is committed + watch. According to logic:
        // let expanded = initiallyExpanded || milestone.planning_state === 'active' || (milestone.risk && milestone.risk !== 'watch');
        // So watch should NOT be expanded by default.
		const card = page.locator('#milestone-2');
		await expect(card.getByText('Phase 2: Security')).toBeVisible();
		await expect(card.getByText('Define scope')).not.toBeVisible();
	});

    test('can toggle expansion', async ({ page }) => {
		await page.goto('/milestones');
		const card = page.locator('#milestone-1');
		await card.getByText('Phase 1: Foundation').click();
		await expect(card.getByText('Linked Tasks')).toBeVisible();
        await expect(card.getByText('No tasks linked to this milestone.')).toBeVisible();
        await card.getByText('Phase 1: Foundation').click();
        await expect(card.getByText('Linked Tasks')).not.toBeVisible();
	});

    test('renders decision summary on collapsed cards', async ({ page }) => {
		await page.goto('/milestones');
		const phase2 = page.locator('#milestone-2');
		await expect(phase2.getByText('1 Proposed', { exact: true })).toBeVisible();
		const phase3 = page.locator('#milestone-3');
		await expect(phase3.getByText('1 Approved', { exact: true })).toBeVisible();
	});

    test('task links point to task view', async ({ page }) => {
		await page.goto('/milestones');
		// Phase 3 is expanded
		const card = page.locator('#milestone-3');
		const taskLink = card.getByRole('link', { name: 'Slack integration' });
		await expect(taskLink).toHaveAttribute('href', '/tasks?task_id=103');
	});

    test('decision CRUD interaction', async ({ page }) => {
        // Mock decision creation
        await page.route('**/api/milestones/2/decisions', async (route) => {
            if (route.request().method() === 'POST') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        id: 203,
                        milestone_id: 2,
                        task_id: null,
                        title: 'New Decision',
                        status: 'proposed',
                        note: 'New note',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString()
                    })
                });
            }
        });

		await page.goto('/milestones');
		// Expand Phase 2
		await page.locator('#milestone-2').getByText('Phase 2: Security').click();
        
        const card = page.locator('#milestone-2');
        // Add decision
        await card.getByRole('button', { name: 'Add Decision' }).click();
        await card.getByPlaceholder('Decision title *').fill('New Decision');
        await card.getByPlaceholder('Notes (optional)').fill('New note');
        
        // Mock the refresh call to show the new decision
        await page.route('**/api/milestones/command-view/', async (route) => {
            const updated = JSON.parse(JSON.stringify(COMMAND_VIEW_FIXTURE));
            updated.lanes.committed[0].decisions.push({
                id: 203,
                milestone_id: 2,
                task_id: null,
                title: 'New Decision',
                status: 'proposed',
                note: 'New note',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            });
			await route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify(updated)
			});
		});

        await card.locator('button:has(svg.lucide-check)').click();
        await expect(page.getByText('Decision created')).toBeVisible();
        await expect(card.getByText('New Decision')).toBeVisible();
	});

    test('mobile lane model (stacked)', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
		await page.goto('/milestones');
        
        // In mobile, they are stacked. Check that we see all lane titles.
		await expect(page.getByRole('heading', { name: /^Planned$/ }).first()).toBeVisible();
		await expect(page.getByRole('heading', { name: /^Committed$/ }).first()).toBeVisible();
		await expect(page.getByRole('heading', { name: /^Active$/ }).first()).toBeVisible();
		await expect(page.getByRole('heading', { name: /^Completed$/ }).first()).toBeVisible();
        
        // Verify we can still see metrics
		await expect(page.getByText('Active', { exact: true }).first()).toBeVisible();
	});
});
