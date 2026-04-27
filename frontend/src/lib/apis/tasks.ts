import { request } from './request';

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
