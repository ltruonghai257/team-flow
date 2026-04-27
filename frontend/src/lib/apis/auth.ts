import { request } from './request';

export const auth = {
    login: (username: string, password: string) => {
        const body = new URLSearchParams({ username, password });
        return fetch('/api/auth/token', {
            method: 'POST',
            body,
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            credentials: 'include',
        }).then(async r => {
            if (!r.ok)
                throw new Error((await r.json()).detail || 'Login failed');
            return r.json();
        });
    },
    register: (data: object) =>
        request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    me: () => request('/auth/me'),
    logout: () => request('/auth/logout', { method: 'POST' }),
};
