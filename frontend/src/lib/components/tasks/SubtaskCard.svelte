<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Trash2 } from 'lucide-svelte';

	export let subtask: {
		title: string;
		priority: string;
		type: string;
		estimated_hours: number;
		description: string;
		milestone_id: string;
	};
	export let milestoneList: any[] = [];

	const dispatch = createEventDispatcher<{
		update: typeof subtask;
		remove: void;
	}>();

	function update(field: string, value: any) {
		dispatch('update', { ...subtask, [field]: value });
	}
</script>

<div class="bg-gray-800 border border-gray-700 rounded-lg p-3 space-y-2">
	<div>
		<label class="label" for="st-title-{subtask.title}">Title</label>
		<input
			id="st-title-{subtask.title}"
			class="input"
			value={subtask.title}
			placeholder="Subtask title"
			aria-label="Subtask title"
			on:input={(e) => update('title', e.currentTarget.value)}
		/>
	</div>

	<div class="flex gap-3">
		<div class="flex-1">
			<label class="label" for="st-priority-{subtask.title}">Priority</label>
			<select
				id="st-priority-{subtask.title}"
				class="input"
				value={subtask.priority}
				on:change={(e) => update('priority', e.currentTarget.value)}
			>
				<option value="low">Low</option>
				<option value="medium">Medium</option>
				<option value="high">High</option>
				<option value="critical">Critical</option>
			</select>
		</div>
		<div class="flex-1">
			<label class="label" for="st-type-{subtask.title}">Type</label>
			<select
				id="st-type-{subtask.title}"
				class="input"
				value={subtask.type || 'task'}
				on:change={(e) => update('type', e.currentTarget.value)}
			>
				<option value="feature">Feature</option>
				<option value="bug">Bug</option>
				<option value="task">Task</option>
				<option value="improvement">Improve</option>
			</select>
		</div>
		<div>
			<label class="label" for="st-hours-{subtask.title}">Est. Hours</label>
			<input
				id="st-hours-{subtask.title}"
				class="input w-24"
				type="number"
				min="0"
				value={subtask.estimated_hours}
				placeholder="hrs"
				aria-label="Estimated hours"
				on:input={(e) => update('estimated_hours', Number(e.currentTarget.value) || 0)}
			/>
		</div>
	</div>

	<div>
		<label class="label" for="st-desc-{subtask.title}">Description</label>
		<textarea
			id="st-desc-{subtask.title}"
			class="input resize-none"
			rows="2"
			value={subtask.description}
			placeholder="Brief description (optional)"
			on:input={(e) => update('description', e.currentTarget.value)}
		></textarea>
	</div>

	<div class="flex items-center gap-2">
		<div class="flex-1">
			<label class="label" for="st-ms-{subtask.title}">Milestone</label>
			<select
				id="st-ms-{subtask.title}"
				class="input"
				value={subtask.milestone_id}
				on:change={(e) => update('milestone_id', e.currentTarget.value)}
			>
				<option value="">No milestone</option>
				{#each milestoneList as m}
					<option value={String(m.id)}>{m.title}</option>
				{/each}
			</select>
		</div>
		<div class="pt-5">
			<button
				type="button"
				class="p-1 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded transition-colors"
				aria-label="Remove subtask"
				on:click={() => dispatch('remove')}
			>
				<Trash2 size={13} />
			</button>
		</div>
	</div>
</div>
