import { request } from './request';

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
