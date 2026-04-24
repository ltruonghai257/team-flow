<script lang="ts">
	import { formatDate, isOverdue, priorityColors, taskTypeColors, taskTypeLabels, initials } from '$lib/utils';
	import { Pencil, Sparkles, Bug, CheckSquare, Wrench } from 'lucide-svelte';

	export let task: any;
	export let onEdit: (t: any) => void = () => {};

	const taskTypeIcons: Record<string, any> = {
		feature: Sparkles,
		bug: Bug,
		task: CheckSquare,
		improvement: Wrench
	};

	function taskTypeValue(t: any) {
		return t.type || 'task';
	}
</script>

<div class="bg-gray-800/80 hover:bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-sm cursor-grab active:cursor-grabbing transition-colors group">
	<div class="flex items-start justify-between gap-2">
		<p class="text-sm font-medium text-gray-100 leading-snug flex-1">{task.title}</p>
		<button
			on:click|stopPropagation={() => onEdit(task)}
			class="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-gray-200 transition-opacity flex-shrink-0"
			title="Edit task"
		>
			<Pencil size={12} />
		</button>
	</div>

	{#if task.description}
		<p class="text-xs text-gray-500 mt-1 line-clamp-2">{task.description}</p>
	{/if}

	<div class="flex items-center gap-1.5 mt-2.5 flex-wrap">
		<span class="badge {taskTypeColors[taskTypeValue(task)]} text-[10px] px-1.5 py-0.5 flex items-center gap-1">
			<svelte:component this={taskTypeIcons[taskTypeValue(task)] || CheckSquare} size={10} />
			{taskTypeLabels[taskTypeValue(task)]}
		</span>
		<span class="badge {priorityColors[task.priority]} text-[10px] px-1.5 py-0.5">{task.priority}</span>
		{#if task.due_date}
			<span
				class="text-[11px] {isOverdue(task.due_date) && task.status !== 'done'
					? 'text-red-400'
					: 'text-gray-500'}"
			>
				{formatDate(task.due_date)}
			</span>
		{/if}
		{#if task.tags}
			{#each task.tags.split(',').slice(0, 2) as tag}
				<span class="badge bg-gray-700 text-gray-400 text-[10px] px-1.5 py-0.5">{tag.trim()}</span>
			{/each}
		{/if}
	</div>

	{#if task.assignee}
		<div class="flex items-center gap-1.5 mt-2 pt-2 border-t border-gray-700/50">
			<div
				class="w-5 h-5 rounded-full bg-primary-700 flex items-center justify-center text-[10px] font-bold text-white"
			>
				{initials(task.assignee.full_name)}
			</div>
			<span class="text-[11px] text-gray-400 truncate">{task.assignee.full_name}</span>
		</div>
	{/if}
</div>
