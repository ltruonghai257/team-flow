<script lang="ts">
	import { onMount } from 'svelte';
	import { users as usersApi, tasks as tasksApi, invites as invitesApi } from '$lib/api';
	import { initials, statusColors, statusLabels, priorityColors, formatDate } from '$lib/utils';
	import { authStore, isSupervisor } from '$lib/stores/auth';
	import { toast } from 'svelte-sonner';
	import { Mail, Users, UserPlus, UserCheck, X, Loader2 } from 'lucide-svelte';

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
			}
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
