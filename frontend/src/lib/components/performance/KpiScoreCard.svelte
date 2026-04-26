<script lang="ts">
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

    $: initials = member.full_name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase();
    $: scoreColor = member.kpi_score >= 80 ? 'text-green-400' : member.kpi_score >= 60 ? 'text-yellow-400' : 'text-red-400';
    $: trendIcon = member.trend === 'up' ? '↑' : member.trend === 'down' ? '↓' : '→';
</script>

<div class="bg-gray-800 rounded-lg p-4 flex flex-col gap-3 border border-gray-700">
    <div class="flex items-center gap-3">
        {#if member.avatar_url}
            <img src={member.avatar_url} alt={member.full_name} class="w-10 h-10 rounded-full object-cover" />
        {:else}
            <div class="w-10 h-10 rounded-full bg-primary-700 flex items-center justify-center text-white font-semibold text-sm">
                {initials}
            </div>
        {/if}
        <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-100 truncate">{member.full_name}</p>
            <p class="text-xs text-gray-400">{trendIcon} {member.trend}</p>
        </div>
        <div class="text-right">
            <p class="text-2xl font-bold {scoreColor}">{member.kpi_score}</p>
            <p class="text-xs text-gray-500">KPI</p>
        </div>
    </div>

    {#if member.reasons.length > 0}
        <ul class="space-y-1">
            {#each member.reasons.slice(0, 3) as reason}
                <li class="text-xs px-2 py-0.5 rounded {reason.severity === 'critical' ? 'bg-red-900/40 text-red-300' : 'bg-yellow-900/40 text-yellow-300'}">
                    {reason.label}
                </li>
            {/each}
        </ul>
    {/if}

    <div class="grid grid-cols-5 gap-1 text-center text-xs">
        <div><p class="text-gray-500">Work</p><p class="font-medium text-gray-200">{member.breakdown.workload}</p></div>
        <div><p class="text-gray-500">Vel</p><p class="font-medium text-gray-200">{member.breakdown.velocity}</p></div>
        <div><p class="text-gray-500">Cycle</p><p class="font-medium text-gray-200">{member.breakdown.cycle_time}</p></div>
        <div><p class="text-gray-500">OnTime</p><p class="font-medium text-gray-200">{member.breakdown.on_time}</p></div>
        <div><p class="text-gray-500">Defects</p><p class="font-medium text-gray-200">{member.breakdown.defects}</p></div>
    </div>

    <div class="flex justify-between items-center">
        <a href="/performance/{member.user_id}" class="text-xs text-primary-400 hover:underline">View detail</a>
        {#if onDrilldown}
            <button type="button" on:click={() => onDrilldown && onDrilldown(member)} class="text-xs text-gray-400 hover:text-gray-200">Drill down</button>
        {/if}
    </div>
</div>
