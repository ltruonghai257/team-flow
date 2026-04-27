import { request } from './request';

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
