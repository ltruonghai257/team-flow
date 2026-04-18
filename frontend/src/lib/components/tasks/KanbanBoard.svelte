<script lang="ts">
	import { dndzone, SOURCES, TRIGGERS } from 'svelte-dnd-action';
	import { flip } from 'svelte/animate';
	import { statusLabels } from '$lib/utils';
	import KanbanCard from './KanbanCard.svelte';

	export let tasks: any[] = [];
	export let onStatusChange: (taskId: number, newStatus: string) => Promise<void> | void = () => {};
	export let onEdit: (task: any) => void = () => {};

	const columns = ['todo', 'in_progress', 'review', 'done', 'blocked'];
	const flipDurationMs = 200;

	type Column = { status: string; items: any[] };

	// Group tasks into columns reactively
	$: grouped = columns.map((status) => ({
		status,
		items: tasks.filter((t) => t.status === status)
	})) as Column[];

	// Track which task is being dragged to avoid updating before drop finalizes
	async function handleConsider(e: CustomEvent, colIndex: number) {
		grouped[colIndex].items = e.detail.items;
		grouped = grouped;
	}

	async function handleFinalize(e: CustomEvent, colIndex: number) {
		const newItems = e.detail.items;
		const targetStatus = columns[colIndex];
		grouped[colIndex].items = newItems;
		grouped = grouped;

		const info = e.detail.info;
		if (info.trigger === TRIGGERS.DROPPED_INTO_ZONE && info.source === SOURCES.POINTER) {
			const draggedId = info.id;
			const moved = newItems.find((t: any) => String(t.id) === String(draggedId));
			if (moved && moved.status !== targetStatus) {
				try {
					await onStatusChange(moved.id, targetStatus);
				} catch {
					// parent handler should revert by reassigning `tasks`
				}
			}
		}
	}
</script>

<div class="flex gap-3 overflow-x-auto pb-4">
	{#each grouped as col, i (col.status)}
		<div class="flex-shrink-0 w-72 bg-gray-900/60 border border-gray-800 rounded-xl flex flex-col max-h-[calc(100vh-220px)]">
			<div class="px-3 py-2.5 border-b border-gray-800 flex items-center justify-between">
				<h3 class="text-sm font-semibold text-gray-200">{statusLabels[col.status]}</h3>
				<span class="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded-full">
					{col.items.length}
				</span>
			</div>
			<div
				use:dndzone={{ items: col.items, flipDurationMs, dropTargetStyle: {} }}
				on:consider={(e) => handleConsider(e, i)}
				on:finalize={(e) => handleFinalize(e, i)}
				class="flex-1 overflow-y-auto p-2 space-y-2 min-h-[120px]"
			>
				{#each col.items as task (task.id)}
					<div animate:flip={{ duration: flipDurationMs }}>
						<KanbanCard {task} {onEdit} />
					</div>
				{/each}
				{#if col.items.length === 0}
					<div class="text-center text-xs text-gray-600 py-4">No tasks</div>
				{/if}
			</div>
		</div>
	{/each}
</div>
