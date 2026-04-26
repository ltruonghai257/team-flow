<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { AlertTriangle } from 'lucide-svelte';
	import { sprints } from '$lib/api';

	const dispatch = createEventDispatcher();

	export let sprint = null;
	export let milestoneId = null;
	export let milestones = [];
	export let existingSprints = [];

	let form = {
		name: '',
		start_date: '',
		end_date: '',
		status: 'planning',
		milestone_id: milestoneId
	};

	if (sprint) {
		form = {
			name: sprint.name,
			start_date: sprint.start_date,
			end_date: sprint.end_date,
			status: sprint.status,
			milestone_id: sprint.milestone_id || milestoneId
		};
	}

	$: milestone = milestones.find((m) => m.id === milestoneId);

	$: warnings = [];
	$: {
		const newWarnings = [];
		if (form.start_date && form.end_date) {
			const start = new Date(form.start_date);
			const end = new Date(form.end_date);

			if (milestone) {
				if (milestone.start_date && start < new Date(milestone.start_date)) {
					newWarnings.push('Start date is before milestone start date.');
				}
				if (milestone.due_date && end > new Date(milestone.due_date)) {
					newWarnings.push('End date is after milestone due date.');
				}
			}

			// Overlap with other sprints
			for (const s of existingSprints) {
				if (sprint && s.id === sprint.id) continue;
				const sStart = new Date(s.start_date);
				const sEnd = new Date(s.end_date);
				if (start <= sEnd && end >= sStart) {
					newWarnings.push(`Overlaps with sprint "${s.name}".`);
				}
			}
		}
		warnings = newWarnings;
	}

	async function handleSubmit() {
		try {
			if (sprint) {
				await sprints.update(sprint.id, form);
			} else {
				await sprints.create(form);
			}
			dispatch('success');
		} catch (e: any) {
			console.error(e);
			alert(e.message || 'Operation failed');
		}
	}
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-4">
	<div>
		<label class="label" for="s-name">Sprint Name *</label>
		<input id="s-name" bind:value={form.name} class="input" required placeholder="e.g. Sprint 1" />
	</div>

	<div class="grid grid-cols-2 gap-4">
		<div>
			<label class="label" for="s-start">Start Date *</label>
			<input id="s-start" bind:value={form.start_date} type="date" class="input" required />
		</div>
		<div>
			<label class="label" for="s-end">End Date *</label>
			<input id="s-end" bind:value={form.end_date} type="date" class="input" required />
		</div>
	</div>

	<div>
		<label class="label" for="s-status">Status</label>
		<select id="s-status" bind:value={form.status} class="input">
			<option value="planning">Planning</option>
			<option value="active">Active</option>
			<option value="completed">Completed</option>
		</select>
	</div>

	{#if warnings.length > 0}
		<div class="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg space-y-1">
			{#each warnings as warning}
				<div class="flex items-center gap-2 text-yellow-500 text-sm">
					<AlertTriangle size={14} />
					<span>{warning}</span>
				</div>
			{/each}
		</div>
	{/if}

	<div class="flex justify-end gap-3 pt-2">
		<button type="button" on:click={() => dispatch('cancel')} class="btn-secondary">Cancel</button>
		<button type="submit" class="btn-primary">{sprint ? 'Save Changes' : 'Create Sprint'}</button>
	</div>
</form>
