const BASE = '/api';

import { subTeamStore } from '$lib/stores/subTeam';

interface SubTeam {
    id: number;
    name: string;
    supervisor_id: number | null;
}

export interface ApiError extends Error {
    detail?: unknown;
    status?: number;
    payload?: unknown;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function request<T = any>(
    path: string,
    options: RequestInit = {}
): Promise<T> {
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
    };

    // Add X-SubTeam-ID header for admins
    let selectedSubTeam: SubTeam | null = null;
    const unsubscribe = subTeamStore.subscribe((v: SubTeam | null) => {
        selectedSubTeam = v;
    });
    unsubscribe();
    const activeSubTeam = selectedSubTeam as SubTeam | null;
    if (activeSubTeam && activeSubTeam.id) {
        headers['X-SubTeam-ID'] = activeSubTeam.id.toString();
    }

    const res = await fetch(`${BASE}${path}`, {
        ...options,
        headers,
        credentials: 'include',
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        const detail = err?.detail ?? err;
        const message =
            typeof detail === 'string'
                ? detail
                : typeof detail?.message === 'string'
                    ? detail.message
                    : typeof err?.message === 'string'
                        ? err.message
                        : res.statusText || 'Request failed';
        const error = new Error(message) as ApiError;
        error.detail = detail;
        error.status = res.status;
        error.payload = err;
        throw error;
    }
    if (res.status === 204) return undefined as T;
    return res.json();
}
