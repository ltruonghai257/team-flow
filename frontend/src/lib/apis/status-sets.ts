import { request } from './request';
import type { StatusTransition, StatusTransitionPair } from '$lib/types/status';

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
