<script lang="ts">
	import { Plus } from 'lucide-svelte';
	import { toast } from 'svelte-sonner';
	import { statusSets } from '$lib/api';
	import type { CustomStatus, StatusSet, StatusTransition, StatusTransitionPair } from '$lib/api';
	import StatusEditorRow from './StatusEditorRow.svelte';
	import StatusReorderList from './StatusReorderList.svelte';
	import StatusDeleteDialog from './StatusDeleteDialog.svelte';
	import StatusTransitionEditor from './StatusTransitionEditor.svelte';

	export let statusSet: StatusSet | null = null;
	export let scopeLabel = 'Sub-team default';
	export let canManage = false;
	export let isMixedProjectView = false;
	export let onRefresh: () => void = () => {};

	let editingStatus: CustomStatus | null = null;
	let deletingStatus: CustomStatus | null = null;
	let creatingNew = false;
	let savingOrder = false;
	let activeTab: 'statuses' | 'transitions' = 'statuses';
	let loadedTransitionSetId: number | null = null;
	let loadingTransitions = false;
	let transitions: StatusTransition[] = [];
	let transitionLoadError = '';

	$: if (isMixedProjectView) {
		activeTab = 'statuses';
	}
	$: if (statusSet?.id && !isMixedProjectView && statusSet.id !== loadedTransitionSetId) {
		void loadTransitions(statusSet.id);
	}
	$: if (!statusSet) {
		loadedTransitionSetId = null;
		transitions = [];
	}

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

	async function loadTransitions(statusSetId: number) {
		loadingTransitions = true;
		transitionLoadError = '';
		try {
			const loaded = await statusSets.getTransitions(statusSetId);
			if (statusSet?.id === statusSetId) {
				transitions = loaded;
				loadedTransitionSetId = statusSetId;
			}
		} catch (e: unknown) {
			transitionLoadError = e instanceof Error ? e.message : 'Failed to load transition rules';
			transitions = [];
			loadedTransitionSetId = statusSetId;
		} finally {
			loadingTransitions = false;
		}
	}

	async function handleSaveTransitions(nextTransitions: StatusTransitionPair[]) {
		if (!statusSet || !canManage) return;
		const saved = await statusSets.replaceTransitions(statusSet.id, nextTransitions);
		transitions = saved;
		loadedTransitionSetId = statusSet.id;
		toast.success('Transition rules saved');
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
		<div class="inline-flex rounded border border-gray-700 bg-gray-900 p-0.5 text-xs">
			<button
				type="button"
				on:click={() => (activeTab = 'statuses')}
				class="rounded px-2 py-1 {activeTab === 'statuses'
					? 'bg-indigo-600 text-white'
					: 'text-gray-400 hover:text-gray-200'}"
			>
				Statuses
			</button>
			<button
				type="button"
				on:click={() => (activeTab = 'transitions')}
				class="rounded px-2 py-1 {activeTab === 'transitions'
					? 'bg-indigo-600 text-white'
					: 'text-gray-400 hover:text-gray-200'}"
			>
				Transition rules
			</button>
		</div>

		{#if activeTab === 'statuses'}
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
		{:else}
			{#if loadingTransitions}
				<p class="text-xs text-gray-500">Loading transition rules...</p>
			{:else if transitionLoadError}
				<p class="text-xs text-red-400">{transitionLoadError}</p>
			{/if}
			<StatusTransitionEditor
				{statusSet}
				{transitions}
				{canManage}
				onSave={handleSaveTransitions}
			/>
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
