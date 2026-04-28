<script lang="ts">
	import type { BoardSummary } from '$lib/apis/board';
	import { createEventDispatcher } from 'svelte';

	export let summary: BoardSummary | null = null;
	export let loading = false;
	export let isCurrentWeek = false;
	export let canSummarize = false;

	const dispatch = createEventDispatcher<{ summarize: void }>();
</script>

<section class="card">
	<div class="flex items-center justify-between gap-3">
		<div>
			<h2 class="text-xl font-semibold text-white">AI Weekly Summary</h2>
			{#if summary}
				<p class="text-xs text-gray-500 mt-1">Updated {new Date(summary.generated_at).toLocaleString()}</p>
			{/if}
		</div>
		{#if isCurrentWeek}
			<button class="btn-primary text-sm" on:click={() => dispatch('summarize')} disabled={!canSummarize || loading}>
				{summary ? 'Refresh summary' : 'Summarize this week'}
			</button>
		{/if}
	</div>
	<div class="mt-4">
		{#if loading}
			<p class="text-sm text-gray-400">Loading summary...</p>
		{:else if summary}
			<p class="text-sm leading-relaxed text-gray-300 whitespace-pre-wrap">{summary.summary_text}</p>
		{:else}
			<p class="text-sm text-gray-400">No summary yet</p>
			<p class="text-xs text-gray-500 mt-1">Generate a summary for this week's updates when you're ready.</p>
		{/if}
	</div>
</section>
