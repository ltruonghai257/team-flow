const BASE = '/api';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function request<T = any>(path: string, options: RequestInit = {}): Promise<T> {
	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(options.headers as Record<string, string>)
	};

	const res = await fetch(`${BASE}${path}`, { ...options, headers, credentials: 'include' });
	if (!res.ok) {
		const err = await res.json().catch(() => ({ detail: res.statusText }));
		throw new Error(err.detail || 'Request failed');
	}
	if (res.status === 204) return undefined as T;
	return res.json();
}

// Auth
export const auth = {
	login: (username: string, password: string) => {
		const body = new URLSearchParams({ username, password });
		return fetch(`${BASE}/auth/token`, {
			method: 'POST',
			body,
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
			credentials: 'include'
		}).then(async (r) => {
			if (!r.ok) throw new Error((await r.json()).detail || 'Login failed');
			return r.json();
		});
	},
	register: (data: object) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
	me: () => request('/auth/me'),
	logout: () => request('/auth/logout', { method: 'POST' })
};

// Users
export const users = {
	list: () => request('/users/'),
	get: (id: number) => request(`/users/${id}`),
	update: (id: number, data: object) => request(`/users/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
};

// Projects
export const projects = {
	list: () => request('/projects/'),
	get: (id: number) => request(`/projects/${id}`),
	create: (data: object) => request('/projects/', { method: 'POST', body: JSON.stringify(data) }),
	update: (id: number, data: object) => request(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
	delete: (id: number) => request(`/projects/${id}`, { method: 'DELETE' })
};

// Milestones
export const milestones = {
	list: (projectId?: number) =>
		request(`/milestones/${projectId ? `?project_id=${projectId}` : ''}`),
	get: (id: number) => request(`/milestones/${id}`),
	create: (data: object) => request('/milestones/', { method: 'POST', body: JSON.stringify(data) }),
	update: (id: number, data: object) =>
		request(`/milestones/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
	delete: (id: number) => request(`/milestones/${id}`, { method: 'DELETE' })
};

// Tasks
export const tasks = {
	list: (params?: Record<string, string | boolean | number>) => {
		const qs = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
		return request(`/tasks/${qs}`);
	},
	get: (id: number) => request(`/tasks/${id}`),
	create: (data: object) => request('/tasks/', { method: 'POST', body: JSON.stringify(data) }),
	update: (id: number, data: object) =>
		request(`/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
	delete: (id: number) => request(`/tasks/${id}`, { method: 'DELETE' }),
	aiParse: (input: string, mode: 'nlp' | 'json', model?: string) =>
		request('/tasks/ai-parse', {
			method: 'POST',
			body: JSON.stringify({ input, mode, ...(model ? { model } : {}) })
		})
};

// Schedules
export const schedules = {
	list: (start?: string, end?: string) => {
		const qs = new URLSearchParams();
		if (start) qs.set('start', start);
		if (end) qs.set('end', end);
		return request(`/schedules/${qs.toString() ? '?' + qs : ''}`);
	},
	create: (data: object) => request('/schedules/', { method: 'POST', body: JSON.stringify(data) }),
	update: (id: number, data: object) =>
		request(`/schedules/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
	delete: (id: number) => request(`/schedules/${id}`, { method: 'DELETE' })
};

// Notifications
export const notifications = {
	create: (data: { event_type: 'schedule' | 'task'; event_ref_id: number; offset_minutes: number }) =>
		request('/notifications', { method: 'POST', body: JSON.stringify(data) }),
	bulkSet: (data: { event_type: 'schedule' | 'task'; event_ref_id: number; offset_minutes_list: number[] }) =>
		request('/notifications/bulk', { method: 'POST', body: JSON.stringify(data) }),
	pending: () => request('/notifications/pending'),
	byEvent: (event_type: 'schedule' | 'task', event_ref_id: number) =>
		request(`/notifications/by-event?event_type=${event_type}&event_ref_id=${event_ref_id}`),
	dismiss: (id: number) => request(`/notifications/${id}/dismiss`, { method: 'PATCH' }),
	dismissAll: () => request('/notifications/dismiss-all', { method: 'POST' }),
	remove: (id: number) => request(`/notifications/${id}`, { method: 'DELETE' })
};

// AI
export const ai = {
	listConversations: () => request('/ai/conversations'),
	createConversation: () => request('/ai/conversations', { method: 'POST' }),
	getConversation: (id: number) => request(`/ai/conversations/${id}`),
	deleteConversation: (id: number) => request(`/ai/conversations/${id}`, { method: 'DELETE' }),
	sendMessage: (convId: number, content: string) =>
		request(`/ai/conversations/${convId}/messages`, {
			method: 'POST',
			body: JSON.stringify({ content })
		}),
	quickChat: (content: string) =>
		request('/ai/quick-chat', { method: 'POST', body: JSON.stringify({ content }) })
};

// Chat
export const chat = {
	listChannels: () => request('/chat/channels'),
	myChannels: () => request('/chat/channels/my'),
	createChannel: (name: string, description?: string) =>
		request('/chat/channels', { method: 'POST', body: JSON.stringify({ name, description }) })
};

// Dashboard
export const dashboard = {
	stats: () => request('/dashboard/')
};
