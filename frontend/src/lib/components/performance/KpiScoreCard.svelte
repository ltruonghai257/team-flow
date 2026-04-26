<script lang="ts">
    import KpiWarnButton from './KpiWarnButton.svelte';

    type KpiMember = {
        user_id: number;
        full_name: string;
        avatar_url?: string | null;
        kpi_score: number;
        trend: string;
        reasons: { label: string; severity: string }[];
        breakdown: { workload: number; velocity: number; cycle_time: number; on_time: number; defects: number };
    };
    export let member: KpiMember;
    export let onDrilldown: ((member: KpiMember) => void) | undefined = undefined;
    export let hideDetailLink: boolean = false;

    $: initials = member.full_name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase();
    $: scoreColor = member.kpi_score >= 80 ? 'text-green-400' : member.kpi_score >= 60 ? 'text-yellow-400' : 'text-red-400';
    $: scoreBg = member.kpi_score >= 80 ? 'bg-green-400' : member.kpi_score >= 60 ? 'bg-yellow-400' : 'bg-red-400';
    $: trendIcon = member.trend === 'up' ? '↑' : member.trend === 'down' ? '↓' : '→';
    $: trendColor = member.trend === 'up' ? 'text-green-400' : member.trend === 'down' ? 'text-red-400' : 'text-gray-400';

    type DimKey = 'workload' | 'velocity' | 'cycle_time' | 'on_time' | 'defects';

    const DIMS: { key: DimKey; label: string; tooltip: string }[] = [
        {
            key: 'workload',
            label: 'Workload',
            tooltip: 'Active task count right now.\n≤7 tasks → 100  |  8–10 → 70  |  >10 → 40',
        },
        {
            key: 'velocity',
            label: 'Velocity',
            tooltip: 'Tasks completed in the last 30 days.\nEach task = +10 pts, capped at 100.',
        },
        {
            key: 'cycle_time',
            label: 'Cycle Time',
            tooltip: 'Average hours from task creation to completion.\n≤48 h → 100  |  49–120 h → 70  |  >120 h → 40\nNo data → 40 (conservative).',
        },
        {
            key: 'on_time',
            label: 'On-Time',
            tooltip: 'Percentage of completed tasks delivered by their due date.\n100% on-time = 100 pts. Equals the on-time rate directly.',
        },
        {
            key: 'defects',
            label: 'Defects',
            tooltip: 'Mean Time to Resolve (MTTR) bugs assigned to this member.\n≤72 h → 100  |  73–168 h → 70  |  >168 h → 40\nNo bugs → 100 (best case).',
        },
    ];

    function dimScore(key: DimKey): number {
        return member.breakdown[key] ?? 0;
    }

    function dimBarColor(score: number): string {
        if (score >= 80) return 'bg-green-500';
        if (score >= 60) return 'bg-yellow-500';
        return 'bg-red-500';
    }

    let tooltip: string | null = null;
    let tooltipStyle = '';

    function showTooltip(e: MouseEvent, text: string) {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
        tooltip = text;
        // Position above the row, left-aligned, clamped so it never goes off-screen
        const tipW = 288; // w-72
        let left = rect.left;
        if (left + tipW > window.innerWidth - 8) left = window.innerWidth - tipW - 8;
        if (left < 8) left = 8;
        tooltipStyle = `position:fixed;left:${left}px;top:${rect.top - 8}px;transform:translateY(-100%);`;
    }
    function hideTooltip() { tooltip = null; }
</script>

<div class="bg-gray-800 rounded-lg p-4 flex flex-col gap-3 border border-gray-700 relative">

    <!-- Header row: avatar + name + KPI score -->
    <div class="flex items-center gap-3">
        {#if member.avatar_url}
            <img src={member.avatar_url} alt={member.full_name} class="w-10 h-10 rounded-full object-cover shrink-0" />
        {:else}
            <div class="w-10 h-10 rounded-full bg-primary-700 flex items-center justify-center text-white font-semibold text-sm shrink-0">
                {initials}
            </div>
        {/if}
        <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-100 truncate">{member.full_name}</p>
            <p class="text-xs {trendColor}">{trendIcon} {member.trend}</p>
        </div>
        <div class="text-right">
            <p class="text-2xl font-bold {scoreColor}">{member.kpi_score}</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-wide">/ 100</p>
        </div>
    </div>

    <!-- Score band legend -->
    <div class="flex gap-2 text-[10px] text-gray-500">
        <span class="text-green-400 font-medium">● ≥80 Good</span>
        <span class="text-yellow-400 font-medium">● 60–79 Fair</span>
        <span class="text-red-400 font-medium">● &lt;60 At Risk</span>
    </div>

    <!-- Per-dimension breakdown bars -->
    <div class="flex flex-col gap-2">
        {#each DIMS as dim}
            {@const score = dimScore(dim.key)}
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div
                class="group cursor-help"
                on:mouseenter={(e) => showTooltip(e, dim.tooltip)}
                on:mouseleave={hideTooltip}
            >
                <div class="flex items-center justify-between mb-0.5">
                    <span class="text-xs text-gray-400 flex items-center gap-1">
                        {dim.label}
                        <span class="text-gray-600 text-[9px]">ⓘ</span>
                    </span>
                    <span class="text-xs font-semibold text-gray-200">{score}</span>
                </div>
                <div class="h-1.5 w-full bg-gray-700 rounded-full overflow-hidden">
                    <div
                        class="h-full rounded-full transition-all {dimBarColor(score)}"
                        style="width: {score}%"
                    ></div>
                </div>
            </div>
        {/each}
    </div>

    <!-- Alert reasons -->
    {#if member.reasons.length > 0}
        <ul class="space-y-1 pt-1 border-t border-gray-700">
            {#each member.reasons as reason}
                <li class="text-xs px-2 py-0.5 rounded flex gap-1 items-start {reason.severity === 'critical' ? 'bg-red-900/40 text-red-300' : 'bg-yellow-900/40 text-yellow-300'}">
                    <span class="shrink-0">{reason.severity === 'critical' ? '⚠' : '!'}</span>
                    {reason.label}
                </li>
            {/each}
        </ul>
    {/if}

    <!-- Footer actions -->
    <div class="flex justify-between items-center pt-1 border-t border-gray-700">
        {#if hideDetailLink}
            <span class="text-xs text-gray-600 italic">Demo member</span>
        {:else}
            <a href="/performance/{member.user_id}" class="text-xs text-primary-400 hover:underline">View detail →</a>
        {/if}
        <div class="flex items-center gap-2">
            {#if !hideDetailLink}
                <KpiWarnButton userId={member.user_id} userName={member.full_name} kpiScore={member.kpi_score} />
            {/if}
            {#if onDrilldown}
                <button type="button" on:click={() => onDrilldown && onDrilldown(member)} class="text-xs text-gray-400 hover:text-gray-200 transition-colors">
                    Drill down
                </button>
            {/if}
        </div>
    </div>

    <!-- Tooltip (portal-style fixed positioning) -->
    {#if tooltip}
        <div
            style={tooltipStyle}
            class="z-[9999] w-72 bg-gray-900 border border-gray-600 rounded-lg p-3 text-xs text-gray-300 shadow-xl whitespace-pre-line pointer-events-none"
            role="tooltip"
        >
            {tooltip}
        </div>
    {/if}
</div>
