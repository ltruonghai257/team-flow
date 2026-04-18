<script lang="ts">
	import { onMount } from 'svelte';
	import { projects as projectsApi } from '$lib/api';
	import { formatDate } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import { Plus, Pencil, Trash2, X, FolderOpen } from 'lucide-svelte';

	let projectList: any[] = [];
	let loading = true;
	let showModal = false;
	let editingProject: any = null;

	let form = { name: '', description: '', color: '#6366f1' };

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
		} catch (e) {
			toast.error(e.message);
		}
	}

	async function deleteProject(id: number) {
		if (!confirm('Delete this project and all its milestones?')) return;
		try {
			await projectsApi.delete(id);
			toast.success('Project deleted');
			projectList = await projectsApi.list();
		} catch (e) {
			toast.error(e.message);
		}
	}
</script>

<svelte:head><title>Projects · TeamFlow</title></svelte:head>

<div class="p-6 max-w-5xl mx-auto">
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
					<div class="mt-3 pt-3 border-t border-gray-800 flex gap-2">
						<a href="/tasks?project_id={p.id}" class="text-xs text-gray-500 hover:text-primary-400 transition-colors">View Tasks →</a>
						<span class="text-gray-700">·</span>
						<a href="/milestones?project_id={p.id}" class="text-xs text-gray-500 hover:text-primary-400 transition-colors">Milestones →</a>
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
