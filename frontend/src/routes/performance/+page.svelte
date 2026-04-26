<script lang="ts">
	import { onMount } from 'svelte';
	import { performance } from '$lib/api';
	import { downloadCsv } from '$lib/components/performance/csv';
	import KpiTabs from '$lib/components/performance/KpiTabs.svelte';
	import KpiScoreCard from '$lib/components/performance/KpiScoreCard.svelte';
	import KpiChartPanel from '$lib/components/performance/KpiChartPanel.svelte';
	import KpiFilters from '$lib/components/performance/KpiFilters.svelte';
	import KpiDrilldown from '$lib/components/performance/KpiDrilldown.svelte';
	import KpiWeightSettings from '$lib/components/performance/KpiWeightSettings.svelte';
	import { toast } from 'svelte-sonner';

	const DEMO_OVERVIEW = {
		summary: { average_score: 74, active_tasks: 31, completed_tasks: 58, average_cycle_time_hours: 36.5, defect_count: 4 },
		scorecards: [
			{
				user_id: 1, full_name: 'Alice Chen', avatar_url: null, kpi_score: 88, trend: 'up',
				reasons: [],
				breakdown: { workload: 100, velocity: 90, cycle_time: 100, on_time: 85, defects: 100 }
			},
			{
				user_id: 2, full_name: 'Ben Torres', avatar_url: null, kpi_score: 72, trend: 'stable',
				reasons: [{ label: 'Low velocity', severity: 'warning' }],
				breakdown: { workload: 100, velocity: 50, cycle_time: 70, on_time: 80, defects: 100 }
			},
			{
				user_id: 3, full_name: 'Carla Müller', avatar_url: null, kpi_score: 55, trend: 'down',
				reasons: [{ label: 'High workload', severity: 'critical' }, { label: 'Slow cycle time', severity: 'critical' }],
				breakdown: { workload: 40, velocity: 70, cycle_time: 40, on_time: 60, defects: 70 }
			},
			{
				user_id: 4, full_name: 'David Park', avatar_url: null, kpi_score: 93, trend: 'up',
				reasons: [],
				breakdown: { workload: 100, velocity: 100, cycle_time: 100, on_time: 92, defects: 100 }
			},
			{
				user_id: 5, full_name: 'Eva Rossi', avatar_url: null, kpi_score: 63, trend: 'stable',
				reasons: [{ label: 'Low on-time rate', severity: 'warning' }, { label: 'High bug MTTR', severity: 'warning' }],
				breakdown: { workload: 70, velocity: 60, cycle_time: 70, on_time: 52, defects: 70 }
			},
		],
		needs_attention: [
			{
				user_id: 3, full_name: 'Carla Müller', avatar_url: null, kpi_score: 55, trend: 'down',
				reasons: [{ label: 'High workload', severity: 'critical' }, { label: 'Slow cycle time', severity: 'critical' }],
				breakdown: { workload: 40, velocity: 70, cycle_time: 40, on_time: 60, defects: 70 }
			},
		],
		weights: { id: 0, sub_team_id: null, workload_weight: 20, velocity_weight: 25, cycle_time_weight: 20, on_time_weight: 20, defect_weight: 15, updated_at: null },
	};

	let isDemo = $state(false);

	const TABS = [
		{ id: 'overview', label: 'Overview' },
		{ id: 'sprint', label: 'Sprint' },
		{ id: 'quality', label: 'Quality' },
		{ id: 'members', label: 'Members' },
		{ id: 'settings', label: 'Settings' },
	];

	let activeTab = $state('overview');
	let refreshedAt = $state('');

	// Overview
	let overviewData = $state<any>(null);
	let overviewLoading = $state(false);

	// Sprint
	let sprintData = $state<any>(null);
	let sprintLoading = $state(false);
	let sprintFilters = $state<Record<string, unknown>>({});

	// Quality
	let qualityData = $state<any>(null);
	let qualityLoading = $state(false);
	let qualityFilters = $state<Record<string, unknown>>({});

	// Members
	let membersData = $state<any>(null);
	let membersLoading = $state(false);
	let memberFilters = $state<Record<string, unknown>>({});

	// Settings
	let weightsData = $state<any>(null);
	let weightsSaving = $state(false);

	// Drilldown
	let drilldownOpen = $state(false);
	let drilldownTitle = $state('');
	let drilldownFilters = $state<Record<string, unknown>>({});
	let drilldownTasks = $state<any[]>([]);

	async function loadOverview() {
		overviewLoading = true;
		try {
			const res = await performance.kpiOverview();
			if (res?.scorecards?.length) {
				overviewData = res;
				isDemo = false;
			} else {
				overviewData = DEMO_OVERVIEW;
				isDemo = true;
			}
		} catch (e) {
			console.error(e);
			overviewData = DEMO_OVERVIEW;
			isDemo = true;
		} finally { overviewLoading = false; }
	}

	async function loadSprint() {
		sprintLoading = true;
		try { sprintData = await performance.kpiSprint(sprintFilters as any); } catch (e) { console.error(e); } finally { sprintLoading = false; }
	}

	async function loadQuality() {
		qualityLoading = true;
		try { qualityData = await performance.kpiQuality(qualityFilters as any); } catch (e) { console.error(e); } finally { qualityLoading = false; }
	}

	async function loadMembers() {
		membersLoading = true;
		try { membersData = await performance.kpiMembers(memberFilters as any); } catch (e) { console.error(e); } finally { membersLoading = false; }
	}

	async function loadWeights() {
		try { weightsData = await performance.kpiWeights(); } catch (e) { console.error(e); }
	}

	async function openDrilldown(metric: string, filters: Record<string, unknown>, title: string) {
		drilldownTitle = title;
		drilldownFilters = filters;
		drilldownOpen = true;
		try {
			const res = await performance.kpiDrilldown({ metric, ...filters } as any);
			drilldownTasks = res?.tasks ?? [];
		} catch (e) { drilldownTasks = []; }
	}

	async function saveWeights(w: any) {
		weightsSaving = true;
		try {
			weightsData = await performance.updateKpiWeights(w);
			toast.success('KPI weights updated.');
		} catch (e: any) {
			const msg = e?.message ?? '';
			if (msg.includes('100')) toast.error('Total weight must equal 100%.');
			else toast.error(msg || 'Failed to save weights');
		} finally { weightsSaving = false; }
	}

	function resetWeights() {
		weightsData = { ...weightsData, workload_weight: 20, velocity_weight: 25, cycle_time_weight: 20, on_time_weight: 20, defect_weight: 15 };
	}

	function exportCurrentTab() {
		if (activeTab === 'overview' && overviewData) {
			downloadCsv('kpi-overview.csv', overviewData.scorecards ?? []);
		} else if (activeTab === 'sprint' && sprintData) {
			const rows = (sprintData.velocity_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, label: p.label, value: p.value })));
			downloadCsv('kpi-sprint.csv', rows);
		} else if (activeTab === 'quality' && qualityData) {
			const rows = (qualityData.bugs_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, label: p.label, value: p.value })));
			downloadCsv('kpi-quality.csv', rows);
		} else if (activeTab === 'members' && membersData) {
			const rows = (membersData.throughput_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, label: p.label, value: p.value })));
			downloadCsv('kpi-members.csv', rows);
		}
	}

	function selectTab(id: string) {
		activeTab = id;
		if (id === 'sprint' && !sprintData) loadSprint();
		if (id === 'quality' && !qualityData) loadQuality();
		if (id === 'members' && !membersData) loadMembers();
		if (id === 'settings' && !weightsData) loadWeights();
	}

	onMount(() => {
		refreshedAt = new Date().toLocaleTimeString();
		loadOverview();
	});
</script>

<div class="p-4 md:p-8 max-w-7xl mx-auto space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold text-white tracking-tight">Performance Dashboard</h1>
			<p class="text-gray-400 mt-1">Track member KPI health, sprint delivery, and quality trends.</p>
			{#if refreshedAt}
				<p class="text-xs text-gray-600 mt-0.5">Refreshed at {refreshedAt}</p>
			{/if}
		</div>
		<button
			type="button"
			on:click={exportCurrentTab}
			class="px-4 py-2 rounded bg-primary-600 text-white text-sm font-medium hover:bg-primary-500 transition-colors whitespace-nowrap self-start"
		>
			Export KPI CSV
		</button>
	</div>

	<!-- Tabs -->
	<KpiTabs tabs={TABS} active={activeTab} onSelect={selectTab} />

	<!-- Overview Tab -->
	{#if activeTab === 'overview'}
		{#if overviewLoading}
			<div class="flex justify-center py-16"><div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div></div>
		{:else if overviewData}
			<!-- Summary tiles -->
			<div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
				<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
					<p class="text-xs text-gray-400">Avg Score</p>
					<p class="text-xl font-bold text-white">{overviewData.summary?.average_score ?? '-'}</p>
				</div>
				<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
					<p class="text-xs text-gray-400">Active Tasks</p>
					<p class="text-xl font-bold text-white">{overviewData.summary?.active_tasks ?? '-'}</p>
				</div>
				<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
					<p class="text-xs text-gray-400">Completed (30d)</p>
					<p class="text-xl font-bold text-white">{overviewData.summary?.completed_tasks ?? '-'}</p>
				</div>
				<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
					<p class="text-xs text-gray-400">Avg Cycle Time</p>
					<p class="text-xl font-bold text-white">{overviewData.summary?.average_cycle_time_hours != null ? overviewData.summary.average_cycle_time_hours + 'h' : '-'}</p>
				</div>
				<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
					<p class="text-xs text-gray-400">Defects</p>
					<p class="text-xl font-bold text-white">{overviewData.summary?.defect_count ?? '-'}</p>
				</div>
			</div>

			<!-- Member scorecards -->
			{#if overviewData.scorecards?.length > 0}
				<div>
					<h2 class="text-lg font-semibold text-gray-100 mb-3">Member Scorecards</h2>
					<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
						{#each overviewData.scorecards as member}
							<KpiScoreCard {member} hideDetailLink={isDemo} onDrilldown={(m) => openDrilldown('overview', { member_id: m.user_id }, m.full_name)} />
						{/each}
					</div>
				</div>
			{/if}

			<!-- Needs attention -->
			<div>
				<h2 class="text-lg font-semibold text-gray-100 mb-3">Needs attention</h2>
				{#if overviewData.needs_attention?.length === 0}
					<p class="text-gray-500 text-sm">No members need attention for the selected period.</p>
				{:else}
					<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
						{#each overviewData.needs_attention as member}
							<KpiScoreCard {member} hideDetailLink={isDemo} />
						{/each}
					</div>
				{/if}
			</div>
		{:else}
			<p class="text-gray-500 text-sm py-8 text-center">No overview data available.</p>
		{/if}
		{#if isDemo && overviewData}
			<div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-900/30 border border-indigo-700/50 text-indigo-300 text-xs">
				<span class="text-lg">🎭</span>
				<span><strong>Demo mode</strong> — no real team data yet. Scorecards above show example values so you can explore every feature.</span>
			</div>
		{/if}
	{/if}

	<!-- Sprint Tab -->
	{#if activeTab === 'sprint'}
		<div class="space-y-4">
			<KpiFilters
				filters={sprintFilters}
				options={sprintData?.filter_options ?? {}}
				mode="sprint"
				onChange={(f) => { sprintFilters = f; loadSprint(); }}
			/>
			{#if sprintLoading}
				<div class="flex justify-center py-16"><div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div></div>
			{:else}
				<KpiChartPanel
					title="Velocity"
					subtitle="Completed tasks per member over last 6 sprints"
					series={sprintData?.velocity_series ?? []}
					onExport={() => downloadCsv('velocity.csv', (sprintData?.velocity_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
					onPointClick={(pt) => openDrilldown('velocity', { ...sprintFilters }, 'Velocity — ' + pt.label)}
				/>
				<KpiChartPanel
					title="Burndown"
					subtitle="Remaining tasks in selected sprint"
					series={sprintData?.burndown_series ?? []}
					onExport={() => downloadCsv('burndown.csv', (sprintData?.burndown_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
				/>
			{/if}
		</div>
	{/if}

	<!-- Quality Tab -->
	{#if activeTab === 'quality'}
		<div class="space-y-4">
			<KpiFilters
				filters={qualityFilters}
				options={qualityData?.filter_options ?? {}}
				mode="quality"
				onChange={(f) => { qualityFilters = f; loadQuality(); }}
			/>
			{#if qualityLoading}
				<div class="flex justify-center py-16"><div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div></div>
			{:else}
				<KpiChartPanel
					title="Bugs Reported vs Resolved"
					subtitle="Daily bug activity for the selected period"
					series={qualityData?.bugs_series ?? []}
					onExport={() => downloadCsv('bugs.csv', (qualityData?.bugs_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
					onPointClick={(pt) => openDrilldown('bugs', { ...qualityFilters }, 'Bugs — ' + pt.label)}
				/>
				<KpiChartPanel
					title="MTTR by Member"
					subtitle="Mean time to resolve bugs (hours)"
					series={qualityData?.mttr_series ?? []}
					onExport={() => downloadCsv('mttr.csv', (qualityData?.mttr_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
					onPointClick={(pt) => openDrilldown('mttr', { ...qualityFilters, member_id: undefined }, 'MTTR — ' + pt.label)}
				/>
			{/if}
		</div>
	{/if}

	<!-- Members Tab -->
	{#if activeTab === 'members'}
		<div class="space-y-4">
			<KpiFilters
				filters={memberFilters}
				options={membersData?.filter_options ?? {}}
				mode="members"
				onChange={(f) => { memberFilters = f; loadMembers(); }}
			/>
			{#if membersLoading}
				<div class="flex justify-center py-16"><div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div></div>
			{:else}
				<KpiChartPanel
					title="Throughput by Member & Type"
					subtitle="Tasks completed per member by type (last 8 weeks)"
					series={membersData?.throughput_series ?? []}
					onExport={() => downloadCsv('throughput.csv', (membersData?.throughput_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
					onPointClick={(pt) => openDrilldown('throughput', { ...memberFilters }, 'Throughput — ' + pt.label)}
				/>
				<KpiChartPanel
					title="Cycle Time by Task Type"
					subtitle="Average hours to complete tasks by type (last 3 months)"
					series={membersData?.cycle_time_series ?? []}
					onExport={() => downloadCsv('cycle-time.csv', (membersData?.cycle_time_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
				/>
			{/if}
		</div>
	{/if}

	<!-- Settings Tab -->
	{#if activeTab === 'settings'}
		<div class="max-w-2xl space-y-6">
			<!-- How-to guide -->
			<div class="rounded-xl border border-gray-700 bg-gray-800/60 p-5 space-y-4">
				<h2 class="font-semibold text-gray-100 text-base">How KPI weights work</h2>
				<p class="text-sm text-gray-400">Each member's KPI score (0–100) is a <strong class="text-gray-200">weighted average</strong> of five dimension scores. Adjust the weights below to reflect what matters most to your team.</p>

				<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
					{#each [
						{ label: 'Workload', icon: '📋', default: '20%', desc: 'Active task count. ≤7 → 100 | 8-10 → 70 | >10 → 40' },
						{ label: 'Velocity', icon: '⚡', default: '25%', desc: 'Tasks completed in last 30 days. Each task = +10 pts, max 100.' },
						{ label: 'Cycle Time', icon: '⏱', default: '20%', desc: 'Avg hours creation→done. ≤48 h → 100 | ≤120 h → 70 | >120 h → 40' },
						{ label: 'On-Time Rate', icon: '✅', default: '20%', desc: 'Tasks finished by due date. Score = on-time % directly.' },
						{ label: 'Defects', icon: '🐛', default: '15%', desc: 'Bug MTTR. ≤72 h → 100 | ≤168 h → 70 | >168 h → 40. No bugs = 100.' },
					] as dim}
						<div class="flex gap-2 items-start bg-gray-700/40 rounded-lg p-3">
							<span class="text-lg shrink-0">{dim.icon}</span>
							<div>
								<p class="font-semibold text-gray-200">{dim.label} <span class="font-normal text-gray-500">(default {dim.default})</span></p>
								<p class="text-gray-400 mt-0.5">{dim.desc}</p>
							</div>
						</div>
					{/each}
				</div>

				<div class="border-t border-gray-700 pt-3 space-y-1 text-xs text-gray-400">
					<p>📐 <strong class="text-gray-300">All five weights must sum to exactly 100.</strong> The form will block saving if the total differs.</p>
					<p>🔒 Weights are stored <strong class="text-gray-300">per sub-team</strong> — different teams can have different priorities.</p>
					<p>♻️ Click <strong class="text-gray-300">Reset defaults</strong> to restore 20 / 25 / 20 / 20 / 15.</p>
					<p>🟢 Score ≥80 = Good · 🟡 60–79 = Fair · 🔴 &lt;60 = At Risk</p>
				</div>
			</div>

			<!-- Weight editor -->
			{#if weightsData}
				<KpiWeightSettings
					weights={weightsData}
					saving={weightsSaving}
					onSave={saveWeights}
					onReset={resetWeights}
				/>
			{:else}
				<p class="text-gray-500 text-sm py-4">Loading settings…</p>
			{/if}
		</div>
	{/if}
</div>

<!-- Drill-down modal -->
<KpiDrilldown
	open={drilldownOpen}
	title={drilldownTitle}
	filters={drilldownFilters}
	tasks={drilldownTasks}
	onClose={() => drilldownOpen = false}
	onExport={() => downloadCsv('drilldown.csv', drilldownTasks)}
/>
