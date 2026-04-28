import { writable, derived } from 'svelte/store';
import { notifications as notifApi } from '$lib/apis';

export interface NotificationItem {
	id: number;
	user_id: number;
	event_type:
		| 'schedule'
		| 'task'
		| 'knowledge_session'
		| 'sprint_end'
		| 'milestone_due'
		| 'reminder_settings_proposal';
	event_ref_id: number;
	title_cache: string;
	start_at_cache: string;
	remind_at: string;
	offset_minutes: number;
	status: 'pending' | 'sent' | 'dismissed';
	created_at: string;
}

type State = {
	items: NotificationItem[];
	loading: boolean;
};

const POLL_INTERVAL_MS = 60_000;

function createStore() {
	const { subscribe, set, update } = writable<State>({ items: [], loading: false });
	let timer: ReturnType<typeof setInterval> | null = null;
	let seenIds = new Set<number>();
	let onNewCallback: ((items: NotificationItem[]) => void) | null = null;

	async function refresh() {
		update((s) => ({ ...s, loading: true }));
		try {
			const items: NotificationItem[] = await notifApi.pending();
			const newOnes = items.filter((n) => !seenIds.has(n.id));
			items.forEach((n) => seenIds.add(n.id));
			set({ items, loading: false });
			if (newOnes.length && onNewCallback) onNewCallback(newOnes);
		} catch {
			update((s) => ({ ...s, loading: false }));
		}
	}

	function start(onNew?: (items: NotificationItem[]) => void) {
		if (onNew) onNewCallback = onNew;
		if (timer) return;
		// First poll seeds seenIds without firing callback
		const firstPoll = async () => {
			try {
				const items: NotificationItem[] = await notifApi.pending();
				items.forEach((n) => seenIds.add(n.id));
				set({ items, loading: false });
			} catch {
				/* ignore */
			}
		};
		firstPoll();
		timer = setInterval(refresh, POLL_INTERVAL_MS);
	}

	function stop() {
		if (timer) {
			clearInterval(timer);
			timer = null;
		}
	}

	async function dismiss(id: number) {
		await notifApi.dismiss(id);
		update((s) => ({ ...s, items: s.items.filter((n) => n.id !== id) }));
	}

	async function dismissAll() {
		await notifApi.dismissAll();
		set({ items: [], loading: false });
	}

	return { subscribe, start, stop, refresh, dismiss, dismissAll };
}

export const notificationStore = createStore();

export const unreadCount = derived(notificationStore, ($s) => $s.items.length);
