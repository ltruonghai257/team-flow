<script lang="ts">
	import { GripVertical, Pencil, Trash2 } from 'lucide-svelte';
	import type { CustomStatus } from '$lib/api';

	export let statuses: CustomStatus[] = [];
	export let managementMode = false;
	export let onEdit: (status: CustomStatus) => void = () => {};
	export let onDelete: (status: CustomStatus) => void = () => {};
	export let onReorder: (orderedIds: number[]) => void = () => {};

	$: sorted = [...statuses].sort((a, b) => a.position - b.position);

	function moveUp(index: number) {
		if (index === 0) return;
		const ids = sorted.map((s) => s.id);
		[ids[index - 1], ids[index]] = [ids[index], ids[index - 1]];
		onReorder(ids);
	}

	function moveDown(index: number) {
		if (index === sorted.length - 1) return;
		const ids = sorted.map((s) => s.id);
		[ids[index], ids[index + 1]] = [ids[index + 1], ids[index]];
		onReorder(ids);
	}
</script>

<ul class="space-y-1">
	{#each sorted as status, i (status.id)}
		<li class="flex items-center gap-2 rounded px-2 py-1.5 hover:bg-gray-700/50 group">
			{#if managementMode}
				<span class="text-gray-500 cursor-grab active:cursor-grabbing">
					<GripVertical size={16} />
				</span>
			{/if}

			<span
				class="h-3 w-3 rounded-full flex-shrink-0"
				style="background-color: {status.color};"
			></span>

			<span class="flex-1 text-sm text-gray-200 truncate">{status.name}</span>

			{#if status.is_done}
				<span class="rounded-full bg-green-900 px-2 py-0.5 text-xs text-green-300">Done</span>
			{/if}

			{#if status.is_archived}
				<span class="rounded-full bg-yellow-900 px-2 py-0.5 text-xs text-yellow-300">Archived</span>
			{/if}

			{#if managementMode}
				<code class="text-xs text-gray-500 font-mono hidden group-hover:inline">{status.slug}</code>

				<button
					on:click={() => moveUp(i)}
					disabled={i === 0}
					aria-label="Move up"
					class="rounded p-0.5 text-gray-400 hover:text-white disabled:opacity-30"
				>
					Move up
				</button>
				<button
					on:click={() => moveDown(i)}
					disabled={i === sorted.length - 1}
					aria-label="Move down"
					class="rounded p-0.5 text-gray-400 hover:text-white disabled:opacity-30"
				>
					Move down
				</button>

				<button
					on:click={() => onEdit(status)}
					aria-label="Edit {status.name}"
					class="rounded p-0.5 text-gray-400 hover:text-white"
				>
					<Pencil size={14} />
				</button>
				<button
					on:click={() => onDelete(status)}
					aria-label="Delete {status.name}"
					class="rounded p-0.5 text-gray-400 hover:text-red-400"
				>
					<Trash2 size={14} />
				</button>
			{/if}
		</li>
	{/each}
</ul>
