<script lang="ts">
	import type { CustomStatus } from '$lib/api';

	export let status: CustomStatus;
	export let availableStatuses: CustomStatus[] = [];
	export let open = false;
	export let onClose: () => void = () => {};
	export let onConfirm: (payload: { mode: string; replacement_status_id?: number }) => void = () => {};

	let mode: 'delete' | 'move_delete' | 'archive' = 'delete';
	let replacementId: number | undefined = undefined;

	$: hasTasksAssigned = status?.task_count > 0;
	$: replacementChoices = availableStatuses.filter(
		(s) => s.id !== status?.id && !s.is_archived
	);
	$: confirmDisabled = mode === 'move_delete' && !replacementId;

	function handleConfirm() {
		if (confirmDisabled) return;
		onConfirm({ mode, replacement_status_id: replacementId });
	}
</script>

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
		<div class="w-full max-w-md rounded-lg bg-gray-800 p-6 shadow-xl">
			{#if hasTasksAssigned}
				<h2 class="mb-1 text-lg font-semibold text-white">
					{status.task_count} tasks use {status.name}
				</h2>
				<p class="mb-4 text-sm text-gray-400">
					Choose how to handle existing tasks before removing this status from active use.
				</p>
				<div class="mb-4 space-y-2">
					<label class="flex items-center gap-2 cursor-pointer">
						<input type="radio" bind:group={mode} value="move_delete" class="accent-indigo-500" />
						<span class="text-sm text-gray-200">Move tasks and delete</span>
					</label>
					{#if mode === 'move_delete'}
						<select
							bind:value={replacementId}
							class="mt-1 ml-6 w-full rounded bg-gray-700 px-3 py-2 text-sm text-white border border-gray-600"
						>
							<option value={undefined}>Select replacement status…</option>
							{#each replacementChoices as s}
								<option value={s.id}>{s.name}</option>
							{/each}
						</select>
					{/if}
					<label class="flex items-center gap-2 cursor-pointer">
						<input type="radio" bind:group={mode} value="archive" class="accent-indigo-500" />
						<span class="text-sm text-gray-200">Archive status</span>
					</label>
				</div>
			{:else}
				<h2 class="mb-1 text-lg font-semibold text-white">Delete {status.name}?</h2>
				<p class="mb-4 text-sm text-gray-400">
					This removes the status from the current set. This cannot be undone.
				</p>
			{/if}

			<div class="flex justify-end gap-2">
				<button
					on:click={onClose}
					class="rounded px-4 py-2 text-sm text-gray-300 hover:bg-gray-700"
				>
					Cancel
				</button>
				{#if hasTasksAssigned}
					<button
						on:click={handleConfirm}
						disabled={confirmDisabled}
						class="rounded px-4 py-2 text-sm font-medium
							{confirmDisabled
							? 'bg-indigo-900 text-indigo-400 cursor-not-allowed'
							: 'bg-indigo-600 text-white hover:bg-indigo-500'}"
					>
						{mode === 'archive' ? 'Archive status' : 'Move tasks and delete'}
					</button>
				{:else}
					<button
						on:click={handleConfirm}
						class="rounded bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-500"
					>
						Delete status
					</button>
				{/if}
			</div>
		</div>
	</div>
{/if}
