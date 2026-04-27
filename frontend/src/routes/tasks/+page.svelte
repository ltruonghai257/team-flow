<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import {
		tasks as tasksApi,
		users as usersApi,
		projects as projectsApi,
		milestones as milestonesApi,
		sprints as sprintsApi,
		statusSets
	} from '$lib/api';
	import type { CustomStatus, StatusSet, StatusTransition } from '$lib/api';
	import StatusSetManager from '$lib/components/statuses/StatusSetManager.svelte';
	import { isSupervisor } from '$lib/stores/auth';
	import {
		formatDate,
		statusColors,
		statusLabels,
		priorityColors,
		taskTypeColors,
		taskTypeLabels,
		taskTypeOptions,
		isOverdue,
		statusDisplayName,
		statusDisplayColor
	} from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import {
		Plus,
		Pencil,
		Trash2,
		X,
		Filter,
		List,
		Columns,
		Layers,
		Sparkles,
		Bug,
		CheckSquare,
		Wrench,
		Zap
	} from 'lucide-svelte';
	import KanbanBoard from '$lib/components/tasks/KanbanBoard.svelte';
	import AgileView from '$lib/components/tasks/AgileView.svelte';
	import AiTaskInput from '$lib/components/tasks/AiTaskInput.svelte';
	import SprintCloseModal from '$lib/components/sprints/SprintCloseModal.svelte';

	type ViewMode = 'list' | 'kanban' | 'agile';
	type StatusManagerTab = 'statuses' | 'transitions';

	let taskList: any[] = [];
	let backlogTaskList: any[] = [];
	let userList: any[] = [];
	let projectList: any[] = [];
	let milestoneList: any[] = [];
	let sprintList: any[] = [];
	let statusSetData: StatusSet | null = null;
	let loading = true;
	let showModal = false;
	let showCloseSprintModal = false;
	let showStatusManager = false;
	let statusManagerTab: StatusManagerTab = 'statuses';
	let editingTask: any = null;
	let filterStatus = '';
	let filterStatusId: number | null = null;
	let selectedTypes: string[] = [];
	let filterMine = false;
	let selectedSprintId: number | null = null;
	let highlightedTaskId: number | null = null;
	let handledRouteKey = '';
	let filterProjectId: number | null = null;
	let viewMode: ViewMode = 'list';
	let aiMode: 'form' | 'nlp' | 'json' | 'breakdown' = 'form';
	let transitionRows: StatusTransition[] = [];

	const VIEW_KEY = 'tasks_view_mode';
	const STATUS_MANAGER_KEY = 'status_manager';
	const STATUS_TAB_KEY = 'status_tab';
	const taskTypeIcons: Record<string, any> = {
		feature: Sparkles,
		bug: Bug,
		task: CheckSquare,
		improvement: Wrench
	};

	let form = {
		title: '',
		description: '',
		status: 'todo',
		custom_status_id: null as number | null,
		priority: 'medium',
		type: 'task',
		due_date: '',
		estimated_hours: '',
		tags: '',
		project_id: '',
		assignee_id: '',
		sprint_id: null as number | null
	};

	$: activeStatuses = statusSetData?.statuses.filter((s: CustomStatus) => !s.is_archived) ?? [];
	$: isMixedProjectView =
		statusSetData?.scope === 'project' && !filterProjectId && projectList.length > 1;
	$: isTaskDone = (t: any) =>
		t.custom_status?.is_done ?? (t.status === 'done');
	$: hasTransitionRules = transitionRows.length > 0;

	onMount(async () => {
		const saved = localStorage.getItem(VIEW_KEY) as ViewMode | null;
		if (saved && ['list', 'kanban', 'agile'].includes(saved)) viewMode = saved;
		await loadAll();
		await applyRouteSelection($page.url.searchParams.toString());
	});

	function parsePositiveId(value: string | null): number | null {
		if (!value) return null;
		const parsed = Number(value);
		return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
	}

	async function applyRouteSelection(routeKey: string) {
		if (routeKey === handledRouteKey) return;
		handledRouteKey = routeKey;

		const params = new URLSearchParams(routeKey);
		const taskId = parsePositiveId(params.get('task_id'));
		const sprintId = parsePositiveId(params.get('sprint_id'));
		const statusManagerParam = params.get(STATUS_MANAGER_KEY);
		const statusTabParam = params.get(STATUS_TAB_KEY);

		showStatusManager =
			statusManagerParam === '1' ||
			statusManagerParam === 'true' ||
			statusTabParam != null;
		if (statusTabParam === 'transitions' || statusTabParam === 'statuses') {
			statusManagerTab = statusTabParam;
		}

		highlightedTaskId = taskId;

		if (taskId) {
			filterStatus = '';
			selectedTypes = [];
			filterMine = false;
			viewMode = 'list';
			try {
				const task = await tasksApi.get(taskId);
				selectedSprintId = task.sprint_id ?? null;
			} catch {
				// Keep the route visible even if the referenced task no longer exists.
			}
			await loadTasks();
			await tick();
			document.getElementById(`task-${taskId}`)?.scrollIntoView({ block: 'center', behavior: 'smooth' });
			return;
		}

		if (sprintId) {
			filterStatus = '';
			selectedTypes = [];
			filterMine = false;
			selectedSprintId = sprintId;
			await loadTasks();
		}
	}

	async function syncStatusManagerRoute(open: boolean, tab: StatusManagerTab = statusManagerTab) {
		const url = new URL($page.url);
		if (open) {
			url.searchParams.set(STATUS_MANAGER_KEY, '1');
			url.searchParams.set(STATUS_TAB_KEY, tab);
		} else {
			url.searchParams.delete(STATUS_MANAGER_KEY);
			url.searchParams.delete(STATUS_TAB_KEY);
		}
		await goto(url, {
			replaceState: true,
			noScroll: true,
			keepFocus: true
		});
	}

	function openStatusManager(tab: StatusManagerTab = statusManagerTab) {
		showStatusManager = true;
		statusManagerTab = tab;
		void syncStatusManagerRoute(true, tab);
	}

	function closeStatusManager() {
		showStatusManager = false;
		void syncStatusManagerRoute(false);
	}

	function setStatusManagerTab(tab: StatusManagerTab) {
		statusManagerTab = tab;
		showStatusManager = true;
		void syncStatusManagerRoute(true, tab);
	}

	async function loadStatusSet() {
		try {
			statusSetData = await statusSets.getEffective(filterProjectId ?? undefined);
		} catch {
			statusSetData = null;
		}
		await loadTransitionRows();
	}

	async function loadTransitionRows() {
		if (!statusSetData?.id) {
			transitionRows = [];
			return;
		}
		try {
			transitionRows = await statusSets.getTransitions(statusSetData.id, true);
		} catch {
			transitionRows = [];
		}
	}

	function setView(v: ViewMode) {
		viewMode = v;
		localStorage.setItem(VIEW_KEY, v);
	}

	async function loadAll() {
		loading = true;
		try {
			const [t, u, p, m, s] = await Promise.all([
				tasksApi.list(),
				usersApi.list(),
				projectsApi.list(),
				milestonesApi.list(),
				sprintsApi.list()
			]);
			taskList = t;
			userList = u;
			projectList = p;
			milestoneList = m;
			sprintList = s;

			if (selectedSprintId && !sprintList.some((s) => s.id === selectedSprintId)) {
				selectedSprintId = null;
			}
			// Set initial selectedSprintId to the first active sprint if none selected
			if (!selectedSprintId && sprintList.length > 0) {
				const active = sprintList.find((s) => s.status === 'active');
				if (active) selectedSprintId = active.id;
			}
			await loadStatusSet();
		} finally {
			loading = false;
		}
	}

	$: if (typeof window !== 'undefined' && !loading) {
		applyRouteSelection($page.url.searchParams.toString());
	}

	async function loadTasks() {
		const params: any = {};
		if (filterStatus) params.status = filterStatus;
		if (selectedTypes.length > 0) params.types = selectedTypes.join(',');
		if (filterMine) params.my_tasks = 'true';
		if (selectedSprintId) params.sprint_id = selectedSprintId;

		taskList = (await tasksApi.list(params)) as any[];

		if (viewMode === 'kanban') {
			backlogTaskList = (await tasksApi.list({ unassigned: true })) as any[];
		}
	}

	$: activeSprint = sprintList.find((s) => s.id === selectedSprintId);
	$: incompleteTasks = taskList.filter((t) => !isTaskDone(t));

	function resolveTaskStatusId(task: any): number | null {
		if (task?.custom_status_id != null) return task.custom_status_id;
		if (task?.custom_status?.id != null) return task.custom_status.id;
		const legacyStatus = task?.status;
		if (!legacyStatus) return null;
		const matched = statusSetData?.statuses.find(
			(s: CustomStatus) => s.legacy_status === legacyStatus || s.slug === legacyStatus
		);
		return matched?.id ?? null;
	}

	function getTaskStatusName(task: any): string {
		return (
			statusDisplayName(task?.custom_status) ||
			statusLabels[task?.status] ||
			task?.status ||
			'Unknown'
		);
	}

	function getStatusById(statusId: number | null | undefined): CustomStatus | null {
		if (statusId == null) return null;
		return (
			statusSetData?.statuses.find((s: CustomStatus) => s.id === statusId) ??
			activeStatuses.find((s: CustomStatus) => s.id === statusId) ??
			null
		);
	}

	function getAllowedTargetStatusIds(currentStatusId: number | null): number[] {
		const activeStatusIds = activeStatuses.map((s: CustomStatus) => s.id);
		if (!hasTransitionRules || currentStatusId == null) return activeStatusIds;
		const allowed = new Set<number>([currentStatusId]);
		for (const transition of transitionRows) {
			if (
				transition.from_status_id === currentStatusId &&
				activeStatusIds.includes(transition.to_status_id)
			) {
				allowed.add(transition.to_status_id);
			}
		}
		return activeStatusIds.filter((statusId) => allowed.has(statusId));
	}

	function isMoveAllowed(task: any, targetStatusId: number | null): boolean {
		const currentStatusId = resolveTaskStatusId(task);
		if (currentStatusId == null || targetStatusId == null) return true;
		if (currentStatusId === targetStatusId || !hasTransitionRules) return true;
		return transitionRows.some(
			(transition) =>
				transition.from_status_id === currentStatusId &&
				transition.to_status_id === targetStatusId
		);
	}

	function getTaskStatusOptions(task: any) {
		const currentStatusId = resolveTaskStatusId(task);
		const allowedStatusIds = getAllowedTargetStatusIds(currentStatusId);
		const allowedStatuses = activeStatuses.filter((status: CustomStatus) =>
			allowedStatusIds.includes(status.id)
		);
		const currentStatus = getStatusById(currentStatusId);
		const currentLabel = getTaskStatusName(task);

		if (currentStatus) {
			if (allowedStatuses.some((status) => status.id === currentStatus.id)) {
				return allowedStatuses;
			}
			return [currentStatus, ...allowedStatuses];
		}

		return [
			{
				id: null,
				status_set_id: statusSetData?.id ?? 0,
				name: currentLabel,
				slug: task?.status ?? '',
				color: task?.custom_status?.color ?? '#64748b',
				position: -1,
				is_done: task?.custom_status?.is_done ?? task?.status === 'done',
				is_archived: false,
				legacy_status: task?.status ?? null,
				task_count: 0,
				created_at: '',
				updated_at: ''
			} as unknown as CustomStatus,
			...allowedStatuses
		];
	}

	function getLegacyStatusOptions(currentStatus: string) {
		const options = [
			{ value: 'todo', label: 'To Do' },
			{ value: 'in_progress', label: 'In Progress' },
			{ value: 'review', label: 'Review' },
			{ value: 'done', label: 'Done' },
			{ value: 'blocked', label: 'Blocked' }
		];
		if (!options.some((option) => option.value === currentStatus)) {
			return [{ value: currentStatus, label: statusLabels[currentStatus] ?? currentStatus }, ...options];
		}
		return options;
	}

	type TaskWorkflowError = {
		code?: string;
		current_status_name?: string;
		target_status_name?: string;
		allowed_status_ids?: number[];
	};

	function getWorkflowErrorDetail(error: any): TaskWorkflowError | null {
		const detail = error?.detail;
		if (detail && typeof detail === 'object' && detail.code === 'status_transition_blocked') {
			return detail as TaskWorkflowError;
		}
		return null;
	}

	function toastWorkflowBlocked(detail: TaskWorkflowError | null, fallback = 'This move is not allowed by the workflow rules.') {
		if (detail?.current_status_name && detail?.target_status_name) {
			toast.error(`Cannot move from ${detail.current_status_name} to ${detail.target_status_name}`);
			return;
		}
		toast.error(fallback);
	}

	async function refreshWorkflowData() {
		await loadStatusSet();
	}

	function isStatusRestricted(targetStatusId: number): boolean {
		if (!hasTransitionRules) return false;
		return activeStatuses.some(
			(status: CustomStatus) => !canMoveStatus(status.id, targetStatusId)
		);
	}

	function resetForm() {
		const defaultStatus = activeStatuses[0] ?? null;
		form = {
			title: '',
			description: '',
			status: 'todo',
			custom_status_id: defaultStatus?.id ?? null,
			priority: 'medium',
			type: 'task',
			due_date: '',
			estimated_hours: '',
			tags: '',
			project_id: '',
			assignee_id: '',
			sprint_id: null
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
			custom_status_id: activeStatuses.length > 0 ? resolveTaskStatusId(t) : null,
			priority: t.priority,
			type: t.type || 'task',
			due_date: t.due_date ? t.due_date.slice(0, 10) : '',
			estimated_hours: t.estimated_hours || '',
			tags: t.tags || '',
			project_id: t.project_id || '',
			assignee_id: t.assignee_id || '',
			sprint_id: t.sprint_id || null
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
			...(fields.type ? { type: fields.type } : {}),
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
			assignee_id: form.assignee_id ? Number(form.assignee_id) : null,
			sprint_id: editingTask ? form.sprint_id : selectedSprintId
		};
		if (editingTask && activeStatuses.length > 0) {
			payload.custom_status_id = form.custom_status_id ?? undefined;
		}
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
			const detail = getWorkflowErrorDetail(e);
			if (detail) {
				toastWorkflowBlocked(detail);
				await refreshWorkflowData();
			} else {
				toast.error(e.message);
			}
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

	function taskTypeIcon(type: string) {
		return taskTypeIcons[type] || CheckSquare;
	}

	function taskTypeValue(t: any) {
		return t.type || 'task';
	}

	function toggleTypeFilter(type: string) {
		selectedTypes = selectedTypes.includes(type)
			? selectedTypes.filter((t) => t !== type)
			: [...selectedTypes, type];
	}

	async function toggleStatus(t: any) {
		if (isTaskDone(t)) {
			// Move back to first non-done status
			const firstNonDone = activeStatuses.find((s: CustomStatus) => !s.is_done);
			if (firstNonDone) {
				await changeStatus(t.id, null, firstNonDone.id);
			} else {
				await changeStatus(t.id, 'todo', null);
			}
		} else {
			const firstDone = activeStatuses.find((s: CustomStatus) => s.is_done);
			if (firstDone) {
				await changeStatus(t.id, null, firstDone.id);
			} else {
				await changeStatus(t.id, 'done', null);
			}
		}
	}

	async function changeStatus(taskId: number, legacyStatus: string | null, customStatusId: number | null) {
		const prev = taskList;
		const patch: any = {};
		if (customStatusId != null) patch.custom_status_id = customStatusId;
		else if (legacyStatus) patch.status = legacyStatus;
		taskList = taskList.map((t) => (t.id === taskId ? { ...t, ...patch } : t));
		try {
			await tasksApi.update(taskId, patch);
		} catch (e: any) {
			taskList = prev;
			const detail = getWorkflowErrorDetail(e);
			if (detail) {
				toastWorkflowBlocked(detail);
				await refreshWorkflowData();
			} else {
				toast.error(e.message || 'Failed to update status');
			}
			throw e;
		}
	}

	async function handleTaskMove(e: CustomEvent) {
		const { id, sprint_id, status, custom_status_id } = e.detail;
		try {
			const patch: any = { sprint_id };
			if (custom_status_id != null) patch.custom_status_id = custom_status_id;
			else if (status) patch.status = status;
			await tasksApi.update(id, patch);
			toast.success('Task moved');
			await loadTasks();
		} catch (e: any) {
			const detail = getWorkflowErrorDetail(e);
			if (detail) {
				toastWorkflowBlocked(detail);
				await refreshWorkflowData();
			} else {
				toast.error(e.message || 'Failed to move task');
			}
			await loadTasks();
		}
	}

	async function handleTaskMoveBlocked(e: CustomEvent) {
		toastWorkflowBlocked(e.detail ?? null);
		await refreshWorkflowData();
		await loadTasks();
	}

	function getBlockedMoveDetail(task: any, targetStatusId: number) {
		const currentStatusId = resolveTaskStatusId(task);
		const targetStatus = getStatusById(targetStatusId);
		const currentStatus = getStatusById(currentStatusId);
		return {
			allowed: isMoveAllowed(task, targetStatusId),
			currentStatusId,
			currentStatusName: currentStatus?.name ?? getTaskStatusName(task),
			targetStatusId,
			targetStatusName: targetStatus?.name ?? 'Selected status',
			allowedStatusIds: getAllowedTargetStatusIds(currentStatusId)
		};
	}

	function assessTaskMove(task: any, targetStatusId: number) {
		return getBlockedMoveDetail(task, targetStatusId);
	}

	function canMoveStatus(currentStatusId: number, targetStatusId: number) {
		if (currentStatusId === targetStatusId || !hasTransitionRules) return true;
		return transitionRows.some(
			(transition) =>
				transition.from_status_id === currentStatusId &&
				transition.to_status_id === targetStatusId
		);
	}

	$: filterStatus, selectedTypes, filterMine, selectedSprintId, viewMode, loadTasks();
</script>

<svelte:head><title>Tasks · TeamFlow</title></svelte:head>

<div class="p-4 md:p-6 max-w-[1600px] mx-auto">
	<div class="flex items-center justify-between mb-4 md:mb-5 flex-wrap gap-3">
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
			<Zap size={14} class="text-gray-400" />
			<select
				bind:value={selectedSprintId}
				class="bg-gray-800 border border-gray-700 text-gray-300 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary-500"
			>
				<option value={null}>No Sprint (Backlog)</option>
				{#each sprintList as s}
					<option value={s.id}>{s.name} ({s.status})</option>
				{/each}
			</select>
			{#if activeSprint && activeSprint.status === 'active'}
				<button
					on:click={() => (showCloseSprintModal = true)}
					class="text-xs text-gray-400 hover:text-white transition-colors ml-1"
				>
					Close Sprint
				</button>
			{/if}
		</div>

		<div class="flex items-center gap-2">
			<Filter size={14} class="text-gray-400" />
			<select
				bind:value={filterStatus}
				class="bg-gray-800 border border-gray-700 text-gray-300 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary-500"
			>
				<option value="">All Status</option>
				{#if activeStatuses.length > 0}
					{#each activeStatuses as s}
						<option value={s.slug}>{s.name}</option>
					{/each}
				{:else}
					<option value="todo">To Do</option>
					<option value="in_progress">In Progress</option>
					<option value="review">Review</option>
					<option value="done">Done</option>
					<option value="blocked">Blocked</option>
				{/if}
			</select>
		</div>

		{#if $isSupervisor}
			<button
				on:click={() => (showStatusManager ? closeStatusManager() : openStatusManager())}
				class="text-xs text-gray-400 hover:text-white border border-gray-700 rounded px-2 py-1.5 transition-colors"
			>
				{showStatusManager ? 'Hide Statuses' : 'Manage Statuses'}
		</button>
	{/if}
		<label class="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
			<input
				type="checkbox"
				bind:checked={filterMine}
				class="rounded bg-gray-800 border-gray-700 text-primary-600 focus:ring-primary-500"
			/>
			My tasks only
		</label>
		<div class="flex items-center gap-2 flex-wrap">
			<span class="text-sm text-gray-500">Type</span>
			{#each taskTypeOptions as type}
				<button
					type="button"
					on:click={() => toggleTypeFilter(type)}
					class="badge flex items-center gap-1 transition-colors {selectedTypes.includes(type)
						? taskTypeColors[type]
						: 'bg-gray-800 text-gray-400 hover:text-gray-200'}"
				>
					<svelte:component this={taskTypeIcon(type)} size={12} />
					{taskTypeLabels[type]}
				</button>
			{/each}
		</div>
	</div>

	{#if showStatusManager}
		<div class="mb-4 rounded-xl border border-gray-700 bg-gray-900/80 p-4">
			<StatusSetManager
				statusSet={statusSetData}
				scopeLabel={filterProjectId && !isMixedProjectView ? 'Project' : 'Sub-team default'}
				canManage={$isSupervisor}
				{isMixedProjectView}
				activeTab={statusManagerTab}
				onTabChange={setStatusManagerTab}
				onRefresh={loadStatusSet}
			/>
			{#if isMixedProjectView}
				<p class="text-xs text-gray-500 mt-2 italic">
					Project-specific statuses are available after filtering to one project.
				</p>
			{/if}
		</div>
	{/if}

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if viewMode === 'kanban'}
		<KanbanBoard
			tasks={taskList}
			backlogTasks={backlogTaskList}
			activeSprintId={selectedSprintId}
			statuses={activeStatuses}
			assessTaskMove={assessTaskMove}
			isStatusRestricted={isStatusRestricted}
			on:taskMove={handleTaskMove}
			on:taskMoveBlocked={handleTaskMoveBlocked}
			onEdit={openEdit}
		/>
	{:else if viewMode === 'agile'}
		<AgileView
			tasks={taskList}
			milestones={milestoneList}
			onStatusChange={(taskId: number, legacyStatus: string) => changeStatus(taskId, legacyStatus, null)}
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
				<div
					id={`task-${t.id}`}
					class="card flex items-start gap-4 hover:border-gray-700 transition-colors py-3.5 {highlightedTaskId === t.id
						? 'ring-1 ring-primary-500/40 border-primary-500/40'
						: ''}"
				>
					<button on:click={() => toggleStatus(t)} class="mt-0.5 flex-shrink-0">
						<div
							class="w-5 h-5 rounded-full border-2 {isTaskDone(t)
								? 'bg-green-500 border-green-500'
								: 'border-gray-600 hover:border-primary-500'} flex items-center justify-center transition-colors"
						>
							{#if isTaskDone(t)}<span class="text-white text-xs">✓</span>{/if}
						</div>
					</button>
					<div class="flex-1 min-w-0">
						<div class="flex items-start justify-between gap-3">
							<div class="flex-1 min-w-0">
								<p class="text-sm font-medium {isTaskDone(t) ? 'line-through text-gray-500' : 'text-gray-200'}">
									{t.title}
								</p>
								{#if t.description}
									<p class="text-xs text-gray-500 mt-0.5 truncate">{t.description}</p>
								{/if}
								<div class="flex items-center gap-2 mt-2 flex-wrap">
									<span class="badge" style="background-color: {t.custom_status ? t.custom_status.color + '33' : ''}; color: {t.custom_status ? t.custom_status.color : ''}">
									{statusDisplayName(t.custom_status) || statusLabels[t.status] || t.status}
								</span>
									<span class="badge {taskTypeColors[taskTypeValue(t)]} flex items-center gap-1">
										<svelte:component this={taskTypeIcon(taskTypeValue(t))} size={11} />
										{taskTypeLabels[taskTypeValue(t)]}
									</span>
									<span class="badge {priorityColors[t.priority]}">{t.priority}</span>
									{#if t.due_date}
										<span
											class="text-xs {isOverdue(t.due_date) && !isTaskDone(t)
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
		<div class="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-lg max-h-[92dvh] overflow-y-auto">
			<div class="flex items-center justify-between p-5 border-b border-gray-800">
				<h2 class="font-semibold text-white">{editingTask ? 'Edit Task' : 'New Task'}</h2>
				<button on:click={() => (showModal = false)} class="text-gray-500 hover:text-gray-300">
					<X size={18} />
				</button>
			</div>

			<div class="p-5">
				{#if !editingTask}
					<AiTaskInput
						bind:mode={aiMode}
						onParsed={applyParsed}
						{projectList}
						{milestoneList}
						{userList}
						{selectedSprintId}
					>
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
							<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
								<div>
									<label class="label" for="t-type">Type</label>
									<select id="t-type" bind:value={form.type} class="input">
										{#each taskTypeOptions as type}
											<option value={type}>{taskTypeLabels[type]}</option>
										{/each}
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
								<label class="label" for="t-sprint">Sprint</label>
								<select id="t-sprint" bind:value={form.sprint_id} class="input">
									<option value={null}>No Sprint (Backlog)</option>
									{#each sprintList as s}
										<option value={s.id}>{s.name} ({s.status})</option>
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
						<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
							<div>
								<label class="label" for="t-status-e">Status</label>
								{#if activeStatuses.length > 0}
									<select id="t-status-e" bind:value={form.custom_status_id} class="input">
										{#each getTaskStatusOptions(editingTask) as s}
											<option value={s.id}>{s.name}</option>
										{/each}
									</select>
								{:else}
									<select id="t-status-e" bind:value={form.status} class="input">
										{#each getLegacyStatusOptions(form.status) as option}
											<option value={option.value}>{option.label}</option>
										{/each}
									</select>
								{/if}
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
							<div>
								<label class="label" for="t-type-e">Type</label>
								<select id="t-type-e" bind:value={form.type} class="input">
									{#each taskTypeOptions as type}
										<option value={type}>{taskTypeLabels[type]}</option>
									{/each}
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
							<label class="label" for="t-sprint-e">Sprint</label>
							<select id="t-sprint-e" bind:value={form.sprint_id} class="input">
								<option value={null}>No Sprint (Backlog)</option>
								{#each sprintList as s}
									<option value={s.id}>{s.name} ({s.status})</option>
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

<SprintCloseModal
	bind:show={showCloseSprintModal}
	sprint={activeSprint}
	{incompleteTasks}
	availableSprints={sprintList}
	on:success={loadAll}
/>
