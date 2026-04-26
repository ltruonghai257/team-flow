<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { performance } from '$lib/api';
	import KpiScoreCard from '$lib/components/performance/KpiScoreCard.svelte';
	// layerchart removed — using inline SVG area chart below
	import { 
		TrendingUp, 
		Clock, 
		CheckCircle2, 
		MessageSquare, 
		ChevronLeft,
		Calendar,
		ArrowUpRight,
		CheckSquare,
		Users
	} from 'lucide-svelte';
	import { format, parseISO } from 'date-fns';

	let loading = $state(true);
	let data = $state<any>(null);
	let fetchError = $state<string | null>(null);
	let kpiScorecard = $state<any>(null);
	const userId = parseInt($page.params.id ?? '0');

	onMount(async () => {
		try {
			data = await performance.memberStats(userId);
		} catch (e: any) {
			console.error('Failed to fetch member stats:', e);
			fetchError = e?.message ?? 'Could not load member data.';
		} finally {
			loading = false;
		}
		try {
			const overview = await performance.kpiOverview();
			kpiScorecard = (overview?.scorecards ?? []).find((s: any) => s.user_id === userId) ?? null;
		} catch (e) { /* non-blocking */ }
	});

	const getStatusColor = (status: string) => {
		switch (status) {
			case 'red': return 'text-red-400 bg-red-500/10 border-red-500/20';
			case 'yellow': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
			case 'green': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
			default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
		}
	};
</script>

<div class="p-8 max-w-7xl mx-auto space-y-8">
	<!-- Back Link & Header -->
	<div class="space-y-4">
		<a 
			href="/performance" 
			class="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors group"
		>
			<ChevronLeft size={16} class="group-hover:-translate-x-0.5 transition-transform" />
			Back to Dashboard
		</a>

		{#if !loading && data}
			<div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
				<div class="flex items-center gap-5">
					<div class="w-16 h-16 rounded-2xl bg-primary-900/40 border border-primary-500/20 flex items-center justify-center text-2xl font-bold text-primary-400 shadow-xl">
						{#if data.metrics.avatar_url}
							<img src={data.metrics.avatar_url} alt={data.full_name} class="w-full h-full rounded-2xl object-cover" />
						{:else}
							{data.full_name.split(' ').map((n: string) => n[0]).join('')}
						{/if}
					</div>
					<div>
						<div class="flex items-center gap-3">
							<h1 class="text-3xl font-bold text-white tracking-tight">{data.full_name}</h1>
							<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border {getStatusColor(data.metrics.status)}">
								{data.metrics.status}
							</span>
						</div>
						<p class="text-gray-400 mt-1 flex items-center gap-2">
							<Users size={14} />
							Team Member • ID: #{data.user_id}
						</p>
					</div>
				</div>

				<div class="flex gap-3">
					<div class="px-4 py-3 bg-gray-900 border border-gray-800 rounded-xl">
						<p class="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1">Collaboration</p>
						<div class="flex items-center gap-2">
							<MessageSquare size={16} class="text-primary-400" />
							<span class="text-xl font-bold text-white leading-none">{data.metrics.collaboration_score}</span>
						</div>
					</div>
					<div class="px-4 py-3 bg-gray-900 border border-gray-800 rounded-xl">
						<p class="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1">On-Time Rate</p>
						<div class="flex items-center gap-2">
							<TrendingUp size={16} class="text-emerald-400" />
							<span class="text-xl font-bold text-white leading-none">{data.metrics.on_time_rate}%</span>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if !data}
		<div class="bg-gray-900/50 border border-gray-800 rounded-2xl p-12 text-center space-y-4">
			<p class="text-4xl">🔍</p>
			<h2 class="text-xl font-bold text-white">Member not found</h2>
			{#if fetchError}
				<p class="text-gray-400 text-sm">{fetchError}</p>
			{:else}
				<p class="text-gray-400 text-sm">No data exists for user ID <code class="bg-gray-800 px-1 rounded">#{userId}</code>.</p>
			{/if}
			<p class="text-gray-500 text-xs">This may be a demo scorecard — real member detail pages only work for users in your team.</p>
			<a href="/performance" class="inline-block mt-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm rounded transition-colors">← Back to Dashboard</a>
		</div>
	{:else if data}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
			<!-- Metrics Sidebar -->
			<div class="lg:col-span-1 space-y-6">
				<div class="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 space-y-6">
					<h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest">Efficiency Metrics</h3>
					
					<div class="space-y-4">
						<div class="flex items-center justify-between p-4 bg-gray-950 rounded-xl border border-gray-800/50">
							<div class="flex items-center gap-3">
								<div class="p-2 bg-blue-500/10 rounded-lg text-blue-400">
									<CheckSquare size={18} />
								</div>
								<span class="text-sm font-medium text-gray-300">Active Tasks</span>
							</div>
							<span class="text-lg font-bold text-white">{data.metrics.active_tasks}</span>
						</div>

						<div class="flex items-center justify-between p-4 bg-gray-950 rounded-xl border border-gray-800/50">
							<div class="flex items-center gap-3">
								<div class="p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
									<CheckCircle2 size={18} />
								</div>
								<span class="text-sm font-medium text-gray-300">Done (30d)</span>
							</div>
							<span class="text-lg font-bold text-white">{data.metrics.completed_30d}</span>
						</div>

						<div class="flex items-center justify-between p-4 bg-gray-950 rounded-xl border border-gray-800/50">
							<div class="flex items-center gap-3">
								<div class="p-2 bg-purple-500/10 rounded-lg text-purple-400">
									<Clock size={18} />
								</div>
								<span class="text-sm font-medium text-gray-300">Avg Cycle Time</span>
							</div>
							<span class="text-lg font-bold text-white">{data.metrics.avg_cycle_time ?? '-'}h</span>
						</div>
					</div>
				</div>

				{#if kpiScorecard}
				<div>
					<h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-3">KPI Score</h3>
					<KpiScoreCard member={kpiScorecard} />
				</div>
				{/if}

				<div class="bg-gray-900/50 border border-gray-800 rounded-2xl p-6">
					<h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Recent Activity</h3>
					<div class="space-y-3">
						{#each data.recent_completed_tasks as task}
							<div class="p-3 bg-gray-950 rounded-lg border border-gray-800/50 group">
								<div class="flex items-start justify-between gap-2">
									<p class="text-xs font-medium text-gray-200 line-clamp-2 leading-relaxed">{task.title}</p>
									<CheckCircle2 size={12} class="text-emerald-500 flex-shrink-0 mt-0.5" />
								</div>
								<div class="flex items-center justify-between mt-2">
									<span class="text-[10px] text-gray-500">Completed {format(parseISO(task.completed_at), 'MMM d')}</span>
									<span class="text-[10px] font-bold text-primary-500/70 uppercase">Done</span>
								</div>
							</div>
						{:else}
							<p class="text-center py-8 text-sm text-gray-500 italic">No recent completions</p>
						{/each}
					</div>
				</div>
			</div>

			<!-- Main Content (Charts) -->
			<div class="lg:col-span-2 space-y-8">
				<div class="bg-gray-900/50 border border-gray-800 rounded-2xl p-8">
					<div class="flex items-center justify-between mb-8">
						<div>
							<h3 class="text-lg font-semibold text-white">Completion Trend</h3>
							<p class="text-sm text-gray-500">Tasks completed over the last 8 weeks</p>
						</div>
						<div class="flex items-center gap-4 text-xs">
							<div class="flex items-center gap-1.5">
								<div class="w-3 h-3 bg-primary-500/20 border border-primary-500 rounded-sm"></div>
								<span class="text-gray-400">Completed Tasks</span>
							</div>
						</div>
					</div>

					<div class="h-[400px] w-full">
					{#if data.trend_data.length > 0}
						{@const W = 600}
						{@const H = 300}
						{@const pad = { top: 20, right: 20, bottom: 40, left: 40 }}
						{@const innerW = W - pad.left - pad.right}
						{@const innerH = H - pad.top - pad.bottom}
						{@const maxCount = Math.max(...data.trend_data.map((d: any) => d.completed_count), 1)}
						{@const stepX = innerW / Math.max(data.trend_data.length - 1, 1)}
						{@const pts = data.trend_data.map((d: any, i: number) => [pad.left + i * stepX, pad.top + innerH - (d.completed_count / maxCount) * innerH] as [number,number])}
						{@const polyline = pts.map(([x,y]: [number,number]) => `${x},${y}`).join(' ')}
						{@const areaPath = `M ${pts[0][0]},${pad.top + innerH} ` + pts.map(([x,y]: [number,number]) => `L ${x},${y}`).join(' ') + ` L ${pts[pts.length-1][0]},${pad.top + innerH} Z`}
						<svg viewBox="0 0 {W} {H}" class="w-full h-full">
							<defs>
								<linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
									<stop offset="0%" stop-color="#6366f1" stop-opacity="0.25"/>
									<stop offset="100%" stop-color="#6366f1" stop-opacity="0.02"/>
								</linearGradient>
							</defs>
							<!-- Grid lines -->
							{#each [0, 0.25, 0.5, 0.75, 1] as frac}
								<line x1={pad.left} y1={pad.top + innerH * (1 - frac)} x2={pad.left + innerW} y2={pad.top + innerH * (1 - frac)} stroke="#1f2937" stroke-width="1"/>
								<text x={pad.left - 6} y={pad.top + innerH * (1 - frac) + 4} text-anchor="end" font-size="9" fill="#6b7280">{Math.round(maxCount * frac)}</text>
							{/each}
							<!-- Area fill -->
							<path d={areaPath} fill="url(#areaGrad)"/>
							<!-- Line -->
							<polyline points={polyline} fill="none" stroke="#6366f1" stroke-width="2" stroke-linejoin="round"/>
							<!-- Data points + x labels -->
							{#each pts as [x, y], i}
								<circle cx={x} cy={y} r="3" fill="#6366f1"/>
								<text x={x} y={H - 8} text-anchor="middle" font-size="9" fill="#6b7280">{format(parseISO(data.trend_data[i].date), 'MMM d')}</text>
							{/each}
						</svg>
					{:else}
						<div class="h-full flex flex-col items-center justify-center text-gray-500 gap-3 border-2 border-dashed border-gray-800 rounded-xl">
							<Calendar size={32} class="opacity-20" />
							<p class="text-sm">Not enough data to show trend</p>
						</div>
					{/if}
				</div>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div class="bg-gray-900/50 border border-gray-800 rounded-2xl p-6">
						<h4 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Productivity Summary</h4>
						<div class="space-y-4">
							<p class="text-sm text-gray-300 leading-relaxed">
								{data.full_name} has completed <span class="text-white font-bold">{data.metrics.completed_30d}</span> tasks in the last 30 days. 
								Their on-time completion rate is <span class={data.metrics.on_time_rate > 80 ? 'text-emerald-400' : 'text-yellow-400'}>{data.metrics.on_time_rate}%</span>, 
								with an average cycle time of <span class="text-white font-bold">{data.metrics.avg_cycle_time ?? 'N/A'}</span> hours per task.
							</p>
							<div class="pt-4 border-t border-gray-800 flex items-center gap-2 text-xs font-bold text-primary-400">
								<ArrowUpRight size={14} />
								TRENDING STABLE
							</div>
						</div>
					</div>

					<div class="bg-primary-600/10 border border-primary-500/20 rounded-2xl p-6 flex flex-col justify-between">
						<div>
							<h4 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-2">Next Steps</h4>
							<p class="text-sm text-gray-300">Recommend reviewing {data.metrics.active_tasks} active tasks to ensure bandwidth for upcoming sprints.</p>
						</div>
						<button class="w-full mt-6 py-2.5 bg-primary-600 hover:bg-primary-500 text-white rounded-xl text-sm font-bold transition-all shadow-lg shadow-primary-600/20">
							Assign New Task
						</button>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
