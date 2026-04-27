import { request } from './request';

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
