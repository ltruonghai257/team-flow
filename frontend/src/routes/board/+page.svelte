<script lang="ts">
	import { onMount } from 'svelte';
	import { board, type BoardPost } from '$lib/apis/board';
	import { boardStore } from '$lib/stores/board';
	import { currentUser } from '$lib/stores/auth';
	import { toast } from 'svelte-sonner';
	import WeeklySummaryPanel from '$lib/components/board/WeeklySummaryPanel.svelte';
	import WeeklyPostComposer from '$lib/components/board/WeeklyPostComposer.svelte';
	import WeeklyPostCard from '$lib/components/board/WeeklyPostCard.svelte';
	import WeekNavigator from '$lib/components/board/WeekNavigator.svelte';

	let selectedYear: number | undefined;
	let selectedWeek: number | undefined;

	async function loadWeek() {
		boardStore.update((s) => ({ ...s, loading: true }));
		try {
			const payload = await board.getWeek({ year: selectedYear, week: selectedWeek });
			selectedYear = payload.selected_iso_year;
			selectedWeek = payload.selected_iso_week;
			boardStore.set({ payload, loading: false, saving: false, summarizing: false });
		} catch (e: any) {
			boardStore.update((s) => ({ ...s, loading: false }));
			toast.error(e.message ?? 'Failed to load the weekly board.');
		}
	}

	onMount(loadWeek);

	async function summarize() {
		if (!selectedYear || !selectedWeek) return;
		boardStore.update((s) => ({ ...s, summarizing: true }));
		try {
			await board.summarizeWeek({ year: selectedYear, week: selectedWeek });
			await loadWeek();
		} catch (e: any) {
			boardStore.update((s) => ({ ...s, summarizing: false }));
			toast.error(e.message ?? 'Failed to generate the weekly summary. Try again.');
		}
	}

	async function createPost(content: string) {
		try {
			await board.createPost({ content });
			toast.success('Weekly update posted');
			await loadWeek();
		} catch (e: any) {
			toast.error(e.message ?? 'Failed to post the weekly update. Try again.');
		}
	}

	async function updatePost(postId: number, content: string) {
		try {
			await board.updatePost(postId, { content });
			toast.success('Weekly update saved');
			await loadWeek();
		} catch (e: any) {
			toast.error(e.message ?? 'Failed to save the weekly update. Try again.');
		}
	}

	async function deletePost(postId: number) {
		try {
			await board.deletePost(postId);
			toast.success('Weekly update deleted');
			await loadWeek();
		} catch (e: any) {
			toast.error(e.message ?? 'Failed to delete the weekly update. Try again.');
		}
	}

	async function appendPost(postId: number, content: string) {
		try {
			await board.createAppend(postId, { content });
			toast.success('Follow-up posted');
			await loadWeek();
		} catch (e: any) {
			toast.error(e.message ?? 'Failed to post follow-up. Try again.');
		}
	}

	function yearWeekShift(year: number, week: number, delta: number) {
		const start = new Date(Date.UTC(year, 0, 1 + (week - 1) * 7));
		start.setUTCDate(start.getUTCDate() + delta * 7);
		const d = new Date(start);
		d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
		const y = d.getUTCFullYear();
		const yStart = new Date(Date.UTC(y, 0, 1));
		const w = Math.ceil((((d.getTime() - yStart.getTime()) / 86400000) + 1) / 7);
		return { year: y, week: w };
	}
</script>

<svelte:head><title>Weekly Board · TeamFlow</title></svelte:head>

<div class="p-4 md:p-6 max-w-5xl mx-auto space-y-6">
	<div>
		<h1 class="text-2xl font-semibold text-white">Weekly Board</h1>
		<p class="text-gray-400 text-sm mt-1">Team updates organized by ISO week, with an AI digest at the top</p>
	</div>

	{#if $boardStore.payload}
		<WeekNavigator
			weekOptions={$boardStore.payload.week_options}
			selectedYear={$boardStore.payload.selected_iso_year}
			selectedWeek={$boardStore.payload.selected_iso_week}
			on:prev={async () => {
				const next = yearWeekShift($boardStore.payload!.selected_iso_year, $boardStore.payload!.selected_iso_week, -1);
				selectedYear = next.year;
				selectedWeek = next.week;
				await loadWeek();
			}}
			on:current={async () => {
				selectedYear = undefined;
				selectedWeek = undefined;
				await loadWeek();
			}}
			on:next={async () => {
				const next = yearWeekShift($boardStore.payload!.selected_iso_year, $boardStore.payload!.selected_iso_week, 1);
				selectedYear = next.year;
				selectedWeek = next.week;
				await loadWeek();
			}}
			on:pick={async (e) => {
				selectedYear = e.detail.year;
				selectedWeek = e.detail.week;
				await loadWeek();
			}}
		/>

		<WeeklySummaryPanel
			summary={$boardStore.payload.summary}
			loading={$boardStore.summarizing}
			isCurrentWeek={$boardStore.payload.is_current_week}
			canSummarize={true}
			on:summarize={summarize}
		/>

		{#if $boardStore.payload.is_current_week}
			{#if !$boardStore.payload.posts.some((p) => p.author_id === $currentUser?.id)}
				<WeeklyPostComposer on:submit={(e) => createPost(e.detail.content)} />
			{/if}
		{:else}
			<div class="card">
				<p class="text-sm text-gray-400">Past weeks are read-only. Switch to the current week to post an update.</p>
			</div>
		{/if}

		{#if !$boardStore.payload.posts.length}
			<div class="card text-center py-12">
				{#if $boardStore.payload.is_current_week}
					<p class="text-gray-400 text-sm font-semibold">No weekly updates yet</p>
					<p class="text-gray-500 text-sm mt-1">Be the first to post an update for this week.</p>
				{:else}
					<p class="text-gray-400 text-sm font-semibold">No updates were posted for this week</p>
					<p class="text-gray-500 text-sm mt-1">Choose another week or return to the current week to add an update.</p>
				{/if}
			</div>
		{:else}
			<div class="space-y-4">
				{#each $boardStore.payload.posts as post (post.id)}
					<WeeklyPostCard
						{post}
						isOwner={post.author_id === $currentUser?.id}
						isCurrentWeek={$boardStore.payload.is_current_week}
						on:update={(e) => updatePost(e.detail.postId, e.detail.content)}
						on:delete={(e) => deletePost(e.detail.postId)}
						on:append={(e) => appendPost(e.detail.postId, e.detail.content)}
					/>
				{/each}
			</div>
		{/if}
	{:else if $boardStore.loading}
		<div class="flex items-center justify-center py-16">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{/if}
</div>
