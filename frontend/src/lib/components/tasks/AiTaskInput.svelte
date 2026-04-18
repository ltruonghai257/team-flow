<script lang="ts">
	import { tasks as tasksApi } from '$lib/api';
	import { Sparkles, Code2, FormInput } from 'lucide-svelte';
	import { onMount } from 'svelte';

	export let onParsed: (fields: Record<string, any>) => void = () => {};

	type Mode = 'form' | 'nlp' | 'json';
	export let mode: Mode = 'form';

	const MODEL_KEY = 'ai_parse_model';
	const models = [
		{ value: 'gpt-4o', label: 'OpenAI · gpt-4o' },
		{ value: 'gpt-3.5-turbo', label: 'OpenAI · gpt-3.5-turbo' },
		{ value: 'ollama/llama3', label: 'Ollama · llama3' },
		{ value: 'ollama/mistral', label: 'Ollama · mistral' }
	];

	let selectedModel = models[0].value;
	let nlpInput = '';
	let jsonInput = '';
	let loading = false;
	let error = '';

	onMount(() => {
		const saved = localStorage.getItem(MODEL_KEY);
		if (saved && models.some((m) => m.value === saved)) selectedModel = saved;
	});

	$: if (typeof localStorage !== 'undefined' && selectedModel) {
		localStorage.setItem(MODEL_KEY, selectedModel);
	}

	async function parse(targetMode: 'nlp' | 'json') {
		const input = targetMode === 'nlp' ? nlpInput : jsonInput;
		if (!input.trim()) return;
		loading = true;
		error = '';
		try {
			const result = (await tasksApi.aiParse(
				input,
				targetMode,
				targetMode === 'nlp' ? selectedModel : undefined
			)) as Record<string, any>;
			// Normalize due_date to YYYY-MM-DD for <input type="date">
			const fields: Record<string, any> = { ...result };
			if (fields.due_date) {
				try {
					fields.due_date = new Date(fields.due_date).toISOString().slice(0, 10);
				} catch {
					delete fields.due_date;
				}
			}
			onParsed(fields);
			mode = 'form';
		} catch (e: any) {
			error = e?.message || 'Parse failed';
		} finally {
			loading = false;
		}
	}
</script>

<div class="border-b border-gray-800 mb-4">
	<div class="flex gap-1">
		<button
			type="button"
			on:click={() => (mode = 'form')}
			class="px-3 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5 {mode ===
			'form'
				? 'border-primary-500 text-primary-400'
				: 'border-transparent text-gray-400 hover:text-gray-200'}"
		>
			<FormInput size={14} /> Form
		</button>
		<button
			type="button"
			on:click={() => (mode = 'nlp')}
			class="px-3 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5 {mode ===
			'nlp'
				? 'border-primary-500 text-primary-400'
				: 'border-transparent text-gray-400 hover:text-gray-200'}"
		>
			<Sparkles size={14} /> NLP
		</button>
		<button
			type="button"
			on:click={() => (mode = 'json')}
			class="px-3 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5 {mode ===
			'json'
				? 'border-primary-500 text-primary-400'
				: 'border-transparent text-gray-400 hover:text-gray-200'}"
		>
			<Code2 size={14} /> JSON
		</button>
	</div>
</div>

{#if mode === 'nlp'}
	<div class="space-y-3">
		<div>
			<label class="label" for="ai-model">AI Model</label>
			<select id="ai-model" bind:value={selectedModel} class="input">
				{#each models as m}
					<option value={m.value}>{m.label}</option>
				{/each}
			</select>
		</div>
		<div>
			<label class="label" for="ai-nlp">Describe the task</label>
			<textarea
				id="ai-nlp"
				bind:value={nlpInput}
				class="input resize-none"
				rows="4"
				placeholder="e.g. Add a high-priority bug fix for the login page due Friday, assign to Alice. Tag: frontend, bug."
			></textarea>
		</div>
		{#if error}
			<p class="text-xs text-red-400">{error}</p>
		{/if}
		<button
			type="button"
			on:click={() => parse('nlp')}
			disabled={loading || !nlpInput.trim()}
			class="btn-primary w-full justify-center"
		>
			{#if loading}
				<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
			{:else}
				<Sparkles size={14} />
			{/if}
			Parse with AI
		</button>
	</div>
{:else if mode === 'json'}
	<div class="space-y-3">
		<div>
			<label class="label" for="ai-json">Paste task JSON</label>
			<textarea
				id="ai-json"
				bind:value={jsonInput}
				class="input resize-none font-mono text-xs"
				rows="8"
				placeholder={'{\n  "title": "Fix login bug",\n  "priority": "high",\n  "due_date": "2025-12-31"\n}'}
			></textarea>
		</div>
		{#if error}
			<p class="text-xs text-red-400">{error}</p>
		{/if}
		<button
			type="button"
			on:click={() => parse('json')}
			disabled={loading || !jsonInput.trim()}
			class="btn-primary w-full justify-center"
		>
			{#if loading}
				<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
			{/if}
			Parse JSON
		</button>
	</div>
{:else}
	<slot />
{/if}
