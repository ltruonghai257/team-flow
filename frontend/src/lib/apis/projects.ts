import { request } from './request';

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
