import { request } from './request';

export const updates = {
    getTemplate: () => request('/updates/template'),
    putTemplate: (data: object) =>
        request('/updates/template', { method: 'PUT', body: JSON.stringify(data) }),
    list: (params?: Record<string, string | number | null>) => {
        const filtered = Object.fromEntries(
            Object.entries(params ?? {}).filter(([, v]) => v != null)
        ) as Record<string, string>;
        const qs = Object.keys(filtered).length
            ? '?' + new URLSearchParams(filtered).toString()
            : '';
        return request(`/updates/${qs}`);
    },
    create: (data: object) =>
        request('/updates/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: object) =>
        request(`/updates/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) =>
        request(`/updates/${id}`, { method: 'DELETE' }),
};
