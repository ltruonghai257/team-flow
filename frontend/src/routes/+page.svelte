<script lang="ts">
	import { onMount } from 'svelte';
	import { dashboard } from '$lib/apis';
	import { formatDate, statusColors, statusLabels, priorityColors, isOverdue, milestoneStatusColors } from '$lib/utils';
	import { CheckSquare, Clock, AlertTriangle, Users, TrendingUp, Flag } from 'lucide-svelte';

	let stats: any = null;
	let loading = true;

	onMount(async () => {
		try {
			stats = await dashboard.stats();
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head><title>Dashboard · TeamFlow</title></svelte:head>

<div class="p-4 md:p-6 max-w-7xl mx-auto">
	<div class="mb-6">
		<h1 class="text-2xl font-bold text-white">Dashboard</h1>
		<p class="text-gray-400 text-sm mt-1">Overview of your projects and team</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if stats}
		<!-- Stat Cards -->
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
			<div class="card">
				<div class="flex items-center justify-between mb-3">
					<span class="text-gray-400 text-sm">Total Tasks</span>
					<CheckSquare class="text-primary-400" size={18} />
				</div>
				<p class="text-3xl font-bold text-white">{stats.total_tasks}</p>
				<p class="text-xs text-gray-500 mt-1">{stats.todo_tasks} to do</p>
			</div>
			<div class="card">
				<div class="flex items-center justify-between mb-3">
					<span class="text-gray-400 text-sm">In Progress</span>
					<TrendingUp class="text-blue-400" size={18} />
				</div>
				<p class="text-3xl font-bold text-white">{stats.in_progress_tasks}</p>
				<p class="text-xs text-gray-500 mt-1">{stats.done_tasks} completed</p>
			</div>
			<div class="card">
				<div class="flex items-center justify-between mb-3">
					<span class="text-gray-400 text-sm">Overdue</span>
					<AlertTriangle class="text-red-400" size={18} />
				</div>
				<p class="text-3xl font-bold {stats.overdue_tasks > 0 ? 'text-red-400' : 'text-white'}">{stats.overdue_tasks}</p>
				<p class="text-xs text-gray-500 mt-1">need attention</p>
			</div>
			<div class="card">
				<div class="flex items-center justify-between mb-3">
					<span class="text-gray-400 text-sm">Team Members</span>
					<Users class="text-green-400" size={18} />
				</div>
				<p class="text-3xl font-bold text-white">{stats.total_team_members}</p>
				<p class="text-xs text-gray-500 mt-1">active</p>
			</div>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Upcoming Milestones -->
			<div class="card">
				<div class="flex items-center gap-2 mb-4">
					<Flag class="text-primary-400" size={18} />
					<h2 class="font-semibold text-white">Upcoming Milestones</h2>
				</div>
				{#if stats.upcoming_milestones.length === 0}
					<p class="text-gray-500 text-sm py-4 text-center">No upcoming milestones in the next 30 days</p>
				{:else}
					<div class="space-y-3">
						{#each stats.upcoming_milestones as m}
							<a href="/milestones" class="flex items-start justify-between p-3 rounded-lg bg-gray-800 hover:bg-gray-750 transition-colors group">
								<div class="flex-1 min-w-0">
									<p class="text-sm font-medium text-gray-200 truncate">{m.title}</p>
									<p class="text-xs text-gray-500 mt-0.5">Due {formatDate(m.due_date)}</p>
								</div>
								<span class="badge ml-3 flex-shrink-0 {milestoneStatusColors[m.status]}">{m.status.replace('_', ' ')}</span>
							</a>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Recent Tasks -->
			<div class="card">
				<div class="flex items-center gap-2 mb-4">
					<Clock class="text-primary-400" size={18} />
					<h2 class="font-semibold text-white">Recent Tasks</h2>
				</div>
				{#if stats.recent_tasks.length === 0}
					<p class="text-gray-500 text-sm py-4 text-center">No tasks yet</p>
				{:else}
					<div class="space-y-2">
						{#each stats.recent_tasks as t}
							<a href="/tasks" class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-800 transition-colors group">
								<div class="flex-1 min-w-0">
									<p class="text-sm text-gray-200 truncate {t.status === 'done' ? 'line-through text-gray-500' : ''}">{t.title}</p>
									{#if t.due_date}
										<p class="text-xs mt-0.5 {isOverdue(t.due_date) && t.status !== 'done' ? 'text-red-400' : 'text-gray-500'}">
											Due {formatDate(t.due_date)}
										</p>
									{/if}
								</div>
								<div class="flex items-center gap-2 flex-shrink-0">
									<span class="badge {priorityColors[t.priority]}">{t.priority}</span>
									<span class="badge {statusColors[t.status]}">{statusLabels[t.status]}</span>
								</div>
							</a>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
