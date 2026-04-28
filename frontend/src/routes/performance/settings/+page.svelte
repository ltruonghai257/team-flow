<script lang="ts">
	import { onMount } from 'svelte';
	import { performance } from '$lib/apis';
	import KpiWeightSettings from '$lib/components/performance/KpiWeightSettings.svelte';
	import { toast } from 'svelte-sonner';

	const STRINGS = {
		TOAST: {
			SUCCESS: 'KPI weights updated.',
			ERROR_TOTAL: 'Total weight must equal 100%.',
			ERROR_DEFAULT: 'Failed to save weights',
		},
		GUIDE: {
			TITLE: 'How KPI weights work',
			DESCRIPTION: 'Each member\'s KPI score (0–100) is a weighted average of five dimension scores. Adjust the weights below to reflect what matters most to your team.',
			DIMENSIONS: [
				{ label: 'Workload', icon: '📋', default: '20%', desc: 'Active task count. ≤7 → 100 | 8-10 → 70 | >10 → 40' },
				{ label: 'Velocity', icon: '⚡', default: '25%', desc: 'Tasks completed in last 30 days. Each task = +10 pts, max 100.' },
				{ label: 'Cycle Time', icon: '⏱', default: '20%', desc: 'Avg hours creation→done. ≤48 h → 100 | ≤120 h → 70 | >120 h → 40' },
				{ label: 'On-Time Rate', icon: '✅', default: '20%', desc: 'Tasks finished by due date. Score = on-time % directly.' },
				{ label: 'Defects', icon: '🐛', default: '15%', desc: 'Bug MTTR. ≤72 h → 100 | ≤168 h → 70 | >168 h → 40. No bugs = 100.' },
			],
			NOTES: [
				'📐 All five weights must sum to exactly 100. The form will block saving if the total differs.',
				'🔒 Weights are stored per sub-team — different teams can have different priorities.',
				'♻️ Click Reset defaults to restore 20 / 25 / 20 / 20 / 15.',
				'🟢 Score ≥80 = Good · 🟡 60–79 = Fair · 🔴 <60 = At Risk',
			],
		},
		MESSAGES: {
			LOADING: 'Loading settings…',
		},
		DEFAULT_WEIGHTS: {
			workload_weight: 20,
			velocity_weight: 25,
			cycle_time_weight: 20,
			on_time_weight: 20,
			defect_weight: 15,
		},
	} as const;

	let weightsData = $state<any>(null);
	let weightsSaving = $state(false);

	async function loadWeights() {
		try { weightsData = await performance.kpiWeights(); } catch (e) { console.error(e); }
	}

	async function saveWeights(w: any) {
		weightsSaving = true;
		try {
			weightsData = await performance.updateKpiWeights(w);
			toast.success(STRINGS.TOAST.SUCCESS);
		} catch (e: any) {
			const msg = e?.message ?? '';
			if (msg.includes('100')) toast.error(STRINGS.TOAST.ERROR_TOTAL);
			else toast.error(msg || STRINGS.TOAST.ERROR_DEFAULT);
		} finally { weightsSaving = false; }
	}

	function resetWeights() {
		weightsData = { ...weightsData, ...STRINGS.DEFAULT_WEIGHTS };
	}

	onMount(() => {
		loadWeights();
	});
</script>

<div class="max-w-2xl space-y-6">
	<!-- How-to guide -->
	<div class="rounded-xl border border-gray-700 bg-gray-800/60 p-5 space-y-4">
		<h2 class="font-semibold text-gray-100 text-base">{STRINGS.GUIDE.TITLE}</h2>
		<p class="text-sm text-gray-400">{STRINGS.GUIDE.DESCRIPTION}</p>

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
			{#each STRINGS.GUIDE.DIMENSIONS as dim}
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
			{#each STRINGS.GUIDE.NOTES as note}
				<p>{@html note.replace(/(All five weights must sum to exactly 100\.|per sub-team|Reset defaults|≥80 = Good|60–79 = Fair|<60 = At Risk)/g, '<strong class="text-gray-300">$1</strong>')}</p>
			{/each}
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
		<p class="text-gray-500 text-sm py-4">{STRINGS.MESSAGES.LOADING}</p>
	{/if}
</div>
