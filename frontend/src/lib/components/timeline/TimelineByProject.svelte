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
			_taskData: task
		};
	}

	function buildGanttData(projs: TimelineProject[]) {
		const rows: any[] = [];
		const ganttTasks: any[] = [];
		const model = viewModel ?? FALLBACK_VIEW_MODEL;

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

	let ganttData = $derived(buildGanttData(projects));
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
					minWidth: 1200,
					headers: [
						{ unit: 'month', format: 'MMMM yyyy', sticky: true },
						{ unit: columnUnit, format: columnUnit === 'week' ? 'w' : 'd' }
					],
					columnUnit,
					columnOffset: 1,
					rowHeight: 56,
					rowPadding: 6,
					modules: [SvelteGanttTable],
					tableHeaders: [{ title: 'Timeline', property: 'label', width: 380 }],
					tableWidth: 380
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

{#if projects.length === 0}
	<div class="flex items-center justify-center h-full" style="height: 100%; min-height: 0;">
		<div class="text-center">
			<div class="w-12 h-12 rounded-full bg-slate-800/50 flex items-center justify-center mx-auto mb-3">
				<svg class="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
				</svg>
			</div>
			<p class="text-sm text-slate-500">No projects yet</p>
			<p class="text-xs mt-1">Add milestones and tasks to see planning timelines here.</p>
		</div>
	</div>
{:else}
	<div class="gantt-wrapper" style="height: max({ganttData.rows.length * 56 + 90}px, 420px);">
		<div bind:this={ganttEl} style="min-width: 1200px; height: 100%;"></div>
	</div>
{/if}

<style>
	.gantt-wrapper:not(:has(.sg-gantt)) {
		display: none;
	}

	.gantt-wrapper {
		position: relative;
		width: 100%;
		height: 100%;
		overflow: auto;
		background: linear-gradient(180deg, #0c1222 0%, #0a0f1e 50%, #050a14 100%);
		border-radius: 20px;
		border: 1px solid rgba(99, 102, 241, 0.2);
		box-shadow: 
			0 0 0 1px rgba(99, 102, 241, 0.1),
			0 10px 40px rgba(0, 0, 0, 0.5),
			0 0 80px rgba(99, 102, 241, 0.1),
			inset 0 1px 0 rgba(255, 255, 255, 0.08);
	}

	.gantt-wrapper :global(*) {
		border-color: transparent !important;
		outline-color: transparent !important;
	}

	.gantt-wrapper :global(.sg-header) {
		background: transparent;
		color: #f8fafc;
		font-size: 13px;
		height: 100% !important;
	}

	.gantt-wrapper :global(.sg-gantt) {
		background: transparent;
		color: #f8fafc;
		font-size: 13px;
		height: 100% !important;
	}

	.gantt-wrapper :global(.sg-table-header) {
		background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
		border-bottom: 2px solid rgba(99, 102, 241, 0.3) !important;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
	}

	.gantt-wrapper :global(.sg-table-header-cell) {
		background: transparent !important;
		color: #e2e8f0 !important;
		font-weight: 800;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		font-size: 10px;
		text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
	}

	.gantt-wrapper :global(.sg-table-row) {
		background: transparent !important;
		border-bottom: 1px solid rgba(30, 41, 59, 0.5) !important;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}

	.gantt-wrapper :global(.sg-table-row:hover) {
		background: linear-gradient(90deg, rgba(99, 102, 241, 0.15) 0%, rgba(30, 41, 59, 0.4) 100%) !important;
	}

	.gantt-wrapper :global(.sg-table-cell) {
		color: #f1f5f9 !important;
	}

	.gantt-wrapper :global(.project-row) {
		background: linear-gradient(135deg, #4f46e5 0%, #4338ca 50%, #312e81 100%) !important;
		font-weight: 900;
		color: #e0e7ff !important;
		box-shadow: 
			0 6px 20px rgba(99, 102, 241, 0.4),
			inset 0 1px 0 rgba(255, 255, 255, 0.15),
			inset 0 -1px 0 rgba(0, 0, 0, 0.1);
		text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
		border-bottom: 1px solid rgba(99, 102, 241, 0.3);
	}

	.gantt-wrapper :global(.milestone-row) {
		background: rgba(15, 23, 42, 0.5) !important;
	}

	.gantt-wrapper :global(.milestone-group-row) {
		background: linear-gradient(135deg, rgba(234, 179, 8, 0.2) 0%, rgba(30, 41, 59, 0.7) 100%) !important;
		font-weight: 900;
		color: #fcd34d !important;
		box-shadow: 
			0 4px 12px rgba(234, 179, 8, 0.3),
			inset 0 1px 0 rgba(251, 191, 36, 0.15);
		border-left: 3px solid #fbbf24;
	}

	.gantt-wrapper :global(.milestone-row-focused) {
		background: linear-gradient(135deg, #4f46e5 0%, #4338ca 50%, #312e81 100%) !important;
		box-shadow: 
			0 0 0 2px #a78bfa,
			0 6px 24px rgba(167, 139, 250, 0.5),
			inset 0 1px 0 rgba(255, 255, 255, 0.15);
	}

	.gantt-wrapper :global(.task-row) {
		background: rgba(2, 6, 23, 0.7) !important;
	}

	.gantt-wrapper :global(.task-group-row) {
		background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(30, 41, 59, 0.7) 100%) !important;
		font-weight: 800;
		color: #c4b5fd !important;
		box-shadow: 
			0 3px 10px rgba(99, 102, 241, 0.3),
			inset 0 1px 0 rgba(167, 139, 250, 0.15);
		border-left: 3px solid #818cf8;
	}

	.gantt-wrapper :global(.no-milestone-row) {
		background: rgba(15, 23, 42, 0.5) !important;
		font-style: italic;
		color: #94a3b8 !important;
	}

	.gantt-wrapper :global(.milestone-header) {
		background: transparent;
		border: none;
		padding: 14px 18px;
		text-align: left;
		width: 100%;
		cursor: pointer;
		border-radius: 12px;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}

	.gantt-wrapper :global(.milestone-header:hover) {
		background: linear-gradient(90deg, rgba(99, 102, 241, 0.2) 0%, rgba(30, 41, 59, 0.6) 100%);
		transform: translateX(6px);
	}

	.gantt-wrapper :global(.milestone-header-focused) {
		background: linear-gradient(135deg, #4f46e5 0%, #4338ca 50%, #312e81 100%);
		border-left: 4px solid #c4b5fd;
		box-shadow: 
			0 6px 20px rgba(196, 181, 253, 0.5),
			inset 0 1px 0 rgba(255, 255, 255, 0.15);
	}

	.gantt-wrapper :global(.milestone-title-row) {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.gantt-wrapper :global(.milestone-title) {
		font-weight: 900;
		color: #ffffff;
		font-size: 15px;
		text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
		letter-spacing: 0.02em;
	}

	.gantt-wrapper :global(.milestone-status) {
		font-size: 8px;
		padding: 4px 12px;
		border-radius: 10px;
		text-transform: uppercase;
		font-weight: 900;
		letter-spacing: 0.1em;
		box-shadow: 
			0 2px 8px rgba(0, 0, 0, 0.3),
			inset 0 1px 0 rgba(255, 255, 255, 0.2);
	}

	.gantt-wrapper :global(.milestone-status-planned) {
		background: linear-gradient(135deg, #3b82f650 0%, #2563eb50 100%);
		color: #60a5fa;
		border: 1px solid #3b82f670;
	}

	.gantt-wrapper :global(.milestone-status-in_progress) {
		background: linear-gradient(135deg, #f59e0b50 0%, #d9770650 100%);
		color: #fbbf24;
		border: 1px solid #f59e0b70;
	}

	.gantt-wrapper :global(.milestone-status-completed) {
		background: linear-gradient(135deg, #10b98150 0%, #05966950 100%);
		color: #34d399;
		border: 1px solid #10b98170;
	}

	.gantt-wrapper :global(.milestone-status-blocked) {
		background: linear-gradient(135deg, #ef444450 0%, #dc262650 100%);
		color: #f87171;
		border: 1px solid #ef444470;
	}

	.gantt-wrapper :global(.milestone-progress) {
		font-size: 13px;
		color: #f1f5f9;
		font-weight: 800;
	}

	.gantt-wrapper :global(.milestone-meta-row) {
		display: flex;
		align-items: center;
		gap: 18px;
		margin-top: 10px;
	}

	.gantt-wrapper :global(.milestone-span) {
		font-size: 12px;
		color: #e2e8f0;
		font-weight: 700;
	}

	.gantt-wrapper :global(.milestone-count) {
		font-size: 10px;
		color: #cbd5e1;
		font-weight: 800;
	}

	.gantt-wrapper :global(.milestone-chip) {
		font-size: 8px;
		padding: 4px 12px;
		border-radius: 8px;
		font-weight: 800;
		letter-spacing: 0.05em;
		box-shadow: 
			0 2px 8px rgba(0, 0, 0, 0.25),
			inset 0 1px 0 rgba(255, 255, 255, 0.15);
	}

	.gantt-wrapper :global(.milestone-chip-risk-low) {
		background: linear-gradient(135deg, #10b98150 0%, #05966950 100%);
		color: #34d399;
		border: 1px solid #10b98160;
	}

	.gantt-wrapper :global(.milestone-chip-risk-medium) {
		background: linear-gradient(135deg, #f59e0b50 0%, #d9770650 100%);
		color: #fbbf24;
		border: 1px solid #f59e0b60;
	}

	.gantt-wrapper :global(.milestone-chip-risk-high) {
		background: linear-gradient(135deg, #ef444450 0%, #dc262650 100%);
		color: #f87171;
		border: 1px solid #ef444460;
	}

	.gantt-wrapper :global(.milestone-chip-decision) {
		background: linear-gradient(135deg, #8b5cf650 0%, #7c3aed50 100%);
		color: #a78bfa;
		border: 1px solid #8b5cf660;
	}

	.gantt-wrapper :global(.sg-timeline-header) {
		background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
		border-bottom: 2px solid rgba(99, 102, 241, 0.3) !important;
		color: #e2e8f0 !important;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
	}

	.gantt-wrapper :global(.sg-timeline-header-cell) {
		background: transparent !important;
		color: #e2e8f0 !important;
		font-weight: 800;
	}

	.gantt-wrapper :global(.sg-timeline-body) {
		background: transparent !important;
	}

	.gantt-wrapper :global(.sg-timeline-row) {
		background: transparent !important;
		border-bottom: 1px solid rgba(30, 41, 59, 0.5) !important;
	}

	.gantt-wrapper :global(.sg-timeline-row:hover) {
		background: linear-gradient(90deg, rgba(99, 102, 241, 0.15) 0%, rgba(30, 41, 59, 0.4) 100%) !important;
	}

	.gantt-wrapper :global(.sg-task:nth-child(2n)) {
		margin-top: 8px;
	}

	.gantt-wrapper :global(.sg-task:nth-child(3n)) {
		margin-top: 16px;
	}

	.gantt-wrapper :global(.sg-task) {
		background: rgba(30, 41, 59, 0.6) !important;
		border: 1px solid rgba(71, 85, 105, 0.5) !important;
		border-radius: 12px;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
	}

	.gantt-wrapper :global(.sg-task:hover) {
		border-color: rgba(99, 102, 241, 0.5) !important;
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
		transform: translateY(-3px) scale(1.03);
	}

	.gantt-wrapper :global(.gantt-task-bar) {
		background: linear-gradient(135deg, #a78bfa 0%, #818cf8 33%, #6366f1 66%, #4f46e5 100%) !important;
		border-radius: 12px;
		box-shadow: 
			0 6px 20px rgba(99, 102, 241, 0.6),
			inset 0 2px 0 rgba(255, 255, 255, 0.25),
			inset 0 -1px 0 rgba(0, 0, 0, 0.1);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		position: relative;
	}

	.gantt-wrapper :global(.sg-task-label) {
		white-space: nowrap !important;
		overflow: hidden !important;
		text-overflow: ellipsis !important;
		font-weight: 700 !important;
		font-size: 12px !important;
		color: #ffffff !important;
		text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6) !important;
		letter-spacing: 0.02em;
	}

	.gantt-wrapper :global(.sg-task-label-container) {
		overflow: hidden !important;
		white-space: nowrap !important;
	}

	.gantt-wrapper :global(.gantt-task-bar:hover) {
		box-shadow: 
			0 10px 30px rgba(99, 102, 241, 0.7),
			inset 0 2px 0 rgba(255, 255, 255, 0.35),
			inset 0 -1px 0 rgba(0, 0, 0, 0.1);
		transform: translateY(-3px);
	}

	.gantt-wrapper :global(.task-unscheduled) {
		background: linear-gradient(135deg, #94a3b8 0%, #64748b 50%, #475569 100%) !important;
		opacity: 0.85;
		box-shadow: 
			0 6px 16px rgba(100, 116, 139, 0.4),
			inset 0 1px 0 rgba(255, 255, 255, 0.15);
	}

	.gantt-wrapper :global(.task-overdue) {
		background: linear-gradient(135deg, #fca5a5 0%, #f87171 33%, #ef4444 66%, #dc2626 100%) !important;
		box-shadow: 
			0 6px 20px rgba(239, 68, 68, 0.6),
			inset 0 2px 0 rgba(255, 255, 255, 0.25),
			inset 0 -1px 0 rgba(0, 0, 0, 0.1);
	}

	.gantt-wrapper :global(.task-done) {
		background: linear-gradient(135deg, #6ee7b7 0%, #34d399 50%, #10b981 66%, #059669 100%) !important;
		opacity: 0.75;
		box-shadow: 
			0 6px 16px rgba(16, 185, 129, 0.4),
			inset 0 1px 0 rgba(255, 255, 255, 0.15);
	}

	.gantt-wrapper :global(.task-focused) {
		box-shadow: 
			0 0 0 5px #c4b5fd,
			0 12px 40px rgba(196, 181, 253, 0.7) !important;
		transform: translateY(-5px) scale(1.06);
		z-index: 10;
	}

	.gantt-wrapper::-webkit-scrollbar {
		width: 12px;
		height: 12px;
	}

	.gantt-wrapper::-webkit-scrollbar-track {
		background: rgba(15, 23, 42, 0.7);
		border-radius: 8px;
		box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
	}

	.gantt-wrapper::-webkit-scrollbar-thumb {
		background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%);
		border-radius: 8px;
		border: 3px solid rgba(15, 23, 42, 0.5);
		box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
	}

	.gantt-wrapper::-webkit-scrollbar-thumb:hover {
		background: linear-gradient(180deg, #818cf8 0%, #6366f1 100%);
	}
</style>
