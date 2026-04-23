<script lang="ts">
	import { onMount } from 'svelte';
	import { performance } from '$lib/api';
	// layerchart removed — using inline SVG bar chart below
	import { 
		TrendingUp, 
		Clock, 
		CheckCircle2, 
		Users, 
		AlertTriangle,
		ExternalLink,
		ChevronRight,
		MessageSquare
	} from 'lucide-svelte';

	let loading = $state(true);
	let data = $state<any>(null);

	onMount(async () => {
		try {
			data = await performance.teamStats();
		} catch (e) {
			console.error('Failed to fetch performance stats:', e);
		} finally {
			loading = false;
		}
	});

	const getStatusColor = (status: string) => {
		switch (status) {
			case 'red': return 'bg-red-500/20 text-red-400 border-red-500/50';
			case 'yellow': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
			case 'green': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50';
			default: return 'bg-gray-500/20 text-gray-400 border-gray-500/50';
		}
	};
</script>

<div class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold text-white tracking-tight">Performance Dashboard</h1>
			<p class="text-gray-400 mt-1">Monitor team workload and productivity metrics.</p>
		</div>
		
		{#if !loading && data}
			<div class="flex gap-3 flex-wrap">
				<div class="bg-gray-900 border border-gray-800 rounded-xl px-4 py-2 flex items-center gap-3">
					<div class="p-2 bg-primary-500/10 rounded-lg">
						<TrendingUp class="w-4 h-4 text-primary-400" />
					</div>
					<div>
						<p class="text-[10px] uppercase tracking-wider text-gray-500 font-bold">On-Time Rate</p>
						<p class="text-lg font-bold text-white leading-none">{data.overall_on_time_rate}%</p>
					</div>
				</div>
				<div class="bg-gray-900 border border-gray-800 rounded-xl px-4 py-2 flex items-center gap-3">
					<div class="p-2 bg-emerald-500/10 rounded-lg">
						<CheckCircle2 class="w-4 h-4 text-emerald-400" />
					</div>
					<div>
						<p class="text-[10px] uppercase tracking-wider text-gray-500 font-bold">Active Tasks</p>
						<p class="text-lg font-bold text-white leading-none">{data.total_active_tasks}</p>
					</div>
				</div>
			</div>
		{/if}
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if data}
		<!-- Workload Chart -->
		<div class="bg-gray-900/50 border border-gray-800 rounded-2xl p-6">
			<h3 class="text-lg font-semibold text-white mb-6">Team Workload Distribution</h3>
			<div class="h-[300px] w-full overflow-x-auto">
				{#if data.team_metrics.length > 0}
					{@const maxVal = Math.max(...data.team_metrics.map((m: any) => m.active_tasks), 1)}
					{@const barW = Math.max(40, Math.min(80, Math.floor(560 / data.team_metrics.length) - 12))}
					{@const chartH = 220}
					<svg
						viewBox="0 0 {data.team_metrics.length * (barW + 12) + 40} {chartH + 40}"
						class="w-full h-full"
						overflow="visible"
					>
						{#each data.team_metrics as member, i}
							{@const barH = Math.max(4, (member.active_tasks / maxVal) * chartH)}
							{@const x = 20 + i * (barW + 12)}
							{@const y = chartH - barH}
							<rect
								x={x}
								y={y}
								width={barW}
								height={barH}
								rx="4"
								class="fill-primary-500/40 hover:fill-primary-500 transition-colors cursor-pointer"
							/>
							<text
								x={x + barW / 2}
								y={chartH + 16}
								text-anchor="middle"
								class="fill-gray-500 text-[10px]"
								font-size="10"
							>{member.full_name.split(' ')[0]}</text>
							<text
								x={x + barW / 2}
								y={y - 4}
								text-anchor="middle"
								class="fill-gray-400"
								font-size="11"
							>{member.active_tasks}</text>
						{/each}
					</svg>
				{:else}
					<div class="flex items-center justify-center h-full text-gray-500 text-sm">No workload data</div>
				{/if}
			</div>
		</div>

		<!-- Team Table -->
		<div class="bg-gray-900/50 border border-gray-800 rounded-2xl overflow-hidden">
			<div class="px-6 py-4 border-b border-gray-800 flex items-center justify-between">
				<h3 class="text-lg font-semibold text-white">Member Performance</h3>
				<span class="text-xs text-gray-500">{data.team_metrics.length} Team Members</span>
			</div>
			<div class="overflow-x-auto">
				<table class="w-full text-left border-collapse">
					<thead>
						<tr class="text-gray-500 text-[11px] uppercase tracking-wider border-b border-gray-800/50">
							<th class="px-6 py-4 font-bold">Member</th>
							<th class="px-6 py-4 font-bold text-center">Status</th>
							<th class="px-6 py-4 font-bold text-center">Active</th>
							<th class="px-6 py-4 font-bold text-center">Done (30d)</th>
							<th class="px-6 py-4 font-bold text-center">On-Time</th>
							<th class="px-6 py-4 font-bold text-center">Cycle Time</th>
							<th class="px-6 py-4 font-bold text-center">Collab</th>
							<th class="px-6 py-4"></th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-800/50">
						{#each data.team_metrics as member}
							<tr class="hover:bg-white/5 transition-colors group">
								<td class="px-6 py-4">
									<div class="flex items-center gap-3">
										<div class="w-9 h-9 rounded-full bg-primary-900/40 border border-primary-500/20 flex items-center justify-center text-sm font-bold text-primary-400">
											{#if member.avatar_url}
												<img src={member.avatar_url} alt={member.full_name} class="w-full h-full rounded-full object-cover" />
											{:else}
												{member.full_name.split(' ').map((n: string) => n[0]).join('')}
											{/if}
										</div>
										<div>
											<p class="text-sm font-medium text-white">{member.full_name}</p>
											<p class="text-xs text-gray-500">ID: #{member.user_id}</p>
										</div>
									</div>
								</td>
								<td class="px-6 py-4 text-center">
									<span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase border {getStatusColor(member.status)}">
										{member.status}
									</span>
								</td>
								<td class="px-6 py-4 text-center">
									<span class="text-sm font-semibold text-white">{member.active_tasks}</span>
								</td>
								<td class="px-6 py-4 text-center">
									<span class="text-sm font-semibold text-white">{member.completed_30d}</span>
								</td>
								<td class="px-6 py-4 text-center">
									<div class="flex flex-col items-center gap-1">
										<span class="text-sm font-semibold text-white">{member.on_time_rate}%</span>
										<div class="w-16 h-1 bg-gray-800 rounded-full overflow-hidden">
											<div class="h-full bg-primary-500" style="width: {member.on_time_rate}%"></div>
										</div>
									</div>
								</td>
								<td class="px-6 py-4 text-center">
									<span class="text-sm font-semibold text-white">{member.avg_cycle_time ?? '-'}h</span>
								</td>
								<td class="px-6 py-4 text-center">
									<div class="flex items-center justify-center gap-1.5 text-gray-400">
										<MessageSquare size={14} />
										<span class="text-sm font-semibold">{member.collaboration_score}</span>
									</div>
								</td>
								<td class="px-6 py-4 text-right">
									<a 
										href="/performance/{member.user_id}"
										class="inline-flex items-center gap-1.5 text-xs font-bold text-primary-400 hover:text-primary-300 transition-colors bg-primary-500/10 px-3 py-1.5 rounded-lg"
									>
										View Profile
										<ChevronRight size={14} />
									</a>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{:else}
		<div class="bg-gray-900/50 border border-gray-800 rounded-2xl p-12 text-center">
			<AlertTriangle class="w-12 h-12 text-yellow-500 mx-auto mb-4" />
			<h3 class="text-xl font-bold text-white mb-2">No Performance Data</h3>
			<p class="text-gray-400">We couldn't find any performance metrics for your team.</p>
		</div>
	{/if}
</div>
