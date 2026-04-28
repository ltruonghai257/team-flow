<script lang="ts">
	import type { BoardPost } from '$lib/apis/board';
	import { createEventDispatcher } from 'svelte';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';
	import AppendEntryComposer from './AppendEntryComposer.svelte';

	export let post: BoardPost;
	export let isOwner = false;
	export let isCurrentWeek = false;

	let editing = false;
	let deleting = false;
	let appendMode = false;
	let editValue = post.content;

	const dispatch = createEventDispatcher<{
		update: { postId: number; content: string };
		delete: { postId: number };
		append: { postId: number; content: string };
	}>();

	function md(text: string) {
		return DOMPurify.sanitize(marked.parse(text || '', { async: false }) as string);
	}
</script>

<article class="card hover:border-gray-700 transition-colors">
	<div class="flex items-start gap-3">
		<div class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-semibold text-gray-300 flex-shrink-0">
			{(post.author?.full_name ?? 'U').charAt(0).toUpperCase()}
		</div>
		<div class="flex-1">
			<p class="text-sm font-semibold text-gray-200">{post.author?.full_name ?? 'Unknown'}</p>
			<p class="text-xs text-gray-500">{new Date(post.created_at).toLocaleString()}</p>
		</div>
	</div>

	{#if editing}
		<textarea class="input min-h-[120px] mt-3" bind:value={editValue}></textarea>
		<div class="flex gap-2 justify-end mt-2">
			<button class="btn-secondary text-xs px-3 py-1.5" on:click={() => (editing = false)}>Discard changes</button>
			<button class="btn-primary text-xs px-3 py-1.5" disabled={!editValue.trim()} on:click={() => dispatch('update', { postId: post.id, content: editValue })}>
				Save changes
			</button>
		</div>
	{:else}
		<div class="mt-3 prose prose-invert max-w-none text-sm">{@html md(post.content)}</div>
	{/if}

	{#if isOwner && isCurrentWeek && !editing}
		<div class="flex gap-2 mt-3">
			<button class="btn-secondary text-xs px-3 py-1.5" on:click={() => (editing = true)}>Edit</button>
			{#if deleting}
				<button class="btn-danger text-xs px-3 py-1.5" on:click={() => dispatch('delete', { postId: post.id })}>Yes, delete</button>
				<button class="btn-secondary text-xs px-3 py-1.5" on:click={() => (deleting = false)}>Keep it</button>
			{:else}
				<button class="btn-secondary text-xs px-3 py-1.5" on:click={() => (deleting = true)}>Delete</button>
			{/if}
			<button class="btn-secondary text-xs px-3 py-1.5" on:click={() => (appendMode = !appendMode)}>Add follow-up</button>
		</div>
	{/if}

	{#if appendMode}
		<AppendEntryComposer on:submit={(e) => { appendMode = false; dispatch('append', { postId: post.id, content: e.detail.content }); }} />
	{/if}

	{#if post.appends.length}
		<div class="mt-4 pl-4 border-l border-gray-700 space-y-3">
			{#each post.appends as append}
				<div>
					<p class="text-xs text-gray-500">{new Date(append.created_at).toLocaleString()}</p>
					<div class="text-sm text-gray-300 prose prose-invert max-w-none">{@html md(append.content)}</div>
				</div>
			{/each}
		</div>
	{/if}
</article>
