<script lang="ts">
	import type { MilestoneDecision } from '$lib/apis/milestones';
	import { Plus, X, Check, Trash2, Pencil, MessageSquare } from 'lucide-svelte';
	import { toast } from 'svelte-sonner';
	import { milestones as milestonesApi } from '$lib/apis';
	import { formatDate } from '$lib/utils';
	import { createEventDispatcher } from 'svelte';

	export let milestoneId: number;
	export let decisions: MilestoneDecision[] = [];

	const dispatch = createEventDispatcher();

	let editingDecision: MilestoneDecision | null = null;
	let showCreateForm = false;

	let form = {
		title: '',
		note: '',
		status: 'proposed' as MilestoneDecision['status'],
		task_id: null as number | null
	};

	function resetForm() {
		form = {
			title: '',
			note: '',
			status: 'proposed',
			task_id: null
		};
		editingDecision = null;
	}

	function openCreate() {
		resetForm();
		showCreateForm = true;
	}

	function openEdit(d: MilestoneDecision) {
		editingDecision = d;
		form = {
			title: d.title,
			note: d.note || '',
			status: d.status,
			task_id: d.task_id
		};
		showCreateForm = true;
	}

	async function handleSubmit() {
		try {
			if (editingDecision) {
				await milestonesApi.decisions.update(editingDecision.id, form);
				toast.success('Decision updated');
			} else {
				await milestonesApi.decisions.create(milestoneId, form);
				toast.success('Decision created');
			}
			showCreateForm = false;
			resetForm();
			dispatch('refresh');
		} catch (e: any) {
			toast.error(e.message);
		}
	}

	async function deleteDecision(id: number) {
		if (!confirm('Delete this decision?')) return;
		try {
			await milestonesApi.decisions.delete(id);
			toast.success('Decision deleted');
			dispatch('refresh');
		} catch (e: any) {
			toast.error(e.message);
		}
	}

	const statusColors = {
		proposed: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
		approved: 'bg-green-500/10 text-green-400 border-green-500/20',
		rejected: 'bg-red-500/10 text-red-400 border-red-500/20',
		superseded: 'bg-slate-500/10 text-slate-400 border-slate-500/20'
	};

	const statusLabels = {
		proposed: 'Proposed',
		approved: 'Approved',
		rejected: 'Rejected',
		superseded: 'Superseded'
	};
</script>

<div class="space-y-4">
	{#if showCreateForm}
		<div class="bg-gray-800/50 border border-gray-700 rounded-lg p-3 space-y-3">
			<div class="flex items-center justify-between">
				<h5 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
					{editingDecision ? 'Edit Decision' : 'New Decision'}
				</h5>
				<button on:click={() => (showCreateForm = false)} class="text-gray-500 hover:text-gray-300">
					<X size={14} />
				</button>
			</div>
			
			<div class="space-y-2">
				<input 
					bind:value={form.title} 
					placeholder="Decision title *" 
					class="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-primary-500"
				/>
				<textarea 
					bind:value={form.note} 
					placeholder="Notes (optional)" 
					rows="2"
					class="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-primary-500 resize-none"
				></textarea>
				
				<div class="flex items-center gap-2">
					<select 
						bind:value={form.status}
						class="flex-1 bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-primary-500"
					>
						{#each Object.entries(statusLabels) as [val, label]}
							<option value={val}>{label}</option>
						{/each}
					</select>
					<button 
						on:click={handleSubmit} 
						disabled={!form.title}
						class="p-1.5 bg-primary-500 text-white rounded hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<Check size={14} />
					</button>
				</div>
			</div>
		</div>
	{:else}
		<button 
			on:click={openCreate}
			class="w-full flex items-center justify-center gap-1.5 py-2 border border-dashed border-gray-700 rounded-lg text-[10px] font-bold text-gray-500 hover:text-gray-300 hover:border-gray-500 transition-colors uppercase tracking-widest"
		>
			<Plus size={12} /> Add Decision
		</button>
	{/if}

	{#if decisions.length > 0}
		<div class="space-y-2">
			{#each decisions as d}
				<div class="group bg-gray-800/30 border border-gray-800 rounded-lg p-2.5 hover:border-gray-700 transition-colors">
					<div class="flex items-start justify-between gap-2 mb-1">
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2 mb-1 flex-wrap">
								<span class="text-xs font-semibold text-gray-200 leading-tight">{d.title}</span>
								<span class="badge {statusColors[d.status]} text-[9px] uppercase tracking-tighter px-1 py-0.5">
									{statusLabels[d.status]}
								</span>
							</div>
							{#if d.note}
								<p class="text-[11px] text-gray-500 leading-relaxed mb-1.5 line-clamp-3">{d.note}</p>
							{/if}
							<div class="flex items-center gap-2 text-[9px] text-gray-600">
								<span class="flex items-center gap-1"><MessageSquare size={10} /> {formatDate(d.created_at)}</span>
								{#if d.task_id}
									<span>·</span>
									<a href="/tasks?task_id={d.task_id}" class="hover:text-primary-400">Linked task</a>
								{/if}
							</div>
						</div>
						<div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
							<button 
								on:click={() => openEdit(d)}
								class="p-1 text-gray-600 hover:text-gray-300 rounded"
							>
								<Pencil size={12} />
							</button>
							<button 
								on:click={() => deleteDecision(d.id)}
								class="p-1 text-gray-600 hover:text-red-400 rounded"
							>
								<Trash2 size={12} />
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
