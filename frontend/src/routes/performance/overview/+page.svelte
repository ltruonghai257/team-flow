<script lang="ts">
	import { onMount } from 'svelte';
	import { performance } from '$lib/apis';
	import { downloadCsv } from '$lib/components/performance/csv';
	import KpiScoreCard from '$lib/components/performance/KpiScoreCard.svelte';
	import KpiDrilldown from '$lib/components/performance/KpiDrilldown.svelte';

	const STRINGS = {
		EXPORT_BUTTON: 'Export KPI CSV',
		CSV_FILENAME: 'kpi-overview.csv',
		DRILLDOWN_CSV_FILENAME: 'drilldown.csv',
		SUMMARY_TILES: {
			AVG_SCORE: 'Avg Score',
			ACTIVE_TASKS: 'Active Tasks',
			COMPLETED_30D: 'Completed (30d)',
			AVG_CYCLE_TIME: 'Avg Cycle Time',
			DEFECTS: 'Defects',
		},
		SECTIONS: {
			MEMBER_SCORECARDS: 'Member Scorecards',
			NEEDS_ATTENTION: 'Needs attention',
		},
		MESSAGES: {
			NO_ATTENTION: 'No members need attention for the selected period.',
			NO_DATA: 'No overview data available.',
		},
	} as const;

	let refreshedAt = $state('');
	let overviewData = $state<any>(null);
	let overviewLoading = $state(false);

	// Drilldown
	let drilldownOpen = $state(false);
	let drilldownTitle = $state('');
	let drilldownFilters = $state<Record<string, unknown>>({});
	let drilldownTasks = $state<any[]>([]);

	async function loadOverview() {
		overviewLoading = true;
		try {
			overviewData = await performance.kpiOverview();
		} catch (e) {
			console.error(e);
		} finally { overviewLoading = false; }
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

	function exportOverview() {
		if (overviewData) {
			downloadCsv(STRINGS.CSV_FILENAME, overviewData.scorecards ?? []);
		}
	}

	onMount(() => {
		refreshedAt = new Date().toLocaleTimeString();
		loadOverview();
	});
</script>

<div class="space-y-6">
	<div class="flex justify-end">
		<button
			type="button"
			on:click={exportOverview}
			class="px-4 py-2 rounded bg-primary-600 text-white text-sm font-medium hover:bg-primary-500 transition-colors whitespace-nowrap"
		>
			{STRINGS.EXPORT_BUTTON}
		</button>
	</div>

	{#if overviewLoading}
		<div class="flex justify-center py-16"><div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div></div>
	{:else if overviewData}
		<!-- Summary tiles -->
		<div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
			<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
				<p class="text-xs text-gray-400">{STRINGS.SUMMARY_TILES.AVG_SCORE}</p>
				<p class="text-xl font-bold text-white">{overviewData.summary?.average_score ?? '-'}</p>
			</div>
			<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
				<p class="text-xs text-gray-400">{STRINGS.SUMMARY_TILES.ACTIVE_TASKS}</p>
				<p class="text-xl font-bold text-white">{overviewData.summary?.active_tasks ?? '-'}</p>
			</div>
			<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
				<p class="text-xs text-gray-400">{STRINGS.SUMMARY_TILES.COMPLETED_30D}</p>
				<p class="text-xl font-bold text-white">{overviewData.summary?.completed_tasks ?? '-'}</p>
			</div>
			<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
				<p class="text-xs text-gray-400">{STRINGS.SUMMARY_TILES.AVG_CYCLE_TIME}</p>
				<p class="text-xl font-bold text-white">{overviewData.summary?.average_cycle_time_hours != null ? overviewData.summary.average_cycle_time_hours + 'h' : '-'}</p>
			</div>
			<div class="bg-gray-800 rounded-lg border border-gray-700 p-3 text-center">
				<p class="text-xs text-gray-400">{STRINGS.SUMMARY_TILES.DEFECTS}</p>
				<p class="text-xl font-bold text-white">{overviewData.summary?.defect_count ?? '-'}</p>
			</div>
		</div>

		<!-- Member scorecards -->
		{#if overviewData.scorecards?.length > 0}
			<div>
				<h2 class="text-lg font-semibold text-gray-100 mb-3">{STRINGS.SECTIONS.MEMBER_SCORECARDS}</h2>
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each overviewData.scorecards as member}
						<KpiScoreCard {member} onDrilldown={(m) => openDrilldown('overview', { member_id: m.user_id }, m.full_name)} />
					{/each}
				</div>
			</div>
		{/if}

		<!-- Needs attention -->
		<div>
			<h2 class="text-lg font-semibold text-gray-100 mb-3">{STRINGS.SECTIONS.NEEDS_ATTENTION}</h2>
			{#if overviewData.needs_attention?.length === 0}
				<p class="text-gray-500 text-sm">{STRINGS.MESSAGES.NO_ATTENTION}</p>
			{:else}
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each overviewData.needs_attention as member}
						<KpiScoreCard {member} />
					{/each}
				</div>
			{/if}
		</div>
	{:else}
		<p class="text-gray-500 text-sm py-8 text-center">{STRINGS.MESSAGES.NO_DATA}</p>
	{/if}
</div>

<!-- Drill-down modal -->
<KpiDrilldown
	open={drilldownOpen}
	title={drilldownTitle}
	filters={drilldownFilters}
	tasks={drilldownTasks}
	onClose={() => drilldownOpen = false}
	onExport={() => downloadCsv(STRINGS.DRILLDOWN_CSV_FILENAME, drilldownTasks)}
/>
