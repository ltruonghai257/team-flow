<script lang="ts">
    export let active: string;
    export let tabs: { id: string; label: string; icon?: unknown }[] = [];
    export let basePath: string = '/performance';
</script>

<div class="flex overflow-x-auto gap-1 border-b border-gray-700 pb-0 scrollbar-none">
    {#each tabs as tab}
        <a
            href="{basePath}/{tab.id}"
            aria-current={active === tab.id ? 'page' : undefined}
            class="px-4 py-2 text-sm font-medium whitespace-nowrap rounded-t transition-colors
                {active === tab.id
                    ? 'bg-primary-600/20 text-primary-400 border-b-2 border-primary-400'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'}"
        >
            {tab.label}
        </a>
    {/each}
</div>
