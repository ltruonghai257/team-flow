<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore, isLoggedIn } from '$lib/stores/auth';
	import { notificationStore, type NotificationItem } from '$lib/stores/notifications';
	import NotificationBell from '$lib/components/NotificationBell.svelte';
	import { Toaster, toast } from 'svelte-sonner';
	import {
		LayoutDashboard,
		CheckSquare,
		Users,
		Milestone,
		Calendar,
		Bot,
		LogOut,
		FolderOpen,
		ChevronRight
	} from 'lucide-svelte';

	const navItems = [
		{ href: '/', label: 'Dashboard', icon: LayoutDashboard },
		{ href: '/projects', label: 'Projects', icon: FolderOpen },
		{ href: '/tasks', label: 'Tasks', icon: CheckSquare },
		{ href: '/milestones', label: 'Milestones', icon: Milestone },
		{ href: '/team', label: 'Team', icon: Users },
		{ href: '/schedule', label: 'Scheduler', icon: Calendar },
		{ href: '/ai', label: 'AI Assistant', icon: Bot }
	];

	onMount(async () => {
		await authStore.loadMe();
		const path = String($page.url.pathname);
		if (!$isLoggedIn && path !== '/login' && path !== '/register') {
			goto('/login');
		}
	});

	// Start/stop notification polling with auth state.
	$: if (typeof window !== 'undefined') {
		if ($isLoggedIn) {
			notificationStore.start((newOnes: NotificationItem[]) => {
				for (const n of newOnes) {
					toast.info(n.title_cache, {
						description: `Reminder · ${n.offset_minutes} min before · ${new Date(n.start_at_cache).toLocaleString()}`
					});
				}
			});
		} else {
			notificationStore.stop();
		}
	}

	$: if (typeof window !== 'undefined' && !$authStore.loading && !$isLoggedIn && !['/login', '/register'].includes(String($page.url.pathname))) {
		goto('/login');
	}

	$: isAuthPage = ['/login', '/register'].includes(String($page.url.pathname));

	async function logout() {
		await authStore.logout();
		goto('/login');
	}
</script>

<Toaster richColors position="top-right" />

{#if isAuthPage}
	<slot />
{:else if $isLoggedIn}
	<div class="flex h-screen overflow-hidden">
		<!-- Sidebar -->
		<aside class="w-60 flex-shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
			<div class="px-5 py-4 border-b border-gray-800">
				<div class="flex items-center gap-2.5">
					<div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">T</div>
					<span class="font-semibold text-white text-lg">TeamFlow</span>
				</div>
			</div>

			<nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
				<NotificationBell />
				{#each navItems as item}
					{@const active = $page.url.pathname === item.href || ($page.url.pathname.startsWith(item.href) && item.href !== '/')}
					<a
						href={item.href}
						class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group {active
							? 'bg-primary-600/20 text-primary-400'
							: 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'}"
					>
						<svelte:component this={item.icon} class="w-4.5 h-4.5 flex-shrink-0" size={18} />
						{item.label}
						{#if active}
							<ChevronRight class="ml-auto" size={14} />
						{/if}
					</a>
				{/each}
			</nav>

			<!-- User -->
			{#if $authStore.user}
				<div class="px-3 py-4 border-t border-gray-800">
					<div class="flex items-center gap-3 px-2">
						<div class="w-8 h-8 rounded-full bg-primary-700 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
							{$authStore.user.full_name.slice(0, 2).toUpperCase()}
						</div>
						<div class="flex-1 min-w-0">
							<p class="text-sm font-medium text-gray-200 truncate">{$authStore.user.full_name}</p>
							<p class="text-xs text-gray-500 truncate capitalize">{$authStore.user.role}</p>
						</div>
						<button on:click={logout} class="text-gray-500 hover:text-red-400 transition-colors" title="Logout">
							<LogOut size={16} />
						</button>
					</div>
				</div>
			{/if}
		</aside>

		<!-- Main -->
		<main class="flex-1 overflow-y-auto bg-gray-950">
			<slot />
		</main>
	</div>
{:else}
	<div class="flex items-center justify-center h-screen bg-gray-950">
		<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
	</div>
{/if}
