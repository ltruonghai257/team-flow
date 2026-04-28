<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { format } from 'date-fns';
	import { Clock, Link2, Pencil, Tag, Trash2, Users } from 'lucide-svelte';
	import type { KnowledgeSession } from '$lib/apis/knowledge-sessions';

	export let session: KnowledgeSession;
	export let canManage = false;
	export let compact = false;
	export let selected = false;

	const dispatch = createEventDispatcher<{
		select: KnowledgeSession;
		edit: KnowledgeSession;
		delete: KnowledgeSession;
	}>();

	const SESSION_TYPE_META: Record<
		KnowledgeSession['session_type'],
		{ label: string; classes: string }
	> = {
		presentation: { label: 'Presentation', classes: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30' },
		demo: { label: 'Demo', classes: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30' },
		workshop: { label: 'Workshop', classes: 'bg-amber-500/15 text-amber-300 border-amber-500/30' },
		qa: { label: 'Q&A', classes: 'bg-rose-500/15 text-rose-300 border-rose-500/30' }
	};

	$: presenterName = session.presenter?.full_name ?? session.presenter?.username ?? 'Unassigned';
	$: scopeLabel = session.sub_team_id ? 'Team Session' : 'Org-wide';
	$: scopeClasses = session.sub_team_id
		? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
		: 'bg-blue-500/15 text-blue-300 border-blue-500/30';
	$: sessionTypeMeta = SESSION_TYPE_META[session.session_type];
	$: timeLabel = `${format(new Date(session.start_time), 'MMM d, p')} · ${formatDuration(
		session.duration_minutes
	)}`;

	function formatDuration(minutes: number) {
		if (minutes >= 60) {
			const hours = Math.floor(minutes / 60);
			const remainder = minutes % 60;
			if (!remainder) return `${hours}h`;
			return `${hours}h ${remainder}m`;
		}
		return `${minutes}m`;
	}
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_to_interactive_role -->
<article
	class="rounded-lg border bg-gray-800 border-gray-700 p-3 transition-colors hover:bg-gray-800/90 hover:border-gray-600 {selected ? 'ring-1 ring-primary-500/40 border-primary-500/40' : ''} {compact ? 'shadow-none' : ''}"
	role="button"
	tabindex="0"
	on:click={() => dispatch('select', session)}
	on:keydown={(event) => {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			dispatch('select', session);
		}
	}}
>
	<div class="flex items-start justify-between gap-3">
		<div class="min-w-0 flex-1">
			<h3 class="text-sm font-semibold text-gray-100 truncate">{session.topic}</h3>
			<p class="mt-1 flex items-center gap-1.5 text-xs text-gray-400">
				<Clock size={11} class="shrink-0" />
				<span>{timeLabel}</span>
			</p>
			<p class="mt-1 flex items-center gap-1.5 text-xs text-gray-400">
				<Users size={11} class="shrink-0" />
				<span class="truncate">{presenterName}</span>
			</p>
		</div>
		{#if canManage}
			<div class="flex shrink-0 items-center gap-1">
				<button
					type="button"
					class="rounded p-1.5 text-gray-500 transition-colors hover:bg-gray-700 hover:text-gray-200"
					aria-label="Edit session"
					on:click|stopPropagation={() => dispatch('edit', session)}
				>
					<Pencil size={13} />
				</button>
				<button
					type="button"
					class="rounded p-1.5 text-gray-500 transition-colors hover:bg-gray-700 hover:text-red-400"
					aria-label="Delete session"
					on:click|stopPropagation={() => dispatch('delete', session)}
				>
					<Trash2 size={13} />
				</button>
			</div>
		{/if}
	</div>

	<div class="mt-2 flex flex-wrap items-center gap-2">
		<span class={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium ${scopeClasses}`}>
			{scopeLabel}
		</span>
		<span class={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium ${sessionTypeMeta.classes}`}>
			{sessionTypeMeta.label}
		</span>
	</div>

	{#if session.tags?.length > 0}
		<div class="mt-2 flex flex-wrap items-center gap-1.5">
			<Tag size={11} class="text-gray-500" />
			{#each session.tags as tag}
				<span class="rounded-full border border-primary-500/25 bg-primary-600/15 px-2.5 py-1 text-xs text-primary-200">
					{tag}
				</span>
			{/each}
		</div>
	{/if}

	{#if !compact && session.description}
		<p class="mt-2 line-clamp-2 text-sm leading-relaxed text-gray-400">
			{session.description}
		</p>
	{/if}

	{#if !compact && session.references}
		<p class="mt-2 flex items-start gap-1.5 text-xs text-gray-500">
			<Link2 size={11} class="mt-0.5 shrink-0" />
			<span class="line-clamp-1">{session.references}</span>
		</p>
	{/if}
</article>
