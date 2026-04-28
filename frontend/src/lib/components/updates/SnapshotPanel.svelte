<script lang="ts">
	import { ChevronDown, ChevronUp } from 'lucide-svelte';
	import { format } from 'date-fns';

	export let tasks: Array<{
		id: number;
		title: string;
		status: string;
		priority: string;
		due_date: string | null;
	}>;

	let expanded = false;

	function statusDotColor(status: string): string {
		switch (status) {
			case 'todo':
				return 'bg-gray-500';
			case 'in_progress':
				return 'bg-blue-400';
			case 'done':
				return 'bg-green-400';
			case 'blocked':
				return 'bg-red-400';
			default:
				return 'bg-gray-500';
		}
	}

	function priorityBadgeColor(priority: string): string {
		switch (priority) {
			case 'high':
				return 'text-red-400';
			case 'medium':
				return 'text-amber-400';
			case 'low':
				return 'text-gray-500';
			default:
				return 'text-gray-500';
		}
	}
</script>

<button
	class="flex items-center justify-between w-full text-xs font-semibold text-gray-500 hover:text-gray-300 transition-colors py-2 border-t border-gray-800 mt-3"
	on:click={() => (expanded = !expanded)}
	type="button"
>
	<span>Task snapshot ({tasks.length} tasks)</span>
	{#if expanded}
		<ChevronUp size={14} />
	{:else}
		<ChevronDown size={14} />
	{/if}
</button>

{#if expanded}
	<div class="mt-2 space-y-2">
		{#if tasks.length === 0}
			<p class="text-xs text-gray-600 py-1">No tasks assigned at time of post.</p>
		{:else}
			{#each tasks as task}
				<div class="flex items-center gap-3 text-xs py-1">
					<span class="w-2 h-2 rounded-full {statusDotColor(task.status)}"></span>
					<span class="flex-1 text-gray-300">{task.title}</span>
					<span class="text-gray-500">{task.status}</span>
					<span class="badge {priorityBadgeColor(task.priority)}">{task.priority}</span>
					<span class="text-gray-600">{task.due_date ? format(new Date(task.due_date), 'MMM d') : '—'}</span>
				</div>
			{/each}
		{/if}
	</div>
{/if}
