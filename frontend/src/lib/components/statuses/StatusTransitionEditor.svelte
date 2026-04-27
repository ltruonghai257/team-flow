<script lang="ts">
	import { Info, Save, Wand2 } from 'lucide-svelte';
	import type {
		CustomStatus,
		StatusSet,
		StatusTransition,
		StatusTransitionPair,
	} from '$lib/types';
	import StatusTransitionPreview from './StatusTransitionPreview.svelte';

	export let statusSet: StatusSet | null = null;
	export let transitions: StatusTransition[] = [];
	export let canManage = false;
	export let onSave: (transitions: StatusTransitionPair[]) => Promise<void> | void = () => {};

	let selected = new Set<string>();
	let savedSelection = new Set<string>();
	let lastTransitionKey = '';
	let lastTouchedEdge: { fromStatusId: number; toStatusId: number; active: boolean } | null = null;
	let saving = false;
	let saveError = '';

	type EdgeState = 'empty' | 'saved' | 'draft-added' | 'draft-removed';

	$: activeStatuses = (statusSet?.statuses ?? [])
		.filter((status: CustomStatus) => !status.is_archived)
		.sort((a: CustomStatus, b: CustomStatus) => a.position - b.position);
	$: statusById = new Map(activeStatuses.map((status) => [status.id, status]));
	$: savedSelection = new Set(
		transitions.map((transition) => edgeKey(transition.from_status_id, transition.to_status_id))
	);
	$: transitionKey = transitions
		.map((transition) => `${transition.from_status_id}:${transition.to_status_id}`)
		.sort()
		.join('|');
	$: if (transitionKey !== lastTransitionKey) {
		selected = new Set(savedSelection);
		lastTransitionKey = transitionKey;
		lastTouchedEdge = null;
	}
	$: selectedPairs = Array.from(selected).map((key) => {
		const [from_status_id, to_status_id] = key.split(':').map(Number);
		return { from_status_id, to_status_id };
	});
	$: draftChangeCount = Array.from(new Set([...selected, ...savedSelection])).filter(
		(key) => selected.has(key) !== savedSelection.has(key)
	).length;

	function edgeKey(fromStatusId: number, toStatusId: number) {
		return `${fromStatusId}:${toStatusId}`;
	}

	function hasEdge(fromStatusId: number, toStatusId: number) {
		return selected.has(edgeKey(fromStatusId, toStatusId));
	}

	function getStatusName(statusId: number) {
		return statusById.get(statusId)?.name ?? 'Unknown status';
	}

	function edgeCellClass(state: EdgeState, enabled: boolean) {
		const base =
			'inline-flex h-8 min-w-9 items-center justify-center rounded border text-xs font-semibold transition-all duration-150';
		if (!enabled) {
			return `${base} border-gray-700 bg-gray-900 text-gray-400 opacity-70`;
		}
		if (state === 'draft-added' || state === 'draft-removed') {
			return `${base} border-transparent bg-transparent text-orange-100`;
		}
		if (state === 'saved') {
			return `${base} border-green-500 bg-green-500/15 text-green-200 shadow-[inset_0_0_0_1px_rgba(34,197,94,0.35)]`;
		}
		return `${base} border-gray-700 bg-gray-900 text-gray-400 hover:border-gray-500 hover:bg-gray-800/80`;
	}

	function transitionCellClass(state: EdgeState) {
		const base =
			'h-9 min-w-10 border-l p-0 text-center transition-colors duration-150';
		if (state === 'draft-added') {
			return `${base} border-orange-400/60 bg-orange-500/20 shadow-[inset_0_0_0_1px_rgba(251,146,60,0.45)]`;
		}
		if (state === 'draft-removed') {
			return `${base} border-orange-400/50 bg-orange-500/10 shadow-[inset_0_0_0_1px_rgba(251,146,60,0.32)]`;
		}
		return `${base} border-gray-800`;
	}

	function edgeState(fromStatusId: number, toStatusId: number): EdgeState {
		const key = edgeKey(fromStatusId, toStatusId);
		const current = selected.has(key);
		const saved = savedSelection.has(key);
		if (current && saved) return 'saved';
		if (current) return 'draft-added';
		if (saved) return 'draft-removed';
		return 'empty';
	}

	function isDraftEdge(fromStatusId: number, toStatusId: number) {
		const state = edgeState(fromStatusId, toStatusId);
		return state === 'draft-added' || state === 'draft-removed';
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
		lastTouchedEdge = {
			fromStatusId,
			toStatusId,
			active: next.has(key)
		};
	}

	function generateLinearFlow() {
		if (!canManage) return;
		const next = new Set<string>();
		for (let i = 0; i < activeStatuses.length - 1; i += 1) {
			next.add(edgeKey(activeStatuses[i].id, activeStatuses[i + 1].id));
		}
		selected = next;
		lastTouchedEdge = null;
	}

	function axisHighlightClass(statusId: number, axis: 'from' | 'to') {
		if (!lastTouchedEdge) return '';
		const highlighted =
			(axis === 'from' && lastTouchedEdge.fromStatusId === statusId) ||
			(axis === 'to' && lastTouchedEdge.toStatusId === statusId);
		return highlighted ? 'bg-green-500/10 text-green-200' : '';
	}

	function draftSelectionLabel() {
		if (draftChangeCount === 0) return 'No unsaved transition changes';
		if (!lastTouchedEdge) return `${draftChangeCount} unsaved transition changes`;
		const fromName = getStatusName(lastTouchedEdge.fromStatusId);
		const toName = getStatusName(lastTouchedEdge.toStatusId);
		const action = lastTouchedEdge.active ? 'Checked' : 'Unchecked';
		const suffix = draftChangeCount === 1 ? 'change' : 'changes';
		return `${draftChangeCount} unsaved ${suffix}; last ${action}: ${fromName} -> ${toName}`;
	}

	function isCheckedState(state: EdgeState) {
		return state === 'saved' || state === 'draft-added';
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
								<span
									class="flex items-center gap-1 truncate rounded px-1 py-0.5 transition-colors {axisHighlightClass(
										toStatus.id,
										'to'
									)}"
									title={toStatus.name}
								>
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
								<span
									class="flex items-center gap-1 truncate rounded px-1 py-0.5 transition-colors {axisHighlightClass(
										fromStatus.id,
										'from'
									)}"
									title={fromStatus.name}
								>
									<span
										class="h-2.5 w-2.5 flex-shrink-0 rounded-full"
										style="background-color: {fromStatus.color};"
									></span>
									<span class="truncate">{fromStatus.name}</span>
								</span>
							</th>
							{#each activeStatuses as toStatus (toStatus.id)}
								{@const state = edgeState(fromStatus.id, toStatus.id)}
								<td class={transitionCellClass(state)}>
									{#if fromStatus.id === toStatus.id}
										<span class="m-1 inline-flex h-8 min-w-9 items-center justify-center rounded bg-gray-800/60 text-gray-500">
											-
										</span>
									{:else}
										<label
											class="group flex h-full min-h-10 w-full items-center justify-center {canManage
												? 'cursor-pointer'
												: 'cursor-default'}"
										>
											<input
												type="checkbox"
												class="sr-only peer"
												checked={hasEdge(fromStatus.id, toStatus.id)}
												disabled={!canManage}
												aria-label="Allow {fromStatus.name} to {toStatus.name}"
												on:change={() => toggleEdge(fromStatus.id, toStatus.id)}
											/>
											<span
												class={edgeCellClass(state, canManage)}
											>
												{#if state === 'draft-added' || state === 'draft-removed'}
													<Info size={14} strokeWidth={2.5} />
												{:else if isCheckedState(state)}
													✓
												{/if}
											</span>
										</label>
									{/if}
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		{#if draftChangeCount > 0}
			<div
				class="flex flex-wrap items-center gap-2 rounded border border-orange-500/30 bg-orange-500/5 px-3 py-2 text-xs text-orange-100"
				aria-live="polite"
				role="status"
			>
				<span class="font-semibold uppercase tracking-wide text-orange-300">Draft changes</span>
				<span>{draftSelectionLabel()}</span>
			</div>
		{/if}

		<StatusTransitionPreview statuses={activeStatuses} transitions={selectedPairs} />
	{/if}
</section>
