<script lang="ts">
	import { dndzone, SOURCES, TRIGGERS } from 'svelte-dnd-action';
	import { flip } from 'svelte/animate';
	import { createEventDispatcher } from 'svelte';
	import { Info } from 'lucide-svelte';
	import { statusLabels } from '$lib/utils';
	import type { CustomStatus } from '$lib/api';
	import KanbanCard from './KanbanCard.svelte';

	export let tasks: any[] = [];
	export let backlogTasks: any[] = [];
	export let activeSprintId: number | null = null;
	export let onEdit: (task: any) => void = () => {};
	export let statuses: CustomStatus[] = [];
	export let assessTaskMove: (task: any, targetStatusId: number) => {
		allowed: boolean;
		currentStatusId: number | null;
		currentStatusName: string;
		targetStatusId: number;
		targetStatusName: string;
		allowedStatusIds: number[];
	} = () => ({
		allowed: true,
		currentStatusId: null,
		currentStatusName: '',
		targetStatusId: 0,
		targetStatusName: '',
		allowedStatusIds: []
	});
	export let isStatusRestricted: (targetStatusId: number) => boolean = () => false;

	const dispatch = createEventDispatcher();
	const flipDurationMs = 200;

	const legacyColumns = ['todo', 'in_progress', 'review', 'done', 'blocked'];

	type Column =
		| { type: 'backlog'; items: any[] }
		| { type: 'status'; statusId: number; statusSlug: string; name: string; color: string; is_done: boolean; items: any[] };

	function cloneGrouped(columns: Column[]): Column[] {
		return columns.map((column) => ({
			...column,
			items: [...column.items]
		}));
	}

	function taskStatusKey(t: any): string {
		if (t.custom_status_id != null) return String(t.custom_status_id);
		return t.status ?? 'todo';
	}

	$: activeStatuses = statuses.filter((s) => !s.is_archived).sort((a, b) => a.position - b.position);
	$: useDbStatuses = activeStatuses.length > 0;
	let dragSnapshot: Column[] | null = null;
	let draggedTask: any = null;

	$: grouped = (() => {
		const cols: Column[] = [{ type: 'backlog', items: backlogTasks }];
		if (useDbStatuses) {
			for (const s of activeStatuses) {
				cols.push({
					type: 'status',
					statusId: s.id,
					statusSlug: s.slug,
					name: s.name,
					color: s.color,
					is_done: s.is_done,
					items: tasks.filter((t) => taskStatusKey(t) === String(s.id))
				});
			}
		} else {
			for (const slug of legacyColumns) {
				cols.push({
					type: 'status',
					statusId: 0,
					statusSlug: slug,
					name: statusLabels[slug] ?? slug,
					color: '#64748b',
					is_done: slug === 'done',
					items: tasks.filter((t) => t.status === slug)
				});
			}
		}
		return cols;
	})();

	function handleConsider(e: CustomEvent, colIndex: number) {
		if (!dragSnapshot) {
			dragSnapshot = cloneGrouped(grouped);
		}
		const info = e.detail.info;
		if (info?.trigger === TRIGGERS.DRAG_STARTED) {
			draggedTask = findTaskById(info.id);
		}
		grouped[colIndex].items = e.detail.items;
		grouped = [...grouped];
	}

	function restoreSnapshot() {
		if (!dragSnapshot) return;
		grouped = cloneGrouped(dragSnapshot);
		dragSnapshot = null;
		draggedTask = null;
	}

	function findTaskById(taskId: number | string) {
		const id = String(taskId);
		return [...tasks, ...backlogTasks].find((task) => String(task.id) === id) ?? null;
	}

	function isColumnDropDisabled(column: Column) {
		if (!draggedTask || !useDbStatuses || column.type !== 'status') return false;
		return !assessTaskMove(draggedTask, column.statusId).allowed;
	}

	function columnClass(column: Column) {
		const base =
			'flex-shrink-0 w-72 bg-gray-900/60 border rounded-xl flex flex-col max-h-[calc(100vh-270px)] md:max-h-[calc(100vh-220px)] transition-colors';
		if (isColumnDropDisabled(column)) {
			return `${base} border-red-900/50 bg-gray-950/80 opacity-55`;
		}
		if (draggedTask && useDbStatuses && column.type === 'status') {
			return `${base} border-green-500/40 bg-green-950/10`;
		}
		return `${base} border-gray-800`;
	}

	function handleFinalize(e: CustomEvent, colIndex: number) {
		const newItems = e.detail.items;
		const column = grouped[colIndex];
		grouped[colIndex].items = newItems;
		grouped = [...grouped];

		const info = e.detail.info;
		if (info.trigger === TRIGGERS.DROPPED_INTO_ZONE && info.source === SOURCES.POINTER) {
			const draggedId = info.id;
			const moved = newItems.find((t: any) => String(t.id) === String(draggedId));
			if (moved && column.type === 'backlog') {
				dragSnapshot = null;
				dispatch('taskMove', { id: moved.id, sprint_id: null, status: moved.status });
			} else if (moved && column.type === 'status') {
				const targetSprintId = activeSprintId;
				if (useDbStatuses && column.statusId) {
					const assessment = assessTaskMove(moved, column.statusId);
					if (!assessment.allowed) {
						restoreSnapshot();
						dispatch('taskMoveBlocked', assessment);
						return;
					}
					dispatch('taskMove', {
						id: moved.id,
						sprint_id: targetSprintId,
						custom_status_id: column.statusId
					});
				} else {
					dragSnapshot = null;
					dispatch('taskMove', {
						id: moved.id,
						sprint_id: targetSprintId,
						status: column.statusSlug
					});
				}
			}
		}
		dragSnapshot = null;
		draggedTask = null;
	}
</script>

<div class="flex gap-3 overflow-x-auto pb-4" style="touch-action: pan-x pan-y;">
	{#each grouped as col, i (col.type === 'backlog' ? 'backlog' : col.type === 'status' ? (col.statusId || col.statusSlug) : 'backlog')}
		{@const dropDisabled = isColumnDropDisabled(col)}
		<div class={columnClass(col)}>
			<div class="px-3 py-2.5 border-b border-gray-800 flex items-center justify-between">
				<div class="flex items-center gap-2 min-w-0">
					{#if col.type === 'status'}
						<span class="h-2.5 w-2.5 rounded-full flex-shrink-0" style="background-color: {col.color};"></span>
					{/if}
					<h3 class="text-sm font-semibold text-gray-200 truncate">
						{col.type === 'backlog' ? 'Backlog' : col.name}
					</h3>
					{#if col.type === 'status' && useDbStatuses && isStatusRestricted(col.statusId)}
						<span
							class="flex-shrink-0 text-gray-500"
							title="Workflow rules restrict some moves into this status"
							aria-label="Workflow rules restrict some moves into this status"
						>
							<Info size={12} />
						</span>
					{/if}
					{#if col.type === 'status' && col.is_done}
						<span class="rounded-full bg-green-900 px-1.5 py-0.5 text-[10px] text-green-300">Done</span>
					{/if}
					{#if dropDisabled}
						<span class="rounded-full bg-red-950 px-1.5 py-0.5 text-[10px] text-red-300">
							Blocked
						</span>
					{/if}
				</div>
				<span class="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded-full">
					{col.items.length}
				</span>
			</div>
			<div
				use:dndzone={{ items: col.items, flipDurationMs, dropTargetStyle: {}, dropFromOthersDisabled: dropDisabled }}
				on:consider={(e) => handleConsider(e, i)}
				on:finalize={(e) => handleFinalize(e, i)}
				class="flex-1 overflow-y-auto p-2 space-y-2 min-h-[120px] {dropDisabled
					? 'cursor-not-allowed'
					: ''}"
			>
				{#each col.items as task (task.id)}
					<div animate:flip={{ duration: flipDurationMs }}>
						<KanbanCard {task} {onEdit} />
					</div>
				{/each}
				{#if col.items.length === 0}
					<div class="text-center text-xs text-gray-600 py-4">No tasks in this status</div>
				{/if}
			</div>
		</div>
	{/each}
</div>
