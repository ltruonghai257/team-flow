import { request } from './request';

export const dashboard = {
    stats: () => request('/dashboard/'),
};
