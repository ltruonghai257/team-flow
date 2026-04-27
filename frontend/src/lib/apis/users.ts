import { request } from './request';

export const users = {
    list: () => request('/users/'),
    get: (id: number) => request(`/users/${id}`),
    update: (id: number, data: object) =>
        request(`/users/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        }),
};
