---
phase: 5
slug: enhanced-ai-features
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-23
reviewed_at: 2026-04-23
---

# Phase 5 — UI Design Contract

> Visual and interaction contract for Enhanced AI Features. Extends existing AiTaskInput.svelte (new 4th tab) and /projects list (inline Summarize button + expandable panel). Generated from CONTEXT.md locked decisions D-01–D-16 + codebase scan. No user questions required.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none (manual TailwindCSS) |
| Preset | not applicable |
| Component library | none (SvelteKit — shadcn not applicable) |
| Icon library | lucide-svelte (tree-shaken per-component) |
| Font | Inter (system-ui fallback) |

**Note:** No `components.json`. Project uses global utility classes defined in `frontend/src/app.css` (`.btn-primary`, `.btn-secondary`, `.btn-danger`, `.card`, `.input`, `.label`, `.badge`). All Phase 5 UI must use these classes — no new utility patterns.

---

## Spacing Scale

Standard 8-point scale — identical to Phase 4, consistent with all existing routes:

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, badge padding, tab icon-to-label gap (`gap-1`) |
| sm | 8px | Subtask card internal field spacing, button icon gap |
| md | 16px | Card internal padding, section spacing inside modal |
| lg | 24px | Summary panel internal padding, modal section breaks |
| xl | 32px | Page-level section breaks |
| 2xl | 48px | Major layout gaps |
| 3xl | 64px | Page top padding |

Exceptions:
- Subtask card list: `space-y-3` (12px) between cards — tighter than standard md to keep the list compact inside the modal
- Expandable summary panel: `p-4` (16px) internal padding, `mt-0` when collapsed (zero height), `mt-3` top margin when expanded (relative to card)
- Breakdown tab context inputs (project / milestone / assignee dropdowns): `space-y-3` (12px) between fields, same as NLP tab field spacing

---

## Typography

Inherited from project Inter font + Tailwind defaults. Identical rules to Phase 4 — max 4 sizes, max 2 weights per component:

| Role | Size | Weight | Line Height | Tailwind Class |
|------|------|--------|-------------|----------------|
| Body / field label / form label / tab text | 14px | 400 | 1.4 | `text-sm` |
| Section heading (modal title, card title) | 16px | 600 | 1.3 | `text-base font-semibold` |
| Summary section heading | 14px | 600 | 1.4 | `text-sm font-semibold` |

**Rule:** Subtask card titles are `text-sm` (14px) inputs. Summary section headings (`Milestone Progress`, `Recent Completions`, `Overdue`, `At-Risk`) use `text-sm font-semibold text-gray-200`. Summary body paragraphs use `text-sm text-gray-400`. No display size needed in this phase. Two weights only: regular (400) and semibold (600).

---

## Color

60/30/10 split — identical to Phase 4, consistent with established dark theme:

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#030712` (`bg-gray-950`) | Page background |
| Secondary (30%) | `#111827` (`bg-gray-900`) | Modal background, project cards (`.card`), summary panel background, subtask cards |
| Accent (10%) | `#6366f1` (`primary-500`) / `#4f46e5` (`primary-600`) | Active tab border, active tab text, focus rings, "Break down" button, "Summarize" button |
| Destructive | `#dc2626` (`red-600`) | Delete subtask button hover state only |

**Accent reserved for:**
1. Active "Breakdown" tab — `border-primary-500 text-primary-400` (same as existing Form/NLP/JSON tabs)
2. "Break down" submit button — `btn-primary` class (uses `bg-primary-600`)
3. "Summarize" button on project cards — `btn-primary` class (small variant: `px-3 py-2 text-xs`)
4. "Create All" batch-create button — `btn-primary` class
5. Focus rings on all `.input` fields — `focus:ring-primary-500` (already in `.input` class)

**Subtask cards:** `bg-gray-800 border border-gray-700 rounded-lg p-3` — one shade lighter than modal background (`bg-gray-900`) to create visual separation. Matches existing `.input` field background.

**Summary panel:** `bg-gray-800/50 border border-gray-700/50 rounded-lg` — slightly muted variant to read as an "appended" region below the card, not a new independent card. Opens with a CSS `transition-all duration-200` height animation.

**Loading spinner:** `w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin` — exact pattern from existing NLP tab in `AiTaskInput.svelte`.

**Summarize button loading state:** Button switches to disabled + spinner inline (same pattern as "Parse with AI" button). Button label changes to "Summarizing..." during load. Button re-enables on completion or error.

**Progress indicator during batch-create:** Small inline text below "Create All" button: `text-xs text-gray-400` — "Creating 2 of 5..." — updates reactively. Not a separate progress bar component.

---

## Component Inventory

Phase 5 adds one new sub-component and modifies two existing files:

### New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `SubtaskCard.svelte` | `frontend/src/lib/components/tasks/SubtaskCard.svelte` | Inline editable card for a single AI-generated subtask draft. Receives subtask data as props, emits `update` and `remove` events. |

### Modified Components

| File | Change |
|------|--------|
| `frontend/src/lib/components/tasks/AiTaskInput.svelte` | Add 4th "Breakdown" tab (D-01). Tab type extended to `'form' \| 'nlp' \| 'json' \| 'breakdown'`. New props: `projectList`, `milestoneList`, `userList`. |
| `frontend/src/routes/projects/+page.svelte` | Add "Summarize" button + expandable summary panel to each project card. New per-card state: `summaryMap: Record<number, string \| null>`, `loadingMap: Record<number, boolean>`, `expandedMap: Record<number, boolean>`. |

### SubtaskCard.svelte — Field Layout

Each subtask card renders fields in this order (top to bottom):

1. **Title** — `<input class="input" />` full width
2. **Row: Priority + Estimated Hours** — `flex gap-3`: `<select class="input">` (priority, flex-1) + `<input type="number" class="input w-24">` (hours)
3. **Description** — `<textarea class="input resize-none" rows="2" />` full width
4. **Row: Milestone + Delete** — `flex items-center gap-2`: milestone `<select class="input flex-1">` + `<button class="p-1 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded transition-colors">` with `<Trash2 size={13} />`

Delete button follows existing project card edit/delete button pattern: `p-1 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded transition-colors`.

---

## Interaction Contract

### Breakdown Tab — Full Flow

1. **Tab activation:** User clicks "Breakdown" tab → `mode = 'breakdown'`. Tab renders context dropdowns (project required, milestone + assignee optional) then textarea + "Break down" button. Same `border-b border-gray-800 mb-4` tab bar container as existing tabs.

2. **Context dropdowns:** Project dropdown is required (`<select required class="input">`). If no project selected, "Break down" button is `disabled`. Milestone dropdown has a "No milestone" `<option value="">` as first item. Assignee dropdown has "Unassigned" `<option value="">` as first item. Labels use `.label` class.

3. **Description textarea:** `<textarea class="input resize-none" rows="4" placeholder="Describe the feature or work to break down into tasks..." />`. Same styling as NLP tab description field.

4. **"Break down" button:** `btn-primary w-full justify-center`. Disabled when: no project selected OR description empty OR `loading === true`. Loading state shows `animate-spin` spinner + no label text (same pattern as "Parse with AI" button in NLP tab).

5. **AI response renders:** Subtask card list appears below the button in `<div class="space-y-3 mt-4">`. Each card is a `SubtaskCard` component. Cards are editable immediately on render.

6. **"Create All" button:** Appears below the card list after subtasks are loaded. `btn-primary w-full justify-center`. Label: "Create All ({n} tasks)" where `{n}` is the current card count (updates as cards are deleted). Disabled while batch-create is in progress.

7. **Batch-create progress:** During creation, "Create All" button is replaced with inline progress text: `<p class="text-center text-xs text-gray-400 py-2">Creating {current} of {total}...</p>`.

8. **Success:** `svelte-sonner` toast — "Created {n} tasks" (success variant). Subtask card list clears. `onParsed` callback is NOT called (breakdown creates tasks directly, does not populate the parent form). Tab resets to 'breakdown' mode with cleared inputs.

9. **Error (AI failure or malformed JSON):** `svelte-sonner` toast — "AI breakdown failed — please try again" (error variant). Loading spinner stops. Inputs remain populated so user can retry without re-typing. No error state inline (toast is sufficient).

10. **Error (individual task POST fails during batch):** Toast — "Some tasks failed to create — check your project settings" (error variant). Successfully created tasks are not rolled back. Progress text updates to show final count of successes.

### Summarize Button — Full Flow

1. **Button placement:** Inside each project card in `/projects`, appended to the existing bottom action row (`mt-3 pt-3 border-t border-gray-800 flex gap-2`). Positioned after the existing "View Tasks →" and "Milestones →" links. Separator `<span class="text-gray-700">·</span>` between Milestones link and Summarize button.

2. **Button appearance (idle):** `<button class="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-primary-400 transition-colors">` with `<Sparkles size={12} />` icon + "Summarize" label. Matches visual weight of existing "View Tasks →" link — NOT a `btn-primary` full-button style. This keeps the card footer visually uncluttered.

3. **Button appearance (loading):** Icon switches from `<Sparkles>` to `animate-spin` spinner (`w-3 h-3 border border-white border-t-transparent rounded-full`). Label changes to "Summarizing...". Button is `disabled` and `cursor-not-allowed`.

4. **Click — first time (no cached summary):** Button enters loading state → `POST /api/ai/project-summary` with `{project_id}` → on success: summary stored in `summaryMap[project.id]`, `expandedMap[project.id] = true`, panel slides open.

5. **Click — subsequent (cached summary):** Toggles `expandedMap[project.id]`. No API call. Button label reads "Hide Summary" when expanded, "Show Summary" when collapsed (summary exists but hidden). "Summarize" only appears when no summary is cached.

6. **Expandable panel animation:** CSS transition on height is fragile in Svelte. Use `{#if expandedMap[p.id]}` render-gate + `transition:slide={{ duration: 200 }}` (Svelte built-in transition). Panel appears/disappears with slide animation. No third-party animation dependency.

7. **Panel layout:** `<div class="mt-3 pt-3 border-t border-gray-700/50 bg-gray-800/40 rounded-b-lg -mx-5 -mb-5 px-5 pb-4">` — inset into the card, visually attached to bottom. Four sections rendered as:
   ```
   <div class="space-y-3">
     <div>
       <p class="text-xs font-semibold text-gray-300 uppercase tracking-wide mb-1">Milestone Progress</p>
       <p class="text-sm text-gray-400">{sections.milestone_progress}</p>
     </div>
     ... repeat for Recent Completions, Overdue, At-Risk
   </div>
   ```

8. **Error (API failure):** `svelte-sonner` toast — "Couldn't summarize project — please try again" (error variant). Button resets to idle state. `summaryMap[project.id]` remains null (not set to error string).

9. **Cache scope:** In-memory component state only (`summaryMap` keyed by `project.id`). Clears on page navigation/reload. No localStorage persistence.

### Modal Impact

The task creation modal in `tasks/+page.svelte` is NOT resized or restructured for this phase. The Breakdown tab content renders inside the existing modal scroll container. If the subtask card list grows long, the modal scrolls (`overflow-y-auto` on the modal content area — confirm this is already set in the existing modal; if not, add it). Modal max-height: `max-h-[85vh]`.

---

## Copywriting Contract

### Breakdown Tab

| Element | Copy |
|---------|------|
| Tab label | "Breakdown" |
| Breakdown tab — project label | "Project" |
| Breakdown tab — milestone label | "Default Milestone" |
| Breakdown tab — assignee label | "Assign all to" |
| Breakdown tab — milestone placeholder | "No milestone" |
| Breakdown tab — assignee placeholder | "Unassigned" |
| Breakdown tab — description label | "What do you want to build?" |
| Breakdown tab — description placeholder | "Describe the feature or work to break down into tasks..." |
| "Break down" button (idle) | "Break down with AI" |
| "Break down" button (loading) | (spinner only, no text) |
| Subtask card — title placeholder | "Subtask title" |
| Subtask card — hours placeholder | "hrs" |
| Subtask card — description placeholder | "Brief description (optional)" |
| Subtask card — priority label | "Priority" |
| Subtask card — milestone label | "Milestone" |
| "Create All" button | "Create All ({n} tasks)" |
| Batch progress indicator | "Creating {current} of {total}..." |
| Batch success toast | "Created {n} tasks successfully" |
| AI breakdown error toast | "AI breakdown failed — please try again" |
| Batch partial-failure toast | "Some tasks couldn't be created — check project settings" |
| Empty state (0 subtasks after deletion) | "All subtasks removed. Break down again to start over." (shown as `text-sm text-gray-500 text-center py-4`) |

### Summarize Button / Panel

| Element | Copy |
|---------|------|
| Summarize button (no summary cached) | "Summarize" |
| Summarize button (loading) | "Summarizing..." |
| Summarize button (summary cached, expanded) | "Hide Summary" |
| Summarize button (summary cached, collapsed) | "Show Summary" |
| Summary section heading — 1 | "Milestone Progress" |
| Summary section heading — 2 | "Recent Completions" |
| Summary section heading — 3 | "Overdue" |
| Summary section heading — 4 | "At-Risk" |
| Summarize error toast | "Couldn't summarize project — please try again" |

### No new destructive actions

The only destructive interaction in this phase is "delete subtask card" — a per-card remove from an in-memory list (not a database delete). No confirmation dialog required (the user has not committed these subtasks to the database yet). The delete button uses `hover:text-red-400` as the only visual signal.

---

## Visual Hierarchy

**Breakdown tab (inside task creation modal):**
1. Tab bar (orientation) — `border-b border-gray-800 mb-4`
2. Context selectors (project / milestone / assignee) — grounding inputs
3. Description textarea — primary intent input
4. "Break down with AI" button — primary action
5. Subtask card list — review zone (scrollable if > 4 cards)
6. "Create All" button — commit action

**Project summary panel (inside /projects card):**
1. Project card header (name, color swatch) — existing, unchanged
2. Card body (description) — existing, unchanged
3. Card footer links + Summarize button — extended with new button
4. Expandable summary panel — appears below footer on demand, visually part of the card

**Accessibility notes:**
- Tab bar: "Breakdown" tab button must include `title="Break down task with AI"` for tooltip
- "Summarize" button: `aria-expanded={expandedMap[p.id] ?? false}` on the button, `aria-label` includes project name: `aria-label="Summarize {p.name}"`
- Subtask card delete buttons: `aria-label="Remove subtask"` on each `<button>`
- Spinner elements: `aria-hidden="true"` on all `animate-spin` elements; loading state announced via button label change (already visible to screen readers)
- All `.input` fields in SubtaskCard.svelte must have associated `id` + `for` label pairs

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none (not initialized) | not applicable |
| npm packages (new) | none — Phase 5 adds no new dependencies | not applicable |

**Note:** Phase 5 introduces zero new npm packages. All UI uses existing `lucide-svelte`, `svelte-sonner`, and Svelte built-in `transition:slide`. No registry vetting gate required.

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
