<script lang="ts">
	import { onMount } from 'svelte';
	import { performance } from '$lib/apis';
	import { downloadCsv } from '$lib/components/performance/csv';
	import KpiFilters from '$lib/components/performance/KpiFilters.svelte';
	import KpiChartPanel from '$lib/components/performance/KpiChartPanel.svelte';
	import KpiDrilldown from '$lib/components/performance/KpiDrilldown.svelte';

	const STRINGS = {
		CHARTS: {
			THROUGHPUT: {
				TITLE: 'Throughput by Member & Type',
				SUBTITLE: 'Tasks completed per member by type (last 8 weeks)',
				CSV_FILENAME: 'throughput.csv',
			},
			CYCLE_TIME: {
				TITLE: 'Cycle Time by Task Type',
				SUBTITLE: 'Average hours to complete tasks by type (last 3 months)',
				CSV_FILENAME: 'cycle-time.csv',
			},
		},
		DRILLDOWN: {
			CSV_FILENAME: 'drilldown.csv',
		},
	} as const;

	let membersData = $state<any>(null);
	let membersLoading = $state(false);
	let memberFilters = $state<Record<string, unknown>>({});

	// Drilldown
	let drilldownOpen = $state(false);
	let drilldownTitle = $state('');
	let drilldownFilters = $state<Record<string, unknown>>({});
	let drilldownTasks = $state<any[]>([]);

	async function loadMembers() {
		membersLoading = true;
		try { membersData = await performance.kpiMembers(memberFilters as any); } catch (e) { console.error(e); } finally { membersLoading = false; }
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

	onMount(() => {
		loadMembers();
	});
</script>

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
			title={STRINGS.CHARTS.THROUGHPUT.TITLE}
			subtitle={STRINGS.CHARTS.THROUGHPUT.SUBTITLE}
			series={membersData?.throughput_series ?? []}
			onExport={() => downloadCsv(STRINGS.CHARTS.THROUGHPUT.CSV_FILENAME, (membersData?.throughput_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
			onPointClick={(pt) => openDrilldown('throughput', { ...memberFilters }, STRINGS.CHARTS.THROUGHPUT.TITLE + ' — ' + pt.label)}
		/>
		<KpiChartPanel
			title={STRINGS.CHARTS.CYCLE_TIME.TITLE}
			subtitle={STRINGS.CHARTS.CYCLE_TIME.SUBTITLE}
			series={membersData?.cycle_time_series ?? []}
			onExport={() => downloadCsv(STRINGS.CHARTS.CYCLE_TIME.CSV_FILENAME, (membersData?.cycle_time_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
		/>
	{/if}
</div>

<!-- Drill-down modal -->
<KpiDrilldown
	open={drilldownOpen}
	title={drilldownTitle}
	filters={drilldownFilters}
	tasks={drilldownTasks}
	onClose={() => drilldownOpen = false}
	onExport={() => downloadCsv(STRINGS.DRILLDOWN.CSV_FILENAME, drilldownTasks)}
/>
