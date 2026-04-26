<script lang="ts">
    export let filters: Record<string, unknown> = {};
    export let options: { sprints?: { id: number; name: string }[]; projects?: { id: number; name: string }[]; members?: { id: number; name: string }[]; task_types?: string[] } = {};
    export let mode: 'sprint' | 'quality' | 'members' = 'sprint';
    export let onChange: (filters: Record<string, unknown>) => void;

    function update(key: string, value: unknown) {
        onChange({ ...filters, [key]: value || undefined });
    }

    function reset() {
        onChange({});
    }
</script>

<div class="flex flex-wrap gap-3 items-end text-sm">
    {#if mode === 'sprint' && options.sprints && options.sprints.length > 0}
        <div class="flex flex-col gap-1">
            <label for="kf-sprint" class="text-xs text-gray-400">Sprint</label>
            <select
                id="kf-sprint"
                class="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-gray-200 text-sm"
                value={filters.sprint_id ?? ''}
                on:change={(e) => update('sprint_id', (e.target as HTMLSelectElement).value)}
            >
                <option value="">All sprints</option>
                {#each options.sprints as s}
                    <option value={s.id}>{s.name}</option>
                {/each}
            </select>
        </div>
    {/if}

    {#if options.projects && options.projects.length > 0}
        <div class="flex flex-col gap-1">
            <label for="kf-project" class="text-xs text-gray-400">Project</label>
            <select
                id="kf-project"
                class="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-gray-200 text-sm"
                value={filters.project_id ?? ''}
                on:change={(e) => update('project_id', (e.target as HTMLSelectElement).value)}
            >
                <option value="">All projects</option>
                {#each options.projects as p}
                    <option value={p.id}>{p.name}</option>
                {/each}
            </select>
        </div>
    {/if}

    {#if options.members && options.members.length > 0}
        <div class="flex flex-col gap-1">
            <label for="kf-member" class="text-xs text-gray-400">Member</label>
            <select
                id="kf-member"
                class="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-gray-200 text-sm"
                value={filters.member_id ?? ''}
                on:change={(e) => update('member_id', (e.target as HTMLSelectElement).value)}
            >
                <option value="">All members</option>
                {#each options.members as m}
                    <option value={m.id}>{m.name}</option>
                {/each}
            </select>
        </div>
    {/if}

    {#if options.task_types && options.task_types.length > 0}
        <div class="flex flex-col gap-1">
            <label for="kf-type" class="text-xs text-gray-400">Task type</label>
            <select
                id="kf-type"
                class="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-gray-200 text-sm"
                value={filters.task_type ?? ''}
                on:change={(e) => update('task_type', (e.target as HTMLSelectElement).value)}
            >
                <option value="">All types</option>
                {#each options.task_types as t}
                    <option value={t}>{t}</option>
                {/each}
            </select>
        </div>
    {/if}

    <div class="flex flex-col gap-1">
        <label for="kf-start" class="text-xs text-gray-400">From</label>
        <input
            id="kf-start"
            type="date"
            class="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-gray-200 text-sm"
            value={filters.start ?? ''}
            on:change={(e) => update('start', (e.target as HTMLInputElement).value)}
        />
    </div>

    <div class="flex flex-col gap-1">
        <label for="kf-end" class="text-xs text-gray-400">To</label>
        <input
            id="kf-end"
            type="date"
            class="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-gray-200 text-sm"
            value={filters.end ?? ''}
            on:change={(e) => update('end', (e.target as HTMLInputElement).value)}
        />
    </div>

    <button
        type="button"
        on:click={reset}
        class="px-3 py-1 text-xs rounded border border-gray-600 text-gray-400 hover:text-gray-200 hover:border-gray-400 transition-colors"
    >
        Clear
    </button>
</div>
