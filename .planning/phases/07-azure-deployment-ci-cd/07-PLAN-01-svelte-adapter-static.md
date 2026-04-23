---
plan: "07-01"
wave: 1
phase: 7
title: "SvelteKit adapter-static Migration"
depends_on: []
files_modified:
  - frontend/svelte.config.js
  - frontend/package.json
  - frontend/src/routes/+layout.ts
autonomous: true
requirements_addressed:
  - REQ-05c
---

# Plan 07-01: SvelteKit adapter-static Migration

## Objective

Switch the SvelteKit frontend from `adapter-node` (SSR/Node.js runtime) to `adapter-static`
(pure static build with SPA fallback). This produces `frontend/build/` as HTML/CSS/JS that
nginx can serve directly — no Node.js process needed at runtime in the monolith container.

## Context

- Current: `svelte.config.js` imports `@sveltejs/adapter-node`, outputs a Node.js server bundle
- Required: `@sveltejs/adapter-static` with `fallback: '200.html'` for SPA client-side routing
- No `+page.ts` / `+layout.ts` files exist — all routes are plain `.svelte` components
- All API calls use relative paths (`/api/*`) — no env vars needed for build
- WebSocket URL is derived from `window.location.host` — works unchanged with nginx monolith

## Tasks

### Task 1: Install @sveltejs/adapter-static

<read_first>
- `frontend/package.json` — current dependencies (adapter-node present, adapter-static absent)
</read_first>

<action>
Add `@sveltejs/adapter-static` to devDependencies in `frontend/package.json`.
Replace the `@sveltejs/adapter-node` entry with `@sveltejs/adapter-static`:

Change:
  `"@sveltejs/adapter-node": "^5.0.1"`

To:
  `"@sveltejs/adapter-static": "^3.0.1"`

Then run: `bun install` in the `frontend/` directory to update `bun.lock`.
</action>

<acceptance_criteria>
- `frontend/package.json` contains `"@sveltejs/adapter-static"` and does NOT contain `"@sveltejs/adapter-node"`
- `frontend/node_modules/@sveltejs/adapter-static/` directory exists after install
- `bun.lock` is updated (mtime changed or `@sveltejs/adapter-static` appears in lockfile)
</acceptance_criteria>

---

### Task 2: Update svelte.config.js to use adapter-static

<read_first>
- `frontend/svelte.config.js` — current adapter-node config
</read_first>

<action>
Replace the contents of `frontend/svelte.config.js` with:

```js
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter({
			fallback: '200.html'
		}),
		alias: {
			$lib: './src/lib'
		}
	}
};

export default config;
```

`fallback: '200.html'` enables SPA mode — nginx serves `200.html` for all unmatched paths,
and SvelteKit's client-side router handles navigation.
</action>

<acceptance_criteria>
- `frontend/svelte.config.js` contains `from '@sveltejs/adapter-static'`
- `frontend/svelte.config.js` contains `fallback: '200.html'`
- `frontend/svelte.config.js` does NOT contain `adapter-node`
</acceptance_criteria>

---

### Task 3: Create +layout.ts to disable SSR globally

<read_first>
- `frontend/src/routes/+layout.svelte` — existing layout (to understand current structure)
</read_first>

<action>
Create `frontend/src/routes/+layout.ts` with the following content:

```ts
export const prerender = true;
export const ssr = false;
```

This disables server-side rendering for all routes globally, which is required for
`adapter-static` when using SPA mode. Without `ssr = false`, SvelteKit will attempt
to prerender every page at build time, which may fail for routes that depend on
runtime data (API calls, auth state, etc.).
</action>

<acceptance_criteria>
- `frontend/src/routes/+layout.ts` exists
- File contains `export const prerender = true`
- File contains `export const ssr = false`
</acceptance_criteria>

---

### Task 4: Verify the static build succeeds

<read_first>
- `frontend/svelte.config.js` — updated config
- `frontend/src/routes/+layout.ts` — new SSR disable file
</read_first>

<action>
Run the SvelteKit build from the `frontend/` directory:

```bash
bun run build
```

Verify the output directory `frontend/build/` is created with:
- `frontend/build/200.html` — SPA fallback file (required for nginx `try_files`)
- `frontend/build/_app/` — bundled JS/CSS assets
- `frontend/build/index.html` or `frontend/build/200.html` as entry point
</action>

<acceptance_criteria>
- `bun run build` exits with code 0 (no build errors)
- `frontend/build/200.html` exists
- `frontend/build/_app/` directory exists and contains `.js` files
- No `frontend/build/index.js` server entry point exists (confirms static build, not node adapter)
</acceptance_criteria>

---

## Verification Criteria

- [ ] `frontend/svelte.config.js` imports `@sveltejs/adapter-static` with `fallback: '200.html'`
- [ ] `frontend/src/routes/+layout.ts` exists with `prerender = true` and `ssr = false`
- [ ] `bun run build` succeeds in `frontend/` and produces `frontend/build/200.html`
- [ ] `frontend/package.json` has `@sveltejs/adapter-static`, not `@sveltejs/adapter-node`

## must_haves

- SvelteKit static build produces `200.html` (SPA fallback for nginx)
- No Node.js runtime process required to serve the frontend
- All existing routes continue to work via client-side routing
