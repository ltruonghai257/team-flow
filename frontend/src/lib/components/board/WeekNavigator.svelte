<script lang="ts">
	import type { BoardWeekOption } from '$lib/apis/board';
	import { createEventDispatcher } from 'svelte';

	export let weekOptions: BoardWeekOption[] = [];
	export let selectedYear: number;
	export let selectedWeek: number;

	const dispatch = createEventDispatcher<{ prev: void; current: void; next: void; pick: { year: number; week: number } }>();

	function onPick(value: string) {
		const [year, week] = value.split('-').map(Number);
		dispatch('pick', { year, week });
	}
</script>

<div class="card p-4">
	<div class="flex flex-wrap items-center gap-2">
		<button class="btn-secondary text-xs px-3 py-2" on:click={() => dispatch('prev')}>Previous week</button>
		<button class="btn-primary text-xs px-3 py-2" on:click={() => dispatch('current')}>Current week</button>
		<button class="btn-secondary text-xs px-3 py-2" on:click={() => dispatch('next')}>Next week</button>
		<label class="text-xs text-gray-400 ml-auto" for="week-picker">Jump to week</label>
		<select
			id="week-picker"
			class="input w-auto text-sm"
			value={`${selectedYear}-${selectedWeek}`}
			on:change={(e) => onPick((e.target as HTMLSelectElement).value)}
		>
			{#each weekOptions as option}
				<option value={`${option.iso_year}-${option.iso_week}`}>
					{option.iso_year} · W{option.iso_week}
				</option>
			{/each}
		</select>
	</div>
</div>
