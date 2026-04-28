<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { currentUser } from '$lib/stores/auth';
	import { updates } from '$lib/apis';
	import type { StandupPost } from '$lib/stores/updates';
	import SnapshotPanel from './SnapshotPanel.svelte';
	import { toast } from 'svelte-sonner';
	import { format, parseISO } from 'date-fns';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	export let post: StandupPost;
	export let fieldTypes: Record<string, string> = {};

	const dispatch = createEventDispatcher();

	let mode: 'read' | 'editing' | 'deleting' | 'saving' | 'confirming-delete' = 'read';
	let editValues: Record<string, string> = {};

	function renderMarkdown(text: string): string {
		if (!text) return '';
		const html = marked.parse(text, { async: false }) as string;
		return DOMPurify.sanitize(html);
	}

	function startEdit() {
		editValues = { ...post.field_values };
		mode = 'editing';
	}

	async function saveEdit() {
		mode = 'saving';
		try {
			const updatedPost = await updates.update(post.id, { field_values: editValues });
			dispatch('updated', updatedPost);
			toast.success('Update saved');
			mode = 'read';
		} catch (e: any) {
			toast.error('Failed to save. Try again.');
			mode = 'editing';
		}
	}

	async function confirmDelete() {
		try {
			await updates.delete(post.id);
			dispatch('deleted', post.id);
			toast.success('Post deleted');
			mode = 'read';
		} catch (e: any) {
			toast.error('Failed to delete. Try again.');
			mode = 'deleting';
		}
	}
</script>

<div class="card hover:border-gray-700 transition-colors">
	{#if mode === 'read'}
		<div class="flex items-start gap-3">
			<div class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-semibold text-gray-300 flex-shrink-0">
				{(post.author?.full_name ?? 'U').charAt(0).toUpperCase()}
			</div>
			<div class="flex-1 min-w-0">
				<p class="text-sm font-semibold text-gray-200">{post.author?.full_name ?? 'Unknown'}</p>
				<p class="text-xs text-gray-500">{format(new Date(post.created_at), 'EEE MMM d, yyyy · HH:mm')}</p>
			</div>
		</div>

		{#each Object.entries(post.field_values).filter(([, v]) => v.trim()) as [fieldName, fieldValue]}
			<div class="space-y-1 mt-3">
				<p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">{fieldName}</p>
				{#if fieldTypes[fieldName] === 'datetime'}
					<p class="text-sm text-gray-300">{format(parseISO(fieldValue), 'PPp')}</p>
				{:else if fieldTypes[fieldName] === 'richtext'}
					<div class="text-sm text-gray-300 prose prose-invert max-w-none">
						{@html renderMarkdown(fieldValue)}
					</div>
				{:else}
					<p class="text-sm text-gray-300 whitespace-pre-wrap">{fieldValue}</p>
				{/if}
			</div>
		{/each}

		<SnapshotPanel tasks={post.task_snapshot} />

		{#if $currentUser?.id === post.author_id}
			<div class="flex gap-2 pt-1">
				<button class="btn-secondary text-xs px-3 py-2" on:click={startEdit}>Edit post</button>
				<button class="btn-secondary text-xs px-3 py-2" on:click={() => (mode = 'deleting')}>Delete post</button>
			</div>
		{/if}
	{:else if mode === 'deleting'}
		<div class="flex items-start gap-3">
			<div class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-semibold text-gray-300 flex-shrink-0">
				{(post.author?.full_name ?? 'U').charAt(0).toUpperCase()}
			</div>
			<div class="flex-1 min-w-0">
				<p class="text-sm font-semibold text-gray-200">{post.author?.full_name ?? 'Unknown'}</p>
				<p class="text-xs text-gray-500">{format(new Date(post.created_at), 'EEE MMM d, yyyy · HH:mm')}</p>
			</div>
		</div>

		{#each Object.entries(post.field_values).filter(([, v]) => v.trim()) as [fieldName, fieldValue]}
			<div class="space-y-1 mt-3">
				<p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">{fieldName}</p>
				{#if fieldTypes[fieldName] === 'datetime'}
					<p class="text-sm text-gray-300">{format(parseISO(fieldValue), 'PPp')}</p>
				{:else if fieldTypes[fieldName] === 'richtext'}
					<div class="text-sm text-gray-300 prose prose-invert max-w-none">
						{@html renderMarkdown(fieldValue)}
					</div>
				{:else}
					<p class="text-sm text-gray-300 whitespace-pre-wrap">{fieldValue}</p>
				{/if}
			</div>
		{/each}

		<div class="flex items-center gap-2 pt-1">
			<span class="text-xs text-gray-400">Delete this post?</span>
			<button class="btn-danger text-xs px-3 py-2" on:click={confirmDelete}>Yes, delete</button>
			<button class="btn-secondary text-xs px-3 py-2" on:click={() => (mode = 'read')}>Keep post</button>
		</div>
	{:else if mode === 'editing' || mode === 'saving'}
		<div class="flex items-start gap-3">
			<div class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-semibold text-gray-300 flex-shrink-0">
				{(post.author?.full_name ?? 'U').charAt(0).toUpperCase()}
			</div>
			<div class="flex-1 min-w-0">
				<p class="text-sm font-semibold text-gray-200">{post.author?.full_name ?? 'Unknown'}</p>
				<p class="text-xs text-gray-500">{format(new Date(post.created_at), 'EEE MMM d, yyyy · HH:mm')}</p>
			</div>
		</div>

		{#each Object.keys(post.field_values) as fieldName}
			<div class="space-y-1 mt-3">
				<label class="text-xs font-semibold text-gray-500 uppercase tracking-wide" for="edit-{fieldName}">{fieldName}</label>
				{#if fieldTypes[fieldName] === 'datetime'}
					<input id="edit-{fieldName}" type="datetime-local" class="input" bind:value={editValues[fieldName]} />
				{:else if fieldTypes[fieldName] === 'richtext'}
					<div class="space-y-2">
						<textarea id="edit-{fieldName}" class="input resize-none h-20" bind:value={editValues[fieldName]} placeholder="Write markdown here..."></textarea>
						{#if editValues[fieldName]}
							<div class="bg-gray-800 border border-gray-700 rounded p-3 text-sm text-gray-300 prose prose-invert max-w-none">
								{@html renderMarkdown(editValues[fieldName])}
							</div>
						{/if}
					</div>
				{:else}
					<textarea id="edit-{fieldName}" class="input resize-none h-20" bind:value={editValues[fieldName]}></textarea>
				{/if}
			</div>
		{/each}

		<div class="flex justify-end gap-2 pt-2">
			<button class="btn-secondary text-xs px-3 py-2" on:click={() => (mode = 'read')} disabled={mode === 'saving'}>
				Discard changes
			</button>
			<button class="btn-primary text-sm" on:click={saveEdit} disabled={mode === 'saving'}>
				{#if mode === 'saving'}
					<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin inline-block"></span>
					Saving...
				{:else}
					Save changes
				{/if}
			</button>
		</div>
	{/if}
</div>
