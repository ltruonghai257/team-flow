<script lang="ts">
	import { tasks as tasksApi } from '$lib/apis';
	import { Sparkles, Code2, FormInput, Layers } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import SubtaskCard from './SubtaskCard.svelte';

	export let onParsed: (fields: Record<string, any>) => void = () => {};
	export let projectList: any[] = [];
	export let milestoneList: any[] = [];
	export let userList: any[] = [];
	export let selectedSprintId: number | null = null;

	type Mode = 'form' | 'nlp' | 'json' | 'breakdown';
	export let mode: Mode = 'form';

	type SubtaskDraft = {
		title: string;
		priority: string;
		type: string;
		estimated_hours: number;
		description: string;
		milestone_id: string;
	};

	let breakdownProject = '';
	let breakdownMilestone = '';
	let breakdownAssignee = '';
	let breakdownDescription = '';
	let breakdownLoading = false;
	let subtasks: SubtaskDraft[] = [];
	let batchProgress = { current: 0, total: 0, running: false };

	$: filteredMilestones = breakdownProject
		? milestoneList.filter((m: any) => m.project_id === Number(breakdownProject))
		: milestoneList;

	async function breakdown() {
		if (!breakdownProject || !breakdownDescription.trim()) return;
		breakdownLoading = true;
		try {
			const result = (await tasksApi.aiBreakdown(
				breakdownDescription,
				Number(breakdownProject)
			)) as { subtasks: any[] };
			subtasks = result.subtasks.map((s) => ({
				...s,
				type: s.type || 'task',
				estimated_hours: s.estimated_hours ?? 0,
				milestone_id: breakdownMilestone
			}));
		} catch {
			toast.error('AI breakdown failed — please try again');
		} finally {
			breakdownLoading = false;
		}
	}

	async function createAll() {
		batchProgress = { current: 0, total: subtasks.length, running: true };
		let successCount = 0;
		for (let i = 0; i < subtasks.length; i++) {
			batchProgress = { ...batchProgress, current: i + 1 };
			try {
				await tasksApi.create({
					title: subtasks[i].title,
					description: subtasks[i].description || null,
					priority: subtasks[i].priority,
					type: subtasks[i].type || 'task',
					estimated_hours: subtasks[i].estimated_hours || null,
					project_id: Number(breakdownProject),
					milestone_id: subtasks[i].milestone_id ? Number(subtasks[i].milestone_id) : null,
					assignee_id: breakdownAssignee ? Number(breakdownAssignee) : null,
					sprint_id: selectedSprintId
				});
				successCount++;
			} catch {
				// continue on individual failure
			}
		}
		const total = subtasks.length;
		batchProgress = { current: 0, total: 0, running: false };
		if (successCount < total) {
			toast.error("Some tasks couldn't be created — check project settings");
		} else {
			toast.success(`Created ${successCount} tasks successfully`);
		}
		subtasks = [];
		breakdownDescription = '';
	}

	function updateSubtask(index: number, updated: SubtaskDraft) {
		subtasks = subtasks.map((s, i) => (i === index ? updated : s));
	}

	function removeSubtask(index: number) {
		subtasks = subtasks.filter((_, i) => i !== index);
	}

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
		<button
			type="button"
			on:click={() => (mode = 'breakdown')}
			title="Break down task with AI"
			class="px-3 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5 {mode ===
			'breakdown'
				? 'border-primary-500 text-primary-400'
				: 'border-transparent text-gray-400 hover:text-gray-200'}"
		>
			<Layers size={14} /> Breakdown
		</button>
	</div>
</div>

{#if mode === 'breakdown'}
	<div class="space-y-3">
		<div>
			<label class="label" for="bd-project">Project</label>
			<select id="bd-project" bind:value={breakdownProject} class="input" required>
				<option value="">Select a project</option>
				{#each projectList as p}
					<option value={String(p.id)}>{p.name}</option>
				{/each}
			</select>
		</div>
		<div>
			<label class="label" for="bd-milestone">Default Milestone</label>
			<select id="bd-milestone" bind:value={breakdownMilestone} class="input">
				<option value="">No milestone</option>
				{#each filteredMilestones as m}
					<option value={String(m.id)}>{m.title}</option>
				{/each}
			</select>
		</div>
		<div>
			<label class="label" for="bd-assignee">Assign all to</label>
			<select id="bd-assignee" bind:value={breakdownAssignee} class="input">
				<option value="">Unassigned</option>
				{#each userList as u}
					<option value={String(u.id)}>{u.full_name}</option>
				{/each}
			</select>
		</div>
		<div>
			<label class="label" for="bd-desc">What do you want to build?</label>
			<textarea
				id="bd-desc"
				bind:value={breakdownDescription}
				class="input resize-none"
				rows="4"
				placeholder="Describe the feature or work to break down into tasks..."
			></textarea>
		</div>
		<button
			type="button"
			on:click={breakdown}
			disabled={breakdownLoading || !breakdownProject || !breakdownDescription.trim()}
			class="btn-primary w-full justify-center"
		>
			{#if breakdownLoading}
				<span aria-hidden="true" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
			{:else}
				Break down with AI
			{/if}
		</button>

		{#if subtasks.length > 0}
			<div class="space-y-3 mt-4">
				{#each subtasks as subtask, i}
					<SubtaskCard
						{subtask}
						milestoneList={filteredMilestones}
						on:update={(e) => updateSubtask(i, e.detail)}
						on:remove={() => removeSubtask(i)}
					/>
				{/each}
			</div>

			{#if batchProgress.running}
				<p class="text-center text-xs text-gray-400 py-2">
					Creating {batchProgress.current} of {batchProgress.total}...
				</p>
			{:else}
				<button
					type="button"
					on:click={createAll}
					class="btn-primary w-full justify-center mt-2"
				>
					Create All ({subtasks.length} tasks)
				</button>
			{/if}
		{:else if !breakdownLoading && breakdownDescription}
			<p class="text-sm text-gray-500 text-center py-4">All subtasks removed. Break down again to start over.</p>
		{/if}
	</div>
{:else if mode === 'nlp'}
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
