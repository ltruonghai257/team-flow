<script lang="ts">
	import { onMount } from 'svelte';
	import { projects as projectsApi, ai as aiApi, statusSets } from '$lib/apis';
	import type { StatusSet } from '$lib/types';
	import { formatDate } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import { Plus, Pencil, Trash2, X, FolderOpen, Sparkles } from 'lucide-svelte';
	import { slide } from 'svelte/transition';
	import ProjectStatusPanel from '$lib/components/statuses/ProjectStatusPanel.svelte';
	import { isSupervisor } from '$lib/stores/auth';

	let projectList: any[] = [];
	let loading = true;
	let showModal = false;
	let editingProject: any = null;

	let form = { name: '', description: '', color: '#6366f1' };

	let summaryMap: Record<number, { summary: string; sections: any } | null> = {};
	let loadingMap: Record<number, boolean> = {};
	let expandedMap: Record<number, boolean> = {};
	let statusExpandedMap: Record<number, boolean> = {};
	let statusSetMap: Record<number, StatusSet | null> = {};

	async function loadProjectStatusSet(projectId: number) {
		try {
			statusSetMap[projectId] = await statusSets.getEffective(projectId);
			statusSetMap = statusSetMap;
		} catch {
			statusSetMap[projectId] = null;
			statusSetMap = statusSetMap;
		}
	}

	function toggleStatusPanel(projectId: number) {
		statusExpandedMap[projectId] = !statusExpandedMap[projectId];
		statusExpandedMap = statusExpandedMap;
		if (statusExpandedMap[projectId] && statusSetMap[projectId] === undefined) {
			loadProjectStatusSet(projectId);
		}
	}

	async function summarizeProject(projectId: number) {
		loadingMap[projectId] = true;
		loadingMap = loadingMap;
		try {
			const result = await aiApi.projectSummary(projectId);
			summaryMap[projectId] = result;
			expandedMap[projectId] = true;
			summaryMap = summaryMap;
			expandedMap = expandedMap;
		} catch {
			toast.error("Couldn't summarize project — please try again");
		} finally {
			loadingMap[projectId] = false;
			loadingMap = loadingMap;
		}
	}

	function toggleSummary(projectId: number) {
		expandedMap[projectId] = !expandedMap[projectId];
		expandedMap = expandedMap;
	}

	const colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#3b82f6', '#ec4899', '#14b8a6'];

	onMount(async () => {
		loading = true;
		try {
			projectList = await projectsApi.list();
		} finally {
			loading = false;
		}
	});

	function openCreate() {
		editingProject = null;
		form = { name: '', description: '', color: '#6366f1' };
		showModal = true;
	}

	function openEdit(p: any) {
		editingProject = p;
		form = { name: p.name, description: p.description || '', color: p.color };
		showModal = true;
	}

	async function handleSubmit() {
		try {
			if (editingProject) {
				await projectsApi.update(editingProject.id, form);
				toast.success('Project updated');
			} else {
				await projectsApi.create(form);
				toast.success('Project created');
			}
			showModal = false;
			projectList = await projectsApi.list();
		} catch (e: any) {
			toast.error(e.message);
		}
	}

	async function deleteProject(id: number) {
		if (!confirm('Delete this project and all its milestones?')) return;
		try {
			await projectsApi.delete(id);
			toast.success('Project deleted');
			projectList = await projectsApi.list();
		} catch (e: any) {
			toast.error(e.message);
		}
	}
</script>

<svelte:head><title>Projects · TeamFlow</title></svelte:head>

<div class="p-4 md:p-6 max-w-5xl mx-auto">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-2xl font-bold text-white">Projects</h1>
			<p class="text-gray-400 text-sm mt-1">{projectList.length} projects</p>
		</div>
		<button on:click={openCreate} class="btn-primary">
			<Plus size={16} /> New Project
		</button>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if projectList.length === 0}
		<div class="card text-center py-12">
			<FolderOpen class="mx-auto text-gray-600 mb-3" size={36} />
			<p class="text-gray-500">No projects yet. Create one to start organizing work!</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
			{#each projectList as p}
				<div class="card hover:border-gray-700 transition-colors group">
					<div class="flex items-start justify-between mb-3">
						<div class="flex items-center gap-3">
							<div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style="background-color: {p.color}20; border: 1px solid {p.color}40">
								<span style="color: {p.color}" class="font-bold text-sm">{p.name[0].toUpperCase()}</span>
							</div>
							<div>
								<p class="font-semibold text-white">{p.name}</p>
								<p class="text-xs text-gray-500">Created {formatDate(p.created_at)}</p>
							</div>
						</div>
						<div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
							<button on:click={() => openEdit(p)} class="p-1.5 text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors">
								<Pencil size={13} />
							</button>
							<button on:click={() => deleteProject(p.id)} class="p-1.5 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded transition-colors">
								<Trash2 size={13} />
							</button>
						</div>
					</div>
					{#if p.description}
						<p class="text-sm text-gray-400 line-clamp-2">{p.description}</p>
					{/if}
					<div class="mt-3 pt-3 border-t border-gray-800 flex gap-2 items-center flex-wrap">
						<a href="/tasks?project_id={p.id}" class="text-xs text-gray-500 hover:text-primary-400 transition-colors">View Tasks →</a>
						<span class="text-gray-700">·</span>
						<a href="/milestones?project_id={p.id}" class="text-xs text-gray-500 hover:text-primary-400 transition-colors">Milestones →</a>
						<span class="text-gray-700">·</span>
						<button
							type="button"
							on:click={() => toggleStatusPanel(p.id)}
							aria-label="{statusExpandedMap[p.id] ? 'Hide' : 'Manage'} Statuses for {p.name}"
							class="text-xs text-gray-500 hover:text-primary-400 transition-colors"
						>
							Statuses
						</button>
						<span class="text-gray-700">·</span>
						{#if summaryMap[p.id]}
							<button
								type="button"
								on:click={() => toggleSummary(p.id)}
								aria-expanded={expandedMap[p.id] ?? false}
								aria-label="{expandedMap[p.id] ? 'Hide' : 'Show'} summary for {p.name}"
								class="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-primary-400 transition-colors"
							>
								<Sparkles size={12} />
								{expandedMap[p.id] ? 'Hide Summary' : 'Show Summary'}
							</button>
						{:else}
							<button
								type="button"
								on:click={() => summarizeProject(p.id)}
								disabled={loadingMap[p.id]}
								aria-label="Summarize {p.name}"
								class="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-primary-400 transition-colors disabled:cursor-not-allowed"
							>
								{#if loadingMap[p.id]}
									<span aria-hidden="true" class="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin"></span>
									Summarizing...
								{:else}
									<Sparkles size={12} />
									Summarize
								{/if}
							</button>
						{/if}
					</div>

					{#if statusExpandedMap[p.id]}
						<div transition:slide={{ duration: 200 }} class="mt-3 pt-3 border-t border-gray-700/50">
							<ProjectStatusPanel
								project={p}
								statusSet={statusSetMap[p.id] ?? null}
								canManage={$isSupervisor}
								onRefresh={() => loadProjectStatusSet(p.id)}
							/>
						</div>
					{/if}

					{#if summaryMap[p.id] && expandedMap[p.id]}
						<div
							transition:slide={{ duration: 200 }}
							class="mt-3 pt-3 border-t border-gray-700/50 bg-gray-800/40 rounded-b-lg -mx-5 -mb-5 px-5 pb-4"
						>
							<div class="space-y-3">
								<div>
									<p class="text-xs font-semibold text-gray-300 uppercase tracking-wide mb-1">Milestone Progress</p>
									<p class="text-sm text-gray-400">{summaryMap[p.id]?.sections?.milestone_progress}</p>
								</div>
								<div>
									<p class="text-xs font-semibold text-gray-300 uppercase tracking-wide mb-1">Recent Completions</p>
									<p class="text-sm text-gray-400">{summaryMap[p.id]?.sections?.recent_completions}</p>
								</div>
								<div>
									<p class="text-xs font-semibold text-gray-300 uppercase tracking-wide mb-1">Overdue</p>
									<p class="text-sm text-gray-400">{summaryMap[p.id]?.sections?.overdue}</p>
								</div>
								<div>
									<p class="text-xs font-semibold text-gray-300 uppercase tracking-wide mb-1">At-Risk</p>
									<p class="text-sm text-gray-400">{summaryMap[p.id]?.sections?.at_risk}</p>
								</div>
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if showModal}
	<div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
		<div class="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-md">
			<div class="flex items-center justify-between p-5 border-b border-gray-800">
				<h2 class="font-semibold text-white">{editingProject ? 'Edit Project' : 'New Project'}</h2>
				<button on:click={() => (showModal = false)} class="text-gray-500 hover:text-gray-300"><X size={18} /></button>
			</div>
			<form on:submit|preventDefault={handleSubmit} class="p-5 space-y-4">
				<div>
					<label class="label" for="p-name">Name *</label>
					<input id="p-name" bind:value={form.name} class="input" required />
				</div>
				<div>
					<label class="label" for="p-desc">Description</label>
					<textarea id="p-desc" bind:value={form.description} class="input resize-none" rows="3"></textarea>
				</div>
				<div>
					<label class="label">Color</label>
					<div class="flex gap-2 flex-wrap">
						{#each colors as c}
							<button
								type="button"
								on:click={() => (form.color = c)}
								class="w-7 h-7 rounded-full transition-transform {form.color === c ? 'ring-2 ring-white ring-offset-2 ring-offset-gray-900 scale-110' : 'hover:scale-105'}"
								style="background-color: {c}"
							></button>
						{/each}
					</div>
				</div>
				<div class="flex justify-end gap-3 pt-2">
					<button type="button" on:click={() => (showModal = false)} class="btn-secondary">Cancel</button>
					<button type="submit" class="btn-primary">{editingProject ? 'Save Changes' : 'Create Project'}</button>
				</div>
			</form>
		</div>
	</div>
{/if}
