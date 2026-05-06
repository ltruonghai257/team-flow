<script lang="ts">
	import { onMount } from 'svelte';
	import { dashboard } from '$lib/apis';
	import type { DashboardPayload } from '$lib/apis/dashboard';
	import { timeAgo, priorityColors, statusColors, statusLabels, initials } from '$lib/utils';
	import { isManagerOrLeader } from '$lib/stores/auth';
	import { CheckSquare, Clock, AlertTriangle, Users, TrendingUp } from 'lucide-svelte';

	let stats: DashboardPayload | null = null;
	let loading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			stats = await dashboard.get();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load dashboard';
			console.error('Dashboard load error:', e);
		} finally {
			loading = false;
		}
	});

	function activityPreview(fv: Record<string, string>): string {
		const first = Object.values(fv).find((v) => v?.trim());
		return first ? first.substring(0, 120) : '';
	}

	function kpiScoreColor(score: number): string {
		if (score >= 80) return 'text-green-400';
		if (score >= 60) return 'text-yellow-400';
		return 'text-red-400';
	}

	const statusDotClass: Record<string, string> = {
		green: 'bg-green-400',
		yellow: 'bg-yellow-400',
		red: 'bg-red-400'
	};
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
	{:else if error}
		<div class="flex flex-col items-center justify-center py-20">
			<AlertTriangle class="text-red-400 mb-3" size={48} />
			<p class="text-gray-400 text-sm">Failed to load dashboard</p>
			<p class="text-gray-500 text-xs mt-1">{error}</p>
			<button onclick={() => window.location.reload()} class="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-500 transition-colors text-sm">
				Retry
			</button>
		</div>
	{:else if stats}
		{#if $isManagerOrLeader && stats.kpi_summary}
			<!-- KPI Summary Strip (supervisor / assistant_manager / manager only — D-12, D-13) -->
			<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6" data-testid="kpi-summary-section">
				<!-- Avg Score -->
				<div class="card">
					<div class="flex items-center justify-between mb-3">
						<span class="text-gray-400 text-sm">Avg Score</span>
						<TrendingUp class="text-primary-400" size={18} />
					</div>
					<p class="text-2xl font-semibold {kpiScoreColor(stats.kpi_summary.avg_score)}" data-testid="kpi-avg-score">{stats.kpi_summary.avg_score}</p>
					<p class="text-xs text-gray-500 mt-1">out of 100</p>
				</div>
				<!-- Completion Rate -->
				<div class="card">
					<div class="flex items-center justify-between mb-3">
						<span class="text-gray-400 text-sm">Completion Rate</span>
						<CheckSquare class="text-primary-400" size={18} />
					</div>
					<p class="text-2xl font-semibold text-white" data-testid="kpi-completion-rate">{Math.round(stats.kpi_summary.completion_rate * 100)}%</p>
					<p class="text-xs text-gray-500 mt-1">last 30 days</p>
				</div>
				<!-- Needs Attention — links to /performance (KPI-03) -->
				<a href="/performance" class="card block hover:border-gray-600 transition-colors">
					<div class="flex items-center justify-between mb-3">
						<span class="text-gray-400 text-sm">Needs Attention</span>
						<AlertTriangle class="text-yellow-400" size={18} />
					</div>
					<p class="text-2xl font-semibold {stats.kpi_summary.needs_attention_count > 0 ? 'text-yellow-400' : 'text-white'}" data-testid="kpi-needs-attention">{stats.kpi_summary.needs_attention_count}</p>
					<p class="text-xs text-gray-500 mt-1">members below 70</p>
				</a>
			</div>
		{/if}

		<!-- Two-column row: My Tasks (left) + Activity Feed (right) — all roles (D-01, D-02) -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
			<!-- My Tasks Panel (D-04 to D-07) -->
			<div class="card" data-testid="my-tasks-section">
				<div class="flex items-center gap-2 mb-4">
					<CheckSquare class="text-primary-400" size={18} />
					<h2 class="font-semibold text-white">My Tasks</h2>
				</div>
				{#if stats.my_tasks.length === 0}
					<p class="text-gray-500 text-sm py-4 text-center">No tasks assigned. <a href="/tasks" class="text-primary-400 hover:underline">View all tasks →</a></p>
				{:else}
					<div class="space-y-1">
						{#each stats.my_tasks as t}
							<a
								href="/tasks"
								class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-800 transition-colors {t.is_overdue ? 'bg-red-950/40' : t.is_due_soon ? 'bg-yellow-950/40' : ''}"
								data-testid="task-card"
								data-overdue={t.is_overdue ? "true" : "false"}
								data-due-soon={t.is_due_soon ? "true" : "false"}
							>
								<div class="flex-1 min-w-0">
									<p class="text-sm text-gray-200 truncate">{t.title}</p>
									{#if t.project_name}
										<p class="text-xs text-gray-500">{t.project_name}</p>
									{/if}
								</div>
								<div class="flex items-center gap-2 flex-shrink-0">
									{#if t.priority}
										<span class="badge {priorityColors[t.priority]}">{t.priority}</span>
									{/if}
									<span class="badge {statusColors[t.status] ?? 'bg-gray-700 text-gray-300'}">{statusLabels[t.status] ?? t.status}</span>
								</div>
							</a>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Activity Feed Panel (D-14 to D-16) -->
			<div class="card" data-testid="activity-feed-section">
				<div class="flex items-center gap-2 mb-4">
					<Clock class="text-primary-400" size={18} />
					<h2 class="font-semibold text-white">Recent Activity</h2>
				</div>
				{#if stats.recent_activity.length === 0}
					<p class="text-gray-500 text-sm py-4 text-center">No recent updates. <a href="/updates" class="text-primary-400 hover:underline">View all updates →</a></p>
				{:else}
					<div>
						{#each stats.recent_activity as activity}
							<div class="flex items-start gap-3 py-2 border-b border-gray-800 last:border-0" data-testid="activity-feed-item">
								<div class="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-semibold text-gray-300 flex-shrink-0">
									{activity.author_name.charAt(0).toUpperCase()}
								</div>
								<div class="flex-1 min-w-0">
									<p class="text-sm font-semibold text-gray-200">{activity.author_name}</p>
									<p class="text-xs text-gray-500">{timeAgo(activity.created_at)}</p>
									{#if activityPreview(activity.field_values)}
										<p class="text-sm text-gray-400 mt-1 truncate">{activityPreview(activity.field_values)}</p>
									{/if}
								</div>
							</div>
						{/each}
					</div>
					<div class="flex justify-end mt-3 pt-3 border-t border-gray-800">
						<a href="/updates" class="text-xs text-primary-400 hover:underline">View all updates →</a>
					</div>
				{/if}
			</div>
		</div>

		{#if $isManagerOrLeader && stats.team_health}
			<!-- Team Health Panel (supervisor / assistant_manager / manager only — D-08 to D-11) -->
			<div class="card" data-testid="team-health-section">
				<div class="flex items-center gap-2 mb-4">
					<Users class="text-primary-400" size={18} />
					<h2 class="font-semibold text-white">Team Health</h2>
				</div>
				{#if stats.team_health.length === 0}
					<p class="text-gray-500 text-sm py-4 text-center">No team members visible</p>
				{:else}
					<div class="grid grid-cols-2 md:grid-cols-3 gap-3">
						{#each stats.team_health as member}
							<div class="bg-gray-800 rounded-lg p-3 border {member.status === 'red' ? 'border-red-500/50' : 'border-gray-700'}" data-testid="team-health-member" data-at-risk={member.status === 'red' ? "true" : "false"}>
								<div class="flex items-center gap-2">
									{#if member.avatar_url}
										<img src={member.avatar_url} alt={member.full_name} class="w-10 h-10 rounded-full object-cover flex-shrink-0" />
									{:else}
										<div class="w-10 h-10 rounded-full bg-primary-700 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
											{initials(member.full_name)}
										</div>
									{/if}
									<div class="flex-1 min-w-0">
										<p class="text-sm text-gray-200 truncate">{member.full_name}</p>
										<div class="flex items-center gap-1 mt-0.5">
											<span class="w-2 h-2 rounded-full {statusDotClass[member.status]} flex-shrink-0"></span>
											<span class="text-xs text-gray-500">{member.active_tasks} active · {member.overdue_tasks} overdue</span>
										</div>
									</div>
								</div>
							</div>
						{/each}
					</div>
					<div class="flex justify-end mt-3 pt-3 border-t border-gray-800">
						<a href="/performance" class="text-xs text-primary-400 hover:underline">View full performance →</a>
					</div>
				{/if}
			</div>
		{/if}
	{/if}
</div>
