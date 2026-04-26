<script lang="ts">
    type KpiWeights = {
        workload_weight: number;
        velocity_weight: number;
        cycle_time_weight: number;
        on_time_weight: number;
        defect_weight: number;
    };
    export let weights: KpiWeights;
    export let saving: boolean = false;
    export let onSave: (weights: KpiWeights) => void;
    export let onReset: () => void;

    let local = { ...weights };
    $: local = { ...weights };

    $: total = (local.workload_weight ?? 0) + (local.velocity_weight ?? 0) + (local.cycle_time_weight ?? 0) + (local.on_time_weight ?? 0) + (local.defect_weight ?? 0);
    $: totalOk = total === 100;

    function handleSave() {
        if (totalOk) onSave(local);
    }
</script>

<div class="bg-gray-800 rounded-lg border border-gray-700 p-5 max-w-md flex flex-col gap-4">
    <h3 class="font-semibold text-gray-100">KPI Weight Settings</h3>
    <p class="text-xs text-gray-400">Adjust how each category contributes to the KPI score. Weights must total 100.</p>

    <div class="flex flex-col gap-3">
        {#each [
            { key: 'workload_weight', label: 'Workload' },
            { key: 'velocity_weight', label: 'Velocity' },
            { key: 'cycle_time_weight', label: 'Cycle Time' },
            { key: 'on_time_weight', label: 'On-Time Rate' },
            { key: 'defect_weight', label: 'Defects / Quality' },
        ] as field}
            <div class="flex items-center justify-between gap-4">
                <label for="w-{field.key}" class="text-sm text-gray-300 w-36">{field.label}</label>
                <input
                    id="w-{field.key}"
                    type="number"
                    min="0"
                    max="100"
                    class="w-20 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-gray-100 text-sm text-right"
                    bind:value={local[field.key as keyof typeof local]}
                />
            </div>
        {/each}
    </div>

    <div class="flex items-center justify-between text-sm mt-1">
        <span class="text-gray-400">Total: <span class="{totalOk ? 'text-green-400' : 'text-red-400'} font-semibold">{total}</span></span>
        {#if !totalOk}
            <span class="text-red-400 text-xs">Total weight must equal 100</span>
        {/if}
    </div>

    <div class="flex gap-3 pt-1">
        <button
            type="button"
            on:click={handleSave}
            disabled={!totalOk || saving}
            class="px-4 py-2 rounded bg-primary-600 text-white text-sm font-medium hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
            {saving ? 'Saving…' : 'Save weights'}
        </button>
        <button
            type="button"
            on:click={onReset}
            class="px-4 py-2 rounded border border-gray-600 text-gray-400 text-sm hover:text-gray-200 hover:border-gray-400 transition-colors"
        >
            Reset defaults
        </button>
    </div>
</div>
