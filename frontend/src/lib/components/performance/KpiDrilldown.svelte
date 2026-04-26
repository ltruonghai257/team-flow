<script lang="ts">
    export let open: boolean;
    export let title: string;
    export let filters: Record<string, unknown> = {};
    export let tasks: {
        id: number;
        title: string;
        task_type?: string | null;
        assignee?: string | null;
        project?: string | null;
        sprint?: string | null;
        status?: string | null;
        created_at?: string | null;
        completed_at?: string | null;
    }[] = [];
    export let onClose: () => void;
    export let onExport: () => void;

    $: activeFilters = Object.entries(filters).filter(([, v]) => v !== undefined && v !== null && v !== '');
</script>

{#if open}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60" on:click|self={onClose}>
        <div class="bg-gray-900 border border-gray-700 rounded-t-2xl sm:rounded-2xl w-full sm:max-w-3xl max-h-[80vh] flex flex-col">
            <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700">
                <h2 class="font-semibold text-gray-100">{title}</h2>
                <div class="flex gap-2">
                    <button type="button" on:click={onExport} class="text-xs px-3 py-1 rounded border border-gray-600 text-gray-400 hover:text-gray-200 transition-colors">
                        Export CSV
                    </button>
                    <button type="button" on:click={onClose} class="text-gray-400 hover:text-gray-200 text-xl leading-none">&times;</button>
                </div>
            </div>

            {#if activeFilters.length > 0}
                <div class="px-5 py-2 flex flex-wrap gap-2 border-b border-gray-800">
                    {#each activeFilters as [k, v]}
                        <span class="text-xs bg-gray-700 text-gray-300 rounded px-2 py-0.5">{k}: {v}</span>
                    {/each}
                </div>
            {/if}

            <div class="overflow-y-auto flex-1">
                {#if tasks.length === 0}
                    <p class="text-center text-gray-500 py-10">No tasks found.</p>
                {:else}
                    <table class="w-full text-sm">
                        <thead class="sticky top-0 bg-gray-900 border-b border-gray-700">
                            <tr class="text-left text-xs text-gray-400">
                                <th class="px-4 py-2">Title</th>
                                <th class="px-4 py-2">Type</th>
                                <th class="px-4 py-2">Assignee</th>
                                <th class="px-4 py-2">Project</th>
                                <th class="px-4 py-2">Status</th>
                                <th class="px-4 py-2">Completed</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each tasks as task}
                                <tr class="border-b border-gray-800 hover:bg-gray-800/40">
                                    <td class="px-4 py-2 text-gray-200 max-w-xs truncate">{task.title}</td>
                                    <td class="px-4 py-2 text-gray-400">{task.task_type ?? '-'}</td>
                                    <td class="px-4 py-2 text-gray-400">{task.assignee ?? '-'}</td>
                                    <td class="px-4 py-2 text-gray-400">{task.project ?? '-'}</td>
                                    <td class="px-4 py-2 text-gray-400">{task.status ?? '-'}</td>
                                    <td class="px-4 py-2 text-gray-400">{task.completed_at ? task.completed_at.slice(0, 10) : '-'}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                {/if}
            </div>
        </div>
    </div>
{/if}
