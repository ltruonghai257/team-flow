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

		function getTaskColor(task: any) {
			return task._color || '#6366f1';
		}

		ganttInstance = new SvelteGantt({
			target: ganttEl,
			props: {
				rows: ganttData.rows,
				tasks: ganttData.tasks,
				from: ganttFrom,
				to: ganttTo,
				fitWidth: true,
				headers: [
					{ unit: 'month', format: 'MMMM yyyy' },
					{ unit: 'day', format: 'd' }
				],
				columnUnit: 'day',
				columnOffset: 1,
				rowHeight: 36,
				rowPadding: 4,
				taskElementHook: (task: any, element: HTMLElement) => {
					element.style.background = getTaskColor(task.model);
					element.style.borderColor = getTaskColor(task.model);
					element.addEventListener('click', () => handleTaskSelect(task));
				},
				modules: [SvelteGanttTable],
				tableHeaders: [{ title: 'Name', property: 'label', width: 180 }],
				tableWidth: 180
			}
		});

		ganttInstance.$on('change', (e: any) => {
			handleTaskChange(e.detail);
		});
	});

	// Update gantt when data changes
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
	:global(.gantt-task-bar) {
		border-radius: 4px;
		font-size: 12px;
		opacity: 0.9;
		cursor: pointer;
		transition: opacity 0.15s;
	}
	:global(.gantt-task-bar:hover) {
		opacity: 1;
	}
	:global(.task-unscheduled) {
		border: 2px dashed currentColor !important;
		background: transparent !important;
		opacity: 0.6;
	}
	:global(.task-overdue) {
		outline: 2px solid #ef4444;
		outline-offset: 1px;
	}
	:global(.task-done) {
		opacity: 0.4;
	}
	:global(.sg-gantt) {
		background: #030712;
		color: #d1d5db;
		font-size: 13px;
	}
	:global(.sg-table-body-cell) {
		background: #111827;
		border-color: #1f2937;
		color: #d1d5db;
		font-size: 12px;
	}
	:global(.sg-header) {
		background: #111827;
		border-color: #1f2937;
		color: #9ca3af;
	}
	:global(.sg-row) {
		border-color: #1f2937;
	}
	:global(.sg-row:hover) {
		background: rgba(255, 255, 255, 0.02);
	}
</style>

<div class="flex-1 overflow-hidden relative h-full">
	{#if ganttData.rows.length === 0}
		<div class="flex flex-col items-center justify-center h-full text-gray-500 py-20">
			<p class="text-sm">No projects with timeline data found.</p>
			<p class="text-xs mt-1">Create projects with tasks and milestones to see the timeline.</p>
		</div>
	{:else}
		<div bind:this={ganttEl} class="w-full h-full"></div>
	{/if}
</div>
