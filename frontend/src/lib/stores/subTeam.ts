import { writable } from 'svelte/store';

interface SubTeam {
	id: number;
	name: string;
	supervisor_id: number | null;
}

const { subscribe, set, update } = writable<SubTeam | null>(null);

// Load from localStorage on init
if (typeof window !== 'undefined') {
	const stored = localStorage.getItem('selectedSubTeam');
	if (stored) set(JSON.parse(stored));
}

// Persist to localStorage on change
subscribe((value) => {
	if (typeof window !== 'undefined') {
		if (value) {
			localStorage.setItem('selectedSubTeam', JSON.stringify(value));
		} else {
			localStorage.removeItem('selectedSubTeam');
		}
	}
});

export const subTeamStore = { subscribe, set, update };
