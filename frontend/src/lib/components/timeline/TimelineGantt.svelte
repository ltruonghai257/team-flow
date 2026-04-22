<script lang="ts">
	import { onMount } from 'svelte';
	import { tasks as taskApi } from '$lib/api';
	import { toast } from 'svelte-sonner';
	import { format } from 'date-fns';

	interface Props {
		projects?: any[];
		viewMode?: 'project' | 'member';
		rangeStart?: Date;
		rangeEnd?: Date;
		ontaskclick?: (task: any) => void;
		onreschedule?: (data: { taskId: number; newDueDate: Date }) => void;
	}

	let {
		projects = [],
		viewMode = 'project',
		rangeStart = new Date(),
		rangeEnd = new Date(),
		ontaskclick,
		onreschedule
	}: Props = $props();

	let ganttEl: HTMLElement = $state(null as unknown as HTMLElement);
	let ganttInstance: any = $state(null);

	// Build gantt rows + tasks from projects data
	function buildGanttData(projs: any[], mode: 'project' | 'member') {
		const rows: any[] = [];
		const ganttTasks: any[] = [];
		const now = new Date();

		if (mode === 'project') {
			for (const project of projs) {
				rows.push({ id: `p-${project.id}`, label: project.name, enableDragging: false });

				for (const milestone of project.milestones) {
					rows.push({ id: `m-${milestone.id}`, label: `  ${milestone.title}`, enableDragging: false });
					for (const task of milestone.tasks) {
						ganttTasks.push(buildTask(task, `m-${milestone.id}`, project.color));
					}
				}

				if (project.unassigned_tasks.length > 0) {
					rows.push({ id: `nm-${project.id}`, label: '  No Milestone', enableDragging: false });
					for (const task of project.unassigned_tasks) {
						ganttTasks.push(buildTask(task, `nm-${project.id}`, project.color));
					}
				}
			}
		} else {
			const memberMap = new Map<string, { label: string; tasks: any[] }>();
			const unassignedTasks: any[] = [];

			for (const project of projs) {
				const allTasks = [
					...project.milestones.flatMap((m: any) => m.tasks),
					...project.unassigned_tasks
				];
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

			const sorted = Array.from(memberMap.entries()).sort((a, b) =>
				a[1].label.localeCompare(b[1].label)
			);
			for (const [memberId, { label, tasks: memberTasks }] of sorted) {
				rows.push({ id: `u-${memberId}`, label, enableDragging: false });
				for (const { task, color } of memberTasks) {
					ganttTasks.push(buildTask(task, `u-${memberId}`, color));
				}
			}

			if (unassignedTasks.length > 0) {
				rows.push({ id: 'u-unassigned', label: 'Unassigned', enableDragging: false });
				for (const { task, color } of unassignedTasks) {
					ganttTasks.push(buildTask(task, 'u-unassigned', color));
				}
			}
		}

		return { rows, tasks: ganttTasks };
	}

	function buildTask(task: any, rowId: string, color: string) {
		const now = new Date();
		const isUnscheduled = !task.due_date;
		const dueDate = task.due_date ? new Date(task.due_date) : new Date(now.getTime() + 60 * 60 * 1000);
		const fromDate = task.due_date
			? new Date(Math.min(new Date(task.created_at).getTime(), dueDate.getTime() - 60 * 60 * 1000))
			: now;

		const isOverdue = !isUnscheduled && dueDate < now && task.status !== 'done';
		const isDone = task.status === 'done';

		const classes = [
			'gantt-task-bar',
			isUnscheduled ? 'task-unscheduled' : '',
			isOverdue ? 'task-overdue' : '',
			isDone ? 'task-done' : ''
		].filter(Boolean);

		return {
			id: task.id,
			resourceId: rowId,
			label: task.title,
			from: fromDate.getTime(),
			to: dueDate.getTime(),
			classes,
			draggable: true,
			resizable: false,
			// Store extra data for click/drag handlers
			_taskData: task,
			_color: color
		};
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
		const svelteTask = event;
		const originalTask = svelteTask.model._taskData;
		if (originalTask) {
			ontaskclick?.(originalTask);
		}
	}

	let ganttData = $derived(buildGanttData(projects, viewMode));
	let ganttFrom = $derived(rangeStart.getTime());
	let ganttTo = $derived(rangeEnd.getTime());

	onMount(async () => {
		if (!ganttEl) return;

		const { SvelteGantt, SvelteGanttTable } = await import('svelte-gantt');

		ganttInstance = new SvelteGantt({
			target: ganttEl,
			props: {
				rows: ganttData.rows,
				tasks: ganttData.tasks,
				from: ganttFrom,
				to: ganttTo,
				fitWidth: false,
				minWidth: 900,
				headers: [
					{ unit: 'month', format: 'MMMM yyyy', sticky: true },
					{ unit: 'day', format: 'd' }
				],
				columnUnit: 'day',
				columnOffset: 1,
				rowHeight: 44,
				rowPadding: 6,
				taskElementHook: (task: any, element: HTMLElement) => {
					const color = task.model._color || '#6366f1';
					// Target the actual task bar child
					const bar = element.querySelector('.sg-task-background') as HTMLElement;
					if (bar) bar.style.background = color + '33';
					element.style.background = color;
					element.style.borderRadius = '6px';
					element.style.color = '#fff';
					element.addEventListener('click', () => handleTaskSelect(task));
				},
				modules: [SvelteGanttTable],
				tableHeaders: [{ title: 'Name', property: 'label', width: 220 }],
				tableWidth: 220
			}
		});

		ganttInstance.$on('change', (e: any) => {
			handleTaskChange(e.detail);
		});
	});

	// Update gantt when data or range changes
	$effect(() => {
		if (!ganttInstance) return;
		const data = ganttData;
		const from = ganttFrom;
		const to = ganttTo;
		ganttInstance.$set({
			rows: data.rows,
			tasks: data.tasks,
			from,
			to
		});
	});
</script>

<style>
	.gantt-wrapper {
		position: relative;
		width: 100%;
		height: 100%;
		overflow-x: auto;
		overflow-y: auto;
	}
	.gantt-wrapper :global(.sg-gantt) {
		background: #0a0f1e;
		color: #e2e8f0;
		font-size: 13px;
		height: 100% !important;
	}
	/* Header rows */
	.gantt-wrapper :global(.sg-header) {
		background: #0f172a;
		border-bottom: 1px solid #1e293b;
		color: #64748b;
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
	.gantt-wrapper :global(.sg-header-unit) {
		border-right: 1px solid #1e293b;
	}
	/* Table (left side) */
	.gantt-wrapper :global(.sg-table-body-cell) {
		background: #0f172a;
		border-right: 1px solid #1e293b;
		border-bottom: 1px solid #1e293b;
		color: #cbd5e1;
		font-size: 12px;
		padding-left: 12px;
	}
	.gantt-wrapper :global(.sg-table-header-cell) {
		background: #0f172a;
		border-right: 1px solid #1e293b;
		border-bottom: 2px solid #334155;
		color: #64748b;
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		padding-left: 12px;
	}
	/* Rows */
	.gantt-wrapper :global(.sg-row) {
		border-bottom: 1px solid #1a2540;
	}
	.gantt-wrapper :global(.sg-row:hover) {
		background: rgba(99, 102, 241, 0.04);
	}
	/* Column lines */
	.gantt-wrapper :global(.sg-column) {
		border-right: 1px solid #1a2540;
	}
	/* Task bars */
	.gantt-wrapper :global(.sg-task) {
		border-radius: 6px !important;
		cursor: pointer;
		box-shadow: 0 1px 3px rgba(0,0,0,0.4);
		transition: filter 0.15s, box-shadow 0.15s;
	}
	.gantt-wrapper :global(.sg-task:hover) {
		filter: brightness(1.15);
		box-shadow: 0 2px 8px rgba(0,0,0,0.5);
	}
	.gantt-wrapper :global(.sg-task-content) {
		padding-left: 10px;
		font-size: 11px;
		font-weight: 500;
		letter-spacing: 0.01em;
		color: rgba(255,255,255,0.92) !important;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.gantt-wrapper :global(.sg-task-background) {
		border-radius: 6px;
		opacity: 0.15;
	}
	/* Task states */
	.gantt-wrapper :global(.task-unscheduled) {
		border: 2px dashed rgba(255,255,255,0.3) !important;
		background: rgba(99,102,241,0.15) !important;
		opacity: 0.7;
	}
	.gantt-wrapper :global(.task-overdue) {
		outline: 2px solid #f87171;
		outline-offset: 2px;
		box-shadow: 0 0 8px rgba(248, 113, 113, 0.3) !important;
	}
	.gantt-wrapper :global(.task-done) {
		opacity: 0.38;
		filter: grayscale(0.3);
	}
	/* Today marker */
	.gantt-wrapper :global(.sg-time-range-highlight) {
		background: rgba(99, 102, 241, 0.08);
	}
</style>

<div class="flex-1 overflow-hidden relative" style="min-height: 0;">
	{#if ganttData.rows.length === 0}
		<div class="flex flex-col items-center justify-center h-full text-gray-500 py-20">
			<p class="text-sm">No projects with timeline data found.</p>
			<p class="text-xs mt-1">Create projects with tasks and milestones to see the timeline.</p>
		</div>
	{:else}
		<div class="gantt-wrapper">
			<div bind:this={ganttEl} style="min-width: 900px; height: 100%;"></div>
		</div>
	{/if}
</div>
