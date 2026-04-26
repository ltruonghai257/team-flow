<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { X, Info } from 'lucide-svelte';
	import { sprints } from '$lib/api';

	const dispatch = createEventDispatcher();

	export let sprint: any;
	export let incompleteTasks: any[] = [];
	export let availableSprints: any[] = [];
	export let show = false;

	let task_mapping: Record<number, number | null> = {};

	$: if (show && incompleteTasks) {
		const mapping: Record<number, number | null> = {};
		incompleteTasks.forEach((task) => {
			mapping[task.id] = null;
		});
		task_mapping = mapping;
	}

	async function handleSubmit() {
		try {
			await sprints.close(sprint.id, { task_mapping });
			show = false;
			dispatch('success');
		} catch (e: any) {
			console.error(e);
			alert(e.message || 'Failed to close sprint');
		}
	}
</script>

{#if show}
	<div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
		<div
			class="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl"
		>
			<div class="flex items-center justify-between p-5 border-b border-gray-800">
				<div>
					<h2 class="font-semibold text-white text-lg">Close Sprint: {sprint?.name}</h2>
					<p class="text-sm text-gray-400 mt-1">Reassign {incompleteTasks.length} incomplete tasks</p>
				</div>
				<button on:click={() => (show = false)} class="text-gray-500 hover:text-gray-300">
					<X size={20} />
				</button>
			</div>

			<div class="p-6 overflow-y-auto flex-1">
				{#if incompleteTasks.length > 0}
					<div class="space-y-4">
						<div
							class="flex items-start gap-3 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-400 text-sm"
						>
							<Info size={18} class="shrink-0 mt-0.5" />
							<p>
								Moving tasks will update their sprint assignment. Tasks moved to "Backlog" will have no
								sprint assigned.
							</p>
						</div>

						<div class="border border-gray-800 rounded-lg overflow-hidden">
							<table class="w-full text-left text-sm">
								<thead class="bg-gray-800/50 text-gray-400 font-medium border-b border-gray-800">
									<tr>
										<th class="px-4 py-3">Task Title</th>
										<th class="px-4 py-3 w-64">Move To</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-800">
									{#each incompleteTasks as task}
										<tr class="hover:bg-gray-800/30 transition-colors">
											<td class="px-4 py-3 text-white truncate max-w-xs">{task.title}</td>
											<td class="px-4 py-3">
												<select bind:value={task_mapping[task.id]} class="input text-xs h-9 py-1">
													<option value={null}>Backlog</option>
													{#each availableSprints as s}
														{#if s.id !== sprint.id}
															<option value={s.id}>{s.name}</option>
														{/if}
													{/each}
												</select>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				{:else}
					<div class="text-center py-8">
						<p class="text-gray-400">All tasks in this sprint are completed.</p>
						<p class="text-sm text-gray-500 mt-1">You can close the sprint directly.</p>
					</div>
				{/if}
			</div>

			<div class="p-5 border-t border-gray-800 bg-gray-900/50 flex justify-end gap-3">
				<button type="button" on:click={() => (show = false)} class="btn-secondary">Cancel</button>
				<button on:click={handleSubmit} class="btn-primary">
					Close Sprint & Move Tasks
				</button>
			</div>
		</div>
	</div>
{/if}
