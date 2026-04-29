<script lang="ts">
	import { ChevronDown, ChevronRight } from 'lucide-svelte';
	import { slide } from 'svelte/transition';

	export let title: string;
	export let count: number = 0;
	export let isOpen = true;

	function toggle() {
		isOpen = !isOpen;
	}
</script>

<div class="flex flex-col h-full min-w-0">
	<!-- Mobile header -->
	<button
		class="flex items-center justify-between p-3 bg-gray-900 border border-gray-800 rounded-lg mb-2 md:hidden"
		on:click={toggle}
	>
		<div class="flex items-center gap-2">
			{#if isOpen}
				<ChevronDown size={18} class="text-gray-400" />
			{:else}
				<ChevronRight size={18} class="text-gray-400" />
			{/if}
			<h2 class="font-semibold text-white">{title}</h2>
			<span class="px-2 py-0.5 bg-gray-800 text-gray-400 text-xs rounded-full">{count}</span>
		</div>
	</button>

	<!-- Desktop header -->
	<div class="hidden md:flex items-center justify-between mb-4 px-1">
		<div class="flex items-center gap-2">
			<h2 class="font-semibold text-gray-300 uppercase tracking-wider text-xs">{title}</h2>
			<span class="px-2 py-0.5 bg-gray-800 text-gray-500 text-xs rounded-full font-medium">{count}</span>
		</div>
	</div>

	<!-- Content -->
	<div class="{isOpen ? 'block' : 'hidden md:block'} flex-1">
		{#if isOpen}
			<div class="space-y-4" transition:slide={{ duration: 200 }}>
				<slot />
			</div>
		{:else}
			<div class="space-y-4 hidden md:block">
				<slot />
			</div>
		{/if}
	</div>
</div>
