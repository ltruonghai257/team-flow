<script lang="ts">
	import { AlertTriangle, ArrowRight } from 'lucide-svelte';
	import type { CustomStatus, StatusTransitionPair } from '$lib/api';

	export let statuses: CustomStatus[] = [];
	export let transitions: StatusTransitionPair[] = [];

	$: statusById = new Map(statuses.map((status) => [status.id, status]));
	$: visibleTransitions = transitions
		.map((transition) => ({
			from: statusById.get(transition.from_status_id),
			to: statusById.get(transition.to_status_id),
		}))
		.filter((transition): transition is { from: CustomStatus; to: CustomStatus } =>
			Boolean(transition.from && transition.to)
		);
	$: rulesExist = visibleTransitions.length > 0;
	$: warnings = buildWarnings(statuses, visibleTransitions, rulesExist);

	function buildWarnings(
		activeStatuses: CustomStatus[],
		edges: { from: CustomStatus; to: CustomStatus }[],
		hasRules: boolean
	) {
		if (!hasRules) return [];
		const outgoing = new Map<number, number[]>();
		for (const edge of edges) {
			outgoing.set(edge.from.id, [...(outgoing.get(edge.from.id) ?? []), edge.to.id]);
		}

		const nextWarnings: string[] = [];
		const statusesWithoutOutgoing = activeStatuses.filter(
			(status) => !status.is_done && (outgoing.get(status.id) ?? []).length === 0
		);
		if (statusesWithoutOutgoing.length > 0) {
			nextWarnings.push(
				`No outgoing transitions from ${statusesWithoutOutgoing.map((status) => status.name).join(', ')}.`
			);
		}

		const doneIds = new Set(activeStatuses.filter((status) => status.is_done).map((status) => status.id));
		if (doneIds.size > 0) {
			const blockedFromDone = activeStatuses.filter(
				(status) => !status.is_done && !canReachDone(status.id, doneIds, outgoing)
			);
			if (blockedFromDone.length > 0) {
				nextWarnings.push(
					`No path to a done status from ${blockedFromDone.map((status) => status.name).join(', ')}.`
				);
			}
		}

		return nextWarnings;
	}

	function canReachDone(startId: number, doneIds: Set<number>, outgoing: Map<number, number[]>) {
		const seen = new Set<number>();
		const queue = [startId];
		while (queue.length > 0) {
			const current = queue.shift();
			if (!current || seen.has(current)) continue;
			if (doneIds.has(current)) return true;
			seen.add(current);
			queue.push(...(outgoing.get(current) ?? []));
		}
		return false;
	}
</script>

<div class="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(220px,0.7fr)]">
	<section class="space-y-2">
		<h4 class="text-sm font-semibold text-gray-300">Preview</h4>
		{#if visibleTransitions.length === 0}
			<p class="rounded border border-gray-800 bg-gray-900/70 p-3 text-xs text-gray-500">
				Save or select transitions to preview the workflow.
			</p>
		{:else}
			<div class="space-y-3 rounded border border-gray-800 bg-gray-950/40 p-3">
				<div class="flex flex-wrap gap-2">
					{#each statuses as status (status.id)}
						<span
							class="inline-flex max-w-40 items-center gap-1 rounded border border-gray-800 bg-gray-900 px-2 py-1 text-xs text-gray-300"
							title={status.name}
						>
							<span
								class="h-2.5 w-2.5 flex-shrink-0 rounded-full"
								style="background-color: {status.color};"
							></span>
							<span class="truncate">{status.name}</span>
						</span>
					{/each}
				</div>
				<div class="flex max-h-44 flex-col gap-1 overflow-y-auto">
					{#each visibleTransitions as transition}
						<div class="flex min-w-0 items-center gap-2 rounded bg-gray-900/80 px-2 py-1 text-xs text-gray-300">
							<span class="flex min-w-0 flex-1 items-center gap-1" title={transition.from.name}>
								<span
									class="h-2 w-2 flex-shrink-0 rounded-full"
									style="background-color: {transition.from.color};"
								></span>
								<span class="truncate">{transition.from.name}</span>
							</span>
							<ArrowRight size={12} class="flex-shrink-0 text-gray-500" aria-hidden="true" />
							<span class="flex min-w-0 flex-1 items-center gap-1" title={transition.to.name}>
								<span
									class="h-2 w-2 flex-shrink-0 rounded-full"
									style="background-color: {transition.to.color};"
								></span>
								<span class="truncate">{transition.to.name}</span>
							</span>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</section>

	{#if warnings.length > 0}
		<section class="space-y-2 rounded border border-yellow-900/60 bg-yellow-950/20 p-3">
			<h4 class="flex items-center gap-1 text-sm font-semibold text-yellow-300">
				<AlertTriangle size={14} />
				Workflow warnings
			</h4>
			<ul class="space-y-1 text-xs text-yellow-100">
				{#each warnings as warning}
					<li class="truncate" title={warning}>{warning}</li>
				{/each}
			</ul>
		</section>
	{/if}
</div>
