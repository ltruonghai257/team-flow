<script lang="ts">
	import { statusColorPalette } from '$lib/utils';
	import type { CustomStatus } from '$lib/api';

	export let status: CustomStatus;
	export let onSave: (data: { name: string; color: string; is_done: boolean }) => void = () => {};
	export let onCancel: () => void = () => {};

	let name = status.name;
	let color = status.color;
	let is_done = status.is_done;
	let customHex = '';

	function applyHex() {
		const hex = customHex.trim();
		if (/^#[0-9a-fA-F]{6}$/.test(hex)) color = hex;
	}

	function handleSave() {
		if (!name.trim()) return;
		onSave({ name: name.trim(), color, is_done });
	}
</script>

<div class="rounded bg-gray-750 border border-gray-600 p-3 space-y-3">
	{#if status.is_archived}
		<span class="inline-block rounded bg-yellow-800 px-2 py-0.5 text-xs text-yellow-200">Archived</span>
	{/if}

	<div class="flex items-center gap-2">
		<input
			bind:value={name}
			placeholder="Status name"
			class="flex-1 rounded bg-gray-700 px-3 py-1.5 text-sm text-white border border-gray-600 focus:outline-none focus:border-indigo-500"
		/>
	</div>

	<div class="text-xs text-gray-400">
		Slug: <code class="font-mono text-gray-300">{status.slug}</code>
	</div>

	<div class="flex flex-wrap gap-2">
		{#each statusColorPalette as hex}
			<button
				on:click={() => (color = hex)}
				class="h-6 w-6 rounded-full border-2 transition-transform {color === hex
					? 'border-white scale-110'
					: 'border-transparent hover:scale-105'}"
				style="background-color: {hex};"
				title={hex}
				aria-label="Color {hex}"
			></button>
		{/each}
	</div>

	<div class="flex items-center gap-2">
		<input
			bind:value={customHex}
			placeholder="#hex"
			maxlength={7}
			class="w-24 rounded bg-gray-700 px-2 py-1 text-xs text-white border border-gray-600 font-mono"
		/>
		<button
			on:click={applyHex}
			class="rounded bg-gray-600 px-2 py-1 text-xs text-gray-200 hover:bg-gray-500"
		>
			Apply
		</button>
		<div class="h-5 w-5 rounded-full" style="background-color: {color};"></div>
	</div>

	<label class="flex items-center gap-2 cursor-pointer">
		<input type="checkbox" bind:checked={is_done} class="accent-indigo-500" />
		<span class="text-sm text-gray-300">Marks tasks complete</span>
	</label>

	<div class="flex gap-2 justify-end">
		<button
			on:click={onCancel}
			class="rounded px-3 py-1.5 text-sm text-gray-400 hover:bg-gray-700"
		>
			Cancel
		</button>
		<button
			on:click={handleSave}
			class="rounded bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500"
		>
			Save
		</button>
	</div>
</div>
