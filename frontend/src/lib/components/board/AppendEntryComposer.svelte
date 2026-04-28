<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let saving = false;
	let content = '';

	const dispatch = createEventDispatcher<{ submit: { content: string } }>();
</script>

<div class="mt-3 p-3 border border-gray-800 rounded-lg bg-gray-900/40">
	<p class="text-xs text-gray-400 mb-2">Add a follow-up note</p>
	<textarea class="input min-h-[90px]" bind:value={content}></textarea>
	<div class="flex justify-end mt-2">
		<button class="btn-secondary text-xs px-3 py-1.5" disabled={!content.trim() || saving} on:click={() => dispatch('submit', { content })}>
			{saving ? 'Posting...' : 'Post follow-up'}
		</button>
	</div>
</div>
