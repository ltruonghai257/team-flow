<script lang="ts">
	import { onMount } from 'svelte';
	import { milestones as milestonesApi, projects as projectsApi } from '$lib/api';
	import { formatDate, milestoneStatusColors } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import { Plus, Pencil, Trash2, X, Flag, Calendar } from 'lucide-svelte';

	let milestoneList: any[] = [];
	let projectList: any[] = [];
	let loading = true;
	let showModal = false;
	let editingMilestone: any = null;

	let form = {
		title: '',
		description: '',
		status: 'planned',
		start_date: '',
		due_date: '',
		project_id: ''
	};

	onMount(async () => {
		loading = true;
		try {
			[milestoneList, projectList] = await Promise.all([milestonesApi.list(), projectsApi.list()]);
		} finally {
			loading = false;
		}
	});

	function openCreate() {
		editingMilestone = null;
		form = { title: '', description: '', status: 'planned', start_date: '', due_date: '', project_id: '' };
		showModal = true;
	}

	function openEdit(m: any) {
		editingMilestone = m;
		form = {
			title: m.title,
			description: m.description || '',
			status: m.status,
			start_date: m.start_date ? m.start_date.slice(0, 10) : '',
			due_date: m.due_date.slice(0, 10),
			project_id: m.project_id
		};
		showModal = true;
	}

	async function handleSubmit() {
		const payload: any = {
			...form,
			start_date: form.start_date ? new Date(form.start_date).toISOString() : null,
			due_date: new Date(form.due_date).toISOString(),
			project_id: Number(form.project_id)
		};
		try {
			if (editingMilestone) {
				await milestonesApi.update(editingMilestone.id, payload);
				toast.success('Milestone updated');
			} else {
				await milestonesApi.create(payload);
				toast.success('Milestone created');
			}
			showModal = false;
			milestoneList = await milestonesApi.list();
		} catch (e) {
			toast.error(e.message);
		}
	}

	async function deleteMilestone(id: number) {
		if (!confirm('Delete this milestone?')) return;
		try {
			await milestonesApi.delete(id);
			toast.success('Milestone deleted');
			milestoneList = await milestonesApi.list();
		} catch (e) {
			toast.error(e.message);
		}
	}

	function projectName(id: number) {
		return projectList.find((p) => p.id === id)?.name || 'Unknown';
	}

	function progressPercent(m: any) {
		if (m.status === 'completed') return 100;
		if (m.status === 'planned') return 0;
		const start = m.start_date ? new Date(m.start_date).getTime() : new Date(m.created_at).getTime();
		const end = new Date(m.due_date).getTime();
		const now = Date.now();
		if (now >= end) return m.status === 'completed' ? 100 : 95;
		return Math.round(((now - start) / (end - start)) * 100);
	}
</script>

<svelte:head><title>Milestones · TeamFlow</title></svelte:head>

<div class="p-6 max-w-5xl mx-auto">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-2xl font-bold text-white">Milestones</h1>
			<p class="text-gray-400 text-sm mt-1">Track releases and major deliverables</p>
		</div>
		<button on:click={openCreate} class="btn-primary">
			<Plus size={16} /> New Milestone
		</button>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if milestoneList.length === 0}
		<div class="card text-center py-12">
			<Flag class="mx-auto text-gray-600 mb-3" size={36} />
			<p class="text-gray-500">No milestones yet. Create one to start tracking!</p>
		</div>
	{:else}
		<div class="space-y-4">
			{#each milestoneList as m}
				{@const pct = progressPercent(m)}
				<div class="card hover:border-gray-700 transition-colors">
					<div class="flex items-start justify-between gap-4">
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-3 mb-1">
								<h3 class="font-semibold text-white">{m.title}</h3>
								<span class="badge {milestoneStatusColors[m.status]}">{m.status.replace('_', ' ')}</span>
							</div>
							{#if m.description}
								<p class="text-sm text-gray-400 mb-3">{m.description}</p>
							{/if}
							<div class="flex items-center gap-4 text-xs text-gray-500 mb-3">
								<span class="flex items-center gap-1"><Calendar size={12} /> Due {formatDate(m.due_date)}</span>
								{#if projectList.length > 0}
									<span class="text-gray-600">·</span>
									<span>{projectName(m.project_id)}</span>
								{/if}
							</div>
							<!-- Progress bar -->
							<div class="w-full bg-gray-800 rounded-full h-1.5">
								<div
									class="h-1.5 rounded-full transition-all {m.status === 'completed' ? 'bg-green-500' : m.status === 'delayed' ? 'bg-red-500' : 'bg-primary-500'}"
									style="width: {pct}%"
								></div>
							</div>
							<p class="text-xs text-gray-600 mt-1">{pct}% time elapsed</p>
						</div>
						<div class="flex items-center gap-1 flex-shrink-0">
							<button on:click={() => openEdit(m)} class="p-1.5 text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors">
								<Pencil size={14} />
							</button>
							<button on:click={() => deleteMilestone(m.id)} class="p-1.5 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded transition-colors">
								<Trash2 size={14} />
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if showModal}
	<div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
		<div class="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-md">
			<div class="flex items-center justify-between p-5 border-b border-gray-800">
				<h2 class="font-semibold text-white">{editingMilestone ? 'Edit Milestone' : 'New Milestone'}</h2>
				<button on:click={() => (showModal = false)} class="text-gray-500 hover:text-gray-300"><X size={18} /></button>
			</div>
			<form on:submit|preventDefault={handleSubmit} class="p-5 space-y-4">
				<div>
					<label class="label" for="m-title">Title *</label>
					<input id="m-title" bind:value={form.title} class="input" required />
				</div>
				<div>
					<label class="label" for="m-desc">Description</label>
					<textarea id="m-desc" bind:value={form.description} class="input resize-none" rows="2"></textarea>
				</div>
				<div>
					<label class="label" for="m-project">Project *</label>
					<select id="m-project" bind:value={form.project_id} class="input" required>
						<option value="">Select project...</option>
						{#each projectList as p}
							<option value={p.id}>{p.name}</option>
						{/each}
					</select>
				</div>
				<div>
					<label class="label" for="m-status">Status</label>
					<select id="m-status" bind:value={form.status} class="input">
						<option value="planned">Planned</option>
						<option value="in_progress">In Progress</option>
						<option value="completed">Completed</option>
						<option value="delayed">Delayed</option>
					</select>
				</div>
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="label" for="m-start">Start Date</label>
						<input id="m-start" bind:value={form.start_date} type="date" class="input" />
					</div>
					<div>
						<label class="label" for="m-due">Due Date *</label>
						<input id="m-due" bind:value={form.due_date} type="date" class="input" required />
					</div>
				</div>
				<div class="flex justify-end gap-3 pt-2">
					<button type="button" on:click={() => (showModal = false)} class="btn-secondary">Cancel</button>
					<button type="submit" class="btn-primary">{editingMilestone ? 'Save Changes' : 'Create'}</button>
				</div>
			</form>
		</div>
	</div>
{/if}
