<script lang="ts">
	export let online = false;
	export let size = 8;
	export let showLabel = false;
	export let label: string | null = null;
</script>

<span class="inline-flex items-center gap-1.5">
	<span
		class="rounded-full {online ? 'bg-green-500' : 'bg-gray-500'}"
		style="width:{size}px;height:{size}px"
		title={online ? 'Online' : 'Offline'}
	></span>
	{#if showLabel}
		<span class="text-xs text-gray-400">{label ?? (online ? 'Online' : 'Offline')}</span>
	{/if}
</span>
