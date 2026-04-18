<script lang="ts">
	import { onMount } from 'svelte';
	import { tasks as tasksApi, users as usersApi, projects as projectsApi } from '$lib/api';
	import { formatDate, statusColors, statusLabels, priorityColors, isOverdue } from '$lib/utils';
	import { authStore } from '$lib/stores/auth';
	import { toast } from 'svelte-sonner';
	import { Plus, Pencil, Trash2, X, Filter } from 'lucide-svelte';

	let taskList: any[] = [];
	let userList: any[] = [];
	let projectList: any[] = [];
	let loading = true;
	let showModal = false;
	let editingTask: any = null;
	let filterStatus = '';
	let filterMine = false;

	let form = {
		title: '',
		description: '',
		status: 'todo',
		priority: 'medium',
		due_date: '',
		estimated_hours: '',
		tags: '',
		project_id: '',
		assignee_id: ''
	};

	onMount(async () => {
		await loadAll();
	});

	async function loadAll() {
		loading = true;
		try {
			[taskList, userList, projectList] = await Promise.all([
				tasksApi.list(),
				usersApi.list(),
				projectsApi.list()
			]);
		} finally {
			loading = false;
		}
	}

	async function loadTasks() {
		const params: any = {};
		if (filterStatus) params.status = filterStatus;
		if (filterMine) params.my_tasks = 'true';
		taskList = await tasksApi.list(params);
	}

	function openCreate() {
		editingTask = null;
		form = { title: '', description: '', status: 'todo', priority: 'medium', due_date: '', estimated_hours: '', tags: '', project_id: '', assignee_id: '' };
		showModal = true;
	}

	function openEdit(t: any) {
		editingTask = t;
		form = {
			title: t.title,
			description: t.description || '',
			status: t.status,
			priority: t.priority,
			due_date: t.due_date ? t.due_date.slice(0, 10) : '',
			estimated_hours: t.estimated_hours || '',
			tags: t.tags || '',
			project_id: t.project_id || '',
			assignee_id: t.assignee_id || ''
		};
		showModal = true;
	}

	async function handleSubmit() {
		const payload: any = {
			...form,
			due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
			estimated_hours: form.estimated_hours ? Number(form.estimated_hours) : null,
			project_id: form.project_id ? Number(form.project_id) : null,
			assignee_id: form.assignee_id ? Number(form.assignee_id) : null
		};
		try {
			if (editingTask) {
				await tasksApi.update(editingTask.id, payload);
				toast.success('Task updated');
			} else {
				await tasksApi.create(payload);
				toast.success('Task created');
			}
			showModal = false;
			await loadTasks();
		} catch (e) {
			toast.error(e.message);
		}
	}

	async function deleteTask(id: number) {
		if (!confirm('Delete this task?')) return;
		try {
			await tasksApi.delete(id);
			toast.success('Task deleted');
			await loadTasks();
		} catch (e) {
			toast.error(e.message);
		}
	}

	async function toggleStatus(t: any) {
		const next = t.status === 'done' ? 'todo' : 'done';
		await tasksApi.update(t.id, { status: next });
		await loadTasks();
	}

	$: filterStatus, filterMine, loadTasks();
</script>

<svelte:head><title>Tasks · TeamFlow</title></svelte:head>

<div class="p-6 max-w-6xl mx-auto">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-2xl font-bold text-white">Tasks</h1>
			<p class="text-gray-400 text-sm mt-1">{taskList.length} tasks</p>
		</div>
		<button on:click={openCreate} class="btn-primary">
			<Plus size={16} /> New Task
		</button>
	</div>

	<!-- Filters -->
	<div class="flex items-center gap-3 mb-5 flex-wrap">
		<div class="flex items-center gap-2">
			<Filter size={14} class="text-gray-400" />
			<select bind:value={filterStatus} class="bg-gray-800 border border-gray-700 text-gray-300 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary-500">
				<option value="">All Status</option>
				<option value="todo">To Do</option>
				<option value="in_progress">In Progress</option>
				<option value="review">Review</option>
				<option value="done">Done</option>
				<option value="blocked">Blocked</option>
			</select>
		</div>
		<label class="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
			<input type="checkbox" bind:checked={filterMine} class="rounded bg-gray-800 border-gray-700 text-primary-600 focus:ring-primary-500" />
			My tasks only
		</label>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if taskList.length === 0}
		<div class="card text-center py-12">
			<p class="text-gray-500">No tasks found. Create one to get started!</p>
		</div>
	{:else}
		<div class="space-y-2">
			{#each taskList as t}
				<div class="card flex items-start gap-4 hover:border-gray-700 transition-colors py-3.5">
					<button on:click={() => toggleStatus(t)} class="mt-0.5 flex-shrink-0">
						<div class="w-5 h-5 rounded-full border-2 {t.status === 'done' ? 'bg-green-500 border-green-500' : 'border-gray-600 hover:border-primary-500'} flex items-center justify-center transition-colors">
							{#if t.status === 'done'}<span class="text-white text-xs">✓</span>{/if}
						</div>
					</button>
					<div class="flex-1 min-w-0">
						<div class="flex items-start justify-between gap-3">
							<div class="flex-1 min-w-0">
								<p class="text-sm font-medium {t.status === 'done' ? 'line-through text-gray-500' : 'text-gray-200'}">{t.title}</p>
								{#if t.description}
									<p class="text-xs text-gray-500 mt-0.5 truncate">{t.description}</p>
								{/if}
								<div class="flex items-center gap-2 mt-2 flex-wrap">
									<span class="badge {statusColors[t.status]}">{statusLabels[t.status]}</span>
									<span class="badge {priorityColors[t.priority]}">{t.priority}</span>
									{#if t.due_date}
										<span class="text-xs {isOverdue(t.due_date) && t.status !== 'done' ? 'text-red-400' : 'text-gray-500'}">
											Due {formatDate(t.due_date)}
										</span>
									{/if}
									{#if t.assignee}
										<span class="text-xs text-gray-500">→ {t.assignee.full_name}</span>
									{/if}
									{#if t.tags}
										{#each t.tags.split(',') as tag}
											<span class="badge bg-gray-800 text-gray-400">{tag.trim()}</span>
										{/each}
									{/if}
								</div>
							</div>
							<div class="flex items-center gap-1 flex-shrink-0">
								<button on:click={() => openEdit(t)} class="p-1.5 text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors">
									<Pencil size={14} />
								</button>
								<button on:click={() => deleteTask(t.id)} class="p-1.5 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded transition-colors">
									<Trash2 size={14} />
								</button>
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Modal -->
{#if showModal}
	<div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
		<div class="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
			<div class="flex items-center justify-between p-5 border-b border-gray-800">
				<h2 class="font-semibold text-white">{editingTask ? 'Edit Task' : 'New Task'}</h2>
				<button on:click={() => (showModal = false)} class="text-gray-500 hover:text-gray-300"><X size={18} /></button>
			</div>
			<form on:submit|preventDefault={handleSubmit} class="p-5 space-y-4">
				<div>
					<label class="label" for="t-title">Title *</label>
					<input id="t-title" bind:value={form.title} class="input" required />
				</div>
				<div>
					<label class="label" for="t-desc">Description</label>
					<textarea id="t-desc" bind:value={form.description} class="input resize-none" rows="3"></textarea>
				</div>
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="label" for="t-status">Status</label>
						<select id="t-status" bind:value={form.status} class="input">
							<option value="todo">To Do</option>
							<option value="in_progress">In Progress</option>
							<option value="review">Review</option>
							<option value="done">Done</option>
							<option value="blocked">Blocked</option>
						</select>
					</div>
					<div>
						<label class="label" for="t-priority">Priority</label>
						<select id="t-priority" bind:value={form.priority} class="input">
							<option value="low">Low</option>
							<option value="medium">Medium</option>
							<option value="high">High</option>
							<option value="critical">Critical</option>
						</select>
					</div>
				</div>
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="label" for="t-due">Due Date</label>
						<input id="t-due" bind:value={form.due_date} type="date" class="input" />
					</div>
					<div>
						<label class="label" for="t-hours">Est. Hours</label>
						<input id="t-hours" bind:value={form.estimated_hours} type="number" min="0" class="input" />
					</div>
				</div>
				<div>
					<label class="label" for="t-assignee">Assignee</label>
					<select id="t-assignee" bind:value={form.assignee_id} class="input">
						<option value="">Unassigned</option>
						{#each userList as u}
							<option value={u.id}>{u.full_name}</option>
						{/each}
					</select>
				</div>
				<div>
					<label class="label" for="t-project">Project</label>
					<select id="t-project" bind:value={form.project_id} class="input">
						<option value="">No Project</option>
						{#each projectList as p}
							<option value={p.id}>{p.name}</option>
						{/each}
					</select>
				</div>
				<div>
					<label class="label" for="t-tags">Tags (comma-separated)</label>
					<input id="t-tags" bind:value={form.tags} class="input" placeholder="frontend, bug, v2" />
				</div>
				<div class="flex justify-end gap-3 pt-2">
					<button type="button" on:click={() => (showModal = false)} class="btn-secondary">Cancel</button>
					<button type="submit" class="btn-primary">{editingTask ? 'Save Changes' : 'Create Task'}</button>
				</div>
			</form>
		</div>
	</div>
{/if}
