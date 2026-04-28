<script lang="ts">
	import { onMount } from 'svelte';
	import { performance } from '$lib/apis';
	import { downloadCsv } from '$lib/components/performance/csv';
	import KpiFilters from '$lib/components/performance/KpiFilters.svelte';
	import KpiChartPanel from '$lib/components/performance/KpiChartPanel.svelte';
	import KpiDrilldown from '$lib/components/performance/KpiDrilldown.svelte';

	const STRINGS = {
		CHARTS: {
			BUGS: {
				TITLE: 'Bugs Reported vs Resolved',
				SUBTITLE: 'Daily bug activity for the selected period',
				CSV_FILENAME: 'bugs.csv',
			},
			MTTR: {
				TITLE: 'MTTR by Member',
				SUBTITLE: 'Mean time to resolve bugs (hours)',
				CSV_FILENAME: 'mttr.csv',
			},
		},
		DRILLDOWN: {
			CSV_FILENAME: 'drilldown.csv',
		},
	} as const;

	let qualityData = $state<any>(null);
	let qualityLoading = $state(false);
	let qualityFilters = $state<Record<string, unknown>>({});

	// Drilldown
	let drilldownOpen = $state(false);
	let drilldownTitle = $state('');
	let drilldownFilters = $state<Record<string, unknown>>({});
	let drilldownTasks = $state<any[]>([]);

	async function loadQuality() {
		qualityLoading = true;
		try { qualityData = await performance.kpiQuality(qualityFilters as any); } catch (e) { console.error(e); } finally { qualityLoading = false; }
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
		loadQuality();
	});
</script>

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
			title={STRINGS.CHARTS.BUGS.TITLE}
			subtitle={STRINGS.CHARTS.BUGS.SUBTITLE}
			series={qualityData?.bugs_series ?? []}
			onExport={() => downloadCsv(STRINGS.CHARTS.BUGS.CSV_FILENAME, (qualityData?.bugs_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
			onPointClick={(pt) => openDrilldown('bugs', { ...qualityFilters }, STRINGS.CHARTS.BUGS.TITLE + ' — ' + pt.label)}
		/>
		<KpiChartPanel
			title={STRINGS.CHARTS.MTTR.TITLE}
			subtitle={STRINGS.CHARTS.MTTR.SUBTITLE}
			series={qualityData?.mttr_series ?? []}
			onExport={() => downloadCsv(STRINGS.CHARTS.MTTR.CSV_FILENAME, (qualityData?.mttr_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
			onPointClick={(pt) => openDrilldown('mttr', { ...qualityFilters, member_id: undefined }, STRINGS.CHARTS.MTTR.TITLE + ' — ' + pt.label)}
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
