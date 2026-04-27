import { request } from './request';

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
