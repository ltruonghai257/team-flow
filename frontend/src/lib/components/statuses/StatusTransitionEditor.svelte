<script lang="ts">
	import { Save, Wand2 } from 'lucide-svelte';
	import type {
		CustomStatus,
		StatusSet,
		StatusTransition,
		StatusTransitionPair,
	} from '$lib/api';

	export let statusSet: StatusSet | null = null;
	export let transitions: StatusTransition[] = [];
	export let canManage = false;
	export let onSave: (transitions: StatusTransitionPair[]) => Promise<void> | void = () => {};

	let selected = new Set<string>();
	let lastTransitionKey = '';
	let saving = false;
	let saveError = '';

	$: activeStatuses = (statusSet?.statuses ?? [])
		.filter((status: CustomStatus) => !status.is_archived)
		.sort((a: CustomStatus, b: CustomStatus) => a.position - b.position);
	$: transitionKey = transitions
		.map((transition) => `${transition.from_status_id}:${transition.to_status_id}`)
		.sort()
		.join('|');
	$: if (transitionKey !== lastTransitionKey) {
		selected = new Set(
			transitions.map((transition) => edgeKey(transition.from_status_id, transition.to_status_id))
		);
		lastTransitionKey = transitionKey;
	}
	$: selectedPairs = Array.from(selected).map((key) => {
		const [from_status_id, to_status_id] = key.split(':').map(Number);
		return { from_status_id, to_status_id };
	});

	function edgeKey(fromStatusId: number, toStatusId: number) {
		return `${fromStatusId}:${toStatusId}`;
	}

	function hasEdge(fromStatusId: number, toStatusId: number) {
		return selected.has(edgeKey(fromStatusId, toStatusId));
	}

	function toggleEdge(fromStatusId: number, toStatusId: number) {
		if (!canManage || fromStatusId === toStatusId) return;
		const next = new Set(selected);
		const key = edgeKey(fromStatusId, toStatusId);
		if (next.has(key)) {
			next.delete(key);
		} else {
			next.add(key);
		}
		selected = next;
	}

	function generateLinearFlow() {
		if (!canManage) return;
		const next = new Set<string>();
		for (let i = 0; i < activeStatuses.length - 1; i += 1) {
			next.add(edgeKey(activeStatuses[i].id, activeStatuses[i + 1].id));
		}
		selected = next;
	}

	async function saveTransitions() {
		if (!canManage) return;
		saving = true;
		saveError = '';
		try {
			await onSave(selectedPairs);
		} catch (e: unknown) {
			saveError = e instanceof Error ? e.message : 'Failed to save transition rules';
		} finally {
			saving = false;
		}
	}
</script>

<section class="space-y-3 border-t border-gray-800 pt-3">
	<div class="flex flex-wrap items-center justify-between gap-2">
		<div>
			<h3 class="text-sm font-semibold text-gray-300">Transition rules</h3>
			<p class="text-xs text-gray-500">
				Empty rules allow tasks to move freely. Add rules to restrict moves.
			</p>
		</div>
		{#if canManage}
			<div class="flex flex-wrap gap-2">
				<button
					type="button"
					on:click={generateLinearFlow}
					disabled={activeStatuses.length < 2 || saving}
					class="flex items-center gap-1 rounded bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
				>
					<Wand2 size={12} />
					Generate linear flow
				</button>
				<button
					type="button"
					on:click={saveTransitions}
					disabled={saving}
					class="flex items-center gap-1 rounded bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
				>
					<Save size={12} />
					{saving ? 'Saving...' : 'Save transitions'}
				</button>
			</div>
		{/if}
	</div>

	{#if transitions.length === 0}
		<div class="rounded border border-gray-800 bg-gray-900/70 p-3">
			<p class="text-sm font-medium text-gray-300">No transition rules</p>
			<p class="mt-1 text-xs text-gray-500">
				Tasks can move between any active statuses until rules are saved.
			</p>
		</div>
	{/if}

	{#if saveError}
		<p class="text-xs text-red-400">{saveError}</p>
	{/if}

	{#if activeStatuses.length === 0}
		<p class="text-xs text-gray-500">No active statuses available.</p>
	{:else}
		<div class="overflow-x-auto rounded border border-gray-800">
			<table class="min-w-max border-collapse text-xs">
				<thead class="bg-gray-900">
					<tr>
						<th class="sticky left-0 z-10 min-w-32 bg-gray-900 px-2 py-2 text-left font-medium text-gray-400">
							From / To
						</th>
						{#each activeStatuses as toStatus (toStatus.id)}
							<th class="min-w-24 max-w-32 px-2 py-2 text-left font-medium text-gray-400">
								<span class="flex items-center gap-1 truncate" title={toStatus.name}>
									<span
										class="h-2.5 w-2.5 flex-shrink-0 rounded-full"
										style="background-color: {toStatus.color};"
									></span>
									<span class="truncate">{toStatus.name}</span>
								</span>
							</th>
						{/each}
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-800">
					{#each activeStatuses as fromStatus (fromStatus.id)}
						<tr class="bg-gray-950/40">
							<th class="sticky left-0 z-10 min-w-32 bg-gray-950 px-2 py-2 text-left font-medium text-gray-300">
								<span class="flex items-center gap-1 truncate" title={fromStatus.name}>
									<span
										class="h-2.5 w-2.5 flex-shrink-0 rounded-full"
										style="background-color: {fromStatus.color};"
									></span>
									<span class="truncate">{fromStatus.name}</span>
								</span>
							</th>
							{#each activeStatuses as toStatus (toStatus.id)}
								<td class="h-9 min-w-10 border-l border-gray-800 px-2 py-1 text-center">
									{#if fromStatus.id === toStatus.id}
										<span class="inline-flex h-8 min-w-9 items-center justify-center rounded bg-gray-800/60 text-gray-500">
											-
										</span>
									{:else}
										<label
											class="inline-flex h-8 min-w-9 items-center justify-center rounded border border-gray-700 bg-gray-900 text-gray-400 hover:border-gray-500 {hasEdge(
												fromStatus.id,
												toStatus.id
											)
												? 'border-green-700 bg-green-950 text-green-300'
												: ''} {canManage ? 'cursor-pointer' : 'cursor-default opacity-70'}"
										>
											<input
												type="checkbox"
												class="sr-only"
												checked={hasEdge(fromStatus.id, toStatus.id)}
												disabled={!canManage}
												aria-label="Allow {fromStatus.name} to {toStatus.name}"
												on:change={() => toggleEdge(fromStatus.id, toStatus.id)}
											/>
											{hasEdge(fromStatus.id, toStatus.id) ? '✓' : ''}
										</label>
									{/if}
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</section>
