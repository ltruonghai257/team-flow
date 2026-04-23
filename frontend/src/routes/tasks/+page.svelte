<script lang="ts">
	import { onMount } from 'svelte';
	import {
		tasks as tasksApi,
		users as usersApi,
		projects as projectsApi,
		milestones as milestonesApi
	} from '$lib/api';
	import { formatDate, statusColors, statusLabels, priorityColors, isOverdue } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import { Plus, Pencil, Trash2, X, Filter, List, Columns, Layers } from 'lucide-svelte';
	import KanbanBoard from '$lib/components/tasks/KanbanBoard.svelte';
	import AgileView from '$lib/components/tasks/AgileView.svelte';
	import AiTaskInput from '$lib/components/tasks/AiTaskInput.svelte';

	type ViewMode = 'list' | 'kanban' | 'agile';

	let taskList: any[] = [];
	let userList: any[] = [];
	let projectList: any[] = [];
	let milestoneList: any[] = [];
	let loading = true;
	let showModal = false;
	let editingTask: any = null;
	let filterStatus = '';
	let filterMine = false;
	let viewMode: ViewMode = 'list';
	let aiMode: 'form' | 'nlp' | 'json' | 'breakdown' = 'form';

	const VIEW_KEY = 'tasks_view_mode';

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
		const saved = localStorage.getItem(VIEW_KEY) as ViewMode | null;
		if (saved && ['list', 'kanban', 'agile'].includes(saved)) viewMode = saved;
		await loadAll();
	});

	function setView(v: ViewMode) {
		viewMode = v;
		localStorage.setItem(VIEW_KEY, v);
	}

	async function loadAll() {
		loading = true;
		try {
			[taskList, userList, projectList, milestoneList] = await Promise.all([
				tasksApi.list(),
				usersApi.list(),
				projectsApi.list(),
				milestonesApi.list()
			]);
		} finally {
			loading = false;
		}
	}

	async function loadTasks() {
		const params: any = {};
		if (filterStatus) params.status = filterStatus;
		if (filterMine) params.my_tasks = 'true';
		taskList = (await tasksApi.list(params)) as any[];
	}

	function resetForm() {
		form = {
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
	}

	function openCreate() {
		editingTask = null;
		aiMode = 'form';
		resetForm();
		showModal = true;
	}

	function openEdit(t: any) {
		editingTask = t;
		aiMode = 'form';
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

	function applyParsed(fields: Record<string, any>) {
		// Resolve assignee_name to id if possible
		if (fields.assignee_name && !fields.assignee_id) {
			const match = userList.find(
				(u: any) =>
					u.full_name.toLowerCase() === String(fields.assignee_name).toLowerCase() ||
					u.username.toLowerCase() === String(fields.assignee_name).toLowerCase()
			);
			if (match) fields.assignee_id = match.id;
		}
		form = {
			...form,
			...(fields.title !== undefined ? { title: fields.title } : {}),
			...(fields.description !== undefined ? { description: fields.description ?? '' } : {}),
			...(fields.status ? { status: fields.status } : {}),
			...(fields.priority ? { priority: fields.priority } : {}),
			...(fields.due_date ? { due_date: fields.due_date } : {}),
			...(fields.estimated_hours !== undefined
				? { estimated_hours: String(fields.estimated_hours ?? '') }
				: {}),
			...(fields.tags !== undefined ? { tags: fields.tags ?? '' } : {}),
			...(fields.assignee_id ? { assignee_id: String(fields.assignee_id) } : {})
		};
		toast.success('Parsed — review and create');
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
		} catch (e: any) {
			toast.error(e.message);
		}
	}

	async function deleteTask(id: number) {
		if (!confirm('Delete this task?')) return;
		try {
			await tasksApi.delete(id);
			toast.success('Task deleted');
			await loadTasks();
		} catch (e: any) {
			toast.error(e.message);
		}
	}

	async function toggleStatus(t: any) {
		const next = t.status === 'done' ? 'todo' : 'done';
		await changeStatus(t.id, next);
	}

	async function changeStatus(taskId: number, newStatus: string) {
		const prev = taskList;
		taskList = taskList.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t));
		try {
			await tasksApi.update(taskId, { status: newStatus });
		} catch (e: any) {
			taskList = prev;
			toast.error(e.message || 'Failed to update status');
			throw e;
		}
	}

	$: filterStatus, filterMine, loadTasks();
</script>

<svelte:head><title>Tasks · TeamFlow</title></svelte:head>

<div class="p-6 max-w-[1600px] mx-auto">
	<div class="flex items-center justify-between mb-5 flex-wrap gap-3">
		<div>
			<h1 class="text-2xl font-bold text-white">Tasks</h1>
			<p class="text-gray-400 text-sm mt-1">{taskList.length} tasks</p>
		</div>
		<div class="flex items-center gap-3">
			<!-- View toggle -->
			<div class="flex items-center bg-gray-900 border border-gray-800 rounded-lg p-0.5">
				<button
					on:click={() => setView('list')}
					class="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-md transition-colors {viewMode ===
					'list'
						? 'bg-gray-800 text-white'
						: 'text-gray-400 hover:text-gray-200'}"
				>
					<List size={14} /> List
				</button>
				<button
					on:click={() => setView('kanban')}
					class="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-md transition-colors {viewMode ===
					'kanban'
						? 'bg-gray-800 text-white'
						: 'text-gray-400 hover:text-gray-200'}"
				>
					<Columns size={14} /> Kanban
				</button>
				<button
					on:click={() => setView('agile')}
					class="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-md transition-colors {viewMode ===
					'agile'
						? 'bg-gray-800 text-white'
						: 'text-gray-400 hover:text-gray-200'}"
				>
					<Layers size={14} /> Agile
				</button>
			</div>
			<button on:click={openCreate} class="btn-primary">
				<Plus size={16} /> New Task
			</button>
		</div>
	</div>

	<!-- Filters -->
	<div class="flex items-center gap-3 mb-5 flex-wrap">
		<div class="flex items-center gap-2">
			<Filter size={14} class="text-gray-400" />
			<select
				bind:value={filterStatus}
				class="bg-gray-800 border border-gray-700 text-gray-300 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary-500"
			>
				<option value="">All Status</option>
				<option value="todo">To Do</option>
				<option value="in_progress">In Progress</option>
				<option value="review">Review</option>
				<option value="done">Done</option>
				<option value="blocked">Blocked</option>
			</select>
		</div>
		<label class="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
			<input
				type="checkbox"
				bind:checked={filterMine}
				class="rounded bg-gray-800 border-gray-700 text-primary-600 focus:ring-primary-500"
			/>
			My tasks only
		</label>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if viewMode === 'kanban'}
		<KanbanBoard tasks={taskList} onStatusChange={changeStatus} onEdit={openEdit} />
	{:else if viewMode === 'agile'}
		<AgileView
			tasks={taskList}
			milestones={milestoneList}
			onStatusChange={changeStatus}
			onEdit={openEdit}
			onDelete={deleteTask}
		/>
	{:else if taskList.length === 0}
		<div class="card text-center py-12">
			<p class="text-gray-500">No tasks found. Create one to get started!</p>
		</div>
	{:else}
		<div class="space-y-2">
			{#each taskList as t}
				<div class="card flex items-start gap-4 hover:border-gray-700 transition-colors py-3.5">
					<button on:click={() => toggleStatus(t)} class="mt-0.5 flex-shrink-0">
						<div
							class="w-5 h-5 rounded-full border-2 {t.status === 'done'
								? 'bg-green-500 border-green-500'
								: 'border-gray-600 hover:border-primary-500'} flex items-center justify-center transition-colors"
						>
							{#if t.status === 'done'}<span class="text-white text-xs">✓</span>{/if}
						</div>
					</button>
					<div class="flex-1 min-w-0">
						<div class="flex items-start justify-between gap-3">
							<div class="flex-1 min-w-0">
								<p class="text-sm font-medium {t.status === 'done' ? 'line-through text-gray-500' : 'text-gray-200'}">
									{t.title}
								</p>
								{#if t.description}
									<p class="text-xs text-gray-500 mt-0.5 truncate">{t.description}</p>
								{/if}
								<div class="flex items-center gap-2 mt-2 flex-wrap">
									<span class="badge {statusColors[t.status]}">{statusLabels[t.status]}</span>
									<span class="badge {priorityColors[t.priority]}">{t.priority}</span>
									{#if t.due_date}
										<span
											class="text-xs {isOverdue(t.due_date) && t.status !== 'done'
												? 'text-red-400'
												: 'text-gray-500'}"
										>
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
								<button
									on:click={() => openEdit(t)}
									class="p-1.5 text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
								>
									<Pencil size={14} />
								</button>
								<button
									on:click={() => deleteTask(t.id)}
									class="p-1.5 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded transition-colors"
								>
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
				<button on:click={() => (showModal = false)} class="text-gray-500 hover:text-gray-300">
					<X size={18} />
				</button>
			</div>

			<div class="p-5">
				{#if !editingTask}
					<AiTaskInput bind:mode={aiMode} onParsed={applyParsed} {projectList} {milestoneList} {userList}>
						<form on:submit|preventDefault={handleSubmit} class="space-y-4">
							<!-- Form fields (shared with edit mode) -->
							<div>
								<label class="label" for="t-title">Title *</label>
								<input id="t-title" bind:value={form.title} class="input" required />
							</div>
							<div>
								<label class="label" for="t-desc">Description</label>
								<textarea id="t-desc" bind:value={form.description} class="input resize-none" rows="3"
								></textarea>
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
									<input
										id="t-hours"
										bind:value={form.estimated_hours}
										type="number"
										min="0"
										class="input"
									/>
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
								<button type="button" on:click={() => (showModal = false)} class="btn-secondary">
									Cancel
								</button>
								<button type="submit" class="btn-primary">Create Task</button>
							</div>
						</form>
					</AiTaskInput>
				{:else}
					<!-- Edit mode: just the form, no AI tabs -->
					<form on:submit|preventDefault={handleSubmit} class="space-y-4">
						<div>
							<label class="label" for="t-title-e">Title *</label>
							<input id="t-title-e" bind:value={form.title} class="input" required />
						</div>
						<div>
							<label class="label" for="t-desc-e">Description</label>
							<textarea id="t-desc-e" bind:value={form.description} class="input resize-none" rows="3"
							></textarea>
						</div>
						<div class="grid grid-cols-2 gap-4">
							<div>
								<label class="label" for="t-status-e">Status</label>
								<select id="t-status-e" bind:value={form.status} class="input">
									<option value="todo">To Do</option>
									<option value="in_progress">In Progress</option>
									<option value="review">Review</option>
									<option value="done">Done</option>
									<option value="blocked">Blocked</option>
								</select>
							</div>
							<div>
								<label class="label" for="t-priority-e">Priority</label>
								<select id="t-priority-e" bind:value={form.priority} class="input">
									<option value="low">Low</option>
									<option value="medium">Medium</option>
									<option value="high">High</option>
									<option value="critical">Critical</option>
								</select>
							</div>
						</div>
						<div class="grid grid-cols-2 gap-4">
							<div>
								<label class="label" for="t-due-e">Due Date</label>
								<input id="t-due-e" bind:value={form.due_date} type="date" class="input" />
							</div>
							<div>
								<label class="label" for="t-hours-e">Est. Hours</label>
								<input
									id="t-hours-e"
									bind:value={form.estimated_hours}
									type="number"
									min="0"
									class="input"
								/>
							</div>
						</div>
						<div>
							<label class="label" for="t-assignee-e">Assignee</label>
							<select id="t-assignee-e" bind:value={form.assignee_id} class="input">
								<option value="">Unassigned</option>
								{#each userList as u}
									<option value={u.id}>{u.full_name}</option>
								{/each}
							</select>
						</div>
						<div>
							<label class="label" for="t-project-e">Project</label>
							<select id="t-project-e" bind:value={form.project_id} class="input">
								<option value="">No Project</option>
								{#each projectList as p}
									<option value={p.id}>{p.name}</option>
								{/each}
							</select>
						</div>
						<div>
							<label class="label" for="t-tags-e">Tags (comma-separated)</label>
							<input id="t-tags-e" bind:value={form.tags} class="input" placeholder="frontend, bug, v2" />
						</div>
						<div class="flex justify-end gap-3 pt-2">
							<button type="button" on:click={() => (showModal = false)} class="btn-secondary">
								Cancel
							</button>
							<button type="submit" class="btn-primary">Save Changes</button>
						</div>
					</form>
				{/if}
			</div>
		</div>
	</div>
{/if}
