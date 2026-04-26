<script lang="ts">
    export let title: string;
    export let subtitle: string;
    export let series: { name: string; points: { label: string; value: number }[] }[] = [];
    export let emptyHeading: string = 'Not enough data';
    export let emptyBody: string = 'No data available for the selected period.';
    export let onExport: (() => void) | undefined = undefined;
    export let onPointClick: ((point: { label: string; value: number; series: string }) => void) | undefined = undefined;

    $: hasData = series.some((s) => s.points.length > 0);

    function allPoints() {
        return series.flatMap((s) => s.points.map((p) => ({ ...p, series: s.name })));
    }

    function maxVal() {
        const pts = series.flatMap((s) => s.points.map((p) => p.value));
        return pts.length ? Math.max(...pts, 1) : 1;
    }

    const COLORS = ['#6366f1', '#22d3ee', '#f59e0b', '#34d399', '#f87171'];
</script>

<div class="bg-gray-800 rounded-lg border border-gray-700 p-4 flex flex-col gap-3">
    <div class="flex items-start justify-between gap-2">
        <div>
            <h3 class="font-semibold text-gray-100">{title}</h3>
            <p class="text-xs text-gray-400 mt-0.5">{subtitle}</p>
        </div>
        {#if onExport}
            <button
                type="button"
                on:click={onExport}
                class="text-xs px-3 py-1 rounded border border-gray-600 text-gray-400 hover:text-gray-200 hover:border-gray-400 transition-colors whitespace-nowrap"
            >
                Export CSV
            </button>
        {/if}
    </div>

    {#if !hasData}
        <div class="py-8 text-center">
            <p class="text-gray-400 font-medium">{emptyHeading}</p>
            <p class="text-xs text-gray-500 mt-1">{emptyBody}</p>
        </div>
    {:else}
        <div class="overflow-x-auto">
            <svg viewBox="0 0 400 120" class="w-full" style="min-width: 300px;">
                {#each series as s, si}
                    {@const color = COLORS[si % COLORS.length]}
                    {@const pts = s.points}
                    {#if pts.length > 1}
                        {@const w = 400 / (pts.length - 1)}
                        {@const mx = maxVal()}
                        <polyline
                            points={pts.map((p, i) => `${i * w},${110 - (p.value / mx) * 100}`).join(' ')}
                            fill="none"
                            stroke={color}
                            stroke-width="2"
                        />
                        {#each pts as pt, i}
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <circle
                                cx={i * w}
                                cy={110 - (pt.value / mx) * 100}
                                r="4"
                                fill={color}
                                style="cursor: pointer;"
                                on:click={() => onPointClick && onPointClick({ ...pt, series: s.name })}
                            />
                        {/each}
                    {:else if pts.length === 1}
                        {@const mx = maxVal()}
                        {#each pts as pt, i}
                            {@const barW = Math.max(20, 380 / (series.length || 1))}
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <rect
                                x={si * (barW + 4)}
                                y={110 - (pt.value / mx) * 100}
                                width={barW}
                                height={(pt.value / mx) * 100}
                                fill={color}
                                style="cursor: pointer;"
                                on:click={() => onPointClick && onPointClick({ ...pt, series: s.name })}
                            />
                        {/each}
                    {/if}
                {/each}
            </svg>
        </div>

        <div class="flex flex-wrap gap-3">
            {#each series as s, si}
                <span class="flex items-center gap-1 text-xs text-gray-400">
                    <span class="inline-block w-3 h-3 rounded-full" style="background:{COLORS[si % COLORS.length]}"></span>
                    {s.name}
                </span>
            {/each}
        </div>
    {/if}
</div>
