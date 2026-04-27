# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: status_transition.spec.ts >> Phase 18: Status Transition Graph >> Transition rules tab shows matrix with draft and save states
- Location: tests/status_transition.spec.ts:29:2

# Error details

```
TimeoutError: page.waitForURL: Timeout 15000ms exceeded.
=========================== logs ===========================
waiting for navigation until "load"
============================================================
```

# Page snapshot

```yaml
- generic [ref=e4]:
  - generic [ref=e5]:
    - generic [ref=e6]: T
    - heading "Welcome back" [level=1] [ref=e7]
    - paragraph [ref=e8]: Sign in to TeamFlow
  - generic [ref=e9]:
    - generic [ref=e10]:
      - generic [ref=e11]: Username
      - textbox "Username" [ref=e12]:
        - /placeholder: your_username
        - text: testuser
    - generic [ref=e13]:
      - generic [ref=e14]: Password
      - generic [ref=e15]:
        - textbox "Password" [ref=e16]:
          - /placeholder: ••••••••
          - text: testpass
        - button [ref=e17] [cursor=pointer]:
          - img [ref=e18]
    - button "Sign In" [ref=e19] [cursor=pointer]
  - paragraph [ref=e20]:
    - text: Don't have an account?
    - link "Register" [ref=e21] [cursor=pointer]:
      - /url: /register
```

# Test source

```ts
  1  | import { type Page } from '@playwright/test';
  2  | 
  3  | /**
  4  |  * Login helper for Playwright tests.
  5  |  * Set credentials via env vars:
  6  |  *   TEST_USERNAME=your_username TEST_PASSWORD=your_password bun run test:mobile
  7  |  * Defaults to the values below if env vars are not set.
  8  |  */
  9  | export async function loginAs(page: Page, username?: string, password?: string) {
  10 | 	const user = username ?? process.env.TEST_USERNAME ?? 'testuser';
  11 | 	const pass = password ?? process.env.TEST_PASSWORD ?? 'testpass';
  12 | 
  13 | 	await page.goto('/login');
  14 | 	await page.locator('#username').fill(user);
  15 | 	await page.locator('#password').fill(pass);
  16 | 	await page.getByRole('button', { name: 'Sign In' }).click();
  17 | 	// Wait for client-side navigation away from /login
> 18 | 	await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 15000 });
     |             ^ TimeoutError: page.waitForURL: Timeout 15000ms exceeded.
  19 | }
  20 | 
```