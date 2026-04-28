<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore, isLoggedIn, isSupervisor } from '$lib/stores/auth';
	import { notificationStore, type NotificationItem } from '$lib/stores/notifications';
	import { subTeamStore } from '$lib/stores/subTeam';
	import NotificationBell from '$lib/components/NotificationBell.svelte';
	import { formatReminderOffset } from '$lib/utils';
	import { Toaster, toast } from 'svelte-sonner';
	import { sub_teams } from '$lib/apis';
	import {
		LayoutDashboard,
		CheckSquare,
		Users,
		Milestone,
		Calendar,
		Bot,
		LogOut,
		FolderOpen,
		ChevronRight,
		ChevronDown,
		TrendingUp,
		GanttChartSquare,
		Menu,
		X,
		MessageSquare
	} from 'lucide-svelte';

	const navItems = [
		{ href: '/', label: 'Dashboard', icon: LayoutDashboard },
		{ href: '/projects', label: 'Projects', icon: FolderOpen },
		{ href: '/tasks', label: 'Tasks', icon: CheckSquare },
		{ href: '/updates', label: 'Updates', icon: MessageSquare },
		{ href: '/milestones', label: 'Milestones', icon: Milestone },
		{ href: '/timeline', label: 'Timeline', icon: GanttChartSquare },
		{ href: '/team', label: 'Team', icon: Users },
		{ href: '/schedule', label: 'Scheduler', icon: Calendar },
		{ href: '/ai', label: 'AI Assistant', icon: Bot }
	];

	$: sidebarItems = $isSupervisor
		? [...navItems.slice(0, 1), { href: '/performance', label: 'Performance', icon: TrendingUp }, ...navItems.slice(1)]
		: navItems;

	$: isAdmin = $authStore.user?.role === 'admin';

	let subTeams: any[] = [];
	let expanded = false;
	let selectedSubTeam: any = null;

	onMount(async () => {
		await authStore.loadMe();
		const path = String($page.url.pathname);
		if (!$isLoggedIn && path !== '/login' && path !== '/register' && !path.startsWith('/invite/accept')) {
			goto('/login');
		}
		if (isAdmin) {
			subTeams = await sub_teams.list();
		}
	});

	subTeamStore.subscribe((v) => selectedSubTeam = v);

	function selectSubTeam(subTeam: any) {
		subTeamStore.set(subTeam);
		expanded = false;
		window.location.reload();
	}

	function selectAllTeams() {
		subTeamStore.set(null);
		expanded = false;
		window.location.reload();
	}

	// Start/stop notification polling with auth state.
	$: if (typeof window !== 'undefined') {
		if ($isLoggedIn) {
			notificationStore.start((newOnes: NotificationItem[]) => {
				for (const n of newOnes) {
					toast.info(n.title_cache, {
						description: `Reminder · ${formatReminderOffset(n.offset_minutes)} before · ${new Date(n.start_at_cache).toLocaleString()}`
					});
				}
			});
		} else {
			notificationStore.stop();
		}
	}

	$: if (typeof window !== 'undefined' && !$authStore.loading && !$isLoggedIn && !['/login', '/register'].includes(String($page.url.pathname)) && !String($page.url.pathname).startsWith('/invite/accept')) {
		goto('/login');
	}

	$: if (typeof window !== 'undefined' && !$authStore.loading && $isLoggedIn && !$isSupervisor) {
		const path = String($page.url.pathname);
		if (path.startsWith('/performance') || path.startsWith('/admin')) {
			goto('/');
		}
	}

	$: isAuthPage = ['/login', '/register'].includes(String($page.url.pathname)) || String($page.url.pathname).startsWith('/invite/accept');

	let sidebarOpen = false;

	function closeSidebar() {
		sidebarOpen = false;
	}

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
		<!-- Mobile overlay backdrop -->
		{#if sidebarOpen}
			<div
				class="fixed inset-0 bg-black/60 z-30 md:hidden"
				role="presentation"
				on:click={closeSidebar}
				on:keydown={(e) => e.key === 'Escape' && closeSidebar()}
			></div>
		{/if}

		<!-- Sidebar: hidden on mobile unless open, always visible md+ -->
		<aside
			class="fixed md:static inset-y-0 left-0 z-40 w-60 flex-shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col transform transition-transform duration-200
				{sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0"
		>
			<div class="px-5 py-4 border-b border-gray-800">
				<div class="flex items-center gap-2.5">
					<div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">T</div>
					<span class="font-semibold text-white text-lg">TeamFlow</span>
				</div>
			</div>

			<nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
				<NotificationBell />
				{#if isAdmin}
				<div class="sub-team-switcher">
					<button on:click={() => expanded = !expanded} class="switcher-button">
						{selectedSubTeam ? selectedSubTeam.name : 'All Teams'}
						<ChevronDown />
					</button>
					{#if expanded}
					<div class="dropdown">
						<button on:click={selectAllTeams} class="dropdown-item">All Teams</button>
						{#each subTeams as subTeam}
						<button
							on:click={() => selectSubTeam(subTeam)}
							class:dropdown-item-selected={selectedSubTeam?.id === subTeam.id}
							class="dropdown-item"
						>
							{subTeam.name}
						</button>
						{/each}
					</div>
					{/if}
				</div>
				{/if}
				{#each sidebarItems as item}
					{@const active = $page.url.pathname === item.href || ($page.url.pathname.startsWith(item.href) && item.href !== '/')}
					<a
						href={item.href}
						on:click={closeSidebar}
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

		<!-- Main content area -->
		<div class="flex-1 flex flex-col min-w-0 overflow-hidden">
			<!-- Mobile top bar -->
			<header class="md:hidden flex items-center gap-3 px-4 py-3 bg-gray-900 border-b border-gray-800 flex-shrink-0">
				<button
					on:click={() => (sidebarOpen = !sidebarOpen)}
					aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
					class="text-gray-400 hover:text-gray-200 transition-colors"
				>
					{#if sidebarOpen}
						<X size={22} />
					{:else}
						<Menu size={22} />
					{/if}
				</button>
				<div class="flex items-center gap-2">
					<div class="w-6 h-6 bg-primary-600 rounded flex items-center justify-center text-white font-bold text-xs">T</div>
					<span class="font-semibold text-white text-sm">TeamFlow</span>
				</div>
				<div class="ml-auto">
					<NotificationBell />
				</div>
			</header>

			<main class="flex-1 overflow-y-auto bg-gray-950">
				<slot />
			</main>
		</div>
	</div>
{:else}
	<div class="flex items-center justify-center h-screen bg-gray-950">
		<div class="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
	</div>
{/if}

<style>
	.sub-team-switcher {
		@apply px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg;
	}
	.switcher-button {
		@apply w-full flex items-center justify-between text-sm font-medium text-gray-300 hover:text-white;
	}
	.dropdown {
		@apply mt-2 space-y-1;
	}
	.dropdown-item {
		@apply w-full text-left px-2 py-1 text-sm text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded;
	}
	.dropdown-item-selected {
		@apply bg-primary-500/20 text-primary-400;
	}
</style>
