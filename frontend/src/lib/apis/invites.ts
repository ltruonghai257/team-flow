import { request } from './request';

export const invites = {
    sendInvite: (email: string, role: string) =>
        request('/teams/invite', {
            method: 'POST',
            body: JSON.stringify({ email, role }),
        }),
    directAdd: (userId: number, role?: string) =>
        request('/teams/add', {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                ...(role ? { role } : {}),
            }),
        }),
    validate: (token: string) =>
        request(`/invites/validate?token=${encodeURIComponent(token)}`),
    accept: (data: {
        token: string;
        validation_code: string;
        username: string;
        full_name: string;
        password: string;
    }) =>
        request('/invites/accept', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    pending: () => request('/invites/pending'),
    cancel: (inviteId: number) =>
        request(`/invites/${inviteId}`, { method: 'DELETE' }),
};
