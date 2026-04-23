<script lang="ts">
	import { onMount } from 'svelte';
	import { users as usersApi, tasks as tasksApi } from '$lib/api';
	import { initials, statusColors, statusLabels, priorityColors, formatDate } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import { Users, Mail, CheckSquare, Clock } from 'lucide-svelte';

	let userList: any[] = [];
	let taskMap: Record<number, any[]> = {};
	let loading = true;
	let selectedUser: any = null;

	onMount(async () => {
		loading = true;
		try {
			userList = await usersApi.list();
			const allTasks = await tasksApi.list();
			for (const u of userList) {
				taskMap[u.id] = allTasks.filter((t: any) => t.assignee_id === u.id);
			}
		} finally {
			loading = false;
		}
	});

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
</script>

<svelte:head><title>Team · TeamFlow</title></svelte:head>

<div class="p-4 md:p-6 max-w-6xl mx-auto">
	<div class="mb-6">
		<h1 class="text-2xl font-bold text-white">Team</h1>
		<p class="text-gray-400 text-sm mt-1">Manage your team members and their workload</p>
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
	{/if}
</div>
