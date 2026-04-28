<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { timeline, tasks as taskApi } from '$lib/apis';
	import { toast } from 'svelte-sonner';
	import TimelineToolbar from '$lib/components/timeline/TimelineToolbar.svelte';
	import TimelineByProject from '$lib/components/timeline/TimelineByProject.svelte';
	import TimelineByMember from '$lib/components/timeline/TimelineByMember.svelte';
	import { buildTimelineViewModel } from '$lib/components/timeline/timeline-view-model';
	import { format } from 'date-fns';
	import { X, Save } from 'lucide-svelte';

	type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done' | 'blocked';
	type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

	let projects = $state<any[]>([]);
	let loading = $state(true);
	let error = $state('');

	// Toolbar state - viewMode from query param
	let viewMode = $derived<'project' | 'member'>($page.url.searchParams.get('view') === 'member' ? 'member' : 'project');
	let rangeType = $state<'week' | 'month' | 'custom'>('month');
	let rangeStart = $state<Date>(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
	let rangeEnd = $state<Date>(new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0));

	// Modal state
	let selectedTask = $state<any>(null);
	let focusedMilestoneId = $state<number | null>(null);
	let focusedTaskId = $state<number | null>(null);
	let editForm = $state({ title: '', status: 'todo' as TaskStatus, priority: 'medium' as TaskPriority, due_date: '', description: '' });
	let saving = $state(false);
	let viewModel = $derived(buildTimelineViewModel(projects));

	async function loadTimeline() {
		loading = true;
		error = '';
		try {
			const nextProjects = await timeline.get();
			const nextViewModel = buildTimelineViewModel(nextProjects);
			projects = nextProjects;
			if (focusedTaskId && !nextViewModel.taskToMilestone.has(focusedTaskId)) {
				focusedTaskId = null;
			}
			if (focusedMilestoneId && !nextViewModel.tasksByMilestone.has(focusedMilestoneId)) {
				focusedMilestoneId = null;
			}
			fitToData();
		} catch (e: any) {
			error = e.message || 'Failed to load timeline';
		} finally {
			loading = false;
		}
	}

	function fitToData() {
		const MS_DAY = 86_400_000;
		let earliest: Date | null = null;
		let latest: Date | null = null;
		const now = new Date();

		for (const project of projects) {
			const allTasks = [
				...project.milestones.flatMap((m: any) => m.tasks),
				...project.unassigned_tasks
			];
			for (const task of allTasks) {
				// Use due_date as the right edge; skip null due_dates (they show near today)
				const due = task.due_date ? new Date(task.due_date) : new Date(now.getTime() + 3 * MS_DAY);
				// Use created_at as the left edge but cap it at 60 days back
				const rawStart = new Date(task.created_at);
				const start = rawStart < new Date(now.getTime() - 60 * MS_DAY) ? new Date(now.getTime() - 60 * MS_DAY) : rawStart;
				if (!earliest || start < earliest) earliest = start;
				if (!latest || due > latest) latest = due;
			}
		}

		if (earliest && latest) {
			// Pad 7 days on each side, minimum 14-day span
			const paddedStart = new Date(earliest.getTime() - 7 * MS_DAY);
			const paddedEnd = new Date(latest.getTime() + 7 * MS_DAY);
			const minEnd = new Date(paddedStart.getTime() + 14 * MS_DAY);
			rangeStart = paddedStart;
			rangeEnd = paddedEnd > minEnd ? paddedEnd : minEnd;
			rangeType = 'custom';
		}
	}

	function handleViewChange(mode: 'project' | 'member') {
		const url = new URL($page.url);
		url.searchParams.set('view', mode);
		goto(url.href);
	}

	function handleRangeChange(range: { type: 'week' | 'month' | 'custom'; start: Date; end: Date }) {
		rangeType = range.type;
		rangeStart = range.start;
		rangeEnd = range.end;
	}

	function handleTaskClick(task: any) {
		focusedTaskId = task.id;
		focusedMilestoneId = task.milestone_id ?? null;
		selectedTask = task;
		editForm = {
			title: task.title,
			status: task.status,
			priority: task.priority,
			due_date: task.due_date ? task.due_date.slice(0, 10) : '',
			description: task.description || ''
		};
	}

	function handleMilestoneFocus(milestoneId: number) {
		focusedMilestoneId = milestoneId;
		focusedTaskId = null;
	}

	async function handleReschedule() {
		await loadTimeline();
	}

	async function saveEdit() {
		if (!selectedTask) return;
		saving = true;
		try {
			const payload: any = {
				title: editForm.title,
				status: editForm.status,
				priority: editForm.priority
			};
			if (editForm.due_date) payload.due_date = new Date(editForm.due_date).toISOString();
			if (editForm.description !== undefined) payload.description = editForm.description;

			await taskApi.update(selectedTask.id, payload);
			toast.success('Task updated');
			selectedTask = null;
			await loadTimeline();
		} catch (e: any) {
			toast.error(e.message || 'Failed to save');
		} finally {
			saving = false;
		}
	}

	onMount(loadTimeline);
</script>

<div class="flex flex-col" style="height: 100%; min-height: 0;">
	<!-- Page header -->
	<div class="px-4 md:px-6 py-3 md:py-4 border-b border-[#1e293b] bg-[#0a0f1e] flex items-center justify-between flex-shrink-0 flex-wrap gap-2">
		<div class="flex items-center gap-3">
			<div class="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
				<svg class="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
				</svg>
			</div>
			<div>
				<h1 class="text-base font-semibold text-white tracking-tight">Team Timeline</h1>
				<p class="text-xs text-slate-500 mt-0.5">Visual project & task progress</p>
			</div>
		</div>
	</div>

	<!-- Toolbar -->
	<TimelineToolbar
		viewMode={viewMode}
		bind:rangeType
		bind:rangeStart
		bind:rangeEnd
		onviewchange={handleViewChange}
		onrangechange={handleRangeChange}
	/>

	<!-- Content -->
	<div class="flex-1 overflow-hidden relative" style="min-height: 0;">
		{#if loading}
			<div class="flex items-center justify-center h-full">
				<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
			</div>
		{:else if error}
			<div class="flex items-center justify-center h-full">
				<p class="text-red-400 text-sm">{error}</p>
			</div>
		{:else if viewMode === 'project'}
			<TimelineByProject
				{projects}
				{viewModel}
				{rangeStart}
				{rangeEnd}
				{focusedMilestoneId}
				{focusedTaskId}
				ontaskclick={handleTaskClick}
				onfocusmilestone={handleMilestoneFocus}
				onreschedule={handleReschedule}
			/>
		{:else}
			<TimelineByMember
				{projects}
				{viewModel}
				{rangeStart}
				{rangeEnd}
				{focusedMilestoneId}
				{focusedTaskId}
				ontaskclick={handleTaskClick}
				onfocusmilestone={handleMilestoneFocus}
				onreschedule={handleReschedule}
			/>
		{/if}
	</div>
</div>

<!-- Task Edit Modal -->
{#if selectedTask}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
		onclick={(e) => { if (e.target === e.currentTarget) selectedTask = null; }}
		role="dialog"
		aria-modal="true"
		tabindex="-1"
	>
		<div class="bg-gray-900 rounded-xl w-full max-w-md border border-gray-800 shadow-2xl">
			<div class="flex items-center justify-between px-6 py-4 border-b border-gray-800">
				<h2 class="text-base font-semibold text-white">Edit Task</h2>
				<button onclick={() => (selectedTask = null)} class="text-gray-500 hover:text-gray-300 transition-colors">
					<X size={18} />
				</button>
			</div>

			<div class="px-6 py-4 space-y-4">
				<div>
					<label for="edit-title" class="block text-xs text-gray-400 mb-1">Title</label>
					<input
						id="edit-title"
						bind:value={editForm.title}
						type="text"
						class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary-500"
					/>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="edit-status" class="block text-xs text-gray-400 mb-1">Status</label>
						<select id="edit-status" bind:value={editForm.status} class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
							<option value="todo">To Do</option>
							<option value="in_progress">In Progress</option>
							<option value="review">Review</option>
							<option value="done">Done</option>
							<option value="blocked">Blocked</option>
						</select>
					</div>
					<div>
						<label for="edit-priority" class="block text-xs text-gray-400 mb-1">Priority</label>
						<select id="edit-priority" bind:value={editForm.priority} class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
							<option value="low">Low</option>
							<option value="medium">Medium</option>
							<option value="high">High</option>
							<option value="critical">Critical</option>
						</select>
					</div>
				</div>

				<div>
					<label for="edit-due-date" class="block text-xs text-gray-400 mb-1">Due Date</label>
					<input
						id="edit-due-date"
						bind:value={editForm.due_date}
						type="date"
						class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white"
					/>
				</div>

				<div>
					<label for="edit-description" class="block text-xs text-gray-400 mb-1">Description</label>
					<textarea
						id="edit-description"
						bind:value={editForm.description}
						rows={3}
						class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white resize-none focus:outline-none focus:border-primary-500"
					></textarea>
				</div>
			</div>

			<div class="px-6 py-4 border-t border-gray-800 flex justify-end gap-3">
				<button
					onclick={() => (selectedTask = null)}
					class="px-4 py-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
				>
					Cancel
				</button>
				<button
					onclick={saveEdit}
					disabled={saving}
					class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
				>
					<Save size={14} />
					{saving ? 'Saving…' : 'Save'}
				</button>
			</div>
		</div>
	</div>
{/if}
