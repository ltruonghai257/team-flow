<script lang="ts">
	import {
		formatDate,
		isOverdue,
		statusColors,
		statusLabels,
		priorityColors,
		taskTypeColors,
		taskTypeLabels,
		initials
	} from '$lib/utils';
	import { Pencil, Trash2, Sparkles, Bug, CheckSquare, Wrench } from 'lucide-svelte';

	export let tasks: any[] = [];
	export let milestones: any[] = [];
	export let onStatusChange: (taskId: number, newStatus: string) => Promise<void> | void = () => {};
	export let onEdit: (task: any) => void = () => {};
	export let onDelete: (taskId: number) => void = () => {};

	const statusCycle: Record<string, string> = {
		todo: 'in_progress',
		in_progress: 'review',
		review: 'done',
		done: 'todo',
		blocked: 'todo'
	};
	const taskTypeIcons: Record<string, any> = {
		feature: Sparkles,
		bug: Bug,
		task: CheckSquare,
		improvement: Wrench
	};

	type Group = {
		id: number | null;
		title: string;
		due_date: string | null;
		tasks: any[];
	};

	$: groups = (() => {
		const map = new Map<number | null, Group>();
		for (const m of milestones) {
			map.set(m.id, { id: m.id, title: m.title, due_date: m.due_date, tasks: [] });
		}
		map.set(null, { id: null, title: 'Unassigned', due_date: null, tasks: [] });
		for (const t of tasks) {
			const key = t.milestone_id ?? null;
			if (!map.has(key)) {
				map.set(key, { id: key, title: 'Unassigned', due_date: null, tasks: [] });
			}
			map.get(key)!.tasks.push(t);
		}
		// Only return groups that have tasks (plus Unassigned even if empty is hidden)
		return Array.from(map.values()).filter((g) => g.tasks.length > 0);
	})();

	function progressFor(group: Group): number {
		if (group.tasks.length === 0) return 0;
		const done = group.tasks.filter((t) => t.status === 'done').length;
		return Math.round((done / group.tasks.length) * 100);
	}

	function priorityCounts(group: Group) {
		const counts: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0 };
		for (const t of group.tasks) counts[t.priority] = (counts[t.priority] ?? 0) + 1;
		return counts;
	}

	function taskTypeValue(t: any) {
		return t.type || 'task';
	}

	async function cycleStatus(task: any) {
		const next = statusCycle[task.status] ?? 'todo';
		await onStatusChange(task.id, next);
	}
</script>

<div class="space-y-6">
	{#each groups as group (group.id ?? 'unassigned')}
		<div class="card p-0 overflow-hidden">
			<div class="px-5 py-4 border-b border-gray-800 bg-gray-900/40">
				<div class="flex items-start justify-between gap-4 flex-wrap">
					<div>
						<h3 class="text-base font-semibold text-white">{group.title}</h3>
						<p class="text-xs text-gray-500 mt-0.5">
							{group.tasks.length} tasks
							{#if group.due_date} · Due {formatDate(group.due_date)}{/if}
						</p>
					</div>
					<div class="flex items-center gap-1.5 flex-wrap">
						{#each Object.entries(priorityCounts(group)) as [p, n]}
							{#if n > 0}
								<span class="badge {priorityColors[p]} text-[10px] px-1.5 py-0.5">{n} {p}</span>
							{/if}
						{/each}
					</div>
				</div>
				<!-- Progress bar -->
				<div class="mt-3">
					<div class="flex items-center justify-between text-xs text-gray-500 mb-1">
						<span>Progress</span>
						<span>{progressFor(group)}%</span>
					</div>
					<div class="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
						<div
							class="h-full bg-gradient-to-r from-primary-500 to-green-500 transition-all duration-300"
							style="width: {progressFor(group)}%"
						></div>
					</div>
				</div>
			</div>

			<div class="divide-y divide-gray-800/50">
				{#each group.tasks as t (t.id)}
					<div class="flex items-center gap-3 px-5 py-2.5 hover:bg-gray-900/40 transition-colors">
						<button
							on:click={() => cycleStatus(t)}
							class="badge {statusColors[t.status]} flex-shrink-0 cursor-pointer hover:ring-1 hover:ring-primary-500/50"
							title="Click to advance status"
						>
							{statusLabels[t.status]}
						</button>
						<div class="flex-1 min-w-0">
							<p class="text-sm {t.status === 'done' ? 'line-through text-gray-500' : 'text-gray-200'} truncate">
								{t.title}
							</p>
						</div>
						<span class="badge {taskTypeColors[taskTypeValue(t)]} text-[10px] flex items-center gap-1 flex-shrink-0">
							<svelte:component this={taskTypeIcons[taskTypeValue(t)] || CheckSquare} size={10} />
							{taskTypeLabels[taskTypeValue(t)]}
						</span>
						<span class="badge {priorityColors[t.priority]} text-[10px] flex-shrink-0">{t.priority}</span>
						{#if t.due_date}
							<span
								class="text-xs flex-shrink-0 {isOverdue(t.due_date) && t.status !== 'done'
									? 'text-red-400'
									: 'text-gray-500'}"
							>
								{formatDate(t.due_date)}
							</span>
						{/if}
						{#if t.assignee}
							<div
								class="w-6 h-6 rounded-full bg-primary-700 flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0"
								title={t.assignee.full_name}
							>
								{initials(t.assignee.full_name)}
							</div>
						{/if}
						<div class="flex items-center gap-1 flex-shrink-0">
							<button
								on:click={() => onEdit(t)}
								class="p-1 text-gray-500 hover:text-gray-200 hover:bg-gray-800 rounded"
							>
								<Pencil size={13} />
							</button>
							<button
								on:click={() => onDelete(t.id)}
								class="p-1 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded"
							>
								<Trash2 size={13} />
							</button>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/each}

	{#if groups.length === 0}
		<div class="card text-center py-12">
			<p class="text-gray-500">No tasks to display.</p>
		</div>
	{/if}
</div>
