import { request } from './request';

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
