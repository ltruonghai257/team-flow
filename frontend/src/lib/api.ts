import { request } from '$lib/apis/request';
import type { StatusTransition, StatusTransitionPair } from '$lib/types/status';

export type { StatusSetScope, CustomStatus, StatusSet, StatusTransition, StatusTransitionPair } from '$lib/types/status';
export type { ReminderSettings, ReminderSettingsProposal } from '$lib/types/notification';

// Auth
export const auth = {
    login: (username: string, password: string) => {
        const body = new URLSearchParams({ username, password });
        return fetch('/api/auth/token', {
            method: 'POST',
            body,
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            credentials: 'include',
        }).then(async r => {
            if (!r.ok)
                throw new Error((await r.json()).detail || 'Login failed');
            return r.json();
        });
    },
    register: (data: object) =>
        request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    me: () => request('/auth/me'),
    logout: () => request('/auth/logout', { method: 'POST' }),
};

// Users
export const users = {
    list: () => request('/users/'),
    get: (id: number) => request(`/users/${id}`),
    update: (id: number, data: object) =>
        request(`/users/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
};

// Projects
export const projects = {
    list: () => request('/projects/'),
    get: (id: number) => request(`/projects/${id}`),
    create: (data: object) =>
        request('/projects/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
        request(`/projects/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
    delete: (id: number) => request(`/projects/${id}`, { method: 'DELETE' }),
};

// Milestones
export const milestones = {
    list: (projectId?: number) =>
        request(`/milestones/${projectId ? `?project_id=${projectId}` : ''}`),
    get: (id: number) => request(`/milestones/${id}`),
    create: (data: object) =>
        request('/milestones/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
        request(`/milestones/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
    delete: (id: number) => request(`/milestones/${id}`, { method: 'DELETE' }),
};

// Sprints
export const sprints = {
    list: (params?: Record<string, string | boolean | number>) => {
        const qs = params
            ? '?' +
              new URLSearchParams(params as Record<string, string>).toString()
            : '';
        return request(`/sprints/${qs}`);
    },
    get: (id: number) => request(`/sprints/${id}`),
    create: (data: object) =>
        request('/sprints/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
        request(`/sprints/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
    delete: (id: number) => request(`/sprints/${id}`, { method: 'DELETE' }),
    close: (id: number, data: object) =>
        request(`/sprints/${id}/close`, {
            method: 'POST',
            body: JSON.stringify(data),
        }),
};

// Tasks
export const tasks = {
    list: (params?: Record<string, string | boolean | number>) => {
        const qs = params
            ? '?' +
              new URLSearchParams(params as Record<string, string>).toString()
            : '';
        return request(`/tasks/${qs}`);
    },
    get: (id: number) => request(`/tasks/${id}`),
    create: (data: object) =>
        request('/tasks/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
        request(`/tasks/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
    delete: (id: number) => request(`/tasks/${id}`, { method: 'DELETE' }),
    aiParse: (input: string, mode: 'nlp' | 'json', model?: string) =>
        request('/tasks/ai-parse', {
            method: 'POST',
            body: JSON.stringify({ input, mode, ...(model ? { model } : {}) }),
        }),
    aiBreakdown: (description: string, projectId: number) =>
        request('/tasks/ai-breakdown', {
            method: 'POST',
            body: JSON.stringify({ description, project_id: projectId }),
        }),
};

// Schedules
export const schedules = {
    list: (start?: string, end?: string) => {
        const qs = new URLSearchParams();
        if (start) qs.set('start', start);
        if (end) qs.set('end', end);
        return request(`/schedules/${qs.toString() ? '?' + qs : ''}`);
    },
    create: (data: object) =>
        request('/schedules/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
        request(`/schedules/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
    delete: (id: number) => request(`/schedules/${id}`, { method: 'DELETE' }),
};

// Notifications
export const notifications = {
    create: (data: {
        event_type: 'schedule' | 'task';
        event_ref_id: number;
        offset_minutes: number;
    }) =>
        request('/notifications', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    bulkSet: (data: {
        event_type: 'schedule' | 'task';
        event_ref_id: number;
        offset_minutes_list: number[];
    }) =>
        request('/notifications/bulk', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    pending: () => request('/notifications/pending'),
    byEvent: (event_type: 'schedule' | 'task', event_ref_id: number) =>
        request(
            `/notifications/by-event?event_type=${event_type}&event_ref_id=${event_ref_id}`
        ),
    dismiss: (id: number) =>
        request(`/notifications/${id}/dismiss`, { method: 'PATCH' }),
    dismissAll: () => request('/notifications/dismiss-all', { method: 'POST' }),
    remove: (id: number) =>
        request(`/notifications/${id}`, { method: 'DELETE' }),
};

// AI
export const ai = {
    listConversations: () => request('/ai/conversations'),
    createConversation: () => request('/ai/conversations', { method: 'POST' }),
    getConversation: (id: number) => request(`/ai/conversations/${id}`),
    deleteConversation: (id: number) =>
        request(`/ai/conversations/${id}`, { method: 'DELETE' }),
    sendMessage: (convId: number, content: string) =>
        request(`/ai/conversations/${convId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ content }),
        }),
    quickChat: (content: string) =>
        request('/ai/quick-chat', {
            method: 'POST',
            body: JSON.stringify({ content }),
        }),
    projectSummary: (projectId: number) =>
        request('/ai/project-summary', {
            method: 'POST',
            body: JSON.stringify({ project_id: projectId }),
        }),
};

// Chat
export const chat = {
    listChannels: () => request('/chat/channels'),
    myChannels: () => request('/chat/channels/my'),
    createChannel: (name: string, description?: string) =>
        request('/chat/channels', {
            method: 'POST',
            body: JSON.stringify({ name, description }),
        }),
};

// Dashboard
export const dashboard = {
    stats: () => request('/dashboard/'),
};

function qs(params?: Record<string, string | number | boolean | null | undefined>): string {
    if (!params) return '';
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
        if (v !== null && v !== undefined && v !== '') p.append(k, String(v));
    }
    const s = p.toString();
    return s ? `?${s}` : '';
}

// Performance
export const performance = {
    teamStats: () => request('/performance/team'),
    memberStats: (id: number) => request(`/performance/user/${id}`),
    kpiOverview: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/overview${qs(params)}`),
    kpiSprint: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/sprint${qs(params)}`),
    kpiQuality: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/quality${qs(params)}`),
    kpiMembers: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/members${qs(params)}`),
    kpiDrilldown: (params?: Record<string, string | number | boolean | null | undefined>) => request(`/performance/kpi/drilldown${qs(params)}`),
    kpiWeights: () => request('/performance/kpi/weights'),
    updateKpiWeights: (data: object) => request('/performance/kpi/weights', { method: 'PATCH', body: JSON.stringify(data) }),
    sendKpiWarningEmail: (data: { user_id: number; kpi_score: number; level: string; message?: string }) =>
        request('/performance/kpi/warning-email', { method: 'POST', body: JSON.stringify(data) }),
};

// Timeline
export const timeline = {
    get: () => request('/timeline/'),
};

// Invites
export const invites = {
    sendInvite: (email: string, role: string) =>
        request('/teams/invite', {
            method: 'POST',
            body: JSON.stringify({ email, role }),
        }),
    directAdd: (userId: number, role?: string) =>
        request('/teams/add', {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                ...(role ? { role } : {}),
            }),
        }),
    validate: (token: string) =>
        request(`/invites/validate?token=${encodeURIComponent(token)}`),
    accept: (data: {
        token: string;
        validation_code: string;
        username: string;
        full_name: string;
        password: string;
    }) =>
        request('/invites/accept', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    pending: () => request('/invites/pending'),
    cancel: (inviteId: number) =>
        request(`/invites/${inviteId}`, { method: 'DELETE' }),
};

// Status Sets
export const statusSets = {
    getDefault: () => request('/status-sets/default'),
    getEffective: (projectId?: number) =>
        request(`/status-sets/effective${projectId ? `?project_id=${projectId}` : ''}`),
    getTransitions: (statusSetId: number, includeArchived = false) =>
        request<StatusTransition[]>(
            `/status-sets/${statusSetId}/transitions${includeArchived ? '?include_archived=true' : ''}`
        ),
    replaceTransitions: (statusSetId: number, transitions: StatusTransitionPair[]) =>
        request<StatusTransition[]>(`/status-sets/${statusSetId}/transitions`, {
            method: 'POST',
            body: JSON.stringify({ transitions }),
        }),
    createStatus: (data: object) =>
        request('/status-sets/default/statuses', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    updateStatus: (statusId: number, data: object) =>
        request(`/status-sets/statuses/${statusId}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
    reorder: (statusSetId: number, statusIds: number[]) =>
        request(`/status-sets/${statusSetId}/reorder`, {
            method: 'POST',
            body: JSON.stringify({ status_ids: statusIds }),
        }),
    deleteStatus: (statusId: number, payload: { mode: string; replacement_status_id?: number }) =>
        request(`/status-sets/statuses/${statusId}/delete`, {
            method: 'POST',
            body: JSON.stringify(payload),
        }),
    createProjectOverride: (projectId: number) =>
        request(`/status-sets/projects/${projectId}/override`, { method: 'POST' }),
    revertProjectOverride: (projectId: number, fallbackMappings: Record<number, number> = {}) =>
        request(`/status-sets/projects/${projectId}/override`, {
            method: 'DELETE',
            body: JSON.stringify({ fallback_mappings: fallbackMappings }),
        }),
};

// SubTeams
export const sub_teams = {
    list: () => request('/sub-teams/'),
    create: (data: { name: string; supervisor_id?: number }) =>
        request('/sub-teams/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: { name?: string; supervisor_id?: number }) =>
        request(`/sub-teams/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),
    delete: (id: number) => request(`/sub-teams/${id}`, { method: 'DELETE' }),
};

export const reminderSettings = {
    current: () => request('/sub-teams/reminder-settings/current'),
    updateCurrent: (data: {
        lead_time_days?: number;
        sprint_reminders_enabled?: boolean;
        milestone_reminders_enabled?: boolean;
    }) =>
        request('/sub-teams/reminder-settings/current', {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
    createProposal: (data: {
        lead_time_days?: number;
        sprint_reminders_enabled?: boolean;
        milestone_reminders_enabled?: boolean;
    }) =>
        request('/sub-teams/reminder-settings/proposals', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    listProposals: () => request('/sub-teams/reminder-settings/proposals'),
    reviewProposal: (id: number, data: { decision: 'approve' | 'reject' }) =>
        request(`/sub-teams/reminder-settings/proposals/${id}/review`, {
            method: 'POST',
            body: JSON.stringify(data),
        }),
};
