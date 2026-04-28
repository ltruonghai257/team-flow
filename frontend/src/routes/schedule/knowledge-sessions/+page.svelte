<script lang="ts">
	import { onMount } from 'svelte';
	import { currentUser } from '$lib/stores/auth';
	import { subTeamStore } from '$lib/stores/subTeam';
	import {
		knowledgeSessions as knowledgeSessionsApi,
		users as usersApi
	} from '$lib/apis';
	import { toast } from 'svelte-sonner';
	import {
		BookOpen,
		Calendar,
		List,
		Plus
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

	type KnowledgeView = 'agenda' | 'calendar';

	let knowledgeSessions: KnowledgeSession[] = [];
	let knowledgeUsers: any[] = [];
	let loading = true;
	let knowledgeViewMode: KnowledgeView = 'agenda';
	let knowledgeSelectedDay: Date | null = null;
	let currentMonth = new Date();
	let showKnowledgeModal = false;
	let editingKnowledgeSession: KnowledgeSession | null = null;
	let knowledgeModalSeedDate: Date | null = null;

	onMount(loadKnowledgeData);

	async function loadKnowledgeData() {
		loading = true;
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
		} finally {
			loading = false;
		}
	}

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

<svelte:head><title>Knowledge Sessions · TeamFlow</title></svelte:head>

<div class="mx-auto max-w-7xl p-4 md:p-6">
	<div class="mb-5 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-white">Knowledge Sessions</h1>
			<p class="mt-1 text-sm text-gray-400">Org sessions and your team's scheduled knowledge sharing.</p>
		</div>
		<div class="flex items-center gap-3">
			{#if canManageKnowledge}
				<button on:click={() => openKnowledgeCreate()} class="btn-primary">
					<Plus size={16} /> Create Session
				</button>
			{/if}
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="h-6 w-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent"></div>
		</div>
	{:else}
		<div class="space-y-6">
			<div class="card">
				<div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
					<div>
						<div class="flex flex-wrap items-center gap-3">
							<h2 class="text-base font-semibold text-white">All Sessions</h2>
							<span class="inline-flex items-center rounded-full border border-gray-700 bg-gray-800 px-2.5 py-1 text-xs font-medium text-gray-300">
								{knowledgeScopeHint}
							</span>
						</div>
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
	{/if}
</div>

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
