<script lang="ts">
	import { onMount } from 'svelte';
	import { tick } from 'svelte';
	import { page } from '$app/stores';
	import { milestones as milestonesApi, projects as projectsApi } from '$lib/apis';
	import type { MilestoneCommandViewResponse } from '$lib/apis/milestones';
	import { toast } from 'svelte-sonner';
	import { Plus, X, Flag, AlertTriangle, CheckCircle2, MessageSquare, Ban } from 'lucide-svelte';
	import MilestoneLane from '$lib/components/milestones/MilestoneLane.svelte';
	import MilestoneCard from '$lib/components/milestones/MilestoneCard.svelte';

	let commandData: MilestoneCommandViewResponse | null = null;
	let projectList: any[] = [];
	let loading = true;
	let showModal = false;
	let editingMilestone: any = null;
	let highlightedMilestoneId: number | null = null;
	let handledRouteKey = '';

	let form = {
		title: '',
		description: '',
		status: 'planned',
		start_date: '',
		due_date: '',
		project_id: ''
	};

	onMount(async () => {
		await loadData();
	});

	async function loadData() {
		loading = true;
		try {
			const [cv, projects] = await Promise.all([
				milestonesApi.commandView(),
				projectsApi.list()
			]);
			commandData = cv;
			projectList = projects;
		} catch (e: any) {
			toast.error('Failed to load milestones command view');
		} finally {
			loading = false;
		}
		await applyRouteHighlight($page.url.searchParams.toString());
	}

	function parsePositiveId(value: string | null): number | null {
		if (!value) return null;
		const parsed = Number(value);
		return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
	}

	async function applyRouteHighlight(routeKey: string) {
		if (routeKey === handledRouteKey || !commandData) return;
		handledRouteKey = routeKey;

		const milestoneId = parsePositiveId(new URLSearchParams(routeKey).get('milestone_id'));
		
		let exists = false;
		if (milestoneId) {
			for (const lane of Object.values(commandData.lanes)) {
				if (lane.some(m => m.id === milestoneId)) {
					exists = true;
					break;
				}
			}
		}

		highlightedMilestoneId = milestoneId && exists ? milestoneId : null;

		await tick();
		if (highlightedMilestoneId) {
			document
				.getElementById(`milestone-${highlightedMilestoneId}`)
				?.scrollIntoView({ block: 'center', behavior: 'smooth' });
		}
	}

	$: if (typeof window !== 'undefined' && !loading && commandData) {
		applyRouteHighlight($page.url.searchParams.toString());
	}

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
			await loadData();
		} catch (e: any) {
			toast.error(e.message);
		}
	}

	const laneOrder = ['planned', 'committed', 'active', 'completed'];
	const laneLabels: Record<string, string> = {
		planned: 'Planned',
		committed: 'Committed',
		active: 'Active',
		completed: 'Completed'
	};
</script>

<svelte:head><title>Milestones · TeamFlow</title></svelte:head>

<div class="p-4 md:p-6 max-w-7xl mx-auto">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-2xl font-bold text-white">Milestones</h1>
			<p class="text-gray-400 text-sm mt-1">Command view for planning and execution</p>
		</div>
		<button on:click={openCreate} class="btn-primary">
			<Plus size={16} /> New Milestone
		</button>
	</div>

	{#if loading && !commandData}
		<div class="flex items-center justify-center py-20">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if commandData}
		<!-- Summary Metrics Row -->
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
			<div class="card p-4 flex items-center gap-4">
				<div class="p-3 rounded-lg bg-primary-500/10 text-primary-500">
					<Flag size={20} />
				</div>
				<div>
					<div class="text-2xl font-bold text-white">{commandData.metrics.active_milestones}</div>
					<div class="text-xs text-gray-500 uppercase tracking-wider font-medium">Active</div>
				</div>
			</div>
			<div class="card p-4 flex items-center gap-4">
				<div class="p-3 rounded-lg bg-amber-500/10 text-amber-500">
					<AlertTriangle size={20} />
				</div>
				<div>
					<div class="text-2xl font-bold text-white">{commandData.metrics.risky_milestones}</div>
					<div class="text-xs text-gray-500 uppercase tracking-wider font-medium">Risky</div>
				</div>
			</div>
			<div class="card p-4 flex items-center gap-4">
				<div class="p-3 rounded-lg bg-indigo-500/10 text-indigo-500">
					<MessageSquare size={20} />
				</div>
				<div>
					<div class="text-2xl font-bold text-white">{commandData.metrics.proposed_decisions}</div>
					<div class="text-xs text-gray-500 uppercase tracking-wider font-medium">Proposed Decisions</div>
				</div>
			</div>
			<div class="card p-4 flex items-center gap-4">
				<div class="p-3 rounded-lg bg-red-500/10 text-red-500">
					<Ban size={20} />
				</div>
				<div>
					<div class="text-2xl font-bold text-white">{commandData.metrics.blocked_tasks}</div>
					<div class="text-xs text-gray-500 uppercase tracking-wider font-medium">Blocked Tasks</div>
				</div>
			</div>
		</div>

		<!-- Lanes -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			{#each laneOrder as laneKey}
				{@const milestones = commandData.lanes[laneKey] || []}
				<MilestoneLane title={laneLabels[laneKey]} count={milestones.length}>
					{#each milestones as m (m.id)}
						<MilestoneCard 
							milestone={m} 
							highlighted={highlightedMilestoneId === m.id}
							on:edit={(e) => openEdit(e.detail)}
							on:refresh={loadData}
						/>
					{/each}
					{#if milestones.length === 0}
						<div class="text-center py-8 border border-dashed border-gray-800 rounded-lg">
							<p class="text-xs text-gray-600">Empty</p>
						</div>
					{/if}
				</MilestoneLane>
			{/each}
		</div>
	{:else}
		<div class="card text-center py-12">
			<Flag class="mx-auto text-gray-600 mb-3" size={36} />
			<p class="text-gray-500">No milestones yet. Create one to start tracking!</p>
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
