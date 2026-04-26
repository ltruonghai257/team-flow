<script lang="ts">
	import { Plus } from 'lucide-svelte';
	import { statusSets } from '$lib/api';
	import type { CustomStatus, StatusSet } from '$lib/api';
	import StatusEditorRow from './StatusEditorRow.svelte';
	import StatusReorderList from './StatusReorderList.svelte';
	import StatusDeleteDialog from './StatusDeleteDialog.svelte';

	export let statusSet: StatusSet | null = null;
	export let scopeLabel = 'Sub-team default';
	export let canManage = false;
	export let isMixedProjectView = false;
	export let onRefresh: () => void = () => {};

	let editingStatus: CustomStatus | null = null;
	let deletingStatus: CustomStatus | null = null;
	let creatingNew = false;
	let savingOrder = false;

	const emptyNew: CustomStatus = {
		id: 0,
		status_set_id: 0,
		name: '',
		slug: '',
		color: '#64748b',
		position: 0,
		is_done: false,
		is_archived: false,
		legacy_status: null,
		task_count: 0,
		created_at: '',
		updated_at: '',
	};

	async function handleReorder(ids: number[]) {
		if (!statusSet) return;
		savingOrder = true;
		try {
			await statusSets.reorder(statusSet.id, ids);
			onRefresh();
		} finally {
			savingOrder = false;
		}
	}

	async function handleEdit(data: { name: string; color: string; is_done: boolean }) {
		if (!editingStatus) return;
		await statusSets.updateStatus(editingStatus.id, data);
		editingStatus = null;
		onRefresh();
	}

	async function handleCreate(data: { name: string; color: string; is_done: boolean }) {
		await statusSets.createStatus(data);
		creatingNew = false;
		onRefresh();
	}

	async function handleDelete(payload: { mode: string; replacement_status_id?: number }) {
		if (!deletingStatus) return;
		await statusSets.deleteStatus(deletingStatus.id, payload);
		deletingStatus = null;
		onRefresh();
	}
</script>

<div class="space-y-3">
	<div class="flex items-center justify-between">
		<h3 class="text-sm font-semibold text-gray-300">Manage Statuses — {scopeLabel}</h3>
		{#if savingOrder}
			<span class="text-xs text-gray-500">Saving order…</span>
		{/if}
		{#if canManage && !isMixedProjectView}
			<button
				on:click={() => (creatingNew = true)}
				class="flex items-center gap-1 rounded bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-500"
			>
				<Plus size={12} />
				Create status
			</button>
		{/if}
	</div>

	{#if isMixedProjectView}
		<p class="text-xs text-gray-500 italic">
			Project-specific statuses are available after filtering to one project.
		</p>
	{:else if !statusSet || statusSet.statuses.length === 0}
		<p class="text-xs text-gray-500">No statuses yet.</p>
	{:else}
		{#if editingStatus}
			<StatusEditorRow
				status={editingStatus}
				onSave={handleEdit}
				onCancel={() => (editingStatus = null)}
			/>
		{/if}

		<StatusReorderList
			statuses={statusSet.statuses.filter((s) => !s.is_archived)}
			managementMode={canManage}
			onEdit={(s) => (editingStatus = s)}
			onDelete={(s) => (deletingStatus = s)}
			onReorder={handleReorder}
		/>

		{@const archived = statusSet.statuses.filter((s) => s.is_archived)}
		{#if archived.length > 0}
			<details class="mt-2">
				<summary class="cursor-pointer text-xs text-gray-500">
					{archived.length} archived status{archived.length === 1 ? '' : 'es'}
				</summary>
				<StatusReorderList
					statuses={archived}
					managementMode={false}
					onEdit={() => {}}
					onDelete={() => {}}
					onReorder={() => {}}
				/>
			</details>
		{/if}
	{/if}

	{#if creatingNew && canManage}
		<StatusEditorRow
			status={emptyNew}
			onSave={handleCreate}
			onCancel={() => (creatingNew = false)}
		/>
	{/if}
</div>

{#if deletingStatus}
	<StatusDeleteDialog
		status={deletingStatus}
		availableStatuses={statusSet?.statuses ?? []}
		open={true}
		onClose={() => (deletingStatus = null)}
		onConfirm={handleDelete}
	/>
{/if}
