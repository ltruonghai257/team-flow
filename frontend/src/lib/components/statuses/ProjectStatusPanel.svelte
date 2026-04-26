<script lang="ts">
	import { statusSets } from '$lib/api';
	import type { StatusSet } from '$lib/api';
	import StatusSetManager from './StatusSetManager.svelte';

	export let project: { id: number; name: string; sub_team_id: number | null };
	export let statusSet: StatusSet | null = null;
	export let onRefresh: () => void = () => {};
	export let canManage: boolean = false;

	let reverting = false;
	let revertError = '';
	let creating = false;

	$: hasOverride = statusSet?.scope === 'project' && statusSet?.project_id === project.id;

	async function handleCreateOverride() {
		creating = true;
		try {
			await statusSets.createProjectOverride(project.id);
			onRefresh();
		} finally {
			creating = false;
		}
	}

	async function handleRevert() {
		reverting = true;
		revertError = '';
		try {
			await statusSets.revertProjectOverride(project.id);
			onRefresh();
		} catch (e: unknown) {
			revertError = e instanceof Error ? e.message : 'Revert failed';
		} finally {
			reverting = false;
		}
	}
</script>

<div class="space-y-3">
	<div class="flex items-center justify-between">
		<div>
			<span class="text-xs font-medium text-gray-400">
				{hasOverride ? 'Custom for this project' : 'Inheriting sub-team defaults'}
			</span>
		</div>
		<div class="flex gap-2">
			{#if canManage}
				{#if !hasOverride}
					<button
						on:click={handleCreateOverride}
						disabled={creating}
						class="rounded bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-500 disabled:opacity-60"
					>
						{creating ? 'Creating…' : 'Create project override'}
					</button>
				{:else}
					<button
						on:click={handleRevert}
						disabled={reverting}
						class="rounded bg-gray-600 px-2 py-1 text-xs text-gray-200 hover:bg-gray-500 disabled:opacity-60"
					>
						{reverting ? 'Reverting…' : 'Revert to defaults'}
					</button>
				{/if}
			{/if}
		</div>
	</div>

	{#if revertError}
		<p class="text-xs text-red-400">{revertError}</p>
	{/if}

	{#if hasOverride && statusSet}
		<div class="text-xs text-gray-500 italic">
			Statuses matched by slug will be automatically mapped when reverting. Unmatched statuses
			with tasks require explicit mapping. Matched by slug: automatic.
		</div>
	{/if}

	<StatusSetManager
		{statusSet}
		scopeLabel={hasOverride ? `${project.name} override` : 'Sub-team default'}
		canManage={canManage && hasOverride}
		isMixedProjectView={false}
		{onRefresh}
	/>
</div>
