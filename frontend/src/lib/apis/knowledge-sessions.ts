import { request } from './request';

export type KnowledgeSessionType = 'presentation' | 'demo' | 'workshop' | 'qa';

export interface KnowledgeSessionPresenter {
	id: number;
	full_name: string;
	username: string;
	avatar_url: string | null;
	sub_team_id: number | null;
}

export interface KnowledgeSession {
	id: number;
	topic: string;
	description: string | null;
	references: string | null;
	presenter_id: number;
	session_type: KnowledgeSessionType;
	start_time: string;
	duration_minutes: number;
	tags: string[];
	sub_team_id: number | null;
	created_by_id: number;
	created_at: string;
	updated_at: string;
	presenter: KnowledgeSessionPresenter | null;
}

export interface KnowledgeSessionPayload {
	topic: string;
	description?: string | null;
	references?: string | null;
	presenter_id?: number | null;
	session_type: KnowledgeSessionType;
	duration_minutes: number;
	start_time: string;
	tags: string[];
	offset_minutes_list: number[];
}

function toIsoString(value: string | Date) {
	return value instanceof Date ? value.toISOString() : value;
}

export const knowledgeSessions = {
	list: (params?: { start?: string | Date | null; end?: string | Date | null }) => {
		const qs = new URLSearchParams();
		if (params?.start) qs.set('start', toIsoString(params.start));
		if (params?.end) qs.set('end', toIsoString(params.end));
		return request(`/knowledge-sessions/${qs.toString() ? `?${qs}` : ''}`);
	},
	get: (id: number) => request(`/knowledge-sessions/${id}`),
	create: (data: KnowledgeSessionPayload) =>
		request('/knowledge-sessions/', { method: 'POST', body: JSON.stringify(data) }),
	update: (id: number, data: Partial<KnowledgeSessionPayload>) =>
		request(`/knowledge-sessions/${id}`, {
			method: 'PATCH',
			body: JSON.stringify(data)
		}),
	delete: (id: number) => request(`/knowledge-sessions/${id}`, { method: 'DELETE' })
};
