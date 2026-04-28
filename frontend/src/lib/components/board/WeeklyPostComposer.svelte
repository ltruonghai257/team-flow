<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	export let title = "Write this week's update";
	export let disabled = false;
	export let initialValue = '';
	export let saving = false;

	let mode: 'write' | 'preview' = 'write';
	let content = initialValue;

	$: if (initialValue !== content && !content) content = initialValue;

	const dispatch = createEventDispatcher<{ submit: { content: string } }>();

	function previewHtml(text: string) {
		return DOMPurify.sanitize(marked.parse(text || '', { async: false }) as string);
	}
</script>

<section class="card">
	<h3 class="text-sm font-semibold text-gray-200 mb-3">{title}</h3>
	<div class="flex items-center gap-2 mb-3">
		<button class={`btn-secondary text-xs px-3 py-1.5 ${mode === 'write' ? 'bg-gray-700' : ''}`} on:click={() => (mode = 'write')}>Write</button>
		<button class={`btn-secondary text-xs px-3 py-1.5 ${mode === 'preview' ? 'bg-gray-700' : ''}`} on:click={() => (mode = 'preview')}>Preview</button>
	</div>

	{#if mode === 'write'}
		<textarea class="input min-h-[140px]" bind:value={content} disabled={disabled}></textarea>
	{:else}
		<div class="input min-h-[140px] prose prose-invert max-w-none">{@html previewHtml(content)}</div>
	{/if}

	<div class="flex justify-end mt-3">
		<button class="btn-primary" disabled={disabled || !content.trim() || saving} on:click={() => dispatch('submit', { content })}>
			{saving ? 'Saving...' : 'Post Update'}
		</button>
	</div>
</section>
