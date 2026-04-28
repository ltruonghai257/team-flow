<script lang="ts">
	import { onMount } from 'svelte';
	import { updates as updatesApi } from '$lib/apis';
	import { updatesStore } from '$lib/stores/updates';
	import type { StandupPost } from '$lib/stores/updates';
	import { currentUser, isSupervisor } from '$lib/stores/auth';
	import { toast } from 'svelte-sonner';
	import { format } from 'date-fns';
	import { MessageSquare, Filter, Trash2 } from 'lucide-svelte';
	import StandupForm from '$lib/components/updates/StandupForm.svelte';
	import StandupCard from '$lib/components/updates/StandupCard.svelte';

	let templateFields: string[] = [];
	let fieldTypes: Record<string, string> = {};
	let loading = true;
	let filterAuthorId: number | null = null;
	let filterDate: string = '';

	// Derive unique authors from posts for the filter dropdown
	$: authorOptions = Array.from(
		new Map($updatesStore.posts.map((p) => [p.author_id, p.author?.full_name ?? String(p.author_id)])).entries()
	).map(([id, name]) => ({ id, name }));

	onMount(async () => {
		loading = true;
		try {
			const [tmpl, feedResult] = await Promise.all([updatesApi.getTemplate(), updatesApi.list()]);
			templateFields = tmpl.fields;
			fieldTypes = tmpl.field_types || {};
			updatesStore.set({
				posts: feedResult.posts,
				nextCursor: feedResult.next_cursor,
				loading: false,
				loadingMore: false,
				filterAuthorId: null,
				filterDate: null,
				fieldTypes: fieldTypes
			});
		} catch (e: any) {
			toast.error(e.message ?? 'Failed to load updates');
		} finally {
			loading = false;
		}
	});

	async function loadFeed(reset = true) {
		const cursor = reset ? null : $updatesStore.nextCursor;
		if (reset) {
			updatesStore.update((s) => ({ ...s, posts: [], nextCursor: null }));
		}
		updatesStore.update((s) => ({ ...s, [reset ? 'loading' : 'loadingMore']: true }));
		try {
			const res = await updatesApi.list({
				cursor,
				author_id: filterAuthorId,
				date: filterDate || null
			});
			updatesStore.update((s) => ({
				...s,
				posts: reset ? res.posts : [...s.posts, ...res.posts],
				nextCursor: res.next_cursor,
				loading: false,
				loadingMore: false
			}));
		} catch (e: any) {
			updatesStore.update((s) => ({ ...s, loading: false, loadingMore: false }));
			toast.error(e.message ?? 'Failed to load updates');
		}
	}

	function clearFilters() {
		filterAuthorId = null;
		filterDate = '';
		loadFeed(true);
	}

	function onPostSubmitted(e: CustomEvent<StandupPost>) {
		updatesStore.update((s) => ({ ...s, posts: [e.detail, ...s.posts] }));
	}

	function onPostUpdated(e: CustomEvent<StandupPost>) {
		updatesStore.update((s) => ({
			...s,
			posts: s.posts.map((p) => (p.id === e.detail.id ? e.detail : p))
		}));
	}

	function onPostDeleted(e: CustomEvent<number>) {
		updatesStore.update((s) => ({
			...s,
			posts: s.posts.filter((p) => p.id !== e.detail)
		}));
	}

	// Supervisor template editor state
	let editableFields: string[] = [];
	let editableFieldTypes: Record<string, string> = {};
	let newFieldName = '';
	let savingTemplate = false;
	$: editableFields = [...templateFields];
	$: editableFieldTypes = { ...fieldTypes };

	function addField() {
		if (newFieldName.trim()) {
			editableFields = [...editableFields, newFieldName.trim()];
			editableFieldTypes[newFieldName.trim()] = 'text'; // Default to text
			newFieldName = '';
		}
	}

	function removeField(i: number) {
		const fieldName = editableFields[i];
		editableFields = editableFields.filter((_, idx) => idx !== i);
		delete editableFieldTypes[fieldName];
	}

	async function saveTemplate() {
		savingTemplate = true;
		try {
			await updatesApi.putTemplate({ fields: editableFields, field_types: editableFieldTypes });
			templateFields = [...editableFields];
			fieldTypes = { ...editableFieldTypes };
			updatesStore.update(s => ({ ...s, fieldTypes: fieldTypes }));
			toast.success('Template saved');
		} catch (e: any) {
			toast.error('Failed to save template. Try again.');
		} finally {
			savingTemplate = false;
		}
	}
</script>

<svelte:head><title>Updates · TeamFlow</title></svelte:head>

<div class="p-4 md:p-6 max-w-4xl mx-auto">
	<!-- Page header -->
	<div class="mb-6">
		<h1 class="text-2xl font-semibold text-white">Updates</h1>
		<p class="text-gray-400 text-sm mt-1">Team standup feed</p>
	</div>

	<!-- StandupForm panel -->
	<div class="mb-6">
		<StandupForm {templateFields} {fieldTypes} on:submitted={onPostSubmitted} />
	</div>

	<!-- Supervisor template editor -->
	{#if $isSupervisor}
		<div class="card mb-6">
			<p class="text-sm font-semibold text-gray-400 mb-4">Configure standup template</p>
			{#each editableFields as field, i}
				<div class="flex items-center gap-2 mb-2">
					<input class="input flex-1 text-sm" bind:value={editableFields[i]} />
					<select class="input w-32 text-sm" bind:value={editableFieldTypes[field]}>
						<option value="text">Text</option>
						<option value="datetime">Date/Time</option>
						<option value="richtext">Rich Text</option>
					</select>
					<button class="btn-secondary p-2" on:click={() => removeField(i)} title="Remove field" aria-label="Remove field">
						<Trash2 size={14} />
					</button>
				</div>
			{/each}
			<div class="flex items-center gap-2 mt-2">
				<input class="input flex-1 text-sm" bind:value={newFieldName} placeholder="New field name" />
				<button class="btn-secondary text-sm px-3 py-2" on:click={addField}>Add field</button>
			</div>
			<div class="flex justify-end mt-4">
				<button class="btn-primary" on:click={saveTemplate} disabled={savingTemplate}>Save template</button>
			</div>
		</div>
	{/if}

	<!-- Filter bar -->
	<div class="flex items-center gap-3 mb-4 flex-wrap">
		<select class="input w-auto text-sm" bind:value={filterAuthorId} on:change={() => loadFeed(true)}>
			<option value={null}>All members</option>
			{#each authorOptions as opt}
				<option value={opt.id}>{opt.name}</option>
			{/each}
		</select>
		<input type="date" class="input w-auto text-sm" bind:value={filterDate} on:change={() => loadFeed(true)} />
		{#if filterAuthorId || filterDate}
			<button class="btn-secondary text-xs px-3 py-2" on:click={clearFilters}>Clear filters</button>
		{/if}
	</div>

	<!-- Feed -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if $updatesStore.posts.length === 0}
		<div class="text-center py-12">
			{#if filterAuthorId || filterDate}
				<p class="text-gray-500 text-sm">No posts match the selected filters.</p>
			{:else}
				<p class="text-gray-400 text-sm font-semibold">No standup posts yet</p>
				<p class="text-gray-500 text-sm mt-1">Be the first to post a standup update for your team.</p>
			{/if}
		</div>
	{:else}
		<div class="space-y-4">
			{#each $updatesStore.posts as post (post.id)}
				<StandupCard {post} {fieldTypes} on:updated={onPostUpdated} on:deleted={onPostDeleted} />
			{/each}
		</div>

		<!-- Load more -->
		{#if $updatesStore.nextCursor !== null}
			<div class="flex justify-center mt-6">
				<button class="btn-secondary" on:click={() => loadFeed(false)} disabled={$updatesStore.loadingMore}>
					{#if $updatesStore.loadingMore}
						<span class="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin inline-block mr-2"></span>
						Loading...
					{:else}
						Load more
					{/if}
				</button>
			</div>
		{/if}
	{/if}
</div>
