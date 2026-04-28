<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { ChevronDown, ChevronUp } from 'lucide-svelte';
	import { updates } from '$lib/apis';
	import { toast } from 'svelte-sonner';

	export let templateFields: string[] = [];
	export let fieldTypes: Record<string, string> = {};

	const dispatch = createEventDispatcher();

	let expanded = false;
	let fieldValues: Record<string, string> = {};
	let submitting = false;

	$: fieldValues = Object.fromEntries(templateFields.map((f) => [f, '']));

	$: allFieldsEmpty = templateFields.every((f) => !(fieldValues[f] ?? '').trim());

	async function handleSubmit() {
		submitting = true;
		try {
			// Convert datetime fields to ISO format before submission
			const formattedValues = { ...fieldValues };
			for (const [fieldName, fieldType] of Object.entries(fieldTypes)) {
				if (fieldType === 'datetime' && formattedValues[fieldName]) {
					// datetime-local input gives YYYY-MM-DDTHH:mm format, convert to ISO
					const date = new Date(formattedValues[fieldName]);
					formattedValues[fieldName] = date.toISOString();
				}
			}
			const createdPost = await updates.create({ field_values: formattedValues });
			toast.success('Standup posted');
			dispatch('submitted', createdPost);
			fieldValues = Object.fromEntries(templateFields.map((f) => [f, '']));
			expanded = false;
		} catch (e: any) {
			toast.error('Failed to post update. Try again.');
		} finally {
			submitting = false;
		}
	}
</script>

{#if !expanded}
	<button
		class="w-full flex items-center justify-between px-5 py-4 bg-gray-900 border border-gray-800 rounded-xl text-sm font-semibold text-gray-300 hover:bg-gray-800 transition-colors"
		on:click={() => (expanded = true)}
		type="button"
	>
		<span>Post a standup update</span>
		<ChevronDown size={16} />
	</button>
{:else}
	<div class="bg-gray-900 border border-gray-800 rounded-xl p-5">
		<button
			class="w-full flex items-center justify-between text-sm font-semibold text-gray-300 hover:text-gray-200 transition-colors"
			on:click={() => (expanded = false)}
			type="button"
		>
			<span>Hide form</span>
			<ChevronUp size={16} />
		</button>

		<form on:submit|preventDefault={handleSubmit} class="mt-4 space-y-4">
			{#each templateFields as fieldName, i}
				<div class="space-y-1">
					<label class="label" for="field-{i}">{fieldName}</label>
					{#if fieldTypes[fieldName] === 'datetime'}
						<input id="field-{i}" type="datetime-local" class="input" bind:value={fieldValues[fieldName]} />
					{:else if fieldTypes[fieldName] === 'richtext'}
						<div class="space-y-2">
							<textarea id="field-{i}" class="input resize-none h-20" bind:value={fieldValues[fieldName]}></textarea>
							<!-- Markdown preview could be added here with marked + dompurify -->
						</div>
					{:else}
						<textarea id="field-{i}" class="input resize-none h-20" bind:value={fieldValues[fieldName]}></textarea>
					{/if}
				</div>
			{/each}

			<div class="flex justify-end pt-2">
				<button
					type="submit"
					class="btn-primary"
					disabled={submitting || allFieldsEmpty}
					class:opacity-50={!submitting && allFieldsEmpty}
					class:cursor-not-allowed={!submitting && allFieldsEmpty}
				>
					{#if submitting}
						<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin inline-block mr-2"></span>
						Posting...
					{:else}
						Post Update
					{/if}
				</button>
			</div>
		</form>
	</div>
{/if}
