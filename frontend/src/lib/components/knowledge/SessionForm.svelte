<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Bell, Calendar, Tag, Trash2, Users, X } from 'lucide-svelte';
	import { format } from 'date-fns';
	import { toast } from 'svelte-sonner';
	import { knowledgeSessions as knowledgeSessionsApi, notifications as notifApi } from '$lib/apis';
	import type {
		KnowledgeSession,
		KnowledgeSessionPresenter,
		KnowledgeSessionType
	} from '$lib/apis/knowledge-sessions';

	export let session: KnowledgeSession | null = null;
	export let users: KnowledgeSessionPresenter[] = [];
	export let currentUserId: number | null = null;
	export let selectedDate: Date | null = null;
	export let canManage = false;
	export let helperText = '';

	const dispatch = createEventDispatcher<{
		cancel: void;
		saved: void;
		deleted: void;
	}>();

	const REMINDER_OFFSETS = [
		{ value: 15, label: '15 min before' },
		{ value: 30, label: '30 min before' },
		{ value: 60, label: '1 hour before' },
		{ value: 1440, label: '1 day before' }
	];

	let topic = '';
	let description = '';
	let references = '';
	let presenterId: number | null = null;
	let sessionType: KnowledgeSessionType = 'presentation';
	let durationMinutes = '60';
	let startTime = '';
	let tags: string[] = [];
	let tagDraft = '';
	let reminderOffsets: number[] = [];
	let loadingReminders = false;
	let deleteConfirm = false;
	let initializedKey = '';

	$: presenterOptions = users.length > 0 ? users : currentUserId ? [{ id: currentUserId, full_name: 'Current user', username: 'current-user', avatar_url: null, sub_team_id: null }] : [];
	$: modalTitle = session ? (canManage ? 'Edit Knowledge Session' : 'Knowledge Session') : 'New Knowledge Session';
	$: primaryAction = session ? 'Save Changes' : 'Create Session';
	$: formKey = `${session?.id ?? 'new'}:${selectedDate ? selectedDate.toISOString().slice(0, 10) : 'today'}`;
	$: if (formKey !== initializedKey) {
		initializedKey = formKey;
		resetForm();
	}

	function resetForm() {
		const baseDate = selectedDate ? new Date(selectedDate) : new Date();
		if (session) {
			topic = session.topic;
			description = session.description ?? '';
			references = session.references ?? '';
			presenterId = session.presenter_id;
			sessionType = session.session_type;
			durationMinutes = String(session.duration_minutes);
			startTime = formatLocalInput(session.start_time);
			tags = [...(session.tags ?? [])];
			tagDraft = '';
			deleteConfirm = false;
			loadReminders(session.id);
		} else {
			topic = '';
			description = '';
			references = '';
			presenterId = currentUserId ?? presenterOptions[0]?.id ?? null;
			sessionType = 'presentation';
			durationMinutes = '60';
			startTime = formatLocalInput(
				new Date(
					baseDate.getFullYear(),
					baseDate.getMonth(),
					baseDate.getDate(),
					9,
					0,
					0,
					0
				)
			);
			tags = [];
			tagDraft = '';
			reminderOffsets = [];
			deleteConfirm = false;
			loadingReminders = false;
		}
	}

	function formatLocalInput(value: string | Date) {
		const date = value instanceof Date ? value : new Date(value);
		const pad = (n: number) => String(n).padStart(2, '0');
		return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(
			date.getHours()
		)}:${pad(date.getMinutes())}`;
	}

	async function loadReminders(id: number) {
		loadingReminders = true;
		try {
			const reminders: any[] = await notifApi.byEvent('knowledge_session', id);
			reminderOffsets = Array.from(
				new Set(reminders.filter((n) => n.status !== 'dismissed').map((n) => n.offset_minutes))
			);
		} catch {
			reminderOffsets = [];
			toast.error('Reminders were not updated.');
		} finally {
			loadingReminders = false;
		}
	}

	function normalizeTag(value: string) {
		return value.trim();
	}

	function addTagFromDraft() {
		const tag = normalizeTag(tagDraft);
		if (!tag) return;
		if (tags.some((existing) => existing.toLowerCase() === tag.toLowerCase())) {
			tagDraft = '';
			return;
		}
		tags = [...tags, tag];
		tagDraft = '';
	}

	function removeTag(tag: string) {
		tags = tags.filter((existing) => existing !== tag);
	}

	function toggleReminder(offset: number) {
		reminderOffsets = reminderOffsets.includes(offset)
			? reminderOffsets.filter((value) => value !== offset)
			: [...reminderOffsets, offset];
	}

	function tagKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' || event.key === ',') {
			event.preventDefault();
			addTagFromDraft();
		}
	}

	async function handleSubmit() {
		if (!topic.trim()) return;
		const payload = {
			topic: topic.trim(),
			description: description.trim() || null,
			references: references.trim() || null,
			presenter_id: presenterId,
			session_type: sessionType,
			duration_minutes: Number(durationMinutes),
			start_time: new Date(startTime).toISOString(),
			tags,
			offset_minutes_list: reminderOffsets
		};
		try {
			if (session) {
				await knowledgeSessionsApi.update(session.id, payload);
				toast.success('Session updated');
			} else {
				await knowledgeSessionsApi.create(payload);
				toast.success('Session created');
			}
			dispatch('saved');
		} catch {
			toast.error('Failed to save session. Try again.');
		}
	}

	async function handleDelete() {
		if (!session) return;
		try {
			await knowledgeSessionsApi.delete(session.id);
			toast.success('Session deleted');
			dispatch('deleted');
		} catch {
			toast.error('Failed to delete session. Try again.');
		}
	}
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
	<div class="flex max-h-[90vh] w-full max-w-xl flex-col overflow-hidden rounded-xl border border-gray-800 bg-gray-900">
		<div class="flex items-start justify-between gap-4 border-b border-gray-800 p-5">
			<div>
				<h2 class="text-base font-semibold text-white">{modalTitle}</h2>
				<p class="mt-1 text-sm text-gray-400">
					{helperText || 'Everyone in scope receives the selected reminders.'}
				</p>
			</div>
			<button type="button" class="rounded p-1.5 text-gray-500 transition-colors hover:text-gray-200" on:click={() => dispatch('cancel')}>
				<X size={18} />
			</button>
		</div>

		<div class="max-h-[calc(90vh-4rem)] overflow-y-auto p-5">
			{#if session && !canManage}
				<div class="space-y-4">
					<div>
						<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Topic</p>
						<p class="mt-1 text-sm text-gray-100">{session.topic}</p>
					</div>
					<div>
						<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Start</p>
						<p class="mt-1 text-sm text-gray-100">{format(new Date(session.start_time), 'PPP p')}</p>
					</div>
					<div>
						<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Duration</p>
						<p class="mt-1 text-sm text-gray-100">{session.duration_minutes} minutes</p>
					</div>
					<div>
						<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Presenter</p>
						<p class="mt-1 text-sm text-gray-100">{session.presenter?.full_name ?? 'Unassigned'}</p>
					</div>
					<div>
						<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Scope</p>
						<p class="mt-1 text-sm text-gray-100">{session.sub_team_id ? 'Team Session' : 'Org-wide'}</p>
					</div>
					<div>
						<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Session Type</p>
						<p class="mt-1 text-sm text-gray-100">
							{session.session_type === 'qa'
								? 'Q&A'
								: session.session_type.charAt(0).toUpperCase() + session.session_type.slice(1)}
						</p>
					</div>
					{#if session.description}
						<div>
							<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Description</p>
							<p class="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-gray-100">{session.description}</p>
						</div>
					{/if}
					{#if session.references}
						<div>
							<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">References</p>
							<p class="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-gray-100">{session.references}</p>
						</div>
					{/if}
					{#if session.tags?.length > 0}
						<div>
							<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Tags</p>
							<div class="mt-2 flex flex-wrap gap-2">
								{#each session.tags as tag}
									<span class="inline-flex items-center rounded-full border border-primary-500/25 bg-primary-600/15 px-2.5 py-1 text-xs text-primary-200">
										{tag}
									</span>
								{/each}
							</div>
						</div>
					{/if}
					{#if loadingReminders}
						<p class="text-sm text-gray-500">Loading reminders...</p>
					{:else if reminderOffsets.length > 0}
						<div>
							<p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Reminders</p>
							<div class="mt-2 flex flex-wrap gap-2">
								{#each REMINDER_OFFSETS as reminder}
									{#if reminderOffsets.includes(reminder.value)}
										<span class="inline-flex rounded-full border border-primary-500 bg-primary-600/20 px-2.5 py-1 text-xs text-primary-200">
											{reminder.label}
										</span>
									{/if}
								{/each}
							</div>
						</div>
					{/if}
					<div class="flex justify-end pt-2">
						<button type="button" class="btn-secondary" on:click={() => dispatch('cancel')}>Close</button>
					</div>
				</div>
			{:else if deleteConfirm}
				<div class="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
					<h3 class="text-sm font-semibold text-red-200">Delete session</h3>
					<p class="mt-1 text-sm text-red-100/80">
						This removes the session and its pending reminders for people in scope.
					</p>
					<div class="mt-4 flex items-center justify-end gap-3">
						<button type="button" class="btn-secondary" on:click={() => (deleteConfirm = false)}>Cancel</button>
						<button type="button" class="btn-danger" on:click={handleDelete}>Delete Session</button>
					</div>
				</div>
			{:else}
				<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
					<div>
						<label class="label" for="ks-topic">Topic *</label>
						<input id="ks-topic" bind:value={topic} class="input" required />
					</div>

					<div>
						<label class="label" for="ks-description">Description</label>
						<textarea id="ks-description" bind:value={description} class="input resize-none" rows="3"></textarea>
					</div>

					<div>
						<label class="label" for="ks-references">References</label>
						<textarea
							id="ks-references"
							bind:value={references}
							class="input resize-none"
							rows="3"
							placeholder="Paste links, docs, or prep notes for attendees"
						></textarea>
					</div>

					<div>
						<label class="label flex items-center gap-1.5" for="ks-presenter">
							<Users size={12} />
							Presenter
						</label>
						<select id="ks-presenter" bind:value={presenterId} class="input" required>
							{#each presenterOptions as user}
								<option value={user.id}>{user.full_name}</option>
							{/each}
						</select>
						<p class="mt-1 text-xs text-gray-500">
							{#if helperText}{helperText}{:else}Presenter must belong to your sub-team.{/if}
						</p>
					</div>

					<div>
						<label class="label" for="ks-type">Session Type</label>
						<select id="ks-type" bind:value={sessionType} class="input">
							<option value="presentation">Presentation</option>
							<option value="demo">Demo</option>
							<option value="workshop">Workshop</option>
							<option value="qa">Q&A</option>
						</select>
					</div>

					<div>
						<label class="label" for="ks-duration">Duration</label>
						<input id="ks-duration" bind:value={durationMinutes} type="number" min="15" step="15" class="input" />
					</div>

					<div>
						<label class="label flex items-center gap-1.5" for="ks-start">
							<Calendar size={12} />
							Start
						</label>
						<input id="ks-start" bind:value={startTime} type="datetime-local" class="input" required />
					</div>

					<div>
						<label class="label flex items-center gap-1.5" for="ks-tags">
							<Tag size={12} />
							Tags
						</label>
						<div class="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2">
							<div class="flex flex-wrap gap-2">
								{#each tags as tag}
									<span class="inline-flex items-center gap-1.5 rounded-full border border-primary-500/25 bg-primary-600/15 px-2.5 py-1 text-xs text-primary-200">
										{tag}
										<button
											type="button"
											class="rounded-full text-primary-200/80 transition-colors hover:text-white"
											aria-label={`Remove ${tag}`}
											on:click={() => removeTag(tag)}
										>
											<X size={11} />
										</button>
									</span>
								{/each}
								<input
									id="ks-tags"
									class="min-w-[8rem] flex-1 bg-transparent text-sm text-gray-100 placeholder-gray-500 focus:outline-none"
									placeholder="Add tags"
									bind:value={tagDraft}
									on:keydown={tagKeydown}
									on:blur={addTagFromDraft}
								/>
							</div>
						</div>
					</div>

					<div>
						<label class="label flex items-center gap-1.5">
							<Bell size={12} />
							Reminders
						</label>
						<div class="flex flex-wrap gap-2">
							{#each REMINDER_OFFSETS as reminder}
								{@const selected = reminderOffsets.includes(reminder.value)}
								<button
									type="button"
									class="rounded-full border px-2.5 py-1 text-xs transition-colors {selected
										? 'border-primary-500 bg-primary-600/20 text-primary-200'
										: 'border-gray-700 bg-gray-800 text-gray-400 hover:text-gray-200'}"
									on:click={() => toggleReminder(reminder.value)}
								>
									{reminder.label}
								</button>
							{/each}
						</div>
						<p class="mt-1.5 text-xs text-gray-500">
							Everyone in scope receives the selected reminders.
						</p>
					</div>

					<div class="flex items-center justify-between gap-3 pt-2">
						{#if session && canManage}
							<button type="button" class="btn-secondary" on:click={() => (deleteConfirm = true)}>
								<Trash2 size={14} />
								Delete Session
							</button>
						{:else}
							<span></span>
						{/if}
						<div class="flex items-center gap-3">
							<button type="button" class="btn-secondary" on:click={() => dispatch('cancel')}>Cancel</button>
							<button type="submit" class="btn-primary" disabled={!topic.trim()}>
								{primaryAction}
							</button>
						</div>
					</div>
				</form>
			{/if}
		</div>
	</div>
</div>
