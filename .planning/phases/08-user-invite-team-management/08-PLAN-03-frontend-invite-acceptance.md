---
id: 08-03
wave: 3
title: Frontend Invite Modal & Acceptance Page
depends_on: [08-02]
files_modified:
  - frontend/src/lib/api.ts
  - frontend/src/routes/team/+page.svelte
  - frontend/src/routes/invite/accept/+page.svelte
  - frontend/src/routes/+layout.svelte
autonomous: true
requirements:
  - REQ-08
---

# Plan 08-03: Frontend Invite Modal & Acceptance Page

## Goal

Implement the frontend invite flow: add "Invite Member" modal and "Add Member" modal to the team page (supervisor/admin only), pending invites list, and the public `/invite/accept` route for new users to complete account setup.

## must_haves

- `frontend/src/lib/api.ts` has `invites` namespace with all invite API calls
- Team page shows "Invite Member" and "Add Member" buttons only for supervisors/admins
- "Invite Member" modal: email input + role selector → calls `POST /api/teams/invite`
- "Add Member" modal: user search by username/email → calls `POST /api/teams/add`
- Pending invites table visible to supervisors/admins: email, role, invited_by (id), expires_at, cancel button
- `/invite/accept` page: public, loads invite metadata from `GET /api/invites/validate?token=…`, shows form (code + username + full_name + password), submits to `POST /api/invites/accept`, redirects to `/` on success
- `/invite/accept` route excluded from auth guard redirect in `+layout.svelte`
- Responsive (mobile-friendly) — consistent with existing `p-4 md:p-6` padding pattern

---

## Tasks

<task id="08-03-T1">
<title>Add invites API namespace to api.ts</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `frontend/src/lib/api.ts` — existing namespace pattern (auth, users, tasks, etc.), `request()` helper function at top
</read_first>

<action>
Add the following `invites` namespace at the END of `frontend/src/lib/api.ts`:

```typescript
// Invites
export const invites = {
	sendInvite: (email: string, role: string) =>
		request('/teams/invite', { method: 'POST', body: JSON.stringify({ email, role }) }),
	directAdd: (userId: number, role?: string) =>
		request('/teams/add', {
			method: 'POST',
			body: JSON.stringify({ user_id: userId, ...(role ? { role } : {}) })
		}),
	validate: (token: string) => request(`/invites/validate?token=${encodeURIComponent(token)}`),
	accept: (data: {
		token: string;
		validation_code: string;
		username: string;
		full_name: string;
		password: string;
	}) => request('/invites/accept', { method: 'POST', body: JSON.stringify(data) }),
	pending: () => request('/invites/pending'),
	cancel: (inviteId: number) => request(`/invites/${inviteId}`, { method: 'DELETE' })
};
```
</action>

<acceptance_criteria>
- `frontend/src/lib/api.ts` contains `export const invites = {`
- `frontend/src/lib/api.ts` contains `sendInvite:`
- `frontend/src/lib/api.ts` contains `directAdd:`
- `frontend/src/lib/api.ts` contains `validate:`
- `frontend/src/lib/api.ts` contains `accept:`
- `frontend/src/lib/api.ts` contains `pending:`
- `frontend/src/lib/api.ts` contains `cancel:`
</acceptance_criteria>
</task>

<task id="08-03-T2">
<title>Update +layout.svelte to exclude /invite/accept from auth guard</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `frontend/src/routes/+layout.svelte` — auth guard logic in `onMount` (lines 41-47) and reactive redirect (lines 64-66)
</read_first>

<action>
In `frontend/src/routes/+layout.svelte`, make two changes:

1. Update the `onMount` auth guard (around line 44) to exclude `/invite/accept`:
```typescript
		if (!$isLoggedIn && path !== '/login' && path !== '/register' && !path.startsWith('/invite/accept')) {
			goto('/login');
		}
```

2. Update the reactive redirect (around line 64) to exclude `/invite/accept`:
```typescript
	$: if (typeof window !== 'undefined' && !$authStore.loading && !$isLoggedIn && !['/login', '/register'].includes(String($page.url.pathname)) && !String($page.url.pathname).startsWith('/invite/accept')) {
		goto('/login');
	}
```

3. Update the `isAuthPage` reactive variable to include invite accept as a public (no-sidebar) page:
```typescript
	$: isAuthPage = ['/login', '/register'].includes(String($page.url.pathname)) || String($page.url.pathname).startsWith('/invite/accept');
```
</action>

<acceptance_criteria>
- `frontend/src/routes/+layout.svelte` contains `!path.startsWith('/invite/accept')` in onMount guard
- `frontend/src/routes/+layout.svelte` contains `!String($page.url.pathname).startsWith('/invite/accept')` in reactive redirect
- `frontend/src/routes/+layout.svelte` contains `String($page.url.pathname).startsWith('/invite/accept')` in isAuthPage
</acceptance_criteria>
</task>

<task id="08-03-T3">
<title>Create /invite/accept public page</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `frontend/src/routes/login/+page.svelte` — existing login form pattern (form styling, error handling, toast, goto, authStore pattern)
- `frontend/src/routes/register/+page.svelte` — existing registration form pattern
- `frontend/src/lib/api.ts` — `invites.validate()` and `invites.accept()` (just added)
- `frontend/src/routes/+layout.svelte` — `isAuthPage` pattern (no sidebar for auth pages)
</read_first>

<action>
Create the directory and file `frontend/src/routes/invite/accept/+page.svelte` with:

```svelte
<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { invites } from '$lib/api';
	import { authStore } from '$lib/stores/auth';
	import { ShieldCheck, Loader2 } from 'lucide-svelte';

	let token = '';
	let inviteData: { email: string; role: string; invited_by_name: string; expires_at: string; valid: boolean } | null = null;
	let loadingInvite = true;
	let inviteError = '';

	let validationCode = '';
	let username = '';
	let fullName = '';
	let password = '';
	let confirmPassword = '';
	let submitting = false;

	onMount(async () => {
		token = $page.url.searchParams.get('token') || '';
		if (!token) {
			inviteError = 'No invite token provided.';
			loadingInvite = false;
			return;
		}
		try {
			inviteData = await invites.validate(token);
			if (!inviteData.valid) {
				inviteError = 'This invite has expired or has already been used.';
			}
		} catch (e: any) {
			inviteError = e.message || 'Invalid or expired invite link.';
		} finally {
			loadingInvite = false;
		}
	});

	async function handleAccept() {
		if (!inviteData?.valid) return;
		if (password !== confirmPassword) {
			toast.error('Passwords do not match');
			return;
		}
		if (password.length < 8) {
			toast.error('Password must be at least 8 characters');
			return;
		}
		submitting = true;
		try {
			await invites.accept({ token, validation_code: validationCode, username, full_name: fullName, password });
			await authStore.loadMe();
			toast.success('Account created! Welcome to TeamFlow.');
			goto('/');
		} catch (e: any) {
			toast.error(e.message || 'Failed to accept invite');
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head><title>Accept Invite · TeamFlow</title></svelte:head>

<div class="min-h-screen bg-gray-950 flex items-center justify-center p-4">
	<div class="w-full max-w-md">
		<div class="flex items-center gap-2.5 justify-center mb-8">
			<div class="w-9 h-9 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-base">T</div>
			<span class="font-semibold text-white text-xl">TeamFlow</span>
		</div>

		{#if loadingInvite}
			<div class="flex items-center justify-center py-16">
				<Loader2 class="animate-spin text-primary-400" size={32} />
			</div>
		{:else if inviteError}
			<div class="card text-center py-12">
				<ShieldCheck class="mx-auto text-gray-600 mb-4" size={40} />
				<h2 class="text-lg font-semibold text-white mb-2">Invalid Invite</h2>
				<p class="text-gray-400 text-sm mb-6">{inviteError}</p>
				<a href="/login" class="text-primary-400 text-sm hover:underline">Go to login</a>
			</div>
		{:else if inviteData}
			<div class="card">
				<div class="mb-6">
					<h1 class="text-xl font-bold text-white mb-1">Accept your invite</h1>
					<p class="text-gray-400 text-sm">
						<span class="text-white font-medium">{inviteData.invited_by_name}</span> invited you to join as
						<span class="text-primary-400 font-medium capitalize">{inviteData.role}</span>
					</p>
					<p class="text-gray-500 text-xs mt-1">Joining as: {inviteData.email}</p>
				</div>

				<form on:submit|preventDefault={handleAccept} class="space-y-4">
					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="code">
							Validation Code <span class="text-gray-500 font-normal">(from your email)</span>
						</label>
						<input
							id="code"
							type="text"
							bind:value={validationCode}
							required
							maxlength="6"
							placeholder="6-digit code"
							class="input w-full tracking-widest text-center text-lg font-mono"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="fullName">Full Name</label>
						<input
							id="fullName"
							type="text"
							bind:value={fullName}
							required
							placeholder="Jane Smith"
							class="input w-full"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="username">Username</label>
						<input
							id="username"
							type="text"
							bind:value={username}
							required
							placeholder="janesmith"
							class="input w-full"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="password">Password</label>
						<input
							id="password"
							type="password"
							bind:value={password}
							required
							minlength="8"
							placeholder="At least 8 characters"
							class="input w-full"
						/>
					</div>

					<div>
						<label class="block text-sm font-medium text-gray-300 mb-1.5" for="confirm">Confirm Password</label>
						<input
							id="confirm"
							type="password"
							bind:value={confirmPassword}
							required
							placeholder="Repeat password"
							class="input w-full"
						/>
					</div>

					<button
						type="submit"
						disabled={submitting}
						class="btn-primary w-full flex items-center justify-center gap-2 py-2.5"
					>
						{#if submitting}
							<Loader2 class="animate-spin" size={16} />
							Creating account…
						{:else}
							Join TeamFlow
						{/if}
					</button>
				</form>

				<p class="text-center text-xs text-gray-500 mt-4">
					Already have an account? <a href="/login" class="text-primary-400 hover:underline">Log in</a>
				</p>
			</div>
		{/if}
	</div>
</div>
```
</action>

<acceptance_criteria>
- File `frontend/src/routes/invite/accept/+page.svelte` exists
- `frontend/src/routes/invite/accept/+page.svelte` contains `invites.validate(token)`
- `frontend/src/routes/invite/accept/+page.svelte` contains `invites.accept({`
- `frontend/src/routes/invite/accept/+page.svelte` contains `goto('/')`
- `frontend/src/routes/invite/accept/+page.svelte` contains `authStore.loadMe()`
- `frontend/src/routes/invite/accept/+page.svelte` contains `<title>Accept Invite · TeamFlow</title>`
- `frontend/src/routes/invite/accept/+page.svelte` contains `tracking-widest text-center text-lg font-mono` (code input styling)
</acceptance_criteria>
</task>

<task id="08-03-T4">
<title>Add invite UI to team page (modals + pending invites)</title>
<type>execute</type>
<priority>blocking</priority>

<read_first>
- `frontend/src/routes/team/+page.svelte` — full file (144 lines), existing imports, `userList`, `loading`, modal patterns
- `frontend/src/lib/stores/auth.ts` — `isSupervisor` store export (used in +layout.svelte)
- `frontend/src/lib/api.ts` — `invites` namespace (just added), `users.list()`
</read_first>

<action>
Replace the entire content of `frontend/src/routes/team/+page.svelte` with the following (preserves all existing functionality, adds invite UI):

```svelte
<script lang="ts">
	import { onMount } from 'svelte';
	import { users as usersApi, tasks as tasksApi, invites as invitesApi } from '$lib/api';
	import { initials, statusColors, statusLabels, priorityColors, formatDate } from '$lib/utils';
	import { authStore, isSupervisor } from '$lib/stores/auth';
	import { toast } from 'svelte-sonner';
	import { Users, Mail, CheckSquare, UserPlus, UserCheck, X, Loader2 } from 'lucide-svelte';

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
```
</action>

<acceptance_criteria>
- `frontend/src/routes/team/+page.svelte` contains `invitesApi` import
- `frontend/src/routes/team/+page.svelte` contains `isSupervisor` import from `$lib/stores/auth`
- `frontend/src/routes/team/+page.svelte` contains `showInviteModal`
- `frontend/src/routes/team/+page.svelte` contains `showAddModal`
- `frontend/src/routes/team/+page.svelte` contains `invitesApi.sendInvite(`
- `frontend/src/routes/team/+page.svelte` contains `invitesApi.directAdd(`
- `frontend/src/routes/team/+page.svelte` contains `invitesApi.cancel(`
- `frontend/src/routes/team/+page.svelte` contains `Pending Invites`
- `frontend/src/routes/team/+page.svelte` contains `$isSupervisor` for conditional rendering
- `frontend/src/routes/team/+page.svelte` contains all original user card grid and task detail panel
</acceptance_criteria>
</task>

---

## Verification

```bash
# Confirm api.ts additions
grep -n "export const invites" frontend/src/lib/api.ts
grep -n "sendInvite:" frontend/src/lib/api.ts

# Confirm layout auth guard updates
grep -n "invite/accept" frontend/src/routes/+layout.svelte

# Confirm acceptance page exists
ls frontend/src/routes/invite/accept/+page.svelte

# Confirm key elements in acceptance page
grep -n "invites.validate" frontend/src/routes/invite/accept/+page.svelte
grep -n "invites.accept" frontend/src/routes/invite/accept/+page.svelte

# Confirm team page updates
grep -n "showInviteModal\|showAddModal\|isSupervisor\|Pending Invites" frontend/src/routes/team/+page.svelte

# Build check
cd frontend && bun run build 2>&1 | tail -5
```
