<script lang="ts">
	import { Bell, X } from 'lucide-svelte';
	import { goto } from '$app/navigation';
	import { notificationStore, unreadCount, type NotificationItem } from '$lib/stores/notifications';
	import { formatDateTime } from '$lib/utils';

	let open = false;

	function toggle() {
		open = !open;
	}

	function close() {
		open = false;
	}

	async function dismissOne(e: MouseEvent, id: number) {
		e.stopPropagation();
		try {
			await notificationStore.dismiss(id);
		} catch {
			/* ignore */
		}
	}

	async function dismissAll() {
		try {
			await notificationStore.dismissAll();
		} catch {
			/* ignore */
		}
	}

	function handleItemClick(n: NotificationItem) {
		close();
		switch (n.event_type) {
			case 'schedule':
				goto('/schedule');
				break;
			case 'task':
				goto('/tasks');
				break;
			case 'sprint_end':
				goto(`/tasks?sprint_id=${n.event_ref_id}`);
				break;
			case 'milestone_due':
				goto(`/milestones?milestone_id=${n.event_ref_id}`);
				break;
			case 'reminder_settings_proposal':
				goto('/team');
				break;
		default:
				goto('/tasks');
		}
	}
</script>

<svelte:window on:click={close} />

<div class="relative" role="presentation" on:click|stopPropagation on:keydown|stopPropagation style="position: static">
	<button
		on:click={toggle}
		class="relative flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm font-medium text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition-colors"
		title="Notifications"
	>
		<Bell size={18} />
		<span>Notifications</span>
		{#if $unreadCount > 0}
			<span
				class="ml-auto inline-flex items-center justify-center min-w-[18px] h-[18px] text-[10px] font-bold text-white bg-red-500 rounded-full px-1"
			>
				{$unreadCount}
			</span>
		{/if}
	</button>

	{#if open}
		<div
			class="fixed left-64 top-4 w-80 max-h-[70vh] overflow-y-auto bg-gray-900 border border-gray-800 rounded-xl shadow-xl z-[9999]"
		>
			<div class="flex items-center justify-between px-4 py-3 border-b border-gray-800 sticky top-0 bg-gray-900">
				<h3 class="text-sm font-semibold text-white">Notifications</h3>
				{#if $unreadCount > 0}
					<button
						on:click={dismissAll}
						class="text-xs text-gray-400 hover:text-gray-200 transition-colors"
					>
						Dismiss all
					</button>
				{/if}
			</div>

			{#if $unreadCount === 0}
				<p class="text-sm text-gray-500 text-center py-8 px-4">No new notifications</p>
			{:else}
				<ul class="divide-y divide-gray-800">
					{#each $notificationStore.items as n (n.id)}
						<li class="flex items-start gap-2 hover:bg-gray-800/50 transition-colors">
							<button
								on:click={() => handleItemClick(n)}
								class="flex-1 min-w-0 p-3 text-left"
							>
								<p class="text-sm font-medium text-gray-200 truncate">{n.title_cache}</p>
								<p class="text-xs text-gray-500 mt-0.5">
									{n.offset_minutes} min reminder · {formatDateTime(n.start_at_cache)}
								</p>
								<p class="text-[10px] text-gray-600 mt-0.5 uppercase tracking-wide">
									{n.event_type}
								</p>
							</button>
							<button
								on:click={(e) => dismissOne(e, n.id)}
								class="p-3 text-gray-500 hover:text-gray-200 rounded transition-colors flex-shrink-0"
								title="Dismiss"
							>
								<X size={14} />
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	{/if}
</div>
