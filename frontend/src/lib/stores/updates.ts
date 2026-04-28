import { writable } from 'svelte/store';

export interface TaskSnapshot {
    id: number;
    title: string;
    status: string;
    priority: string;
    due_date: string | null;
}

export interface StandupPost {
    id: number;
    author_id: number;
    sub_team_id: number;
    field_values: Record<string, string>;
    task_snapshot: TaskSnapshot[];
    created_at: string;
    updated_at: string;
    author: { id: number; full_name: string } | null;
}

interface UpdatesState {
    posts: StandupPost[];
    nextCursor: number | null;
    loading: boolean;
    loadingMore: boolean;
    filterAuthorId: number | null;
    filterDate: string | null;
    fieldTypes: Record<string, string>;
}

export const updatesStore = writable<UpdatesState>({
    posts: [],
    nextCursor: null,
    loading: false,
    loadingMore: false,
    filterAuthorId: null,
    filterDate: null,
    fieldTypes: {},
});
