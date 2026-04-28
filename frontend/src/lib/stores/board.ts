import { writable } from 'svelte/store';
import type { BoardWeekPayload } from '$lib/apis/board';

interface BoardState {
	payload: BoardWeekPayload | null;
	loading: boolean;
	saving: boolean;
	summarizing: boolean;
}

export const boardStore = writable<BoardState>({
	payload: null,
	loading: false,
	saving: false,
	summarizing: false
});
