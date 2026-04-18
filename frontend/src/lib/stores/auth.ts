import { writable, derived } from 'svelte/store';
import { auth as authApi } from '$lib/api';

interface User {
	id: number;
	email: string;
	username: string;
	full_name: string;
	role: string;
	avatar_url: string | null;
	is_active: boolean;
	created_at: string;
}

interface AuthState {
	user: User | null;
	loading: boolean;
}

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>({
		user: null,
		loading: true
	});

	return {
		subscribe,
		async login(username: string, password: string) {
			update((s) => ({ ...s, loading: true }));
			try {
				await authApi.login(username, password);
				const user = await authApi.me() as User;
				set({ user, loading: false });
				return user;
			} catch (e) {
				update((s) => ({ ...s, loading: false }));
				throw e;
			}
		},
		async loadMe() {
			update((s) => ({ ...s, loading: true }));
			try {
				const user = await authApi.me() as User;
				update((s) => ({ ...s, user, loading: false }));
			} catch {
				set({ user: null, loading: false });
			}
		},
		async logout() {
			try {
				await authApi.logout();
			} catch {
				// ignore errors — clear local state regardless
			}
			set({ user: null, loading: false });
		}
	};
}

export const authStore = createAuthStore();
export const currentUser = derived(authStore, ($a) => $a.user);
export const isLoggedIn = derived(authStore, ($a) => !!$a.user);
