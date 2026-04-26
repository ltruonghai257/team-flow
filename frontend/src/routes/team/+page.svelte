<script lang="ts">
	import { onMount } from 'svelte';
	import {
		users as usersApi,
		tasks as tasksApi,
		invites as invitesApi,
		sub_teams as subTeamsApi,
		reminderSettings as reminderSettingsApi,
		type ReminderSettings,
		type ReminderSettingsProposal
	} from '$lib/api';
	import { initials, statusColors, statusLabels, priorityColors, formatDate } from '$lib/utils';
	import { authStore, isSupervisor } from '$lib/stores/auth';
	import { toast } from 'svelte-sonner';
	import { Mail, Users, UserPlus, UserCheck, X, Loader2, Layers, Plus, Edit, Trash2 } from 'lucide-svelte';

	let userList: any[] = [];
	let taskMap: Record<number, any[]> = {};
	let loading = true;
	let selectedUser: any = null;

	// Invite modal state
	let showInviteModal = false;
	let inviteEmail = '';
	let inviteRole = 'member';
	let inviting = false;

	// Direct-add modal state
	let showAddModal = false;
	let addSearchQuery = '';
	let addUserId: number | null = null;
	let addRole = 'member';
	let adding = false;

	// Pending invites
	let pendingInvites: any[] = [];
	let loadingInvites = false;

	// Reminder settings
	let reminderSettings: ReminderSettings | null = null;
	let reminderLeadTimeDays = 2;
	let reminderSprintEnabled = true;
	let reminderMilestoneEnabled = true;
	let reminderLoading = false;
	let reminderSaving = false;
	let reminderError: string | null = null;
	let pendingProposals: ReminderSettingsProposal[] = [];
	let reviewingProposalId: number | null = null;

	// Sub-Teams
	let subTeams: any[] = [];
	let activeTab = 'members';
	let editingSubTeam: any = null;
	let showSubTeamModal = false;
	let subTeamName = '';
	let subTeamSupervisorId: number | null = null;

	onMount(async () => {
		loading = true;
		try {
			userList = await usersApi.list();
			const allTasks = await tasksApi.list();
			for (const u of userList) {
				taskMap[u.id] = allTasks.filter((t: any) => t.assignee_id === u.id);
			}
			if ($isSupervisor) {
				await loadPendingInvites();
				await loadSubTeams();
			}
			await loadReminderSettings();
		} finally {
			loading = false;
		}
	});

	async function loadPendingInvites() {
		loadingInvites = true;
		try {
			pendingInvites = await invitesApi.pending();
		} catch {
			pendingInvites = [];
		} finally {
			loadingInvites = false;
		}
	}

	async function loadSubTeams() {
		try {
			subTeams = await subTeamsApi.list();
		} catch {
			subTeams = [];
		}
	}

	async function loadReminderSettings() {
		reminderLoading = true;
		reminderError = null;
		try {
			const currentSettings = await reminderSettingsApi.current();
			reminderSettings = currentSettings;
			reminderLeadTimeDays = currentSettings.lead_time_days;
			reminderSprintEnabled = currentSettings.sprint_reminders_enabled;
			reminderMilestoneEnabled = currentSettings.milestone_reminders_enabled;
			if ($authStore.user?.role === 'admin') {
				pendingProposals = await reminderSettingsApi.listProposals();
			} else {
				pendingProposals = [];
			}
		} catch (e: any) {
			reminderError = e?.message || 'Failed to load reminder settings';
			reminderSettings = null;
			pendingProposals = [];
		} finally {
			reminderLoading = false;
		}
	}

	async function saveReminderSettings() {
		if (!$authStore.user || $authStore.user.role === 'member') return;
		reminderSaving = true;
		try {
			const payload = {
				lead_time_days: reminderLeadTimeDays,
				sprint_reminders_enabled: reminderSprintEnabled,
				milestone_reminders_enabled: reminderMilestoneEnabled
			};
			if ($authStore.user.role === 'admin') {
				await reminderSettingsApi.updateCurrent(payload);
				toast.success('Reminder settings updated');
			} else {
				await reminderSettingsApi.createProposal(payload);
				toast.success('Reminder settings proposal submitted');
			}
			await loadReminderSettings();
		} catch (e: any) {
			toast.error(e.message || 'Failed to save reminder settings');
		} finally {
			reminderSaving = false;
		}
	}

	async function reviewProposal(id: number, decision: 'approve' | 'reject') {
		reviewingProposalId = id;
		try {
			await reminderSettingsApi.reviewProposal(id, { decision });
			toast.success(decision === 'approve' ? 'Proposal approved' : 'Proposal rejected');
			await loadReminderSettings();
		} catch (e: any) {
			toast.error(e.message || 'Failed to review proposal');
		} finally {
			reviewingProposalId = null;
		}
	}

	async function saveSubTeam() {
		if (!subTeamName) return;
		try {
			const data: any = { name: subTeamName };
			if (subTeamSupervisorId !== null) data.supervisor_id = subTeamSupervisorId;

			if (editingSubTeam) {
				await subTeamsApi.update(editingSubTeam.id, data);
				toast.success('Sub-team updated');
			} else {
				await subTeamsApi.create(data);
				toast.success('Sub-team created');
			}
			showSubTeamModal = false;
			subTeamName = '';
			subTeamSupervisorId = null;
			editingSubTeam = null;
			await loadSubTeams();
		} catch (e: any) {
			toast.error(e.message || 'Failed to save sub-team');
		}
	}

	async function deleteSubTeam(id: number) {
		if (!confirm('Are you sure you want to delete this sub-team?')) return;
		try {
			await subTeamsApi.delete(id);
			toast.success('Sub-team deleted');
			await loadSubTeams();
		} catch (e: any) {
			toast.error(e.message || 'Failed to delete sub-team');
		}
	}

	function proposalLabel(proposal: ReminderSettingsProposal) {
		const changes: string[] = [];
		if (proposal.lead_time_days !== null) changes.push(`${proposal.lead_time_days} days`);
		if (proposal.sprint_reminders_enabled !== null) {
			changes.push(`sprint ${proposal.sprint_reminders_enabled ? 'on' : 'off'}`);
		}
		if (proposal.milestone_reminders_enabled !== null) {
			changes.push(`milestone ${proposal.milestone_reminders_enabled ? 'on' : 'off'}`);
		}
		return changes.join(' · ');
	}

	function editSubTeam(subTeam: any) {
		editingSubTeam = subTeam;
		subTeamName = subTeam.name;
		subTeamSupervisorId = subTeam.supervisor_id;
		showSubTeamModal = true;
	}

	function createSubTeam() {
		editingSubTeam = null;
		subTeamName = '';
		subTeamSupervisorId = null;
		showSubTeamModal = true;
	}

	async function sendInvite() {
		if (!inviteEmail) return;
		inviting = true;
		try {
			await invitesApi.sendInvite(inviteEmail, inviteRole);
			toast.success(`Invite sent to ${inviteEmail}`);
			showInviteModal = false;
			inviteEmail = '';
			inviteRole = 'member';
			await loadPendingInvites();
		} catch (e: any) {
			toast.error(e.message || 'Failed to send invite');
		} finally {
			inviting = false;
		}
	}

	async function directAdd() {
		if (!addUserId) return;
		adding = true;
		try {
			await invitesApi.directAdd(addUserId, addRole);
			toast.success('Member added successfully');
			showAddModal = false;
			addUserId = null;
			addRole = 'member';
			userList = await usersApi.list();
		} catch (e: any) {
			toast.error(e.message || 'Failed to add member');
		} finally {
			adding = false;
		}
	}

	async function cancelInvite(id: number) {
		try {
			await invitesApi.cancel(id);
			toast.success('Invite cancelled');
			pendingInvites = pendingInvites.filter((inv) => inv.id !== id);
		} catch (e: any) {
			toast.error(e.message || 'Failed to cancel invite');
		}
	}

	$: filteredUsers = addSearchQuery
		? userList.filter(
				(u) =>
					u.username.toLowerCase().includes(addSearchQuery.toLowerCase()) ||
					u.email.toLowerCase().includes(addSearchQuery.toLowerCase()) ||
					u.full_name.toLowerCase().includes(addSearchQuery.toLowerCase())
			)
		: userList;

	function roleColor(role: string) {
		const map: Record<string, string> = {
			admin: 'bg-blue-100 text-blue-800',
			supervisor: 'bg-purple-100 text-purple-800',
			member: 'bg-gray-700 text-gray-300'
		};
		return map[role] || 'bg-gray-700 text-gray-300';
	}

	function taskStats(uid: number) {
		const t = taskMap[uid] || [];
		return {
			total: t.length,
			done: t.filter((x) => x.status === 'done').length,
			inProgress: t.filter((x) => x.status === 'in_progress').length
		};
	}

	function formatExpiry(dt: string) {
		return new Date(dt).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
	}
</script>

<svelte:head><title>Team · TeamFlow</title></svelte:head>

<div class="p-4 md:p-6 max-w-6xl mx-auto">
	<div class="mb-6 flex items-start justify-between gap-4">
		<div>
			<h1 class="text-2xl font-bold text-white">Team</h1>
			<p class="text-gray-400 text-sm mt-1">Manage your team members and their workload</p>
		</div>
	</div>

	<!-- Tabs -->
	{#if $isSupervisor}
	<div class="mb-6 flex gap-2 border-b border-gray-800">
		<button
			on:click={() => (activeTab = 'members')}
			class="px-4 py-2 text-sm font-medium transition-colors {activeTab === 'members'
				? 'text-white border-b-2 border-primary-600'
				: 'text-gray-500 hover:text-gray-300'}"
		>
			Members
		</button>
		<button
			on:click={() => (activeTab = 'sub-teams')}
			class="px-4 py-2 text-sm font-medium transition-colors {activeTab === 'sub-teams'
				? 'text-white border-b-2 border-primary-600'
				: 'text-gray-500 hover:text-gray-300'}"
		>
			Sub-Teams
		</button>
	</div>
	{/if}

	<div class="mb-6 rounded-xl border border-gray-800 bg-gray-900/70 p-4">
		<div class="flex items-start justify-between gap-4">
			<div>
				<h2 class="text-sm font-semibold text-white">Reminder settings</h2>
				<p class="text-xs text-gray-500 mt-1">
					Shared lead time for sprint-end and milestone due-date reminders.
				</p>
			</div>
			{#if reminderSettings && $authStore.user?.role !== 'member'}
				<button
					on:click={saveReminderSettings}
					disabled={reminderSaving}
					class="btn-primary flex items-center gap-2 text-sm"
				>
					{#if reminderSaving}
						<Loader2 class="animate-spin" size={14} />
					{/if}
					{$authStore.user?.role === 'admin' ? 'Save settings' : 'Submit proposal'}
				</button>
			{/if}
		</div>

		{#if reminderLoading}
			<div class="flex items-center justify-center py-6">
				<Loader2 class="animate-spin text-gray-500" size={18} />
			</div>
		{:else if reminderSettings}
			<div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
				<div>
					<label class="label" for="reminderLeadTime">Lead time (days)</label>
					<input
						id="reminderLeadTime"
						type="number"
						min="0"
						max="30"
						bind:value={reminderLeadTimeDays}
						disabled={$authStore.user?.role === 'member'}
						class="input"
					/>
				</div>
				<label class="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-950/60 px-3 py-2.5 text-sm text-gray-300">
					<input
						type="checkbox"
						bind:checked={reminderSprintEnabled}
						disabled={$authStore.user?.role === 'member'}
						class="rounded border-gray-700 bg-gray-800 text-primary-600 focus:ring-primary-500"
					/>
					Sprint reminders
				</label>
				<label class="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-950/60 px-3 py-2.5 text-sm text-gray-300">
					<input
						type="checkbox"
						bind:checked={reminderMilestoneEnabled}
						disabled={$authStore.user?.role === 'member'}
						class="rounded border-gray-700 bg-gray-800 text-primary-600 focus:ring-primary-500"
					/>
					Milestone reminders
				</label>
			</div>
			<p class="mt-3 text-xs text-gray-500">
				{#if $authStore.user?.role === 'member'}
					Read-only view for your team.
				{:else if $authStore.user?.role === 'admin'}
					Edits apply immediately to the active sub-team.
				{:else}
					Submissions become proposals until an admin approves them.
				{/if}
			</p>
		{:else}
			<p class="mt-4 text-sm text-red-400">
				{reminderError || 'Reminder settings are unavailable for the current sub-team.'}
			</p>
		{/if}
	</div>

	{#if $authStore.user?.role === 'admin' && pendingProposals.length > 0}
		<div class="mb-6 rounded-xl border border-gray-800 bg-gray-900/70 p-4">
			<div class="flex items-center justify-between gap-4 mb-4">
				<div>
					<h2 class="text-sm font-semibold text-white">Pending reminder proposals</h2>
					<p class="text-xs text-gray-500 mt-1">Review supervisor-submitted changes for the active sub-team.</p>
				</div>
				<span class="text-xs text-gray-500">{pendingProposals.length} pending</span>
			</div>
			<div class="space-y-2">
				{#each pendingProposals as proposal}
					<div class="flex items-start justify-between gap-4 rounded-lg border border-gray-800 bg-gray-950/60 p-3">
						<div class="min-w-0">
							<p class="text-sm font-medium text-gray-200">Proposal #{proposal.id}</p>
							<p class="text-xs text-gray-500 mt-0.5 truncate">{proposalLabel(proposal)}</p>
						</div>
						<div class="flex items-center gap-2 flex-shrink-0">
							<button
								on:click={() => reviewProposal(proposal.id, 'reject')}
								disabled={reviewingProposalId === proposal.id}
								class="btn-secondary text-xs"
							>
								Reject
							</button>
							<button
								on:click={() => reviewProposal(proposal.id, 'approve')}
								disabled={reviewingProposalId === proposal.id}
								class="btn-primary text-xs"
							>
								{#if reviewingProposalId === proposal.id}
									<Loader2 class="animate-spin" size={14} />
								{/if}
								Approve
							</button>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}

	{#if activeTab === 'members'}
	<div class="mb-6 flex items-start justify-between gap-4">
		{#if $isSupervisor}
			<div class="flex gap-2 flex-shrink-0">
				<button
					on:click={() => (showAddModal = true)}
					class="btn-secondary flex items-center gap-1.5 text-sm"
				>
					<UserCheck size={15} />
					Add Member
				</button>
				<button
					on:click={() => (showInviteModal = true)}
					class="btn-primary flex items-center gap-1.5 text-sm"
				>
					<UserPlus size={15} />
					Invite Member
				</button>
			</div>
		{/if}
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
		</div>
	{:else if userList.length === 0}
		<div class="card text-center py-12">
			<Users class="mx-auto text-gray-600 mb-3" size={36} />
			<p class="text-gray-500">No team members yet.</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
			{#each userList as u}
				{@const stats = taskStats(u.id)}
				<button
					on:click={() => (selectedUser = selectedUser?.id === u.id ? null : u)}
					class="card text-left hover:border-gray-700 transition-all {selectedUser?.id === u.id ? 'border-primary-600/50 ring-1 ring-primary-600/30' : ''}"
				>
					<div class="flex items-center gap-3 mb-4">
						<div class="w-10 h-10 rounded-full bg-primary-700 flex items-center justify-center text-sm font-bold text-white flex-shrink-0">
							{initials(u.full_name)}
						</div>
						<div class="flex-1 min-w-0">
							<p class="font-semibold text-white truncate">{u.full_name}</p>
							<p class="text-xs text-gray-500 truncate">@{u.username}</p>
						</div>
						{#if u.role === 'admin'}
						<span class="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">Admin</span>
					{:else if u.role === 'supervisor'}
						<span class="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-800">Supervisor</span>
					{:else}
						<span class="badge {roleColor(u.role)}">{u.role}</span>
					{/if}
					</div>
					<div class="flex items-center gap-1 text-xs text-gray-500 mb-4">
						<Mail size={12} />
						<span class="truncate">{u.email}</span>
					</div>
					<div class="grid grid-cols-3 gap-2 text-center">
						<div class="bg-gray-800 rounded-lg py-2">
							<p class="text-lg font-bold text-white">{stats.total}</p>
							<p class="text-xs text-gray-500">Tasks</p>
						</div>
						<div class="bg-gray-800 rounded-lg py-2">
							<p class="text-lg font-bold text-blue-400">{stats.inProgress}</p>
							<p class="text-xs text-gray-500">Active</p>
						</div>
						<div class="bg-gray-800 rounded-lg py-2">
							<p class="text-lg font-bold text-green-400">{stats.done}</p>
							<p class="text-xs text-gray-500">Done</p>
						</div>
					</div>
				</button>
			{/each}
		</div>

		<!-- Task detail panel -->
		{#if selectedUser}
			{@const userTasks = taskMap[selectedUser.id] || []}
			<div class="mt-6 card">
				<div class="flex items-center gap-3 mb-4">
					<div class="w-8 h-8 rounded-full bg-primary-700 flex items-center justify-center text-xs font-bold text-white">
						{initials(selectedUser.full_name)}
					</div>
					<h2 class="font-semibold text-white">{selectedUser.full_name}'s Tasks</h2>
					<span class="text-xs text-gray-500 ml-auto">{userTasks.length} total</span>
				</div>

				{#if userTasks.length === 0}
					<p class="text-gray-500 text-sm text-center py-6">No tasks assigned</p>
				{:else}
					<div class="space-y-2">
						{#each userTasks as t}
							<div class="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
								<div class="flex-1 min-w-0">
									<p class="text-sm text-gray-200 truncate {t.status === 'done' ? 'line-through text-gray-500' : ''}">{t.title}</p>
									{#if t.due_date}
										<p class="text-xs text-gray-500 mt-0.5">Due {formatDate(t.due_date)}</p>
									{/if}
								</div>
								<div class="flex items-center gap-2 ml-3 flex-shrink-0">
									<span class="badge {priorityColors[t.priority]}">{t.priority}</span>
									<span class="badge {statusColors[t.status]}">{statusLabels[t.status]}</span>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}

		<!-- Pending Invites (supervisor/admin only) -->
		{#if $isSupervisor && (pendingInvites.length > 0 || loadingInvites)}
			<div class="mt-6 card">
				<h2 class="font-semibold text-white mb-4 flex items-center gap-2">
					<Mail size={16} class="text-primary-400" />
					Pending Invites
					<span class="text-xs text-gray-500 font-normal">({pendingInvites.length})</span>
				</h2>
				{#if loadingInvites}
					<div class="flex items-center justify-center py-6">
						<Loader2 class="animate-spin text-gray-500" size={20} />
					</div>
				{:else}
					<div class="space-y-2">
						{#each pendingInvites as inv}
							<div class="flex items-center justify-between p-3 bg-gray-800 rounded-lg gap-3">
								<div class="flex-1 min-w-0">
									<p class="text-sm text-gray-200 truncate">{inv.email}</p>
									<p class="text-xs text-gray-500 mt-0.5">
										Role: <span class="capitalize">{inv.role}</span> · Expires {formatExpiry(inv.expires_at)}
									</p>
								</div>
								<button
									on:click={() => cancelInvite(inv.id)}
									class="text-gray-500 hover:text-red-400 transition-colors flex-shrink-0"
									title="Cancel invite"
								>
									<X size={16} />
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	{/if}
	{/if}

	<!-- Sub-Teams Tab -->
	{#if activeTab === 'sub-teams'}
	<div class="mb-6 flex items-start justify-between gap-4">
		<button
			on:click={createSubTeam}
			class="btn-primary flex items-center gap-1.5 text-sm"
		>
			<Plus size={15} />
			Create Sub-Team
		</button>
	</div>

	{#if subTeams.length === 0}
		<div class="card text-center py-12">
			<Layers class="mx-auto text-gray-600 mb-3" size={36} />
			<p class="text-gray-500">No sub-teams yet.</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			{#each subTeams as subTeam}
			<div class="card">
				<div class="flex items-start justify-between mb-4">
					<div class="flex-1">
						<h3 class="font-semibold text-white">{subTeam.name}</h3>
						{#if subTeam.supervisor_id}
							{@const supervisor = userList.find((u) => u.id === subTeam.supervisor_id)}
							{#if supervisor}
								<p class="text-xs text-gray-500">Supervisor: {supervisor.full_name}</p>
							{/if}
						{:else}
							<p class="text-xs text-gray-500">No supervisor</p>
						{/if}
					</div>
					<div class="flex gap-2">
						<button
							on:click={() => editSubTeam(subTeam)}
							class="text-gray-500 hover:text-gray-300 transition-colors"
							title="Edit"
						>
							<Edit size={16} />
						</button>
						<button
							on:click={() => deleteSubTeam(subTeam.id)}
							class="text-gray-500 hover:text-red-400 transition-colors"
							title="Delete"
						>
							<Trash2 size={16} />
						</button>
					</div>
				</div>
			</div>
			{/each}
		</div>
	{/if}
	{/if}
</div>

<!-- Invite Member Modal -->
{#if showInviteModal}
	<div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
		<div class="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-md p-6">
			<div class="flex items-center justify-between mb-5">
				<h2 class="text-lg font-semibold text-white">Invite Member</h2>
				<button on:click={() => (showInviteModal = false)} class="text-gray-500 hover:text-gray-300">
					<X size={20} />
				</button>
			</div>
			<form on:submit|preventDefault={sendInvite} class="space-y-4">
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1.5" for="inviteEmail">Email Address</label>
					<input
						id="inviteEmail"
						type="email"
						bind:value={inviteEmail}
						required
						placeholder="colleague@company.com"
						class="input w-full"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1.5" for="inviteRole">Role</label>
					<select id="inviteRole" bind:value={inviteRole} class="input w-full">
						<option value="member">Member</option>
						<option value="supervisor">Supervisor</option>
						{#if $authStore.user?.role === 'admin'}
							<option value="admin">Admin</option>
						{/if}
					</select>
				</div>
				<div class="flex gap-3 pt-1">
					<button
						type="button"
						on:click={() => (showInviteModal = false)}
						class="btn-secondary flex-1"
					>Cancel</button>
					<button
						type="submit"
						disabled={inviting}
						class="btn-primary flex-1 flex items-center justify-center gap-2"
					>
						{#if inviting}<Loader2 class="animate-spin" size={15} />{/if}
						Send Invite
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Add Member Modal -->
{#if showAddModal}
	<div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
		<div class="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-md p-6">
			<div class="flex items-center justify-between mb-5">
				<h2 class="text-lg font-semibold text-white">Add Existing User</h2>
				<button on:click={() => (showAddModal = false)} class="text-gray-500 hover:text-gray-300">
					<X size={20} />
				</button>
			</div>
			<div class="space-y-4">
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1.5" for="addSearch">Search Users</label>
					<input
						id="addSearch"
						type="text"
						bind:value={addSearchQuery}
						placeholder="Search by name, username, or email"
						class="input w-full"
					/>
				</div>
				{#if addSearchQuery}
					<div class="max-h-48 overflow-y-auto space-y-1">
						{#each filteredUsers as u}
							<button
								on:click={() => { addUserId = u.id; addSearchQuery = u.full_name; }}
								class="w-full flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-800 transition-colors text-left {addUserId === u.id ? 'bg-gray-800 ring-1 ring-primary-600/40' : ''}"
							>
								<div class="w-8 h-8 rounded-full bg-primary-700 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
									{initials(u.full_name)}
								</div>
								<div class="flex-1 min-w-0">
									<p class="text-sm text-white truncate">{u.full_name}</p>
									<p class="text-xs text-gray-500 truncate">@{u.username}</p>
								</div>
							</button>
						{/each}
						{#if filteredUsers.length === 0}
							<p class="text-gray-500 text-sm text-center py-3">No users found</p>
						{/if}
					</div>
				{/if}
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1.5" for="addRole">Assign Role</label>
					<select id="addRole" bind:value={addRole} class="input w-full">
						<option value="member">Member</option>
						<option value="supervisor">Supervisor</option>
						{#if $authStore.user?.role === 'admin'}
							<option value="admin">Admin</option>
						{/if}
					</select>
				</div>
				<div class="flex gap-3 pt-1">
					<button
						type="button"
						on:click={() => (showAddModal = false)}
						class="btn-secondary flex-1"
					>Cancel</button>
					<button
						on:click={directAdd}
						disabled={adding || !addUserId}
						class="btn-primary flex-1 flex items-center justify-center gap-2"
					>
						{#if adding}<Loader2 class="animate-spin" size={15} />{/if}
						Add Member
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<!-- Sub-Team Modal -->
{#if showSubTeamModal}
	<div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
		<div class="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-md p-6">
			<div class="flex items-center justify-between mb-5">
				<h2 class="text-lg font-semibold text-white">{editingSubTeam ? 'Edit Sub-Team' : 'Create Sub-Team'}</h2>
				<button on:click={() => (showSubTeamModal = false)} class="text-gray-500 hover:text-gray-300">
					<X size={20} />
				</button>
			</div>
			<form on:submit|preventDefault={saveSubTeam} class="space-y-4">
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1.5" for="subTeamName">Name</label>
					<input
						id="subTeamName"
						type="text"
						bind:value={subTeamName}
						required
						placeholder="Engineering Team"
						class="input w-full"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium text-gray-300 mb-1.5" for="subTeamSupervisor">Supervisor</label>
					<select id="subTeamSupervisor" bind:value={subTeamSupervisorId} class="input w-full">
						<option value={null}>No supervisor</option>
						{#each userList.filter(u => u.role === 'supervisor' || u.role === 'admin') as user}
							<option value={user.id}>{user.full_name} (@{user.username})</option>
						{/each}
					</select>
				</div>
				<div class="flex gap-3 pt-1">
					<button
						type="button"
						on:click={() => (showSubTeamModal = false)}
						class="btn-secondary flex-1"
					>Cancel</button>
					<button
						type="submit"
						class="btn-primary flex-1"
					>
						{editingSubTeam ? 'Update' : 'Create'}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
