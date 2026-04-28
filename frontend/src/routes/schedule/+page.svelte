<script lang="ts">
	import { onMount } from 'svelte';
	import { currentUser } from '$lib/stores/auth';
	import { subTeamStore } from '$lib/stores/subTeam';
	import {
		schedules as schedulesApi,
		tasks as tasksApi,
		notifications as notifApi,
		knowledgeSessions as knowledgeSessionsApi,
		users as usersApi
	} from '$lib/apis';
	import { formatDateTime } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import {
		BookOpen,
		Calendar,
		CheckSquare,
		Clock,
		Bell,
		List,
		MapPin,
		Pencil,
		Plus,
		Trash2,
		X
	} from 'lucide-svelte';
	import {
		format,
		startOfMonth,
		endOfMonth,
		eachDayOfInterval,
		isSameDay,
		isSameMonth,
		startOfWeek,
		endOfWeek
	} from 'date-fns';
	import SessionCard from '$lib/components/knowledge/SessionCard.svelte';
	import SessionForm from '$lib/components/knowledge/SessionForm.svelte';
	import type { KnowledgeSession } from '$lib/apis/knowledge-sessions';

	type EventItem = {
		id: number;
		source: 'schedule' | 'task';
		title: string;
		description?: string;
		start_time: string;
		end_time: string;
		color: string;
		location?: string;
		raw: any;
	};

	type TabKey = 'schedule' | 'knowledge';
	type KnowledgeView = 'agenda' | 'calendar';

	const REMINDER_OFFSETS = [
		{ value: 15, label: '15 min before' },
		{ value: 30, label: '30 min before' },
		{ value: 60, label: '1 hour before' },
		{ value: 1440, label: '1 day before' }
	];

	let scheduleList: any[] = [];
	let taskEvents: EventItem[] = [];
	let knowledgeSessions: KnowledgeSession[] = [];
	let knowledgeUsers: any[] = [];
	let loading = true;
	let activeTab: TabKey = 'schedule';
	let knowledgeViewMode: KnowledgeView = 'agenda';
	let knowledgeSelectedDay: Date | null = null;
	let currentMonth = new Date();
	let showScheduleModal = false;
	let editingSchedule: any = null;
	let showKnowledgeModal = false;
	let editingKnowledgeSession: KnowledgeSession | null = null;
	let knowledgeModalSeedDate: Date | null = null;

	let form = {
		title: '',
		description: '',
		start_time: '',
		end_time: '',
		all_day: false,
		color: '#6366f1',
		location: ''
	};
	let formReminders: number[] = [];

	onMount(loadAll);

	async function loadAll() {
		loading = true;
		try {
			await Promise.all([loadScheduleData(), loadKnowledgeData()]);
		} finally {
			loading = false;
		}
	}

	async function loadScheduleData() {
		const [schedules, taskList] = await Promise.all([schedulesApi.list(), tasksApi.list()]);
		scheduleList = schedules;
		taskEvents = (taskList as any[])
			.filter((t) => !!t.due_date)
			.map((t) => ({
				id: t.id,
				source: 'task' as const,
				title: t.title,
				description: t.description,
				start_time: t.due_date,
				end_time: t.due_date,
				color: '#f59e0b',
				location: undefined,
				raw: t
			}));
	}

	async function loadKnowledgeData() {
		try {
			knowledgeSessions = await knowledgeSessionsApi.list();
		} catch {
			knowledgeSessions = [];
			toast.error('Failed to load knowledge sessions.');
		}
		try {
			knowledgeUsers = await usersApi.list();
		} catch {
			knowledgeUsers = [];
		}
	}

	function scheduleToEvent(s: any): EventItem {
		return {
			id: s.id,
			source: 'schedule',
			title: s.title,
			description: s.description,
			start_time: s.start_time,
			end_time: s.end_time,
			color: s.color,
			location: s.location,
			raw: s
		};
	}

	$: allEvents = [...scheduleList.map(scheduleToEvent), ...taskEvents];
	$: allEventsSorted = allEvents
		.slice()
		.sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
	$: knowledgeSessionsSorted = knowledgeSessions
		.slice()
		.sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
	$: knowledgeAgendaGroups = buildKnowledgeGroups(knowledgeSessionsSorted);
	$: knowledgeUpcomingSessions = knowledgeSessionsSorted.filter(
		(session) => new Date(session.start_time).getTime() >= Date.now()
	);
	$: knowledgeSelectedDaySessions = (() => {
		const selectedDay = knowledgeSelectedDay;
		return selectedDay
			? knowledgeSessionsSorted.filter((session) =>
					isSameDay(new Date(session.start_time), selectedDay)
				)
			: [];
	})();
	$: calDays = (() => {
		const start = startOfWeek(startOfMonth(currentMonth), { weekStartsOn: 1 });
		const end = endOfWeek(endOfMonth(currentMonth), { weekStartsOn: 1 });
		return eachDayOfInterval({ start, end });
	})();
	$: currentUserRole = $currentUser?.role ?? 'member';
	$: canManageKnowledge = currentUserRole === 'admin' || currentUserRole === 'supervisor';
	$: knowledgePresenterHint =
		currentUserRole === 'admin' && !$subTeamStore
			? 'Org-wide sessions can use any active presenter.'
			: 'Presenter must belong to your sub-team.';
	$: knowledgeScopeHint = $subTeamStore?.name ?? (currentUserRole === 'admin' ? 'All teams' : 'Your team');

	function buildKnowledgeGroups(sessions: KnowledgeSession[]) {
		const groups: { label: string; sessions: KnowledgeSession[] }[] = [];
		let currentLabel = '';
		for (const session of sessions) {
			const label = format(new Date(session.start_time), 'eeee, MMM d');
			if (!groups.length || label !== currentLabel) {
				currentLabel = label;
				groups.push({ label, sessions: [session] });
			} else {
				groups[groups.length - 1].sessions.push(session);
			}
		}
		return groups;
	}

	function setActiveTab(tab: TabKey) {
		if (activeTab === tab) return;
		activeTab = tab;
		showScheduleModal = false;
		editingSchedule = null;
		closeKnowledgeModal();
		if (tab === 'knowledge') {
			knowledgeViewMode = 'agenda';
			knowledgeSelectedDay = null;
		}
	}

	function openCreate(date?: Date) {
		editingSchedule = null;
		const base = date ? format(date, 'yyyy-MM-dd') : format(new Date(), 'yyyy-MM-dd');
		form = {
			title: '',
			description: '',
			start_time: `${base}T09:00`,
			end_time: `${base}T10:00`,
			all_day: false,
			color: '#6366f1',
			location: ''
		};
		formReminders = [];
		showScheduleModal = true;
	}

	async function openEdit(s: any) {
		editingSchedule = s;
		form = {
			title: s.title,
			description: s.description || '',
			start_time: s.start_time.slice(0, 16),
			end_time: s.end_time.slice(0, 16),
			all_day: s.all_day,
			color: s.color,
			location: s.location || ''
		};
		try {
			const existing: any[] = await notifApi.byEvent('schedule', s.id);
			formReminders = Array.from(
				new Set(existing.filter((n) => n.status !== 'dismissed').map((n) => n.offset_minutes))
			);
		} catch {
			formReminders = [];
		}
		showScheduleModal = true;
	}

	function toggleReminder(offset: number) {
		if (formReminders.includes(offset)) {
			formReminders = formReminders.filter((o) => o !== offset);
		} else {
			formReminders = [...formReminders, offset];
		}
	}

	async function handleSubmit() {
		const payload = {
			...form,
			start_time: new Date(form.start_time).toISOString(),
			end_time: new Date(form.end_time).toISOString()
		};
		try {
			let eventId: number;
			if (editingSchedule) {
				const updated: any = await schedulesApi.update(editingSchedule.id, payload);
				eventId = updated?.id ?? editingSchedule.id;
				toast.success('Event updated');
			} else {
				const created: any = await schedulesApi.create(payload);
				eventId = created.id;
				toast.success('Event created');
			}
			try {
				await notifApi.bulkSet({
					event_type: 'schedule',
					event_ref_id: eventId,
					offset_minutes_list: formReminders
				});
			} catch (err: any) {
				toast.error(`Reminders not saved: ${err.message}`);
			}
			showScheduleModal = false;
			await loadScheduleData();
		} catch (e: any) {
			toast.error(e.message);
		}
	}

	async function deleteSchedule(id: number) {
		if (!confirm('Delete this event?')) return;
		try {
			await schedulesApi.delete(id);
			toast.success('Event deleted');
			await loadScheduleData();
		} catch (e: any) {
			toast.error(e.message);
		}
	}

	function openKnowledgeCreate(date?: Date) {
		if (!canManageKnowledge) return;
		knowledgeModalSeedDate = date ?? knowledgeSelectedDay ?? new Date();
		editingKnowledgeSession = null;
		showKnowledgeModal = true;
	}

	function openKnowledgeEdit(session: KnowledgeSession) {
		knowledgeModalSeedDate = new Date(session.start_time);
		editingKnowledgeSession = session;
		showKnowledgeModal = true;
	}

	function closeKnowledgeModal() {
		showKnowledgeModal = false;
		editingKnowledgeSession = null;
		knowledgeModalSeedDate = null;
	}

	async function handleKnowledgeSaved() {
		closeKnowledgeModal();
		await loadKnowledgeData();
	}

	async function handleKnowledgeDeleted() {
		closeKnowledgeModal();
		await loadKnowledgeData();
	}

	function selectKnowledgeDay(day: Date) {
		knowledgeSelectedDay = day;
	}

	function knowledgeSessionsOnDay(day: Date): KnowledgeSession[] {
		return knowledgeSessionsSorted.filter((session) =>
			isSameDay(new Date(session.start_time), day)
		);
	}
</script>

<svelte:head><title>Schedule · TeamFlow</title></svelte:head>

<div class="mx-auto max-w-6xl p-4 md:p-6">
	<div class="mb-5 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-white">Scheduler</h1>
			<p class="mt-1 text-sm text-gray-400">Upcoming events, task deadlines, and knowledge sharing sessions</p>
		</div>
		<div class="flex items-center gap-3">
			{#if activeTab === 'schedule'}
				<button on:click={() => openCreate()} class="btn-primary">
					<Plus size={16} /> New Event
				</button>
			{/if}
		</div>
	</div>

	<div class="inline-flex rounded-lg border border-gray-800 bg-gray-900 p-1">
		<button
			type="button"
			class="inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors {activeTab === 'schedule'
				? 'bg-primary-600 text-white shadow-sm'
				: 'text-gray-400 hover:text-gray-200'}"
			on:click={() => setActiveTab('schedule')}
		>
			<Calendar size={14} />
			My Schedule
		</button>
		<button
			type="button"
			class="inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors {activeTab === 'knowledge'
				? 'bg-primary-600 text-white shadow-sm'
				: 'text-gray-400 hover:text-gray-200'}"
			on:click={() => setActiveTab('knowledge')}
		>
			<BookOpen size={14} />
			Knowledge Sessions
		</button>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="h-6 w-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent"></div>
		</div>
	{:else if activeTab === 'schedule'}
		<div class="mt-6 flex items-center gap-4 text-xs text-gray-500">
			<span class="flex items-center gap-1.5">
				<span class="h-2.5 w-2.5 rounded-sm bg-indigo-500"></span>Scheduled event
			</span>
			<span class="flex items-center gap-1.5">
				<span class="h-2.5 w-2.5 rounded-sm bg-amber-500"></span>Task due date
			</span>
		</div>

		<div class="mt-4 grid grid-cols-1 gap-6 lg:grid-cols-3">
			<div class="card lg:col-span-2">
				<div class="mb-4 flex items-center justify-between">
					<button
						on:click={() => (currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1))}
						class="rounded p-1.5 text-gray-400 transition-colors hover:bg-gray-800 hover:text-white"
					>
						‹
					</button>
					<h2 class="font-semibold text-white">{format(currentMonth, 'MMMM yyyy')}</h2>
					<button
						on:click={() => (currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1))}
						class="rounded p-1.5 text-gray-400 transition-colors hover:bg-gray-800 hover:text-white"
					>
						›
					</button>
				</div>

				<div class="mb-1 grid grid-cols-7 gap-1">
					{#each ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as dayLabel}
						<div class="py-1 text-center text-xs font-medium text-gray-500">{dayLabel}</div>
					{/each}
				</div>

				<div class="grid grid-cols-7 gap-1">
					{#each calDays as day}
						{@const events = allEvents.filter((event) => isSameDay(new Date(event.start_time), day))}
						{@const isToday = isSameDay(day, new Date())}
						{@const inMonth = isSameMonth(day, currentMonth)}
						<button
							on:click={() => openCreate(day)}
							class="min-h-[64px] rounded-lg p-1 text-left transition-colors hover:bg-gray-800 {inMonth
								? ''
								: 'opacity-30'} {isToday ? 'ring-1 ring-primary-500' : ''}"
						>
							<span
								class="mb-1 block px-0.5 text-xs {isToday
									? 'font-bold text-primary-400'
									: 'text-gray-400'}"
							>
								{format(day, 'd')}
							</span>
							{#each events.slice(0, 2) as event}
								<div
									class="mb-0.5 truncate rounded border-l-2 px-1 py-0.5 text-xs text-white"
									style="background-color: {event.color}20; border-left-color: {event.color};"
								>
									{event.title}
								</div>
							{/each}
							{#if events.length > 2}
								<span class="px-1 text-xs text-gray-500">+{events.length - 2} more</span>
							{/if}
						</button>
					{/each}
				</div>
			</div>

			<div class="card">
				<h2 class="mb-4 flex items-center gap-2 font-semibold text-white">
					<Calendar size={16} class="text-primary-400" /> Upcoming
				</h2>
				{#if allEventsSorted.length === 0}
					<p class="py-6 text-center text-sm text-gray-500">No upcoming events</p>
				{:else}
					<div class="max-h-[500px] space-y-2 overflow-y-auto">
						{#each allEventsSorted as ev}
							<div class="rounded-lg border-l-2 bg-gray-800 p-3" style="border-color: {ev.color}">
								<div class="flex items-start justify-between gap-2">
									<div class="min-w-0 flex-1">
										<div class="flex items-center gap-1.5">
											{#if ev.source === 'task'}
												<CheckSquare size={11} class="shrink-0 text-amber-400" />
											{/if}
											<p class="truncate text-sm font-medium text-gray-200">{ev.title}</p>
										</div>
										<p class="mt-0.5 flex items-center gap-1 text-xs text-gray-500">
											<Clock size={10} /> {formatDateTime(ev.start_time)}
										</p>
										{#if ev.location}
											<p class="mt-0.5 flex items-center gap-1 text-xs text-gray-500">
												<MapPin size={10} /> {ev.location}
											</p>
										{/if}
										{#if ev.source === 'task'}
											<p class="mt-0.5 text-[10px] uppercase tracking-wide text-amber-500/80">Task · read-only</p>
										{/if}
									</div>
									{#if ev.source === 'schedule'}
										<div class="flex shrink-0 gap-1">
											<button
												on:click={() => openEdit(ev.raw)}
												class="rounded p-1 text-gray-500 transition-colors hover:text-gray-300"
												title="Edit"
											>
												<Pencil size={12} />
											</button>
											<button
												on:click={() => deleteSchedule(ev.id)}
												class="rounded p-1 text-gray-500 transition-colors hover:text-red-400"
												title="Delete"
											>
												<Trash2 size={12} />
											</button>
										</div>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{:else}
		<div class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
			<div class="space-y-6 lg:col-span-2">
				<div class="card">
					<div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
						<div>
							<div class="flex flex-wrap items-center gap-3">
								<h2 class="text-base font-semibold text-white">Knowledge Sessions</h2>
								<span class="inline-flex items-center rounded-full border border-gray-700 bg-gray-800 px-2.5 py-1 text-xs font-medium text-gray-300">
									{knowledgeScopeHint}
								</span>
							</div>
							<p class="mt-1 text-sm text-gray-400">Org sessions and your team's scheduled knowledge sharing.</p>
						</div>
						<div class="flex items-center gap-3">
							<div class="inline-flex rounded-lg border border-gray-800 bg-gray-900 p-1">
								<button
									type="button"
									class="inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors {knowledgeViewMode === 'agenda'
										? 'bg-primary-600 text-white shadow-sm'
										: 'text-gray-400 hover:text-gray-200'}"
									on:click={() => (knowledgeViewMode = 'agenda')}
								>
									<List size={14} />
									Agenda
								</button>
								<button
									type="button"
									class="inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors {knowledgeViewMode === 'calendar'
										? 'bg-primary-600 text-white shadow-sm'
										: 'text-gray-400 hover:text-gray-200'}"
									on:click={() => (knowledgeViewMode = 'calendar')}
								>
									<Calendar size={14} />
									Calendar
								</button>
							</div>
							{#if canManageKnowledge}
								<button on:click={() => openKnowledgeCreate()} class="btn-primary">
									<Plus size={16} /> Create Session
								</button>
							{/if}
						</div>
					</div>
				</div>

				{#if knowledgeViewMode === 'agenda'}
					{#if knowledgeSessionsSorted.length === 0}
						<div class="card text-center py-12">
							<BookOpen class="mx-auto mb-3 text-gray-600" size={36} />
							<p class="text-gray-200 font-medium">No knowledge sessions yet</p>
							<p class="mt-2 text-sm text-gray-500">
								{#if canManageKnowledge}
									Schedule a session to share upcoming demos, workshops, or Q&A time.
								{:else}
									Sessions for your scope will appear here when they're scheduled.
								{/if}
							</p>
							{#if canManageKnowledge}
								<div class="mt-5">
									<button on:click={() => openKnowledgeCreate()} class="btn-primary">
										<Plus size={16} /> Create Session
									</button>
								</div>
							{/if}
						</div>
					{:else}
						<div class="space-y-5">
							{#each knowledgeAgendaGroups as group}
								<div class="space-y-3">
									<div class="flex items-center gap-3">
										<div class="h-px flex-1 bg-gray-800"></div>
										<h3 class="text-xs font-semibold uppercase tracking-wide text-gray-500">{group.label}</h3>
										<div class="h-px flex-1 bg-gray-800"></div>
									</div>
									<div class="space-y-3">
										{#each group.sessions as session}
											<SessionCard
												{session}
												compact={false}
												canManage={canManageKnowledge}
												on:select={() => openKnowledgeEdit(session)}
												on:edit={() => openKnowledgeEdit(session)}
												on:delete={() => openKnowledgeEdit(session)}
											/>
										{/each}
									</div>
								</div>
							{/each}
						</div>
					{/if}
				{:else}
					<div class="grid grid-cols-1 gap-6 xl:grid-cols-3">
						<div class="card xl:col-span-2">
							<div class="mb-4 flex items-center justify-between">
								<button
									on:click={() => (currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1))}
									class="rounded p-1.5 text-gray-400 transition-colors hover:bg-gray-800 hover:text-white"
								>
									‹
								</button>
								<h2 class="font-semibold text-white">{format(currentMonth, 'MMMM yyyy')}</h2>
								<button
									on:click={() => (currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1))}
									class="rounded p-1.5 text-gray-400 transition-colors hover:bg-gray-800 hover:text-white"
								>
									›
								</button>
							</div>

							<div class="mb-1 grid grid-cols-7 gap-1">
								{#each ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as dayLabel}
									<div class="py-1 text-center text-xs font-medium text-gray-500">{dayLabel}</div>
								{/each}
							</div>

							<div class="grid grid-cols-7 gap-1">
								{#each calDays as day}
									{@const daySessions = knowledgeSessionsOnDay(day)}
									{@const isToday = isSameDay(day, new Date())}
									{@const inMonth = isSameMonth(day, currentMonth)}
									{@const selected = knowledgeSelectedDay && isSameDay(day, knowledgeSelectedDay)}
									<button
										on:click={() => selectKnowledgeDay(day)}
										class="min-h-[72px] rounded-lg p-1 text-left transition-colors hover:bg-gray-800 {inMonth
											? ''
											: 'opacity-30'} {selected ? 'ring-1 ring-primary-500' : ''} {isToday && !selected
											? 'ring-1 ring-gray-600'
											: ''}"
									>
										<span
											class="mb-1 block px-0.5 text-xs {selected
												? 'font-bold text-primary-400'
												: isToday
													? 'font-bold text-gray-200'
													: 'text-gray-400'}"
										>
											{format(day, 'd')}
										</span>
										{#each daySessions.slice(0, 2) as session}
											<div
												class="mb-0.5 truncate rounded border-l-2 border-primary-500 bg-primary-600/15 px-1 py-0.5 text-xs text-primary-100"
											>
												{session.topic}
											</div>
										{/each}
										{#if daySessions.length > 2}
											<span class="px-1 text-xs text-gray-500">+{daySessions.length - 2} more</span>
										{/if}
									</button>
								{/each}
							</div>
						</div>

						<div class="card">
							<h2 class="mb-4 flex items-center gap-2 font-semibold text-white">
								<Calendar size={16} class="text-primary-400" />
								{knowledgeSelectedDay ? 'Selected Day' : 'Upcoming Sessions'}
							</h2>

							{#if knowledgeSelectedDay && knowledgeSelectedDaySessions.length === 0}
								<div class="rounded-lg border border-gray-800 bg-gray-800/70 p-4 text-center">
									<p class="text-sm font-medium text-gray-200">Nothing scheduled for this day</p>
									<p class="mt-1 text-sm text-gray-500">Choose another date or create a new session here.</p>
									{#if canManageKnowledge}
										<button on:click={() => openKnowledgeCreate(knowledgeSelectedDay ?? undefined)} class="btn-primary mt-4">
											<Plus size={16} /> Create Session
										</button>
									{/if}
								</div>
							{:else if knowledgeSelectedDay}
								<div class="space-y-2 max-h-[500px] overflow-y-auto">
									{#each knowledgeSelectedDaySessions as session}
										<SessionCard
											{session}
											compact={true}
											canManage={canManageKnowledge}
											selected={true}
											on:select={() => openKnowledgeEdit(session)}
											on:edit={() => openKnowledgeEdit(session)}
											on:delete={() => openKnowledgeEdit(session)}
										/>
									{/each}
								</div>
							{:else if knowledgeUpcomingSessions.length === 0}
								<div class="rounded-lg border border-gray-800 bg-gray-800/70 p-4 text-center">
									<p class="text-sm font-medium text-gray-200">No knowledge sessions yet</p>
									<p class="mt-1 text-sm text-gray-500">
										{#if canManageKnowledge}
											Schedule a session to share upcoming demos, workshops, or Q&A time.
										{:else}
											Sessions for your scope will appear here when they're scheduled.
										{/if}
									</p>
									{#if canManageKnowledge}
										<button on:click={() => openKnowledgeCreate()} class="btn-primary mt-4">
											<Plus size={16} /> Create Session
										</button>
									{/if}
								</div>
							{:else}
								<div class="space-y-2 max-h-[500px] overflow-y-auto">
									{#each knowledgeUpcomingSessions as session}
										<SessionCard
											{session}
											compact={true}
											canManage={canManageKnowledge}
											on:select={() => openKnowledgeEdit(session)}
											on:edit={() => openKnowledgeEdit(session)}
											on:delete={() => openKnowledgeEdit(session)}
										/>
									{/each}
								</div>
							{/if}
						</div>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

{#if showScheduleModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
		<div class="w-full max-w-md rounded-xl border border-gray-800 bg-gray-900">
			<div class="flex items-center justify-between border-b border-gray-800 p-5">
				<h2 class="font-semibold text-white">{editingSchedule ? 'Edit Event' : 'New Event'}</h2>
				<button on:click={() => (showScheduleModal = false)} class="text-gray-500 hover:text-gray-300">
					<X size={18} />
				</button>
			</div>
			<form on:submit|preventDefault={handleSubmit} class="space-y-4 p-5">
				<div>
					<label class="label" for="s-title">Title *</label>
					<input id="s-title" bind:value={form.title} class="input" required />
				</div>
				<div>
					<label class="label" for="s-desc">Description</label>
					<textarea id="s-desc" bind:value={form.description} class="input resize-none" rows="2"></textarea>
				</div>
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="label" for="s-start">Start *</label>
						<input id="s-start" bind:value={form.start_time} type="datetime-local" class="input" required />
					</div>
					<div>
						<label class="label" for="s-end">End *</label>
						<input id="s-end" bind:value={form.end_time} type="datetime-local" class="input" required />
					</div>
				</div>
				<div>
					<label class="label" for="s-location">Location</label>
					<input id="s-location" bind:value={form.location} class="input" placeholder="Conference room, URL..." />
					</div>
					<div>
						<div class="label">Color</div>
						<div class="flex flex-wrap gap-2">
						{#each [
							{ value: '#6366f1', label: 'Indigo' },
							{ value: '#10b981', label: 'Green' },
							{ value: '#f59e0b', label: 'Amber' },
							{ value: '#ef4444', label: 'Red' },
							{ value: '#8b5cf6', label: 'Purple' },
							{ value: '#3b82f6', label: 'Blue' }
						] as c}
							<button
								type="button"
								on:click={() => (form.color = c.value)}
								class="h-7 w-7 rounded-full transition-transform {form.color === c.value
									? 'scale-110 ring-2 ring-white ring-offset-2 ring-offset-gray-900'
									: 'hover:scale-105'}"
								style="background-color: {c.value}"
								title={c.label}
							></button>
						{/each}
					</div>
				</div>
				<div>
					<label class="label flex items-center gap-1.5">
						<Bell size={12} /> Reminders
					</label>
					<div class="flex flex-wrap gap-2">
						{#each REMINDER_OFFSETS as reminder}
							{@const selected = formReminders.includes(reminder.value)}
							<button
								type="button"
								on:click={() => toggleReminder(reminder.value)}
								class="rounded-full border px-2.5 py-1 text-xs transition-colors {selected
									? 'border-primary-500 bg-primary-600/20 text-primary-200'
									: 'border-gray-700 bg-gray-800 text-gray-400 hover:text-gray-200'}"
							>
								{reminder.label}
							</button>
						{/each}
					</div>
					<p class="mt-1.5 text-[11px] text-gray-500">You'll receive a toast and a bell notification at each selected time.</p>
				</div>
				<div class="flex justify-end gap-3 pt-2">
					<button type="button" on:click={() => (showScheduleModal = false)} class="btn-secondary">Cancel</button>
					<button type="submit" class="btn-primary">{editingSchedule ? 'Save Changes' : 'Create Event'}</button>
				</div>
			</form>
		</div>
	</div>
{/if}

{#if showKnowledgeModal}
	<SessionForm
		session={editingKnowledgeSession}
		users={knowledgeUsers}
		currentUserId={$currentUser?.id ?? null}
		selectedDate={knowledgeModalSeedDate}
		canManage={canManageKnowledge}
		helperText={knowledgePresenterHint}
		on:cancel={closeKnowledgeModal}
		on:saved={handleKnowledgeSaved}
		on:deleted={handleKnowledgeDeleted}
	/>
{/if}
