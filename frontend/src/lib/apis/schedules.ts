import { request } from './request';

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
