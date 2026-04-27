import { request } from './request';

export const timeline = {
    get: () => request('/timeline/'),
};
