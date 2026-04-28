<script lang="ts">
	import { onMount } from 'svelte';
	import { tasks as taskApi } from '$lib/apis';
	import type { TimelineProject, TimelineTask } from '$lib/apis/timeline';
	import type { TimelineViewModel } from './timeline-view-model';
	import { toast } from 'svelte-sonner';
	import { format } from 'date-fns';

	interface Props {
		projects?: TimelineProject[];
		viewModel?: TimelineViewModel;
		viewMode?: 'project' | 'member';
		rangeStart?: Date;
		rangeEnd?: Date;
		focusedMilestoneId?: number | null;
		focusedTaskId?: number | null;
		ontaskclick?: (task: TimelineTask) => void;
		onfocusmilestone?: (milestoneId: number) => void;
		onreschedule?: (data: { taskId: number; newDueDate: Date }) => void;
	}

	let {
		projects = [],
		viewModel,
		viewMode = 'project',
		rangeStart = new Date(),
		rangeEnd = new Date(),
		focusedMilestoneId = null,
		focusedTaskId = null,
		ontaskclick,
		onfocusmilestone,
		onreschedule
	}: Props = $props();

	let ganttEl: HTMLElement = $state(null as unknown as HTMLElement);
	let ganttInstance: any = $state(null);

	const MS_DAY = 86_400_000;
	const FALLBACK_VIEW_MODEL = {
		projects: [],
		milestones: [],
		tasksByMilestone: new Map<number, TimelineTask[]>(),
		taskToMilestone: new Map<number, number>()
	};

	function escapeHtml(value: string) {
		return value.replace(/[&<>"']/g, (char) => {
			if (char === '&') return '&amp;';
			if (char === '<') return '&lt;';
			if (char === '>') return '&gt;';
			if (char === '"') return '&quot;';
			return '&#39;';
		});
	}

	function riskLabel(level: 'low' | 'medium' | 'high') {
		if (level === 'high') return 'At risk';
		if (level === 'medium') return 'Watch';
		return 'On track';
	}

	function buildMilestoneHeader(milestone: any, isFocused: boolean) {
		const counts = milestone.progress.counts;
		const span = `${format(new Date(milestone.startDate ?? milestone.dueDate), 'MMM d')} - ${format(new Date(milestone.dueDate), 'MMM d')}`;
		const badges = [
			`<span class="milestone-chip milestone-chip-risk-${milestone.signals.risk}">${riskLabel(milestone.signals.risk)}</span>`,
			milestone.signals.decision ? '<span class="milestone-chip milestone-chip-decision">Decision</span>' : '',
			milestone.signals.planning ? '<span class="milestone-chip">Planning window</span>' : ''
		].filter(Boolean).join('');
		const focusClass = isFocused ? 'milestone-header-focused' : '';
		return `
			<button type="button" class="milestone-header ${focusClass}" data-milestone-focus="${milestone.id}">
				<div class="milestone-title-row">
					<span class="milestone-title">${escapeHtml(milestone.title)}</span>
					<span class="milestone-status milestone-status-${milestone.status}">${escapeHtml(milestone.status.replace('_', ' '))}</span>
					<span class="milestone-progress">${milestone.progress.percent}%</span>
				</div>
				<div class="milestone-meta-row">
					<span class="milestone-span">${span}</span>
					<span class="milestone-count">${counts.done}/${milestone.progress.total} done</span>
					<span class="milestone-count">${counts.blocked} blocked</span>
					<span class="milestone-count">${counts.in_progress} active</span>
					${badges}
				</div>
			</button>
		`;
	}

	function buildTask(task: TimelineTask, rowId: string, color: string, html?: string) {
		const now = new Date();
		const isUnscheduled = !task.due_date;
		const dueDate = task.due_date ? new Date(task.due_date) : new Date(now.getTime() + 3 * MS_DAY);
		const rawFrom = task.due_date ? new Date(task.created_at) : now;
		const minFrom = new Date(dueDate.getTime() - 2 * MS_DAY);
		const fromDate = rawFrom < minFrom ? rawFrom : minFrom;
		const isOverdue = !isUnscheduled && dueDate < now && task.status !== 'done';
		const isDone = task.status === 'done';
		const classes = [
			'gantt-task-bar',
			isUnscheduled ? 'task-unscheduled' : '',
			isOverdue ? 'task-overdue' : '',
			isDone ? 'task-done' : '',
			focusedTaskId === task.id ? 'task-focused' : ''
		].filter(Boolean);

		return {
			id: task.id,
			resourceId: rowId,
			label: task.title,
			html,
			from: fromDate.getTime(),
			to: dueDate.getTime(),
			classes,
			draggable: true,
			resizable: false,
			_taskData: task,
			_color: color
		};
	}

	function buildGanttData(projs: TimelineProject[], mode: 'project' | 'member') {
		const rows: any[] = [];
		const ganttTasks: any[] = [];
		const model = viewModel ?? FALLBACK_VIEW_MODEL;

		if (mode === 'project') {
			for (const project of projs) {
				const projectRow: any = {
					id: `p-${project.id}`,
					label: project.name,
					enableDragging: false,
					classes: 'project-row',
					children: []
				};

				for (const milestone of model.milestones.filter((item) => item.projectId === project.id)) {
					const milestoneRowId = `m-${milestone.id}`;
					const milestoneRow: any = {
						id: milestoneRowId,
						label: milestone.title,
						headerHtml: buildMilestoneHeader(milestone, focusedMilestoneId === milestone.id),
						enableDragging: false,
						classes: ['milestone-row', focusedMilestoneId === milestone.id ? 'milestone-row-focused' : ''],
						expanded: milestone.expandedByDefault || focusedMilestoneId === milestone.id,
						children: []
					};

					for (const task of milestone.tasks) {
						const taskRowId = `mt-${task.id}`;
						milestoneRow.children.push({
							id: taskRowId,
							label: task.title,
							enableDragging: true,
							classes: 'task-row'
						});
						ganttTasks.push(buildTask(task, taskRowId, project.color));
					}

					projectRow.children.push(milestoneRow);
				}

				if (project.unassigned_tasks.length > 0) {
					const bucketRow: any = {
						id: `nm-${project.id}`,
						label: 'No Milestone',
						enableDragging: false,
						classes: 'no-milestone-row',
						children: []
					};
					for (const task of project.unassigned_tasks) {
						const taskRowId = `nm-task-${task.id}`;
						bucketRow.children.push({ id: taskRowId, label: task.title, enableDragging: true });
						ganttTasks.push(buildTask(task, taskRowId, project.color));
					}
					projectRow.children.push(bucketRow);
				}

				rows.push(projectRow);
			}
		} else {
			const memberMap = new Map<string, { label: string; tasks: Array<{ task: TimelineTask; color: string }> }>();
			const unassignedTasks: Array<{ task: TimelineTask; color: string }> = [];
			const milestoneMap = new Map(model.milestones.map((item) => [item.id, item]));

			for (const project of projs) {
				const allTasks = [...project.milestones.flatMap((m) => m.tasks), ...project.unassigned_tasks];
				for (const task of allTasks) {
					if (task.assignee) {
						const key = String(task.assignee.id);
						if (!memberMap.has(key)) {
							memberMap.set(key, { label: task.assignee.full_name, tasks: [] });
						}
						memberMap.get(key)!.tasks.push({ task, color: project.color });
					} else {
						unassignedTasks.push({ task, color: project.color });
					}
				}
			}

			const sorted = Array.from(memberMap.entries()).sort((a, b) => a[1].label.localeCompare(b[1].label));
			for (const [memberId, { label, tasks: memberTasks }] of sorted) {
				const rowId = `u-${memberId}`;
				rows.push({ id: rowId, label, enableDragging: false, classes: 'member-row' });
				for (const { task, color } of memberTasks) {
					const milestoneId = task.milestone_id;
					const milestone = milestoneId ? milestoneMap.get(milestoneId) : null;
					const context = milestone ? `<span class="task-context-badge">${escapeHtml(milestone.title)}</span>` : '<span class="task-context-badge">No milestone</span>';
					const html = `<div class="task-label">${escapeHtml(task.title)} ${context}</div>`;
					ganttTasks.push(buildTask(task, rowId, color, html));
				}
			}

			if (unassignedTasks.length > 0) {
				rows.push({ id: 'u-unassigned', label: 'Unassigned', enableDragging: false, classes: 'member-row' });
				for (const { task, color } of unassignedTasks) {
					ganttTasks.push(buildTask(task, 'u-unassigned', color, `<div class="task-label">${escapeHtml(task.title)} <span class="task-context-badge">No milestone</span></div>`));
				}
			}
		}

		return { rows, tasks: ganttTasks };
	}

	async function handleTaskChange(event: any) {
		const { task } = event;
		const newDueDate = new Date(task.model.to);
		try {
			await taskApi.update(task.model.id as number, { due_date: newDueDate.toISOString() });
			toast.success(`Rescheduled to ${format(newDueDate, 'MMM d')}`);
			onreschedule?.({ taskId: task.model.id as number, newDueDate });
		} catch (err: any) {
			toast.error(`Failed to reschedule: ${err.message}`);
		}
	}

	function handleTaskSelect(event: any) {
		const originalTask = event.model._taskData;
		if (originalTask) {
			ontaskclick?.(originalTask);
		}
	}

	function handleTableClick(event: MouseEvent) {
		const target = event.target as HTMLElement;
		const clickable = target.closest('[data-milestone-focus]') as HTMLElement | null;
		if (!clickable) return;
		event.preventDefault();
		const raw = clickable.getAttribute('data-milestone-focus');
		if (!raw) return;
		onfocusmilestone?.(Number(raw));
	}

	let ganttData = $derived(buildGanttData(projects, viewMode));
	let ganttFrom = $derived(rangeStart.getTime() - 2 * MS_DAY);
	let ganttTo = $derived(rangeEnd.getTime() + 2 * MS_DAY);
	let columnUnit = $derived((rangeEnd.getTime() - rangeStart.getTime()) > 30 * MS_DAY ? 'week' : 'day');
	let focusedMilestone = $derived((viewModel?.milestones ?? []).find((m) => m.id === focusedMilestoneId) ?? null);

	onMount(() => {
		if (!ganttEl) return;
		let disposed = false;
		ganttEl.addEventListener('click', handleTableClick);

		const init = async () => {
			const { SvelteGantt, SvelteGanttTable } = await import('svelte-gantt');
			if (disposed) return;
			ganttInstance = new SvelteGantt({
				target: ganttEl,
				props: {
					rows: ganttData.rows,
					tasks: ganttData.tasks,
					from: ganttFrom,
					to: ganttTo,
					fitWidth: true,
					minWidth: 900,
					headers: [
						{ unit: 'month', format: 'MMMM yyyy', sticky: true },
						{ unit: columnUnit, format: columnUnit === 'week' ? 'w' : 'd' }
					],
					columnUnit,
					columnOffset: 1,
					rowHeight: 52,
					rowPadding: 6,
					modules: [SvelteGanttTable],
					tableHeaders: [{ title: 'Timeline', property: 'label', width: 340 }],
					tableWidth: 340
				}
			});

			ganttInstance.$on('change', (e: any) => {
				handleTaskChange(e.detail);
			});
		};

		init();
		return () => {
			disposed = true;
			ganttEl.removeEventListener('click', handleTableClick);
		};
	});

	$effect(() => {
		if (!ganttInstance) return;
		const data = ganttData;
		const from = ganttFrom;
		const to = ganttTo;
		const unit = columnUnit;
		ganttInstance.$set({
			rows: data.rows,
			tasks: data.tasks,
			from,
			to,
			columnUnit: unit,
			headers: [
				{ unit: 'month', format: 'MMMM yyyy', sticky: true },
				{ unit, format: unit === 'week' ? 'w' : 'd' }
			]
		});
	});
</script>

<style>
	.focus-banner {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 12px;
		border-bottom: 1px solid #1f2a44;
		background: #101a33;
		color: #c7d2fe;
		font-size: 12px;
	}

	.gantt-wrapper {
		position: relative;
		width: 100%;
		height: 100%;
		overflow-x: auto;
		overflow-y: auto;
		background: #080d1a;
	}

	.gantt-wrapper :global(*) {
		border-color: transparent !important;
		outline-color: transparent !important;
	}

	.gantt-wrapper :global(.sg-gantt) {
		background: #080d1a;
		color: #94a3b8;
		font-size: 12px;
		height: 100% !important;
	}

	.gantt-wrapper :global(.sg-header) {
		background: #080d1a !important;
		border-bottom: 1px solid #151f35 !important;
		color: #475569;
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	.gantt-wrapper :global(.sg-table-body-cell) {
		background: #0b1120 !important;
		border-right: 1px solid #151f35 !important;
		border-bottom: 1px solid #111827 !important;
		color: #94a3b8;
		font-size: 12px;
		padding: 6px 10px;
	}

	.gantt-wrapper :global(.sg-table-header-cell) {
		background: #080d1a !important;
		border-right: 1px solid #151f35 !important;
		border-bottom: 1px solid #151f35 !important;
		color: #334155;
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		padding-left: 12px;
	}

	.gantt-wrapper :global(.milestone-header) {
		width: 100%;
		background: rgba(15, 23, 42, 0.9);
		border: 1px solid #24314e;
		border-radius: 8px;
		padding: 8px;
		text-align: left;
		cursor: pointer;
	}

	.gantt-wrapper :global(.milestone-header-focused) {
		border-color: #4f46e5;
		box-shadow: 0 0 0 1px #4f46e5aa;
	}

	.gantt-wrapper :global(.milestone-title-row) {
		display: flex;
		align-items: center;
		gap: 6px;
		margin-bottom: 4px;
	}

	.gantt-wrapper :global(.milestone-title) {
		font-weight: 600;
		color: #e2e8f0;
	}

	.gantt-wrapper :global(.milestone-status) {
		font-size: 10px;
		padding: 2px 6px;
		border-radius: 999px;
		text-transform: capitalize;
		background: #1e293b;
		color: #cbd5e1;
	}

	.gantt-wrapper :global(.milestone-progress) {
		margin-left: auto;
		font-size: 11px;
		font-weight: 600;
		color: #c7d2fe;
	}

	.gantt-wrapper :global(.milestone-meta-row) {
		display: flex;
		align-items: center;
		gap: 6px;
		flex-wrap: wrap;
		font-size: 11px;
		color: #94a3b8;
	}

	.gantt-wrapper :global(.milestone-chip),
	.gantt-wrapper :global(.milestone-count),
	.gantt-wrapper :global(.milestone-span) {
		padding: 1px 6px;
		border-radius: 999px;
		background: #1e293b;
	}

	.gantt-wrapper :global(.milestone-chip-risk-high) {
		background: rgba(239, 68, 68, 0.2);
		color: #fca5a5;
	}

	.gantt-wrapper :global(.milestone-chip-risk-medium) {
		background: rgba(245, 158, 11, 0.2);
		color: #fde68a;
	}

	.gantt-wrapper :global(.milestone-chip-risk-low) {
		background: rgba(34, 197, 94, 0.2);
		color: #bbf7d0;
	}

	.gantt-wrapper :global(.milestone-chip-decision) {
		background: rgba(79, 70, 229, 0.2);
		color: #c7d2fe;
	}

	.gantt-wrapper :global(.task-context-badge) {
		font-size: 10px;
		padding: 1px 6px;
		border-radius: 999px;
		background: rgba(15, 23, 42, 0.7);
		border: 1px solid rgba(148, 163, 184, 0.25);
		margin-left: 6px;
	}

	.gantt-wrapper :global(.task-label) {
		display: inline-flex;
		align-items: center;
	}

	.gantt-wrapper :global(.sg-row) {
		border-bottom: 1px solid #0f1a2e !important;
	}

	.gantt-wrapper :global(.sg-column) {
		border-right: 1px solid #0f1a2e !important;
	}

	.gantt-wrapper :global(.sg-task) {
		border-radius: 6px !important;
		border: none !important;
		cursor: pointer;
		transition: filter 0.12s, transform 0.12s !important;
	}

	.gantt-wrapper :global(.sg-task:hover) {
		filter: brightness(1.2) !important;
		transform: translateY(-1px) !important;
	}

	.gantt-wrapper :global(.sg-task-content) {
		padding-left: 10px !important;
		font-size: 11px !important;
		font-weight: 500 !important;
		color: rgba(255, 255, 255, 0.95) !important;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.gantt-wrapper :global(.sg-task-background) {
		border-radius: 6px !important;
		background: rgba(0, 0, 0, 0.18) !important;
	}

	.gantt-wrapper :global(.task-unscheduled) {
		background: rgba(99, 102, 241, 0.18) !important;
		border: 1px dashed rgba(99, 102, 241, 0.45) !important;
		opacity: 0.75;
	}

	.gantt-wrapper :global(.task-overdue) {
		box-shadow: 0 0 0 1.5px #f87171, 0 0 10px rgba(248, 113, 113, 0.25) !important;
	}

	.gantt-wrapper :global(.task-done) {
		opacity: 0.35 !important;
		filter: grayscale(0.4);
	}

	.gantt-wrapper :global(.task-focused) {
		box-shadow: 0 0 0 2px #a5b4fc, 0 2px 10px rgba(79, 70, 229, 0.4) !important;
	}

	.gantt-wrapper::-webkit-scrollbar {
		width: 5px;
		height: 5px;
	}

	.gantt-wrapper::-webkit-scrollbar-track {
		background: #080d1a;
	}

	.gantt-wrapper::-webkit-scrollbar-thumb {
		background: #1e293b;
		border-radius: 99px;
	}
</style>

<div class="flex-1 relative" style="min-height: 0; height: 100%;">
	{#if viewMode === 'member' && focusedMilestone}
		<div class="focus-banner">
			Focused milestone: <strong>{focusedMilestone.title}</strong>
		</div>
	{/if}
	{#if ganttData.rows.length === 0}
		<div class="flex flex-col items-center justify-center h-full text-gray-500 py-20">
			<p class="text-sm">No timeline data yet</p>
			<p class="text-xs mt-1">Add milestones and tasks to see planning timelines here.</p>
		</div>
	{:else}
		<div class="gantt-wrapper" style="height: max({ganttData.rows.length * 56 + 90}px, 420px);">
			<div bind:this={ganttEl} style="min-width: 900px; height: 100%;"></div>
		</div>
	{/if}
</div>
