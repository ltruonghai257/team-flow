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
					// Force override sg-task-default via inline style (highest specificity)
					element.style.setProperty('background', color, 'important');
					element.style.setProperty('border-radius', '5px', 'important');
					element.style.setProperty('border', 'none', 'important');
					element.style.setProperty('box-shadow', `0 0 0 1px ${color}88, 0 2px 6px rgba(0,0,0,0.45)`, 'important');
					// Dim the inner progress overlay
					const bg = element.querySelector('.sg-task-background') as HTMLElement;
					if (bg) {
						bg.style.setProperty('background', 'rgba(0,0,0,0.15)', 'important');
					}
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
		background: #080d1a;
	}

	/* ── Reset ALL svelte-gantt borders to transparent first ── */
	.gantt-wrapper :global(*) {
		border-color: transparent !important;
		outline-color: transparent !important;
	}

	/* ── Root ── */
	.gantt-wrapper :global(.sg-gantt) {
		background: #080d1a;
		color: #94a3b8;
		font-size: 12px;
		height: 100% !important;
	}

	/* ── Header date rows ── */
	.gantt-wrapper :global(.sg-header) {
		background: #080d1a !important;
		border-bottom: 1px solid #151f35 !important;
		color: #475569;
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}
	.gantt-wrapper :global(.sg-header-unit) {
		border-right: 1px solid #151f35 !important;
	}

	/* ── Left name table ── */
	.gantt-wrapper :global(.sg-table-body-cell) {
		background: #0b1120 !important;
		border-right: 1px solid #151f35 !important;
		border-bottom: 1px solid #111827 !important;
		color: #94a3b8;
		font-size: 12px;
		padding-left: 14px;
	}
	.gantt-wrapper :global(.sg-table-header-cell) {
		background: #080d1a !important;
		border-right: 1px solid #151f35 !important;
		border-bottom: 1px solid #151f35 !important;
		color: #334155;
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		padding-left: 14px;
	}

	/* ── Rows ── */
	.gantt-wrapper :global(.sg-row) {
		border-bottom: 1px solid #0f1a2e !important;
	}
	.gantt-wrapper :global(.sg-row:hover) {
		background: rgba(99, 102, 241, 0.03) !important;
	}

	/* ── Column day lines ── */
	.gantt-wrapper :global(.sg-column) {
		border-right: 1px solid #0f1a2e !important;
	}

	/* ── Kill the default blue ── */
	.gantt-wrapper :global(.sg-task-default) {
		background: #6366f1 !important;
		color: #fff !important;
	}
	.gantt-wrapper :global(.sg-task-default:hover) {
		background: #6366f1 !important;
	}
	.gantt-wrapper :global(.sg-task-default.selected) {
		background: #6366f1 !important;
	}

	/* ── Task bars ── */
	.gantt-wrapper :global(.sg-task) {
		border-radius: 5px !important;
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
		border-radius: 5px !important;
		background: rgba(0, 0, 0, 0.18) !important;
	}

	/* ── Task states ── */
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

	/* ── Scrollbar ── */
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
	.gantt-wrapper::-webkit-scrollbar-thumb:hover {
		background: #334155;
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
