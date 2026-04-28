<script lang="ts">
	import { onMount } from 'svelte';
	import { performance } from '$lib/apis';
	import { downloadCsv } from '$lib/components/performance/csv';
	import KpiFilters from '$lib/components/performance/KpiFilters.svelte';
	import KpiChartPanel from '$lib/components/performance/KpiChartPanel.svelte';
	import KpiDrilldown from '$lib/components/performance/KpiDrilldown.svelte';

	const STRINGS = {
		CHARTS: {
			VELOCITY: {
				TITLE: 'Velocity',
				SUBTITLE: 'Completed tasks per member over last 6 sprints',
				CSV_FILENAME: 'velocity.csv',
			},
			BURNDOWN: {
				TITLE: 'Burndown',
				SUBTITLE: 'Remaining tasks in selected sprint',
				CSV_FILENAME: 'burndown.csv',
			},
		},
		DRILLDOWN: {
			CSV_FILENAME: 'drilldown.csv',
		},
	} as const;

	let sprintData = $state<any>(null);
	let sprintLoading = $state(false);
	let sprintFilters = $state<Record<string, unknown>>({});

	// Drilldown
	let drilldownOpen = $state(false);
	let drilldownTitle = $state('');
	let drilldownFilters = $state<Record<string, unknown>>({});
	let drilldownTasks = $state<any[]>([]);

	async function loadSprint() {
		sprintLoading = true;
		try { sprintData = await performance.kpiSprint(sprintFilters as any); } catch (e) { console.error(e); } finally { sprintLoading = false; }
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
		loadSprint();
	});
</script>

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
			title={STRINGS.CHARTS.VELOCITY.TITLE}
			subtitle={STRINGS.CHARTS.VELOCITY.SUBTITLE}
			series={sprintData?.velocity_series ?? []}
			onExport={() => downloadCsv(STRINGS.CHARTS.VELOCITY.CSV_FILENAME, (sprintData?.velocity_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
			onPointClick={(pt) => openDrilldown('velocity', { ...sprintFilters }, STRINGS.CHARTS.VELOCITY.TITLE + ' — ' + pt.label)}
		/>
		<KpiChartPanel
			title={STRINGS.CHARTS.BURNDOWN.TITLE}
			subtitle={STRINGS.CHARTS.BURNDOWN.SUBTITLE}
			series={sprintData?.burndown_series ?? []}
			onExport={() => downloadCsv(STRINGS.CHARTS.BURNDOWN.CSV_FILENAME, (sprintData?.burndown_series ?? []).flatMap((s: any) => s.points.map((p: any) => ({ series: s.name, ...p }))))}
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
