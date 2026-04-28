import { request } from './request';

export interface BoardWeekOption {
	iso_year: number;
	iso_week: number;
	week_start_date: string;
	label: string;
	is_current_week: boolean;
}

export interface BoardSummary {
	id: number;
	sub_team_id: number;
	iso_year: number;
	iso_week: number;
	week_start_date: string;
	summary_text: string;
	source_post_count: number;
	generated_by_mode: string;
	generated_at: string;
}

export interface BoardAppend {
	id: number;
	author_id: number;
	content: string;
	created_at: string;
	updated_at: string;
	author: { id: number; full_name: string } | null;
}

export interface BoardPost {
	id: number;
	author_id: number;
	sub_team_id: number;
	iso_year: number;
	iso_week: number;
	week_start_date: string;
	content: string;
	created_at: string;
	updated_at: string;
	author: { id: number; full_name: string } | null;
	appends: BoardAppend[];
}

export interface BoardWeekPayload {
	selected_iso_year: number;
	selected_iso_week: number;
	selected_week_start_date: string;
	summary: BoardSummary | null;
	posts: BoardPost[];
	week_options: BoardWeekOption[];
	viewer_can_post: boolean;
	is_current_week: boolean;
}

export const board = {
	getWeek: (params?: { year?: number; week?: number }) => {
		const search = new URLSearchParams();
		if (params?.year !== undefined) search.set('year', String(params.year));
		if (params?.week !== undefined) search.set('week', String(params.week));
		const qs = search.toString() ? `?${search.toString()}` : '';
		return request<BoardWeekPayload>(`/board/week${qs}`);
	},
	createPost: (data: { content: string }) => request<BoardPost>('/board/posts', { method: 'POST', body: JSON.stringify(data) }),
	updatePost: (id: number, data: { content: string }) =>
		request<BoardPost>(`/board/posts/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
	deletePost: (id: number) => request<void>(`/board/posts/${id}`, { method: 'DELETE' }),
	createAppend: (postId: number, data: { content: string }) =>
		request<BoardAppend>(`/board/posts/${postId}/appends`, { method: 'POST', body: JSON.stringify(data) }),
	updateAppend: (appendId: number, data: { content: string }) =>
		request<BoardAppend>(`/board/appends/${appendId}`, { method: 'PATCH', body: JSON.stringify(data) }),
	deleteAppend: (appendId: number) => request<void>(`/board/appends/${appendId}`, { method: 'DELETE' }),
	summarizeWeek: (params?: { year?: number; week?: number }) => {
		const search = new URLSearchParams();
		if (params?.year !== undefined) search.set('year', String(params.year));
		if (params?.week !== undefined) search.set('week', String(params.week));
		const qs = search.toString() ? `?${search.toString()}` : '';
		return request<BoardSummary>(`/board/week/summary${qs}`, { method: 'POST' });
	}
};
