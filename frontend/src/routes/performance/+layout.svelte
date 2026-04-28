<script lang="ts">
	import { page } from '$app/stores';
	import KpiTabs from '$lib/components/performance/KpiTabs.svelte';

	const STRINGS = {
		PAGE_TITLE: 'Performance Dashboard',
		PAGE_SUBTITLE: 'Track member KPI health, sprint delivery, and quality trends.',
		BASE_PATH: '/performance',
		DEFAULT_TAB: 'overview',
		TABS: [
			{ id: 'overview', label: 'Overview', description: 'View overall team KPI scores, member scorecards, and identify members needing attention.' },
			{ id: 'sprint', label: 'Sprint', description: 'Track sprint velocity, burndown progress, and delivery metrics over time.' },
			{ id: 'quality', label: 'Quality', description: 'Monitor bug trends, defect rates, and mean time to resolve (MTTR) metrics.' },
			{ id: 'members', label: 'Members', description: 'Analyze individual member throughput, cycle time, and task completion patterns.' },
			{ id: 'settings', label: 'Settings', description: 'Configure KPI weight settings to customize how scores are calculated for your team.' },
		],
	};

	let activeTab = $derived($page.url.pathname.split('/').pop() || STRINGS.DEFAULT_TAB);
	let activeTabDescription = $derived(STRINGS.TABS.find(t => t.id === activeTab)?.description || '');
</script>

<div class="p-4 md:p-8 max-w-[1800px] mx-auto space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold text-white tracking-tight">{STRINGS.PAGE_TITLE}</h1>
			<p class="text-gray-400 mt-1">{STRINGS.PAGE_SUBTITLE}</p>
		</div>
	</div>

	<!-- Tabs -->
	<KpiTabs tabs={STRINGS.TABS} active={activeTab} basePath={STRINGS.BASE_PATH} />

	<!-- Tab description -->
	{#if activeTabDescription}
		<div class="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
			<p class="text-sm text-gray-300">{activeTabDescription}</p>
		</div>
	{/if}

	<!-- Slot for child routes -->
	<slot />
</div>
